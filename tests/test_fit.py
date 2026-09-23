from types import SimpleNamespace

import numpy as np
import pytest

import rcwe.fit as fit_module
from rcwe.fit import _decode, _log_likelihood_and_gradient, fit_rcwe, predefined_starts
from rcwe.integrate import forecast_means
from rcwe.synthetic import DEFAULT_SCENARIOS


OBSERVED = np.array([0.0, 0.25, 0.5, 0.75, 1.0, 0.75, 0.5, 0.25])
LOWER = 1e-6


def test_likelihood_gradient_matches_centered_finite_difference():
    vector = np.array([0.45, np.log(0.12), np.log(6.0), -0.7, 0.3, np.log(0.18 - LOWER)])
    likelihood, gradient = _log_likelihood_and_gradient(OBSERVED, vector, LOWER)
    numerical = np.empty_like(vector)
    step = 1e-5
    for index in range(len(vector)):
        plus = vector.copy()
        minus = vector.copy()
        plus[index] += step
        minus[index] -= step
        numerical[index] = (
            _log_likelihood_and_gradient(OBSERVED, plus, LOWER)[0]
            - _log_likelihood_and_gradient(OBSERVED, minus, LOWER)[0]
        ) / (2 * step)
    assert np.isfinite(likelihood)
    assert np.allclose(gradient, numerical, rtol=3e-3, atol=3e-3)


def assert_no_synthetic_truth_start(starts):
    # Noise scale must not hide a leaked dynamical truth. Check every scenario
    # and every start, including appended starts and near-truth perturbations.
    for scenario in DEFAULT_SCENARIOS:
        truth = scenario.parameters
        expected = (truth.Delta, truth.R, truth.Omega, truth.s0, truth.v0)
        for vector in starts:
            params, _sigma = _decode(vector, LOWER)
            actual = (params.Delta, params.R, params.Omega, params.s0, params.v0)
            assert not np.allclose(actual, expected, rtol=0.05, atol=1e-8), scenario.name


def test_predefined_starts_are_data_independent_and_not_synthetic_truth():
    first = predefined_starts(np.zeros(8), LOWER)
    second = predefined_starts(np.ones(8), LOWER)
    assert len(first) == len(second)
    assert all(np.array_equal(a, b) for a, b in zip(first, second))
    assert_no_synthetic_truth_start(first)


@pytest.mark.parametrize("scenario", DEFAULT_SCENARIOS, ids=lambda item: item.name)
@pytest.mark.parametrize("factor", [1.0, 1.02])
def test_truth_start_guard_detects_appended_truth_even_with_different_noise(scenario, factor, monkeypatch):
    truth = scenario.parameters
    leaked = np.array([truth.Delta * factor, np.log(truth.R * factor),
                       np.log(truth.Omega * factor), truth.s0 * factor,
                       truth.v0 * factor, np.log(0.3 - LOWER)])
    mutated = [*predefined_starts(OBSERVED, LOWER), leaked]
    monkeypatch.setitem(globals(), "predefined_starts", lambda *_args: mutated)
    with pytest.raises(AssertionError, match=scenario.name):
        test_predefined_starts_are_data_independent_and_not_synthetic_truth()


def test_fit_optimizer_moves_and_does_not_reduce_best_initial_likelihood():
    starts = predefined_starts(OBSERVED, LOWER)[:2]
    initial_best = max(_log_likelihood_and_gradient(OBSERVED, item, LOWER)[0] for item in starts)
    fitted = fit_rcwe(OBSERVED, sigma_lower_bound=LOWER, starts=starts, maxiter=12)
    assert fitted.fit_log_likelihood >= initial_best - 1e-7
    assert any(not np.allclose(record.initial_vector, record.final_vector) for record in fitted.starts)
    assert fitted.sigma_pred >= LOWER
    _means, states = forecast_means(fitted.parameters, len(OBSERVED))
    assert np.allclose(fitted.terminal_state, states[-1])


def test_converged_requires_cross_start_likelihood_agreement(monkeypatch):
    calls = iter([-10.0, -9.0])

    def fake_minimize(_objective, initial, **_kwargs):
        return SimpleNamespace(
            success=True,
            status=0,
            message="synthetic success",
            nit=1,
            x=np.asarray(initial, dtype=float),
            fun=next(calls),
        )

    monkeypatch.setattr(fit_module, "minimize", fake_minimize)
    monkeypatch.setattr(
        fit_module,
        "_log_likelihood_and_gradient",
        lambda _observed, vector, _lower: (float(vector[0]), np.zeros(6)),
    )
    # The agreement unit test must not depend on the scientific start registry.
    starts = [np.array([delta, np.log(.1), np.log(8), -1, .2, np.log(.2 - LOWER)])
              for delta in (.25, .75)]
    fitted = fit_rcwe(OBSERVED, starts=starts)
    assert fitted.successful_starts == 2
    assert fitted.top_two_log_likelihood_gap == 0.5
    assert not fitted.optimizer_agreement
    assert not fitted.converged


def test_invalid_region_penalty_is_finite_and_has_consistent_gradient():
    invalid = np.array([5.0, np.log(100.0), np.log(100.0), 12.0, 10.0, np.log(5.0)])
    likelihood, gradient = _log_likelihood_and_gradient(OBSERVED, invalid, LOWER)
    assert np.isfinite(likelihood)
    assert np.all(np.isfinite(gradient))
    assert likelihood < -1e6
    assert np.allclose(gradient, -2.0 * invalid)
