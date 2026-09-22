import numpy as np

from rcwe.model import RCWEParameters, classify_local_regime, sigmoid


def test_sigmoid_correctness():
    values = np.array([-1000.0, -1.0, 0.0, 1.0, 1000.0])
    result = sigmoid(values)
    assert result[0] == 0.0
    assert result[-1] == 1.0
    assert result[2] == 0.5
    assert np.isclose(result[1] + result[3], 1.0)


def test_g_is_derived_and_strong_cases_have_expected_local_stability():
    stable = RCWEParameters(0.5, 0.1, 8.0, -1.0, 0.2)
    oscillatory = RCWEParameters(0.5, 0.1, 12.0, -1.0, 0.2)
    assert np.isclose(stable.G, 0.8)
    assert np.isclose(oscillatory.G, 1.2)
    assert str(classify_local_regime(stable)["classification"]).startswith("stable")
    assert classify_local_regime(oscillatory)["classification"] == "unstable_focus"
