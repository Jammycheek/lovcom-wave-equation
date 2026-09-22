"""Frozen minimal RCWE model and local equilibrium classification."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
from scipy.optimize import root_scalar
from scipy.special import expit


def sigmoid(value):
    """Numerically stable logistic sigmoid."""
    return expit(value)


@dataclass(frozen=True)
class RCWEParameters:
    Delta: float
    R: float
    Omega: float
    s0: float
    v0: float

    def __post_init__(self) -> None:
        if self.R <= 0 or self.Omega <= 0:
            raise ValueError("R and Omega must be positive")

    @property
    def G(self) -> float:
        return self.R * self.Omega

    def as_dict(self) -> dict[str, float]:
        result = asdict(self)
        result["G"] = self.G
        return result


def rhs(_tau: float, state: np.ndarray, params: RCWEParameters) -> np.ndarray:
    s, v = state
    return np.array(
        [params.Omega * (params.Delta - v + params.R * np.tanh(s)), -v + sigmoid(s)],
        dtype=float,
    )


def _equilibrium_function(s: float, params: RCWEParameters) -> float:
    return float(sigmoid(s) - params.Delta - params.R * np.tanh(s))


def equilibria(params: RCWEParameters, search_limit: float = 40.0) -> list[float]:
    """Return finite equilibria found by deterministic bracketing.

    The broad search range is a numerical search guard, not a scientific
    parameter bound. Roots outside it are reported as unavailable.
    """
    grid = np.linspace(-search_limit, search_limit, 4001)
    values = np.array([_equilibrium_function(x, params) for x in grid])
    roots: list[float] = []
    for left, right, f_left, f_right in zip(grid[:-1], grid[1:], values[:-1], values[1:]):
        if f_left == 0:
            root = float(left)
        elif f_left * f_right < 0:
            root = float(root_scalar(_equilibrium_function, args=(params,), bracket=(left, right)).root)
        else:
            continue
        if not roots or abs(root - roots[-1]) > 1e-7:
            roots.append(root)
    if values[-1] == 0 and (not roots or abs(grid[-1] - roots[-1]) > 1e-7):
        roots.append(float(grid[-1]))
    return roots


def classify_local_regime(params: RCWEParameters) -> dict[str, object]:
    roots = equilibria(params)
    if not roots:
        return {"classification": "no_finite_equilibrium_found", "equilibria": []}

    details = []
    for s_star in roots:
        p_star = float(sigmoid(s_star))
        derivative = p_star * (1.0 - p_star) - params.R / np.cosh(s_star) ** 2
        trace = params.Omega * params.R / np.cosh(s_star) ** 2 - 1.0
        determinant = params.Omega * derivative
        discriminant = trace * trace - 4.0 * determinant
        if determinant < 0:
            label = "saddle"
        elif trace < 0:
            label = "stable_focus" if discriminant < 0 else "stable_node"
        elif trace > 0:
            label = "unstable_focus" if discriminant < 0 else "unstable_node"
        else:
            label = "boundary"
        details.append(
            {
                "s": s_star,
                "v": p_star,
                "trace": float(trace),
                "determinant": float(determinant),
                "classification": label,
            }
        )
    primary = min(details, key=lambda item: abs(float(item["s"])))
    return {"classification": primary["classification"], "equilibria": details}
