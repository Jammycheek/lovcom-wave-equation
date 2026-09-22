"""Reference preparation and analysis for Tension Bridge Experiment v1.0."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import math
from typing import Iterable, Mapping

import numpy as np
from scipy.stats import t as student_t

WINDOW_SIZE = 5
MIN_RATERS = 12
RELIABILITY_REPEATS = 1000
RELIABILITY_GATE = 0.70
QUESTION_CODES = ("L", "T", "D")


class ModelIdentificationError(ValueError):
    """The frozen linear model cannot be identified for a specified fold."""


@dataclass(frozen=True)
class ChannelIE:
    work_id: str
    pair: str
    global_order: int
    ie_id: str
    vector: tuple[float, float, float, float]

    def __post_init__(self) -> None:
        values = np.asarray(self.vector, dtype=float)
        if values.shape != (4,) or np.any(values < 0) or not np.isclose(values.sum(), 1.0, atol=1e-12):
            raise ValueError("channel vector must be a nonnegative D/S/C/P simplex")
        if not np.allclose(values * 4.0, np.round(values * 4.0), atol=1e-12):
            raise ValueError("channel values must use the frozen 0.25 grid")


@dataclass(frozen=True)
class WindowMetric:
    window_id: str
    work_id: str
    pair: str
    ie_ids: tuple[str, str, str, str, str]
    p_ac: float
    p_switch: float

    def as_dict(self) -> dict[str, object]:
        value = asdict(self)
        value["ie_ids"] = list(self.ie_ids)
        return value


@dataclass(frozen=True)
class Rating:
    rater_id: str
    work_id: str
    window_id: str
    prior_exposure: str
    knows_future: str
    exposure_uncertain: str
    question_order: str
    l_obs: int
    t_obs: int
    d_obs: int
    future_blind: bool
    valid_primary: bool

    def __post_init__(self) -> None:
        if not self.rater_id or not self.work_id or not self.window_id:
            raise ValueError("rater_id, work_id, and window_id are required")
        for name, value in (("l_obs", self.l_obs), ("t_obs", self.t_obs), ("d_obs", self.d_obs)):
            if isinstance(value, bool) or int(value) != value or not 0 <= value <= 100:
                raise ValueError(f"{name} must be an integer from 0 to 100")
        if sorted(self.question_order.split("-")) != sorted(QUESTION_CODES):
            raise ValueError("question_order must contain L, T, and D exactly once")


@dataclass(frozen=True)
class AggregatedWindow:
    window_id: str
    work_id: str
    pair: str
    p_ac: float
    p_switch: float
    l_obs: float
    t_obs: float
    d_obs: float
    median_l_obs: float
    median_t_obs: float
    median_d_obs: float
    rating_count: int

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class ReliabilityResult:
    construct: str
    repeats_requested: int
    repeats_valid: int
    median_r_sb: float | None
    percentile_2_5: float | None
    percentile_97_5: float | None
    passed: bool

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class ActivationResult:
    passed: bool
    status: str
    eligible_windows: int
    independent_works: int
    dyads: int
    work_window_counts: dict[str, int]
    all_windows_have_min_raters: bool
    channel_reliability_passed: bool
    audience_reliability_passed: bool
    manifest_frozen: bool
    role_separation_passed: bool

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def channel_metrics(vectors: Iterable[Iterable[float]]) -> tuple[float, float]:
    matrix = np.asarray(list(vectors), dtype=float)
    if matrix.shape != (WINDOW_SIZE, 4):
        raise ValueError("a confirmatory window must contain exactly five four-channel vectors")
    if np.any(matrix < 0) or not np.allclose(matrix.sum(axis=1), 1.0, atol=1e-12):
        raise ValueError("every channel vector must lie on the D/S/C/P simplex")
    mean = matrix.mean(axis=0)
    p_ac = float(np.mean(np.sum((matrix - mean) ** 2, axis=1)))
    p_switch = float(np.mean(np.sum(np.diff(matrix, axis=0) ** 2, axis=1)))
    return p_ac, p_switch


def channel_reliability(coder_a, coder_b) -> dict[str, object]:
    a = np.asarray(coder_a, dtype=float)
    b = np.asarray(coder_b, dtype=float)
    if a.shape != b.shape or a.ndim != 2 or a.shape[1] != 4 or len(a) == 0:
        raise ValueError("coder channel arrays must be nonempty N x 4 arrays of equal shape")
    for values in (a, b):
        if np.any(values < 0) or not np.allclose(values.sum(axis=1), 1.0, atol=1e-12):
            raise ValueError("raw coder vectors must lie on the D/S/C/P simplex")
        if not np.allclose(values * 4.0, np.round(values * 4.0), atol=1e-12):
            raise ValueError("raw coder values must use the frozen 0.25 grid")
    distances = 0.5 * np.sum(np.abs(a - b), axis=1)
    median = float(np.median(distances))
    return {"median_d_tv": median, "row_count": len(a), "passed": median <= 0.25}


def build_windows(ies: Iterable[ChannelIE]) -> list[WindowMetric]:
    groups: dict[tuple[str, str], list[ChannelIE]] = {}
    for ie in ies:
        groups.setdefault((ie.work_id, ie.pair), []).append(ie)
    windows: list[WindowMetric] = []
    for (work_id, pair), group in sorted(groups.items()):
        ordered = sorted(group, key=lambda item: item.global_order)
        orders = [item.global_order for item in ordered]
        if len(orders) != len(set(orders)):
            raise ValueError(f"duplicate global_order for {work_id}/{pair}")
        complete_count = len(ordered) // WINDOW_SIZE
        for index in range(complete_count):
            chunk = ordered[index * WINDOW_SIZE : (index + 1) * WINDOW_SIZE]
            p_ac, p_switch = channel_metrics(item.vector for item in chunk)
            windows.append(
                WindowMetric(
                    window_id=f"{work_id}::{pair}::W{index + 1:03d}",
                    work_id=work_id,
                    pair=pair,
                    ie_ids=tuple(item.ie_id for item in chunk),
                    p_ac=p_ac,
                    p_switch=p_switch,
                )
            )
    return windows


def deterministic_question_order(master_seed: str | int, work_id: str, window_id: str, rater_id: str) -> str:
    prefix = f"{master_seed}|{work_id}|{window_id}|{rater_id}"
    ordered = sorted(QUESTION_CODES, key=lambda code: hashlib.sha256(f"{prefix}|{code}".encode()).digest())
    return "-".join(ordered)


def is_primary_eligible(rating: Rating) -> bool:
    return (
        rating.prior_exposure.strip().lower() == "no"
        and rating.knows_future.strip().lower() == "no"
        and rating.exposure_uncertain.strip().lower() == "no"
        and rating.future_blind
        and rating.valid_primary
    )


def validate_question_orders(ratings: Iterable[Rating], master_seed: str | int) -> None:
    for rating in ratings:
        expected = deterministic_question_order(master_seed, rating.work_id, rating.window_id, rating.rater_id)
        if rating.question_order != expected:
            raise ValueError(f"question order mismatch for {rating.rater_id}/{rating.window_id}")


def validate_role_separation(
    coder_ids_by_work: Mapping[str, set[str]],
    adjudicator_ids_by_work: Mapping[str, set[str]],
    ratings: Iterable[Rating],
) -> bool:
    raters_by_work: dict[str, set[str]] = {}
    for rating in ratings:
        raters_by_work.setdefault(rating.work_id, set()).add(rating.rater_id)
    all_works = set(coder_ids_by_work) | set(adjudicator_ids_by_work) | set(raters_by_work)
    for work_id in sorted(all_works):
        raters = raters_by_work.get(work_id, set())
        coders = set(coder_ids_by_work.get(work_id, set()))
        adjudicators = set(adjudicator_ids_by_work.get(work_id, set()))
        coder_adjudicator_overlap = coders & adjudicators
        if coder_adjudicator_overlap:
            raise ValueError(
                f"coder and adjudicator roles overlap for {work_id}: {sorted(coder_adjudicator_overlap)}"
            )
        overlap = raters & (coders | adjudicators)
        if overlap:
            raise ValueError(f"coder/adjudicator and rater roles overlap for {work_id}: {sorted(overlap)}")
    return True


def aggregate_ratings(
    windows: Iterable[WindowMetric], ratings: Iterable[Rating]
) -> tuple[list[AggregatedWindow], dict[str, str], list[Rating]]:
    window_list = list(windows)
    window_map = {window.window_id: window for window in window_list}
    if len(window_map) != len(window_list):
        raise ValueError("duplicate window_id")
    eligible = [rating for rating in ratings if is_primary_eligible(rating)]
    grouped: dict[str, list[Rating]] = {window_id: [] for window_id in window_map}
    seen: set[tuple[str, str]] = set()
    for rating in eligible:
        if rating.window_id not in window_map:
            raise ValueError(f"rating references unknown window: {rating.window_id}")
        if rating.work_id != window_map[rating.window_id].work_id:
            raise ValueError("rating work_id does not match window work_id")
        key = (rating.window_id, rating.rater_id)
        if key in seen:
            raise ValueError("duplicate rater/window rating")
        seen.add(key)
        grouped[rating.window_id].append(rating)
    aggregates: list[AggregatedWindow] = []
    statuses: dict[str, str] = {}
    for window_id, window in window_map.items():
        values = grouped[window_id]
        if len(values) < MIN_RATERS:
            statuses[window_id] = "INSUFFICIENT_RATERS"
            continue
        statuses[window_id] = "ELIGIBLE"
        l_values = np.array([rating.l_obs for rating in values], dtype=float)
        t_values = np.array([rating.t_obs for rating in values], dtype=float)
        d_values = np.array([rating.d_obs for rating in values], dtype=float)
        aggregates.append(
            AggregatedWindow(
                window_id=window_id,
                work_id=window.work_id,
                pair=window.pair,
                p_ac=window.p_ac,
                p_switch=window.p_switch,
                l_obs=float(l_values.mean()),
                t_obs=float(t_values.mean()),
                d_obs=float(d_values.mean()),
                median_l_obs=float(np.median(l_values)),
                median_t_obs=float(np.median(t_values)),
                median_d_obs=float(np.median(d_values)),
                rating_count=len(values),
            )
        )
    return aggregates, statuses, eligible


def _stable_seed(master_seed: str | int, *parts: object) -> int:
    material = "|".join(map(str, (master_seed, *parts))).encode()
    return int.from_bytes(hashlib.sha256(material).digest()[:8], "big")


def split_half_reliability(
    ratings: Iterable[Rating],
    construct: str,
    *,
    master_seed: str | int,
    repeats: int = RELIABILITY_REPEATS,
) -> ReliabilityResult:
    field = {"L": "l_obs", "T": "t_obs", "D": "d_obs"}.get(construct)
    if field is None:
        raise ValueError("construct must be L, T, or D")
    grouped: dict[str, list[Rating]] = {}
    for rating in ratings:
        if is_primary_eligible(rating):
            grouped.setdefault(rating.window_id, []).append(rating)
    grouped = {key: sorted(value, key=lambda item: item.rater_id) for key, value in grouped.items() if len(value) >= MIN_RATERS}
    corrected: list[float] = []
    if len(grouped) >= 2:
        for repeat in range(repeats):
            half_a, half_b, work_ids = [], [], []
            for window_id, values in sorted(grouped.items()):
                rng = np.random.default_rng(_stable_seed(master_seed, construct, repeat, window_id))
                order = rng.permutation(len(values))
                split = len(values) // 2
                a = [getattr(values[index], field) for index in order[:split]]
                b = [getattr(values[index], field) for index in order[split : split * 2]]
                half_a.append(float(np.mean(a)))
                half_b.append(float(np.mean(b)))
                work_ids.append(values[0].work_id)
            centered_a, centered_b = [], []
            for work_id in sorted(set(work_ids)):
                indices = [index for index, value in enumerate(work_ids) if value == work_id]
                if len(indices) < 2:
                    continue
                mean_a = float(np.mean([half_a[index] for index in indices]))
                mean_b = float(np.mean([half_b[index] for index in indices]))
                centered_a.extend(half_a[index] - mean_a for index in indices)
                centered_b.extend(half_b[index] - mean_b for index in indices)
            if len(centered_a) < 2 or np.std(centered_a) == 0 or np.std(centered_b) == 0:
                continue
            correlation = float(np.corrcoef(centered_a, centered_b)[0, 1])
            if not np.isfinite(correlation) or np.isclose(1.0 + correlation, 0.0):
                continue
            corrected.append(2.0 * correlation / (1.0 + correlation))
    if not corrected:
        return ReliabilityResult(construct, repeats, 0, None, None, None, False)
    array = np.asarray(corrected)
    median = float(np.median(array))
    return ReliabilityResult(
        construct,
        repeats,
        len(corrected),
        median,
        float(np.percentile(array, 2.5)),
        float(np.percentile(array, 97.5)),
        median >= RELIABILITY_GATE,
    )


def activation_gate(
    windows: Iterable[AggregatedWindow],
    reliability: Mapping[str, ReliabilityResult],
    *,
    channel_reliability_passed: bool,
    manifest_frozen: bool,
    role_separation_passed: bool,
) -> ActivationResult:
    data = list(windows)
    works = {window.work_id for window in data}
    dyads = {(window.work_id, window.pair) for window in data}
    counts = {work: sum(window.work_id == work for window in data) for work in sorted(works)}
    all_min_raters = all(window.rating_count >= MIN_RATERS for window in data)
    audience_passed = set(reliability) == {"L", "T", "D"} and all(reliability[key].passed for key in ("L", "T", "D"))
    measurement_failure = bool(data) and not (channel_reliability_passed and audience_passed and role_separation_passed)
    passed = (
        len(data) >= 30
        and len(works) >= 4
        and len(dyads) >= 4
        and bool(counts)
        and all(count >= 5 for count in counts.values())
        and all_min_raters
        and channel_reliability_passed
        and audience_passed
        and manifest_frozen
        and role_separation_passed
    )
    status = "READY" if passed else "MEASUREMENT_FAILURE" if measurement_failure else "INSUFFICIENT_BRIDGE_DATA"
    return ActivationResult(
        passed, status, len(data), len(works), len(dyads), counts, all_min_raters,
        channel_reliability_passed, audience_passed, manifest_frozen, role_separation_passed,
    )


def standardize_train_holdout(train: np.ndarray, holdout: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    train = np.asarray(train, dtype=float)
    holdout = np.asarray(holdout, dtype=float)
    means = train.mean(axis=0)
    scales = train.std(axis=0, ddof=0)
    if np.any(scales == 0):
        raise ModelIdentificationError("TRAIN predictor SD is zero")
    return (train - means) / scales, (holdout - means) / scales, means, scales


def ols_predictive_distribution(train_x, train_y, holdout_x) -> tuple[np.ndarray, np.ndarray, int, np.ndarray]:
    x = np.asarray(train_x, dtype=float)
    y = np.asarray(train_y, dtype=float)
    x_holdout = np.asarray(holdout_x, dtype=float)
    n, p = x.shape
    if n - p <= 0 or np.linalg.matrix_rank(x) < p:
        raise ModelIdentificationError("singular design or non-positive residual degrees of freedom")
    inverse = np.linalg.inv(x.T @ x)
    beta = inverse @ x.T @ y
    residual = y - x @ beta
    variance = float(residual @ residual / (n - p))
    if variance <= 0 or not np.isfinite(variance):
        raise ModelIdentificationError("non-positive residual variance")
    locations = x_holdout @ beta
    leverage = np.einsum("ij,jk,ik->i", x_holdout, inverse, x_holdout)
    scales = np.sqrt(variance * (1.0 + leverage))
    return locations, scales, n - p, beta


MODEL_COLUMNS = {
    "ML": (0,),
    "MLAC": (0, 2),
    "M0": (0, 1),
    "M1": (0, 1, 2),
}


def leave_one_work_out(windows: Iterable[AggregatedWindow]) -> dict[str, object]:
    data = sorted(windows, key=lambda item: (item.work_id, item.window_id))
    works = sorted({item.work_id for item in data})
    if len(works) < 2:
        raise ModelIdentificationError("leave-one-work-out requires at least two works")
    rows = []
    totals = {model: [] for model in MODEL_COLUMNS}
    for holdout_work in works:
        train = [item for item in data if item.work_id != holdout_work]
        holdout = [item for item in data if item.work_id == holdout_work]
        train_works = sorted({item.work_id for item in train})
        train_predictors = np.array([[item.l_obs, item.d_obs, item.p_ac] for item in train])
        holdout_predictors = np.array([[item.l_obs, item.d_obs, item.p_ac] for item in holdout])
        train_z, holdout_z, means, scales = standardize_train_holdout(train_predictors, holdout_predictors)
        train_y = np.array([item.t_obs for item in train])
        holdout_y = np.array([item.t_obs for item in holdout])
        for model, columns in MODEL_COLUMNS.items():
            train_design = np.column_stack([np.ones(len(train)), train_z[:, columns]])
            holdout_design = np.column_stack([np.ones(len(holdout)), holdout_z[:, columns]])
            locations, predictive_scales, df, beta = ols_predictive_distribution(train_design, train_y, holdout_design)
            log_scores = student_t.logpdf(holdout_y, df=df, loc=locations, scale=predictive_scales)
            for item, observed, location, scale, score in zip(holdout, holdout_y, locations, predictive_scales, log_scores):
                row = {
                    "holdout_work": holdout_work,
                    "window_id": item.window_id,
                    "model": model,
                    "observed_t": float(observed),
                    "predicted_t": float(location),
                    "predictive_scale": float(scale),
                    "df": int(df),
                    "log_predictive_density": float(score),
                    "train_work_count": len(works) - 1,
                    "train_works": train_works,
                    "train_predictor_means": means.tolist(),
                    "train_predictor_sds": scales.tolist(),
                    "coefficients": beta.tolist(),
                }
                rows.append(row)
                totals[model].append(float(score))
    scores = {model: math.fsum(values) for model, values in totals.items()}
    full_predictors = np.array([[item.l_obs, item.d_obs, item.p_ac] for item in data])
    full_means = full_predictors.mean(axis=0)
    full_scales = full_predictors.std(axis=0, ddof=0)
    if np.any(full_scales == 0):
        raise ModelIdentificationError("full-dataset predictor SD is zero")
    full_z = (full_predictors - full_means) / full_scales
    full_design = np.column_stack([np.ones(len(data)), full_z])
    full_y = np.array([item.t_obs for item in data])
    _locations, _scales, _df, full_beta = ols_predictive_distribution(full_design, full_y, full_design[:1])
    beta_pac = float(full_beta[3])
    delta_primary = scores["M1"] - scores["M0"]
    delta_love = scores["MLAC"] - scores["ML"]
    status = bridge_verdict(beta_pac, delta_primary)
    return {
        "predictions": rows,
        "scores": scores,
        "delta_ls_primary": delta_primary,
        "delta_ls_love": delta_love,
        "beta_pac_full": beta_pac,
        "primary_status": status,
    }


def bridge_verdict(beta_pac: float, delta_ls_primary: float, *, static_tension_failed: bool = False) -> str:
    if static_tension_failed:
        return "FAIL_STATIC_TENSION_CHALLENGE"
    if beta_pac > 0 and delta_ls_primary >= 2:
        return "SUPPORT"
    if beta_pac > 0 and 0 < delta_ls_primary < 2:
        return "INDETERMINATE"
    return "FAIL"


def static_tension_challenge(windows: Iterable[AggregatedWindow]) -> dict[str, object]:
    candidates = [item for item in windows if item.t_obs >= 75.0 and item.p_ac <= 0.02]
    works = sorted({item.work_id for item in candidates})
    failed = len(candidates) >= 3 and len(works) >= 2
    return {
        "status": "FAIL" if failed else "NOT_TRIGGERED",
        "candidate_count": len(candidates),
        "independent_works": len(works),
        "window_ids": [item.window_id for item in candidates],
    }
