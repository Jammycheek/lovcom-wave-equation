"""Five-bin discretized Gaussian observation model."""

from __future__ import annotations

import math

import numpy as np
from scipy.special import log_ndtr

VALID_OBSERVATIONS = np.array([0.0, 0.25, 0.5, 0.75, 1.0])
BIN_BOUNDARIES = np.array([-np.inf, 0.125, 0.375, 0.625, 0.875, np.inf])


def _logdiffexp(log_a: float, log_b: float) -> float:
    """Return log(exp(log_a) - exp(log_b)) for log_a >= log_b."""
    if log_b == -np.inf:
        return float(log_a)
    if log_b > log_a:
        raise ValueError("log-difference arguments are reversed")
    if log_a == log_b:
        return -np.inf
    return float(log_a + np.log(-np.expm1(log_b - log_a)))


def log_normal_interval_prob(lo: float, hi: float, mu: float, sigma: float) -> float:
    """Stable log probability for ``lo < Normal(mu,sigma) <= hi``."""
    if sigma <= 0 or not np.isfinite(sigma):
        raise ValueError("sigma must be finite and positive")
    if lo >= hi:
        raise ValueError("lo must be smaller than hi")
    if math.isinf(lo) and lo < 0 and math.isinf(hi) and hi > 0:
        return 0.0
    z_lo = (lo - mu) / sigma
    z_hi = (hi - mu) / sigma
    if math.isinf(lo) and lo < 0:
        return float(log_ndtr(z_hi))
    if math.isinf(hi) and hi > 0:
        return float(log_ndtr(-z_lo))
    if z_lo >= 0:
        return _logdiffexp(float(log_ndtr(-z_lo)), float(log_ndtr(-z_hi)))
    return _logdiffexp(float(log_ndtr(z_hi)), float(log_ndtr(z_lo)))


def category_log_probabilities(mu: float, sigma: float) -> np.ndarray:
    return np.array(
        [
            log_normal_interval_prob(lo, hi, mu, sigma)
            for lo, hi in zip(BIN_BOUNDARIES[:-1], BIN_BOUNDARIES[1:])
        ],
        dtype=float,
    )


def observation_index(y: float) -> int:
    matches = np.flatnonzero(np.isclose(VALID_OBSERVATIONS, y, atol=1e-12, rtol=0.0))
    if len(matches) != 1:
        raise ValueError(f"invalid coded observation: {y!r}")
    return int(matches[0])


def observation_log_probability(y: float, mu: float, sigma: float) -> float:
    return float(category_log_probabilities(mu, sigma)[observation_index(y)])


def quantize_latent(values) -> np.ndarray:
    values_array = np.asarray(values, dtype=float)
    indices = np.digitize(values_array, BIN_BOUNDARIES[1:-1], right=True)
    return VALID_OBSERVATIONS[indices]


def coder_scale_lower_bound(coder_a, coder_b) -> tuple[float, bool]:
    a = np.asarray(coder_a, dtype=float)
    b = np.asarray(coder_b, dtype=float)
    if a.shape != b.shape or a.size == 0:
        raise ValueError("coder arrays must be nonempty and have equal shapes")
    raw = float(np.sqrt(np.sum((a - b) ** 2) / (2.0 * a.size)))
    inactive_floor = raw == 0.0
    return (1e-6 if inactive_floor else raw), inactive_floor
