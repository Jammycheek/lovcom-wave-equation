"""Deterministic interaction-clock integration for RCWE."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
from scipy.integrate import solve_ivp

from .model import RCWEParameters, rhs, sigmoid


@dataclass(frozen=True)
class SolverConfig:
    method: str = "DOP853"
    rtol: float = 1e-9
    atol: float = 1e-11
    max_step: float = 0.05

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


REFERENCE_SOLVER = SolverConfig()


def integrate_states(
    params: RCWEParameters,
    count: int,
    *,
    initial_state: tuple[float, float] | None = None,
    include_initial: bool = True,
    config: SolverConfig = REFERENCE_SOLVER,
) -> np.ndarray:
    """Integrate a number of qualified interaction-index observations.

    With ``include_initial=True``, the first returned row is the supplied
    state at interaction index zero. With it false, rows are at indices
    one through ``count``; this is used for open-loop holdout forecasting.
    """
    if count < 0:
        raise ValueError("count cannot be negative")
    if count == 0:
        return np.empty((0, 2), dtype=float)
    state0 = np.asarray((params.s0, params.v0) if initial_state is None else initial_state, dtype=float)
    if include_initial:
        if count == 1:
            return state0.reshape(1, 2)
        times = np.arange(count, dtype=float)
        horizon = float(count - 1)
    else:
        times = np.arange(1, count + 1, dtype=float)
        horizon = float(count)
    solution = solve_ivp(
        rhs,
        (0.0, horizon),
        state0,
        args=(params,),
        method=config.method,
        t_eval=times,
        rtol=config.rtol,
        atol=config.atol,
        max_step=config.max_step,
    )
    if not solution.success or solution.y.shape[1] != len(times):
        raise RuntimeError(f"RCWE integration failed: {solution.message}")
    return solution.y.T


def forecast_means(
    params: RCWEParameters,
    count: int,
    *,
    initial_state: tuple[float, float] | None = None,
    include_initial: bool = True,
    config: SolverConfig = REFERENCE_SOLVER,
) -> tuple[np.ndarray, np.ndarray]:
    states = integrate_states(
        params,
        count,
        initial_state=initial_state,
        include_initial=include_initial,
        config=config,
    )
    return np.asarray(sigmoid(states[:, 0]), dtype=float), states


def qualified_values(values, qualified) -> np.ndarray:
    """Remove gaps before assigning interaction indices.

    Gaps are neither scored zeros nor elapsed interaction-clock steps.
    """
    values_array = np.asarray(values, dtype=float)
    mask = np.asarray(qualified, dtype=bool)
    if values_array.shape != mask.shape:
        raise ValueError("values and qualified mask must have the same shape")
    return values_array[mask]
