"""Synthetic truth generation and developer numerical recovery fixtures."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
from scipy.optimize import least_squares

from .integrate import forecast_means
from .model import RCWEParameters, classify_local_regime
from .observation import quantize_latent


@dataclass(frozen=True)
class SyntheticScenario:
    name: str
    parameters: RCWEParameters
    sigma_true: float
    fit_count: int
    holdout_count: int

    def as_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "parameters": self.parameters.as_dict(),
            "sigma_true": self.sigma_true,
            "fit_count": self.fit_count,
            "holdout_count": self.holdout_count,
            "local_regime": classify_local_regime(self.parameters),
        }


@dataclass(frozen=True)
class SyntheticSeries:
    scenario: SyntheticScenario
    seed: int
    states: np.ndarray
    continuous_mu: np.ndarray
    latent_observation: np.ndarray
    coded_observation: np.ndarray


STRONG_STABLE = SyntheticScenario(
    "strong_stable",
    RCWEParameters(Delta=0.5, R=0.10, Omega=8.0, s0=-1.0, v0=0.20),
    sigma_true=0.08,
    fit_count=60,
    holdout_count=20,
)
STRONG_OSCILLATORY = SyntheticScenario(
    "strong_oscillatory",
    RCWEParameters(Delta=0.5, R=0.10, Omega=12.0, s0=-1.0, v0=0.20),
    sigma_true=0.08,
    fit_count=60,
    holdout_count=20,
)
DEFAULT_SCENARIOS = (STRONG_STABLE, STRONG_OSCILLATORY)


def generate_synthetic(scenario: SyntheticScenario, seed: int) -> SyntheticSeries:
    count = scenario.fit_count + scenario.holdout_count
    means, states = forecast_means(scenario.parameters, count)
    rng = np.random.default_rng(seed)
    latent = rng.normal(means, scenario.sigma_true)
    coded = quantize_latent(latent)
    return SyntheticSeries(scenario, seed, states, means, latent, coded)


def fit_continuous_fixture(
    truth: RCWEParameters,
    *,
    count: int = 60,
    start: RCWEParameters | None = None,
) -> tuple[RCWEParameters, float]:
    """Developer-only recovery from continuous means, not scientific validation."""
    target, _states = forecast_means(truth, count)
    initial = start or RCWEParameters(
        Delta=truth.Delta + 0.02,
        R=truth.R * 1.05,
        Omega=truth.Omega * 0.95,
        s0=truth.s0 + 0.05,
        v0=truth.v0 - 0.03,
    )
    x0 = np.array([initial.Delta, np.log(initial.R), np.log(initial.Omega), initial.s0, initial.v0])

    def residual(vector):
        try:
            params = RCWEParameters(
                Delta=float(vector[0]),
                R=float(np.exp(vector[1])),
                Omega=float(np.exp(vector[2])),
                s0=float(vector[3]),
                v0=float(vector[4]),
            )
            means, _ = forecast_means(params, count)
            return means - target
        except (ValueError, RuntimeError, OverflowError):
            return np.full(count, 1e6)

    result = least_squares(
        residual,
        x0,
        bounds=([-5.0, np.log(1e-4), np.log(1e-4), -12.0, -10.0], [5.0, np.log(100), np.log(100), 12, 10]),
        xtol=1e-13,
        ftol=1e-13,
        gtol=1e-13,
        max_nfev=1500,
    )
    fitted = RCWEParameters(
        Delta=float(result.x[0]),
        R=float(np.exp(result.x[1])),
        Omega=float(np.exp(result.x[2])),
        s0=float(result.x[3]),
        v0=float(result.x[4]),
    )
    return fitted, float(np.max(np.abs(residual(result.x))))
