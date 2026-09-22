from types import SimpleNamespace

import numpy as np

import rcwe.fit as fit_module
from rcwe.fit import _decode, _log_likelihood_and_gradient, fit_rcwe, predefined_starts
from rcwe.integrate import forecast_means


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


def test_predefined_starts_are_data_independent_and_not_synthetic_truth():
    first = predefined_starts(np.zeros(8), LOWER)
    second = predefined_starts(np.ones(8), LOWER)
    assert all(np.array_equal(a, b) for a, b in zip(first, second))
    decoded = []
    for item in first:
        params, sigma = _decode(item, LOWER)
        decoded.append((params.Delta, params.R, params.Omega, params.s0, params.v0, sigma))
    truth = (0.5, 0.1, 8.0, -1.0, 0.2, 0.1)
    assert not any(np.allclose(item, truth) for item in decoded)


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
    fitted = fit_rcwe(OBSERVED, starts=predefined_starts(OBSERVED, LOWER)[:2])
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
