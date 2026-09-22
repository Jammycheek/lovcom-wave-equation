"""FIT-only open-loop predictive baselines."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
from scipy.optimize import minimize, minimize_scalar

from .observation import observation_log_probability


@dataclass(frozen=True)
class BaselineFit:
    name: str
    coefficients: dict[str, float]
    sigma_pred: float
    sigma_lower_bound: float
    fit_log_likelihood: float
    converged: bool
    fit_count: int

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def _likelihood(y: np.ndarray, means: np.ndarray, sigma: float) -> float:
    return float(
        np.sum([observation_log_probability(float(actual), float(mu), sigma) for actual, mu in zip(y, means)])
    )


def _fit_scale(y: np.ndarray, means: np.ndarray, lower: float) -> tuple[float, float, bool]:
    result = minimize_scalar(
        lambda log_excess: -_likelihood(y, means, lower + np.exp(log_excess)),
        bounds=(np.log(1e-8), np.log(5.0)),
        method="bounded",
        options={"xatol": 1e-11},
    )
    sigma = float(lower + np.exp(result.x))
    return sigma, -float(result.fun), bool(result.success)


def fit_persistence(observed_fit, *, sigma_lower_bound: float = 1e-6) -> BaselineFit:
    y = np.asarray(observed_fit, dtype=float)
    if len(y) < 2:
        raise ValueError("persistence needs at least two FIT observations")
    sigma, likelihood, converged = _fit_scale(y[1:], y[:-1], sigma_lower_bound)
    return BaselineFit(
        name="persistence",
        coefficients={"last_fit": float(y[-1])},
        sigma_pred=sigma,
        sigma_lower_bound=sigma_lower_bound,
        fit_log_likelihood=likelihood,
        converged=converged,
        fit_count=len(y),
    )


def forecast_persistence(fit: BaselineFit, count: int) -> np.ndarray:
    return np.full(count, fit.coefficients["last_fit"], dtype=float)


def _fit_regression_likelihood(y, design, names, lower, starts) -> BaselineFit:
    y = np.asarray(y, dtype=float)
    design = np.asarray(design, dtype=float)

    def objective(vector):
        means = design @ vector[:-1]
        sigma = lower + np.exp(vector[-1])
        return -_likelihood(y, means, sigma)

    results = [
        minimize(
            objective,
            np.asarray(start, dtype=float),
            method="L-BFGS-B",
            bounds=[(-5.0, 5.0)] * (design.shape[1]) + [(np.log(1e-8), np.log(5.0))],
            options={"maxiter": 500, "ftol": 1e-12},
        )
        for start in starts
    ]
    successful = [result for result in results if result.success]
    best = min(successful or results, key=lambda result: result.fun)
    coefficients = {name: float(value) for name, value in zip(names, best.x[:-1])}
    return BaselineFit(
        name="ar1" if names == ("alpha", "phi") else "quadratic_narrative_position",
        coefficients=coefficients,
        sigma_pred=float(lower + np.exp(best.x[-1])),
        sigma_lower_bound=lower,
        fit_log_likelihood=-float(best.fun),
        converged=bool(successful),
        fit_count=len(y) + (1 if names == ("alpha", "phi") else 0),
    )


def fit_ar1(observed_fit, *, sigma_lower_bound: float = 1e-6) -> BaselineFit:
    y = np.asarray(observed_fit, dtype=float)
    if len(y) < 3:
        raise ValueError("AR(1) needs at least three FIT observations")
    design = np.column_stack([np.ones(len(y) - 1), y[:-1]])
    starts = [
        [float(np.mean(y)), 0.0, np.log(0.1)],
        [0.0, 1.0, np.log(0.1)],
        [0.5, 0.5, np.log(0.25)],
    ]
    return _fit_regression_likelihood(y[1:], design, ("alpha", "phi"), sigma_lower_bound, starts)


def forecast_ar1(fit: BaselineFit, count: int, *, last_fit: float) -> np.ndarray:
    result = np.empty(count, dtype=float)
    previous = float(last_fit)
    for index in range(count):
        previous = fit.coefficients["alpha"] + fit.coefficients["phi"] * previous
        result[index] = previous
    return result


def narrative_position_indices(fit_count: int, total_count: int) -> tuple[np.ndarray, float, float]:
    if fit_count < 2 or total_count < fit_count:
        raise ValueError("invalid narrative-position lengths")
    fit_indices = np.arange(fit_count, dtype=float)
    mean = float(np.mean(fit_indices))
    scale = float(np.std(fit_indices, ddof=0))
    return (np.arange(total_count, dtype=float) - mean) / scale, mean, scale


def fit_narrative_position(observed_fit, *, sigma_lower_bound: float = 1e-6) -> BaselineFit:
    y = np.asarray(observed_fit, dtype=float)
    z, mean, scale = narrative_position_indices(len(y), len(y))
    design = np.column_stack([np.ones(len(y)), z, z * z])
    starts = [
        [float(np.mean(y)), 0.0, 0.0, np.log(0.1)],
        [0.5, 0.1, 0.0, np.log(0.25)],
        [0.5, 0.0, 0.1, np.log(0.25)],
    ]
    result = _fit_regression_likelihood(y, design, ("a", "b", "c"), sigma_lower_bound, starts)
    coefficients = dict(result.coefficients)
    coefficients.update({"fit_index_mean": mean, "fit_index_sd": scale})
    return BaselineFit(
        name=result.name,
        coefficients=coefficients,
        sigma_pred=result.sigma_pred,
        sigma_lower_bound=result.sigma_lower_bound,
        fit_log_likelihood=result.fit_log_likelihood,
        converged=result.converged,
        fit_count=len(y),
    )


def forecast_narrative_position(fit: BaselineFit, count: int) -> np.ndarray:
    indices = np.arange(fit.fit_count, fit.fit_count + count, dtype=float)
    z = (indices - fit.coefficients["fit_index_mean"]) / fit.coefficients["fit_index_sd"]
    return fit.coefficients["a"] + fit.coefficients["b"] * z + fit.coefficients["c"] * z * z
