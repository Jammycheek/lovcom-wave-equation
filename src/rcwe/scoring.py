"""Per-interaction and aggregate predictive scoring."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math

import numpy as np

from .observation import observation_log_probability


@dataclass(frozen=True)
class ScoreRow:
    interaction_index: int
    observed: float
    predicted_mu: float
    probability: float
    log_probability: float
    absolute_error: float

    def as_dict(self) -> dict[str, float | int]:
        return asdict(self)


@dataclass(frozen=True)
class ScoreResult:
    rows: tuple[ScoreRow, ...]
    LS_total: float
    LS_mean_per_IE: float
    MAE: float

    def as_dict(self) -> dict[str, object]:
        return {
            "LS_total": self.LS_total,
            "LS_mean_per_IE": self.LS_mean_per_IE,
            "MAE": self.MAE,
            "rows": [row.as_dict() for row in self.rows],
        }


def score_predictions(observed, predicted_mu, sigma: float, *, start_index: int = 0) -> ScoreResult:
    y = np.asarray(observed, dtype=float)
    mu = np.asarray(predicted_mu, dtype=float)
    if y.shape != mu.shape or y.ndim != 1 or y.size == 0:
        raise ValueError("observed and predicted_mu must be nonempty one-dimensional arrays")
    rows = []
    for offset, (actual, forecast) in enumerate(zip(y, mu)):
        log_probability = observation_log_probability(float(actual), float(forecast), sigma)
        rows.append(
            ScoreRow(
                interaction_index=start_index + offset,
                observed=float(actual),
                predicted_mu=float(forecast),
                probability=float(np.exp(log_probability)),
                log_probability=log_probability,
                absolute_error=abs(float(actual - forecast)),
            )
        )
    total = float(math.fsum(row.log_probability for row in rows))
    return ScoreResult(
        rows=tuple(rows),
        LS_total=total,
        LS_mean_per_IE=total / len(rows),
        MAE=float(np.mean([row.absolute_error for row in rows])),
    )
