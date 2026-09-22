import numpy as np

from rcwe.baselines import (
    fit_ar1,
    fit_narrative_position,
    fit_persistence,
    forecast_ar1,
    forecast_narrative_position,
    forecast_persistence,
    narrative_position_indices,
)


FIT = np.array([0.0, 0.25, 0.25, 0.5, 0.5, 0.75, 0.75, 1.0])


def test_persistence_holds_last_fit_value_open_loop():
    fitted = fit_persistence(FIT)
    assert np.array_equal(forecast_persistence(fitted, 4), np.full(4, FIT[-1]))


def test_ar1_holdout_is_recursive_not_reset_by_observations():
    fitted = fit_ar1(FIT)
    forecast = forecast_ar1(fitted, 4, last_fit=float(FIT[-1]))
    expected_second = fitted.coefficients["alpha"] + fitted.coefficients["phi"] * forecast[0]
    assert forecast[1] == expected_second
    assert np.array_equal(forecast, forecast_ar1(fitted, 4, last_fit=float(FIT[-1])))


def test_narrative_position_standardization_is_not_reset_at_holdout():
    z, mean, scale = narrative_position_indices(len(FIT), len(FIT) + 3)
    assert z[len(FIT)] == (len(FIT) - mean) / scale
    assert z[len(FIT)] > z[len(FIT) - 1]
    fitted = fit_narrative_position(FIT)
    forecast = forecast_narrative_position(fitted, 3)
    assert len(forecast) == 3
