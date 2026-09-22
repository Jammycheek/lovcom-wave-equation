import json
from pathlib import Path

import numpy as np
import pytest

from rcwe.synthetic import STRONG_OSCILLATORY, STRONG_STABLE, fit_continuous_fixture, generate_synthetic


def test_same_seed_produces_identical_synthetic_data():
    first = generate_synthetic(STRONG_STABLE, 1234)
    second = generate_synthetic(STRONG_STABLE, 1234)
    assert np.array_equal(first.states, second.states)
    assert np.array_equal(first.latent_observation, second.latent_observation)
    assert np.array_equal(first.coded_observation, second.coded_observation)


@pytest.mark.parametrize("scenario", [STRONG_STABLE, STRONG_OSCILLATORY])
def test_known_continuous_synthetic_fixture_can_be_fitted(scenario):
    fitted, maximum_trajectory_error = fit_continuous_fixture(scenario.parameters)
    assert maximum_trajectory_error < 1e-7
    assert abs(fitted.Delta - scenario.parameters.Delta) < 1e-5
    assert abs(fitted.R - scenario.parameters.R) < 1e-5
    assert abs(fitted.Omega - scenario.parameters.Omega) < 1e-4
    assert abs(fitted.s0 - scenario.parameters.s0) < 1e-5
    assert abs(fitted.v0 - scenario.parameters.v0) < 1e-5


def test_generated_results_contain_provenance_metadata():
    root = Path(__file__).resolve().parents[1] / "results" / "synthetic_recovery"
    config = json.loads((root / "config.json").read_text(encoding="utf-8"))
    environment = json.loads((root / "environment.json").read_text(encoding="utf-8"))
    report = (root / "REPORT.md").read_text(encoding="utf-8")
    assert config["command"]
    assert config["seeds"]
    assert config["solver"]["method"] == "DOP853"
    assert environment["git_commit"]
    assert environment["python"] and environment["numpy"] and environment["scipy"]
    assert "Exact command" in report and "Known failures and warnings" in report
