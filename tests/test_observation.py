import numpy as np
import pytest

from rcwe.observation import (
    BIN_BOUNDARIES,
    category_log_probabilities,
    coder_scale_lower_bound,
    log_normal_interval_prob,
    observation_log_probability,
)


@pytest.mark.parametrize("mu", np.linspace(-1.0, 2.0, 13))
@pytest.mark.parametrize("sigma", [1e-3, 0.01, 0.1, 0.5, 2.0])
def test_five_bin_probabilities_sum_to_one(mu, sigma):
    probabilities = np.exp(category_log_probabilities(mu, sigma))
    assert abs(float(np.sum(probabilities)) - 1.0) <= 1e-12


def test_edge_bins_are_unbounded_tails():
    assert np.isclose(
        observation_log_probability(0.0, 0.2, 0.1),
        log_normal_interval_prob(-np.inf, BIN_BOUNDARIES[1], 0.2, 0.1),
    )
    assert np.isclose(
        observation_log_probability(1.0, 0.8, 0.1),
        log_normal_interval_prob(BIN_BOUNDARIES[-2], np.inf, 0.8, 0.1),
    )


def test_extreme_tail_log_probability_remains_finite_without_floor():
    value = log_normal_interval_prob(0.375, 0.625, -20.0, 0.01)
    assert np.isfinite(value)
    assert value < -1e6


def test_interval_helper_handles_full_line_and_interior():
    assert log_normal_interval_prob(-np.inf, np.inf, 0.0, 1.0) == 0.0
    assert np.isfinite(log_normal_interval_prob(-0.1, 0.2, 0.0, 1.0))


def test_zero_coder_disagreement_uses_reportable_floor():
    lower, inactive = coder_scale_lower_bound([0.5, 0.5], [0.5, 0.5])
    assert lower == 1e-6
    assert inactive is True
