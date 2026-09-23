"""Frozen Subject 6 prequential comparison of M_A and M_B."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from typing import Iterable

PAIRS = ("KM", "KT", "KB")
CATEGORIES = ("-1", "0", "+1", "mixed")
ALPHA = 1.0
DIRECTION_KAPPA_GATE = 0.70


@dataclass(frozen=True)
class Subject6Row:
    global_order: int
    pair_ie_order: int
    ie_id: str
    pair: str
    r_dir: str
    x_shared: int
    source_locator: str
    direction_adjudicated: bool
    shared_event_adjudicated: bool

    def __post_init__(self) -> None:
        if self.global_order < 0:
            raise ValueError("global_order must be nonnegative")
        if not 1 <= self.pair_ie_order <= 10:
            raise ValueError("pair_ie_order must be in the frozen range 1..10")
        if not self.ie_id:
            raise ValueError("ie_id is required")
        if not self.source_locator:
            raise ValueError("source_locator is required")
        if self.pair not in PAIRS:
            raise ValueError(f"invalid pair: {self.pair!r}")
        if self.r_dir not in CATEGORIES:
            raise ValueError(f"invalid r_dir: {self.r_dir!r}")
        if self.x_shared not in (0, 1):
            raise ValueError("x_shared must be 0 or 1")
        if not self.direction_adjudicated:
            raise ValueError("confirmatory scoring requires adjudicated Direction")
        if not self.shared_event_adjudicated:
            raise ValueError("confirmatory scoring requires adjudicated shared-event exposure")


@dataclass(frozen=True)
class PredictionRow:
    global_order: int
    pair_ie_order: int
    ie_id: str
    pair: str
    r_dir: str
    x_shared: int
    source_locator: str
    p_a_observed: float
    p_b_observed: float
    ls_a: float
    ls_b: float
    delta_ls: float
    p_a_minus1: float
    p_a_zero: float
    p_a_plus1: float
    p_a_mixed: float
    p_b_minus1: float
    p_b_zero: float
    p_b_plus1: float
    p_b_mixed: float

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class ScoreSummary:
    scope: str
    row_count: int
    ls_a: float
    ls_b: float
    delta_ls: float
    mean_ls_a: float | None
    mean_ls_b: float | None

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class ActivationGate:
    passed: bool
    total_rows: int
    x_shared_0_rows: int
    x_shared_1_rows: int
    pairs_with_both_exposures: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class ComparisonResult:
    predictions: tuple[PredictionRow, ...]
    pooled: ScoreSummary
    pair_summaries: tuple[ScoreSummary, ...]
    activation_gate: ActivationGate
    status: str

    def as_dict(self) -> dict[str, object]:
        return {
            "pooled": self.pooled.as_dict(),
            "pair_summaries": [summary.as_dict() for summary in self.pair_summaries],
            "activation_gate": self.activation_gate.as_dict(),
            "status": self.status,
        }


class _DirichletCategorical:
    def __init__(self, keys: Iterable[object]):
        self._counts = {key: {category: 0 for category in CATEGORIES} for key in keys}

    def probabilities(self, key: object) -> dict[str, float]:
        counts = self._counts[key]
        denominator = sum(counts.values()) + len(CATEGORIES) * ALPHA
        return {category: (counts[category] + ALPHA) / denominator for category in CATEGORIES}

    def update(self, key: object, category: str) -> None:
        self._counts[key][category] += 1

    def counts(self, key: object) -> dict[str, int]:
        return dict(self._counts[key])


def ordered_rows(rows: Iterable[Subject6Row]) -> list[Subject6Row]:
    result = sorted(rows, key=lambda row: row.global_order)
    orders = [row.global_order for row in result]
    if len(orders) != len(set(orders)):
        raise ValueError("duplicate global_order is not allowed")
    if len(result) > 30:
        raise ValueError("Subject 6 confirmatory corpus is capped at 10 qualified IEs per pair")
    pair_orders = [(row.pair, row.pair_ie_order) for row in result]
    if len(pair_orders) != len(set(pair_orders)):
        raise ValueError("duplicate pair_ie_order is not allowed")
    return result


def activation_gate(rows: Iterable[Subject6Row]) -> ActivationGate:
    data = list(rows)
    x0 = sum(row.x_shared == 0 for row in data)
    x1 = sum(row.x_shared == 1 for row in data)
    both = tuple(
        pair
        for pair in PAIRS
        if {row.x_shared for row in data if row.pair == pair} == {0, 1}
    )
    passed = len(data) >= 12 and x0 >= 4 and x1 >= 4 and len(both) >= 2
    return ActivationGate(passed, len(data), x0, x1, both)


def _summary(scope: str, rows: list[PredictionRow]) -> ScoreSummary:
    ls_a = math.fsum(row.ls_a for row in rows)
    ls_b = math.fsum(row.ls_b for row in rows)
    count = len(rows)
    return ScoreSummary(
        scope=scope,
        row_count=count,
        ls_a=ls_a,
        ls_b=ls_b,
        delta_ls=ls_b - ls_a,
        mean_ls_a=ls_a / count if count else None,
        mean_ls_b=ls_b / count if count else None,
    )


def verdict(delta_ls: float) -> str:
    if delta_ls >= 2.0:
        return "PRACTICAL_SUPPORT_M_B"
    if delta_ls <= -2.0:
        return "PRACTICAL_SUPPORT_M_A"
    return "INDETERMINATE"


def compare(rows: Iterable[Subject6Row]) -> ComparisonResult:
    """Predict, record, reveal, score, then update in global order."""
    data = ordered_rows(rows)
    model_a = _DirichletCategorical(PAIRS)
    model_b = _DirichletCategorical((pair, exposure) for pair in PAIRS for exposure in (0, 1))
    predictions: list[PredictionRow] = []
    for row in data:
        probabilities_a = model_a.probabilities(row.pair)
        probabilities_b = model_b.probabilities((row.pair, row.x_shared))
        p_a = probabilities_a[row.r_dir]
        p_b = probabilities_b[row.r_dir]
        predictions.append(
            PredictionRow(
                global_order=row.global_order,
                pair_ie_order=row.pair_ie_order,
                ie_id=row.ie_id,
                pair=row.pair,
                r_dir=row.r_dir,
                x_shared=row.x_shared,
                source_locator=row.source_locator,
                p_a_observed=p_a,
                p_b_observed=p_b,
                ls_a=math.log(p_a),
                ls_b=math.log(p_b),
                delta_ls=math.log(p_b) - math.log(p_a),
                p_a_minus1=probabilities_a["-1"],
                p_a_zero=probabilities_a["0"],
                p_a_plus1=probabilities_a["+1"],
                p_a_mixed=probabilities_a["mixed"],
                p_b_minus1=probabilities_b["-1"],
                p_b_zero=probabilities_b["0"],
                p_b_plus1=probabilities_b["+1"],
                p_b_mixed=probabilities_b["mixed"],
            )
        )
        model_a.update(row.pair, row.r_dir)
        model_b.update((row.pair, row.x_shared), row.r_dir)

    pooled = _summary("pooled", predictions)
    pair_summaries = tuple(_summary(pair, [row for row in predictions if row.pair == pair]) for pair in PAIRS)
    gate = activation_gate(data)
    status = verdict(pooled.delta_ls) if gate.passed else "INSUFFICIENT_SHARED_EVENT_EXPOSURE"
    return ComparisonResult(tuple(predictions), pooled, pair_summaries, gate, status)


def parse_boolean(value: str, field: str) -> bool:
    normalized = value.strip().lower()
    if normalized in ("true", "1", "yes"):
        return True
    if normalized in ("false", "0", "no"):
        return False
    raise ValueError(f"{field} must be an explicit boolean")


def row_from_mapping(mapping: dict[str, str]) -> Subject6Row:
    required = (
        "global_order",
        "pair_ie_order",
        "ie_id",
        "pair",
        "r_dir",
        "x_shared",
        "source_locator",
        "direction_adjudicated",
        "shared_event_adjudicated",
    )
    missing = [field for field in required if field not in mapping]
    if missing:
        raise ValueError(f"missing required columns: {', '.join(missing)}")
    return Subject6Row(
        global_order=int(mapping["global_order"]),
        pair_ie_order=int(mapping["pair_ie_order"]),
        ie_id=mapping["ie_id"].strip(),
        pair=mapping["pair"].strip(),
        r_dir=mapping["r_dir"].strip(),
        x_shared=int(mapping["x_shared"]),
        source_locator=mapping["source_locator"].strip(),
        direction_adjudicated=parse_boolean(mapping["direction_adjudicated"], "direction_adjudicated"),
        shared_event_adjudicated=parse_boolean(mapping["shared_event_adjudicated"], "shared_event_adjudicated"),
    )
