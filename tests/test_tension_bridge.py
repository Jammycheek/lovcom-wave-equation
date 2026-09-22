import math
from pathlib import Path
import json
import subprocess
import sys

import numpy as np
import pytest

from rcwe.tension_bridge import (
    AggregatedWindow,
    ChannelIE,
    Rating,
    ReliabilityResult,
    WindowMetric,
    activation_gate,
    aggregate_ratings,
    build_windows,
    channel_metrics,
    deterministic_question_order,
    leave_one_work_out,
    ols_predictive_distribution,
    split_half_reliability,
    standardize_train_holdout,
    static_tension_challenge,
    validate_role_separation,
)


BASE = (1.0, 0.0, 0.0, 0.0)
SHIFT = (0.75, 0.25, 0.0, 0.0)


def ies(count, vectors=None, work="W1", pair="P1"):
    vectors = vectors or [BASE] * count
    return [ChannelIE(work, pair, index, f"IE-{index}", tuple(vectors[index])) for index in range(count)]


def window(index=0, work="W1", pair="P1", p_ac=0.01):
    return WindowMetric(f"{work}-{pair}-{index}", work, pair, tuple(f"IE-{index}-{j}" for j in range(5)), p_ac, p_ac)


def rating(rater, metric, *, seed="seed", prior="no", future="no", uncertain="no", l=50, t=50, d=50):
    return Rating(
        rater, metric.work_id, metric.window_id, prior, future, uncertain,
        deterministic_question_order(seed, metric.work_id, metric.window_id, rater),
        l, t, d, True, True,
    )


def aggregate(index, work, pair, *, pac, l, t, d, count=12):
    return AggregatedWindow(
        f"{work}-{pair}-{index}", work, pair, pac, pac, l, t, d, l, t, d, count
    )


def passing_reliability():
    return {
        key: ReliabilityResult(key, 1000, 1000, 0.9, 0.8, 0.95, True)
        for key in ("L", "T", "D")
    }


def toy(kind="ac"):
    data = []
    for work_index in range(4):
        work = f"W{work_index}"
        for index in range(8):
            l = 20 + 3 * index + 2 * work_index
            d = 30 + ((index * 7 + work_index * 3) % 20)
            pac = 0.005 + 0.006 * ((index * 3 + work_index) % 8)
            noise = ((index * 11 + work_index * 7) % 7) - 3
            if kind == "ac":
                t = 10 + 0.35 * l + 0.4 * d + 400 * pac + noise
            else:
                t = 10 + 0.45 * l + 0.55 * d + noise
            data.append(aggregate(index, work, f"P{work_index}", pac=pac, l=l, t=t, d=d))
    return data


def test_five_ie_windows_are_non_overlapping():
    result = build_windows(ies(10))
    assert len(result) == 2
    assert set(result[0].ie_ids).isdisjoint(result[1].ie_ids)
    assert result[0].ie_ids == tuple(f"IE-{i}" for i in range(5))
    assert result[1].ie_ids == tuple(f"IE-{i}" for i in range(5, 10))


def test_remainder_under_five_is_excluded():
    result = build_windows(ies(14))
    assert len(result) == 2
    assert "IE-10" not in {ie for item in result for ie in item.ie_ids}


def test_window_boundaries_do_not_depend_on_pac():
    low = build_windows(ies(10, [BASE] * 10))
    high = build_windows(ies(10, [BASE, SHIFT] * 5))
    assert [item.ie_ids for item in low] == [item.ie_ids for item in high]


def test_pac_known_fixture():
    vectors = [BASE, SHIFT, BASE, SHIFT, BASE]
    expected = float(np.mean(np.sum((np.array(vectors) - np.mean(vectors, axis=0)) ** 2, axis=1)))
    assert channel_metrics(vectors)[0] == pytest.approx(expected)


def test_constant_sequence_has_zero_pac():
    assert channel_metrics([BASE] * 5)[0] == 0.0


def test_minimum_one_step_fixture_has_pac_point_zero_two():
    assert channel_metrics([BASE, BASE, BASE, BASE, SHIFT])[0] == pytest.approx(0.02)


def test_p_switch_fixture():
    assert channel_metrics([BASE, BASE, BASE, BASE, SHIFT])[1] == pytest.approx(0.03125)


def test_coder_and_rater_cannot_overlap_for_same_work():
    metric = window()
    ratings = [rating("person-1", metric)]
    with pytest.raises(ValueError, match="roles overlap"):
        validate_role_separation({"W1": {"person-1"}}, {"W1": set()}, ratings)


def test_prior_familiar_rater_is_excluded():
    metric = window()
    ratings = [rating(f"R{i}", metric, prior="yes" if i == 0 else "no") for i in range(13)]
    aggregates, _statuses, eligible = aggregate_ratings([metric], ratings)
    assert len(eligible) == 12
    assert aggregates[0].rating_count == 12


def test_each_window_requires_twelve_valid_ratings():
    metric = window()
    aggregates, statuses, _eligible = aggregate_ratings([metric], [rating(f"R{i}", metric) for i in range(11)])
    assert aggregates == []
    assert statuses[metric.window_id] == "INSUFFICIENT_RATERS"


def test_rating_aggregate_is_arithmetic_mean():
    metric = window()
    ratings = [rating(f"R{i}", metric, l=i, t=2 * i, d=3 * i) for i in range(12)]
    result = aggregate_ratings([metric], ratings)[0][0]
    assert result.l_obs == np.mean(range(12))
    assert result.t_obs == np.mean([2 * i for i in range(12)])
    assert result.d_obs == np.mean([3 * i for i in range(12)])


def test_question_randomization_is_deterministic_and_context_specific():
    first = deterministic_question_order("master", "W", "WIN", "R")
    assert first == deterministic_question_order("master", "W", "WIN", "R")
    orders = {deterministic_question_order("master", "W", f"WIN{i}", "R") for i in range(20)}
    assert first in {"L-T-D", "L-D-T", "T-L-D", "T-D-L", "D-L-T", "D-T-L"}
    assert len(orders) > 1


def reliability_ratings(kind="pass"):
    values = []
    for window_index in range(8):
        metric = window(window_index, work=f"W{window_index % 4}")
        for rater_index in range(12):
            if kind == "pass":
                score = 10 + 9 * window_index + (rater_index % 3) - 1
            else:
                score = 5 + 8 * rater_index
            values.append(rating(f"R{rater_index}", metric, l=score, t=score, d=score))
    return values


def test_reliability_calculation_is_deterministic():
    ratings = reliability_ratings()
    first = split_half_reliability(ratings, "T", master_seed="fixed", repeats=100)
    second = split_half_reliability(ratings, "T", master_seed="fixed", repeats=100)
    assert first == second


def test_reliability_gate_pass_and_fail_fixtures():
    passed = split_half_reliability(reliability_ratings("pass"), "T", master_seed="fixed", repeats=100)
    failed = split_half_reliability(reliability_ratings("fail"), "T", master_seed="fixed", repeats=100)
    assert passed.passed
    assert not failed.passed


def test_work_never_appears_in_train_and_holdout():
    result = leave_one_work_out(toy("ac"))
    for row in result["predictions"]:
        assert row["holdout_work"] not in row["train_works"]


def test_standardization_uses_train_only():
    train_z, holdout_z, means, scales = standardize_train_holdout(np.array([[0.0], [2.0]]), np.array([[100.0]]))
    assert means[0] == 1.0 and scales[0] == 1.0
    assert np.array_equal(train_z[:, 0], [-1.0, 1.0])
    assert holdout_z[0, 0] == 99.0


def test_ols_coefficients_match_closed_form():
    x = np.column_stack([np.ones(6), np.arange(6, dtype=float)])
    y = np.array([2.0, 5.2, 7.8, 11.1, 13.9, 17.2])
    expected = np.linalg.inv(x.T @ x) @ x.T @ y
    _loc, _scale, _df, beta = ols_predictive_distribution(x, y, x[:2])
    assert np.allclose(beta, expected)


def test_student_t_predictive_logpdf_is_finite():
    result = leave_one_work_out(toy("ac"))
    assert all(np.isfinite(row["log_predictive_density"]) for row in result["predictions"])


def test_total_log_score_equals_per_window_sum():
    result = leave_one_work_out(toy("ac"))
    for model, total in result["scores"].items():
        assert total == math.fsum(row["log_predictive_density"] for row in result["predictions"] if row["model"] == model)


def test_delta_ls_calculation():
    result = leave_one_work_out(toy("ac"))
    assert result["delta_ls_primary"] == result["scores"]["M1"] - result["scores"]["M0"]
    assert result["delta_ls_love"] == result["scores"]["MLAC"] - result["scores"]["ML"]


def test_beta_pac_sign_and_ac_toy_advantage():
    result = leave_one_work_out(toy("ac"))
    assert result["beta_pac_full"] > 0
    assert result["scores"]["M1"] > result["scores"]["M0"]


def test_love_drama_only_toy_does_not_support_m1():
    result = leave_one_work_out(toy("ld"))
    assert result["delta_ls_primary"] < 2
    assert result["primary_status"] != "SUPPORT"


def test_activation_gate_exact_pass_and_failure():
    data = toy("ac")[:30]
    passed = activation_gate(data, passing_reliability(), channel_reliability_passed=True, manifest_frozen=True, role_separation_passed=True)
    assert passed.passed
    assert passed.eligible_windows == 30
    failed = activation_gate(data[:-1], passing_reliability(), channel_reliability_passed=True, manifest_frozen=True, role_separation_passed=True)
    assert not failed.passed
    measurement = activation_gate(data, {**passing_reliability(), "T": ReliabilityResult("T", 1000, 1000, 0.69, 0.6, 0.8, False)}, channel_reliability_passed=True, manifest_frozen=True, role_separation_passed=True)
    assert measurement.status == "MEASUREMENT_FAILURE"


def test_static_tension_rule_exact():
    data = [
        aggregate(0, "W1", "P1", pac=0.02, l=80, t=75, d=40),
        aggregate(1, "W1", "P1", pac=0.0, l=80, t=90, d=40),
        aggregate(0, "W2", "P2", pac=0.01, l=80, t=85, d=40),
    ]
    result = static_tension_challenge(data)
    assert result["status"] == "FAIL"
    assert result["candidate_count"] == 3
    assert result["independent_works"] == 2
    assert static_tension_challenge(data[:2])["status"] == "NOT_TRIGGERED"


def test_same_input_and_seed_give_same_output():
    data = toy("ac")
    assert leave_one_work_out(data) == leave_one_work_out(data)
    ratings = reliability_ratings()
    assert split_half_reliability(ratings, "L", master_seed=99, repeats=50) == split_half_reliability(ratings, "L", master_seed=99, repeats=50)


def test_templates_require_no_copyrighted_content():
    root = Path(__file__).resolve().parents[1]
    for name in (
        "tension_bridge_windows_template.csv",
        "tension_bridge_ratings_template.csv",
        "tension_bridge_work_manifest_template.csv",
    ):
        lines = (root / "data" / name).read_text(encoding="utf-8").splitlines()
        assert len(lines) == 1
        assert "transcript" not in lines[0].lower()
        assert "dialogue" not in lines[0].lower()


def test_empty_template_runner_returns_no_data(tmp_path):
    root = Path(__file__).resolve().parents[1]
    output = tmp_path / "bridge-output"
    subprocess.run(
        [sys.executable, str(root / "scripts" / "run_tension_bridge_analysis.py"), "--output", str(output)],
        cwd=root,
        check=True,
    )
    summary = json.loads((output / "model_summary.json").read_text(encoding="utf-8"))
    assert summary["status"] == "NO_DATA"
    assert summary["scores"] is None
    assert {path.name for path in output.iterdir()} == {
        "config.json", "environment.json", "window_metrics.csv", "rater_reliability.json",
        "fold_predictions.csv", "model_summary.json", "REPORT.md",
    }
