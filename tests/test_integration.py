import numpy as np
from scipy.integrate import solve_ivp

from rcwe.fit import RCWEFit, forecast_holdout
from rcwe.integrate import forecast_means, integrate_states, qualified_values
from rcwe.model import RCWEParameters, rhs


PARAMS = RCWEParameters(0.5, 0.1, 8.0, -1.0, 0.2)


def test_ode_integration_is_deterministic():
    first = integrate_states(PARAMS, 20)
    second = integrate_states(PARAMS, 20)
    assert np.array_equal(first, second)


def test_reference_matches_alternative_small_step_integration():
    reference = integrate_states(PARAMS, 12)
    times = np.arange(12, dtype=float)
    alternative = solve_ivp(
        rhs,
        (0.0, 11.0),
        (PARAMS.s0, PARAMS.v0),
        args=(PARAMS,),
        method="RK45",
        t_eval=times,
        rtol=1e-11,
        atol=1e-13,
        max_step=0.005,
    ).y.T
    assert np.max(np.abs(reference - alternative)) < 1e-8


def test_gap_does_not_advance_interaction_clock():
    observed = qualified_values([0.0, 99.0, 0.25, 99.0, 0.5], [True, False, True, False, True])
    means, _ = forecast_means(PARAMS, len(observed))
    direct, _ = forecast_means(PARAMS, 3)
    assert np.array_equal(observed, [0.0, 0.25, 0.5])
    assert np.array_equal(means, direct)


def test_holdout_values_cannot_modify_rcwe_state():
    fit_means, states = forecast_means(PARAMS, 8)
    fit = RCWEFit(PARAMS, 0.1, 1e-6, tuple(states[-1]), -1.0, True, (), 7)
    predictions_before = forecast_holdout(fit, 5)
    holdout_a = np.array([0.0, 0.0, 0.0, 0.0, 0.0])
    holdout_b = np.array([1.0, 1.0, 1.0, 1.0, 1.0])
    assert not np.array_equal(holdout_a, holdout_b)
    predictions_after = forecast_holdout(fit, 5)
    assert np.array_equal(predictions_before, predictions_after)
    assert len(fit_means) == 8
