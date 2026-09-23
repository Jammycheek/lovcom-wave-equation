import csv

import pytest

from scripts.compare_synthetic_runs import compare


def write(path, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture
def runs(tmp_path):
    rows = [dict(scenario="stable", seed=str(seed), converged=str(seed == 1),
                 FIT_log_likelihood=-10, fitted_Delta=.5, fitted_R=.1, fitted_Omega=8,
                 holdout_LS_RCWE=-5) for seed in (1, 2)]
    predictions = [dict(scenario="stable", seed=str(seed), model="rcwe", interaction_index=n,
                        predicted_mu=.5) for seed in (1, 2) for n in (60, 61)]
    for name in ("a", "b"):
        (tmp_path / name).mkdir()
        write(tmp_path / name / "replicates.csv", rows)
        write(tmp_path / name / "predictions.csv", predictions)
    return tmp_path / "a", tmp_path / "b", rows, predictions


def test_equal_counts_do_not_hide_flipped_ids(runs):
    a, b, rows, _ = runs
    for row in rows:
        row["converged"] = str(row["converged"] == "False")
    write(b / "replicates.csv", rows)
    result = compare(a, b)
    assert len(result["convergence_flipped_ids"]) == 2
    assert result["numerical_tolerances_met"] is True
    assert result["acceptance_status"] == "NOT_ASSESSED"


def test_per_ie_mean_tolerance_is_not_replaced_by_total_score(runs):
    a, b, _, predictions = runs
    predictions[0]["predicted_mu"] += 1e-7
    write(b / "predictions.csv", predictions)
    result = compare(a, b)
    assert result["maximum_absolute_differences"]["holdout_LS_RCWE"] == 0
    assert result["numerical_tolerances_met"] is False


def test_missing_forecast_cannot_pass(runs):
    a, b, _, predictions = runs
    write(b / "predictions.csv", predictions[:-1])
    with pytest.raises(ValueError, match="prediction membership"):
        compare(a, b)


def test_duplicate_replicate_cannot_pass(runs):
    a, b, rows, _ = runs
    write(b / "replicates.csv", [*rows, rows[0]])
    with pytest.raises(ValueError, match="duplicate"):
        compare(a, b)
