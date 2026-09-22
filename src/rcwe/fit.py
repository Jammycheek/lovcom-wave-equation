"""FIT-only maximum-likelihood estimation for the frozen RCWE model."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import platform

import numpy as np
import scipy
from scipy.integrate import solve_ivp
from scipy.optimize import minimize

from .integrate import REFERENCE_SOLVER, forecast_means
from .model import RCWEParameters, sigmoid
from .observation import observation_log_probability


# These broad bounds prevent overflow and pathological solver calls. They are
# implementation guards, not scientific parameter bounds.
OPTIMIZER_GUARDS = {
    "Delta": (-5.0, 5.0),
    "log_R": (float(np.log(1e-4)), float(np.log(100.0))),
    "log_Omega": (float(np.log(1e-4)), float(np.log(100.0))),
    "s0": (-12.0, 12.0),
    "v0": (-10.0, 10.0),
    "log_sigma_excess": (float(np.log(1e-8)), float(np.log(5.0))),
}
_BOUNDS = list(OPTIMIZER_GUARDS.values())
FROZEN_OPTIMIZER = {
    "method": "L-BFGS-B",
    "maxiter": 80,
    "ftol": 1e-12,
    "gtol": 1e-7,
    "start_agreement_log_likelihood_tolerance": 1e-6,
}


@dataclass(frozen=True)
class StartResult:
    initial_vector: tuple[float, ...]
    converged: bool
    status: int
    message: str
    iterations: int
    final_vector: tuple[float, ...]
    log_likelihood: float

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class RCWEFit:
    parameters: RCWEParameters
    sigma_pred: float
    sigma_lower_bound: float
    terminal_state: tuple[float, float]
    fit_log_likelihood: float
    converged: bool
    optimizer_agreement: bool
    successful_starts: int
    top_two_log_likelihood_gap: float | None
    starts: tuple[StartResult, ...]
    seed: int | None

    def as_dict(self) -> dict[str, object]:
        return {
            "parameters": self.parameters.as_dict(),
            "sigma_pred": self.sigma_pred,
            "sigma_lower_bound": self.sigma_lower_bound,
            "terminal_state": list(self.terminal_state),
            "fit_log_likelihood": self.fit_log_likelihood,
            "converged": self.converged,
            "optimizer_agreement": self.optimizer_agreement,
            "successful_starts": self.successful_starts,
            "top_two_log_likelihood_gap": self.top_two_log_likelihood_gap,
            "starts": [start.as_dict() for start in self.starts],
            "seed": self.seed,
            "solver": REFERENCE_SOLVER.as_dict(),
            "optimizer": "scipy.optimize.minimize/L-BFGS-B",
            "optimizer_settings": FROZEN_OPTIMIZER,
            "optimizer_guards": OPTIMIZER_GUARDS,
            "environment": software_versions(),
        }


def software_versions() -> dict[str, str]:
    return {
        "python": platform.python_version(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
    }


def _decode(vector: np.ndarray, sigma_lower_bound: float) -> tuple[RCWEParameters, float]:
    params = RCWEParameters(
        Delta=float(vector[0]),
        R=float(np.exp(vector[1])),
        Omega=float(np.exp(vector[2])),
        s0=float(vector[3]),
        v0=float(vector[4]),
    )
    sigma = float(sigma_lower_bound + np.exp(vector[5]))
    return params, sigma


def _trajectory_with_sensitivities(params: RCWEParameters, count: int) -> tuple[np.ndarray, np.ndarray]:
    """Integrate states and sensitivities for Delta, logR, logOmega, s0, v0."""
    initial_sensitivity = np.zeros((2, 5), dtype=float)
    initial_sensitivity[0, 3] = 1.0
    initial_sensitivity[1, 4] = 1.0
    initial = np.concatenate(([params.s0, params.v0], initial_sensitivity.ravel()))

    def augmented_rhs(_tau, augmented):
        s, v = augmented[:2]
        sensitivity = augmented[2:].reshape(2, 5)
        p = float(sigmoid(s))
        tanh_s = float(np.tanh(s))
        sech_squared = 1.0 / float(np.cosh(s)) ** 2
        f1 = params.Omega * (params.Delta - v + params.R * tanh_s)
        f2 = -v + p
        state_jacobian = np.array(
            [[params.Omega * params.R * sech_squared, -params.Omega], [p * (1.0 - p), -1.0]]
        )
        direct = np.zeros((2, 5), dtype=float)
        direct[0, 0] = params.Omega
        direct[0, 1] = params.Omega * params.R * tanh_s
        direct[0, 2] = f1
        sensitivity_derivative = state_jacobian @ sensitivity + direct
        return np.concatenate(([f1, f2], sensitivity_derivative.ravel()))

    times = np.arange(count, dtype=float)
    solution = solve_ivp(
        augmented_rhs,
        (0.0, float(count - 1)),
        initial,
        method=REFERENCE_SOLVER.method,
        t_eval=times,
        rtol=REFERENCE_SOLVER.rtol,
        atol=REFERENCE_SOLVER.atol,
        max_step=REFERENCE_SOLVER.max_step,
    )
    if not solution.success:
        raise RuntimeError(solution.message)
    states = solution.y[:2].T
    sensitivities = solution.y[2:].T.reshape(count, 2, 5)
    return states, sensitivities


def _log_likelihood_and_gradient(
    observed: np.ndarray, vector: np.ndarray, sigma_lower_bound: float
) -> tuple[float, np.ndarray]:
    """Likelihood and analytic ODE-sensitivity gradient.

    Observation-score derivatives are centered numerical derivatives of the
    stable scalar log-probability. They do not alter or floor probabilities.
    """
    try:
        params, sigma = _decode(vector, sigma_lower_bound)
        states, sensitivities = _trajectory_with_sensitivities(params, len(observed))
        means = np.asarray(sigmoid(states[:, 0]), dtype=float)
        dmu_dtheta = means[:, None] * (1.0 - means[:, None]) * sensitivities[:, 0, :]
        log_values = np.empty(len(observed))
        dlog_dmu = np.empty(len(observed))
        dlog_dsigma = np.empty(len(observed))
        mu_step = 1e-6
        sigma_step = min(max(1e-8, sigma * 1e-5), (sigma - sigma_lower_bound) * 0.49)
        sigma_step = max(sigma_step, 1e-12)
        for index, (actual, mu) in enumerate(zip(observed, means)):
            log_values[index] = observation_log_probability(float(actual), float(mu), sigma)
            plus = observation_log_probability(float(actual), float(mu + mu_step), sigma)
            minus = observation_log_probability(float(actual), float(mu - mu_step), sigma)
            dlog_dmu[index] = (plus - minus) / (2.0 * mu_step)
            plus_sigma = observation_log_probability(float(actual), float(mu), sigma + sigma_step)
            minus_sigma = observation_log_probability(float(actual), float(mu), sigma - sigma_step)
            dlog_dsigma[index] = (plus_sigma - minus_sigma) / (2.0 * sigma_step)
        likelihood = float(np.sum(log_values))
        gradient = np.empty(6, dtype=float)
        gradient[:5] = dmu_dtheta.T @ dlog_dmu
        gradient[5] = float(np.sum(dlog_dsigma)) * float(np.exp(vector[5]))
        if not np.isfinite(likelihood) or not np.all(np.isfinite(gradient)):
            raise FloatingPointError("non-finite likelihood gradient")
        return likelihood, gradient
    except (ValueError, RuntimeError, FloatingPointError, OverflowError):
        return -1e300, np.zeros(6, dtype=float)


def predefined_starts(observed, sigma_lower_bound: float) -> list[np.ndarray]:
    del observed  # Frozen starts must not encode a synthetic truth or the first outcome.
    sigma = lambda value: np.log(max(value - sigma_lower_bound, 1e-5))
    return [
        np.array([0.25, np.log(0.03), np.log(3.0), -2.0, 0.80, sigma(0.20)]),
        np.array([0.75, np.log(0.30), np.log(20.0), 2.0, 0.20, sigma(0.05)]),
        np.array([0.40, np.log(0.05), np.log(15.0), 1.5, 0.80, sigma(0.15)]),
        np.array([0.60, np.log(0.25), np.log(5.0), -1.5, 0.20, sigma(0.30)]),
    ]


def fit_rcwe(
    observed,
    *,
    sigma_lower_bound: float = 1e-6,
    starts: list[np.ndarray] | None = None,
    random_starts: int = 0,
    seed: int | None = None,
    maxiter: int = int(FROZEN_OPTIMIZER["maxiter"]),
) -> RCWEFit:
    """Fit only the supplied FIT observations using multiple starts."""
    y = np.asarray(observed, dtype=float)
    if y.ndim != 1 or len(y) < 2:
        raise ValueError("at least two FIT observations are required")
    if sigma_lower_bound <= 0:
        raise ValueError("sigma lower bound must be positive")
    all_starts = list(predefined_starts(y, sigma_lower_bound) if starts is None else starts)
    rng = np.random.default_rng(seed)
    for _ in range(random_starts):
        all_starts.append(
            np.array(
                [
                    rng.uniform(0.0, 1.0),
                    rng.uniform(np.log(0.02), np.log(0.5)),
                    rng.uniform(np.log(1.0), np.log(20.0)),
                    rng.uniform(-2.0, 2.0),
                    rng.uniform(0.0, 1.0),
                    rng.uniform(np.log(0.02), np.log(0.5)),
                ]
            )
        )
    if len(all_starts) < 2:
        raise ValueError("multiple-start optimization requires at least two starts")

    records: list[StartResult] = []
    optimizer_results = []
    for initial in all_starts:
        def objective(vector):
            likelihood, gradient = _log_likelihood_and_gradient(y, vector, sigma_lower_bound)
            return -likelihood, -gradient

        result = minimize(
            objective,
            np.asarray(initial, dtype=float),
            method="L-BFGS-B",
            jac=True,
            bounds=_BOUNDS,
            options={"maxiter": maxiter, "ftol": FROZEN_OPTIMIZER["ftol"], "gtol": FROZEN_OPTIMIZER["gtol"]},
        )
        log_likelihood = -float(result.fun)
        records.append(
            StartResult(
                initial_vector=tuple(float(x) for x in initial),
                converged=bool(result.success),
                status=int(result.status),
                message=str(result.message),
                iterations=int(result.nit),
                final_vector=tuple(float(x) for x in result.x),
                log_likelihood=log_likelihood,
            )
        )
        optimizer_results.append(result)

    converged = [(record, result) for record, result in zip(records, optimizer_results) if record.converged]
    candidates = converged or list(zip(records, optimizer_results))
    best_record, best_result = max(candidates, key=lambda pair: pair[0].log_likelihood)
    ranked_likelihoods = sorted((record.log_likelihood for record, _ in converged), reverse=True)
    gap = ranked_likelihoods[0] - ranked_likelihoods[1] if len(ranked_likelihoods) >= 2 else None
    agreement = gap is not None and gap <= float(FROZEN_OPTIMIZER["start_agreement_log_likelihood_tolerance"])
    params, sigma = _decode(best_result.x, sigma_lower_bound)
    _means, states = forecast_means(params, len(y))
    return RCWEFit(
        parameters=params,
        sigma_pred=sigma,
        sigma_lower_bound=sigma_lower_bound,
        terminal_state=tuple(float(x) for x in states[-1]),
        fit_log_likelihood=best_record.log_likelihood,
        converged=agreement,
        optimizer_agreement=agreement,
        successful_starts=len(converged),
        top_two_log_likelihood_gap=gap,
        starts=tuple(records),
        seed=seed,
    )


def forecast_holdout(fit: RCWEFit, count: int) -> np.ndarray:
    """Forecast from frozen FIT terminal state without observations."""
    means, _states = forecast_means(
        fit.parameters,
        count,
        initial_state=fit.terminal_state,
        include_initial=False,
    )
    return means
