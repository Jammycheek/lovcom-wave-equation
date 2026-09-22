import json
import math
from pathlib import Path
import subprocess
import sys

import pytest

from scripts.run_subject6_comparison import parse_and_join

from rcwe.subject6_compare import (
    CATEGORIES,
    PAIRS,
    Subject6Row,
    activation_gate,
    compare,
)


def row(order, pair="KM", category="0", exposure=0, **overrides):
    values = {
        "global_order": order,
        "pair_ie_order": order % 10 + 1,
        "ie_id": f"IE-{order}",
        "pair": pair,
        "r_dir": category,
        "x_shared": exposure,
        "source_locator": f"locator-{order}",
        "direction_adjudicated": True,
        "shared_event_adjudicated": True,
    }
    values.update(overrides)
    return Subject6Row(**values)


def activation_rows():
    data = []
    for order in range(12):
        pair = "KM" if order < 4 else "KT" if order < 8 else "KB"
        exposure = order % 2 if order < 8 else 0
        data.append(row(order, pair=pair, category=CATEGORIES[order % 4], exposure=exposure))
    return data


def test_cold_start_probability_is_exactly_quarter():
    prediction = compare([row(0)]).predictions[0]
    assert [prediction.p_a_minus1, prediction.p_a_zero, prediction.p_a_plus1, prediction.p_a_mixed] == [0.25] * 4
    assert [prediction.p_b_minus1, prediction.p_b_zero, prediction.p_b_plus1, prediction.p_b_mixed] == [0.25] * 4


def test_every_prediction_distribution_sums_to_one():
    result = compare(activation_rows())
    for prediction in result.predictions:
        assert math.fsum([prediction.p_a_minus1, prediction.p_a_zero, prediction.p_a_plus1, prediction.p_a_mixed]) == 1.0
        assert math.fsum([prediction.p_b_minus1, prediction.p_b_zero, prediction.p_b_plus1, prediction.p_b_mixed]) == 1.0


def test_model_a_updates_only_same_pair():
    result = compare([row(0, pair="KM", category="+1"), row(1, pair="KT", category="+1")])
    assert result.predictions[1].p_a_observed == 0.25


def test_model_b_updates_only_same_pair_and_exposure_stratum():
    result = compare([
        row(0, pair="KM", category="+1", exposure=0),
        row(1, pair="KM", category="+1", exposure=1),
        row(2, pair="KM", category="+1", exposure=0),
    ])
    assert result.predictions[1].p_b_observed == 0.25
    assert result.predictions[2].p_b_observed == 0.4


def test_current_target_is_not_counted_before_prediction():
    result = compare([row(0, category="mixed"), row(1, category="mixed")])
    assert result.predictions[0].p_a_observed == 0.25
    assert result.predictions[1].p_a_observed == 0.4


def test_other_pair_does_not_contaminate_counts():
    result = compare([row(0, pair="KB", category="-1"), row(1, pair="KM", category="-1")])
    assert result.predictions[1].p_a_minus1 == 0.25
    assert result.predictions[1].p_b_minus1 == 0.25


def test_exposure_zero_and_one_remain_separate():
    result = compare([row(0, category="-1", exposure=0), row(1, category="-1", exposure=1)])
    assert result.predictions[1].p_b_minus1 == 0.25
    assert result.predictions[1].p_a_minus1 == 0.4


def test_mixed_is_retained_as_fourth_category():
    prediction = compare([row(0, category="mixed")]).predictions[0]
    assert prediction.r_dir == "mixed"
    assert prediction.p_a_mixed == 0.25


def test_natural_log_total_equals_per_row_sum():
    result = compare(activation_rows())
    assert result.pooled.ls_a == math.fsum(item.ls_a for item in result.predictions)
    assert result.pooled.ls_b == math.fsum(item.ls_b for item in result.predictions)
    assert result.pooled.delta_ls == result.pooled.ls_b - result.pooled.ls_a


def test_global_order_is_deterministic():
    result = compare([row(2), row(0), row(1)])
    assert [item.global_order for item in result.predictions] == [0, 1, 2]


def test_duplicate_global_order_is_rejected():
    with pytest.raises(ValueError, match="duplicate"):
        compare([row(0), row(0, ie_id="other")])


def test_invalid_pair_is_rejected():
    with pytest.raises(ValueError, match="invalid pair"):
        row(0, pair="KH")


def test_invalid_category_is_rejected():
    with pytest.raises(ValueError, match="invalid r_dir"):
        row(0, category="approach")


def test_non_adjudicated_direction_is_rejected():
    with pytest.raises(ValueError, match="adjudicated Direction"):
        row(0, direction_adjudicated=False)


def test_non_adjudicated_exposure_is_rejected():
    with pytest.raises(ValueError, match="adjudicated shared-event"):
        row(0, shared_event_adjudicated=False)


def test_exposure_must_be_frozen_before_outcome_reveal():
    exposures = [{
        "global_order": "0", "pair_ie_order": "1", "ie_id": "IE-0", "pair": "KM", "x_shared": "0",
        "source_locator": "loc", "shared_event_adjudicated": "true",
        "exposure_frozen_at": "2026-01-03T00:00:00+09:00", "exposure_commit": "exp",
    }]
    outcomes = [{
        "ie_id": "IE-0", "r_dir": "+1", "direction_coder_a": "+1", "direction_coder_b": "+1",
        "direction_adjudicated": "true", "outcome_revealed_at": "2026-01-02T00:00:00+09:00", "outcome_commit": "out",
    }]
    manifest = [{"qualified_ie_coding_complete": "true", "exposure_freeze_commit": "exp", "outcome_commit": "out"}]
    with pytest.raises(ValueError, match="before outcome reveal"):
        parse_and_join(exposures, outcomes, manifest)


def test_activation_gate_passes_exact_frozen_boundary():
    gate = activation_gate(activation_rows())
    assert gate.passed
    assert gate.total_rows == 12
    assert gate.x_shared_0_rows == 8
    assert gate.x_shared_1_rows == 4
    assert gate.pairs_with_both_exposures == ("KM", "KT")


@pytest.mark.parametrize(
    "data",
    [
        activation_rows()[:11],
        [row(i, pair=PAIRS[i % 3], exposure=0) for i in range(12)],
        [row(i, pair="KM" if i < 8 else "KT", exposure=1 if i < 4 else 0) for i in range(12)],
    ],
)
def test_activation_gate_fails_when_any_requirement_is_missing(data):
    assert not activation_gate(data).passed


def test_same_input_produces_identical_result():
    data = activation_rows()
    assert compare(data) == compare(data)


def test_m_c_is_not_silently_implemented():
    result = compare(activation_rows()).as_dict()
    serialized = json.dumps(result)
    assert "M_C" not in serialized
    assert set(result) == {"pooled", "pair_summaries", "activation_gate", "status"}


def test_event_independent_toy_sequence_is_scoreable_without_forced_winner():
    data = [row(i, pair=PAIRS[i % 3], category=CATEGORIES[i % 4], exposure=i % 2) for i in range(24)]
    result = compare(data)
    assert result.activation_gate.passed
    assert math.isfinite(result.pooled.delta_ls)


def test_strongly_event_conditioned_toy_sequence_favors_model_b():
    data = []
    for i in range(30):
        exposure = i % 2
        data.append(row(i, pair=PAIRS[i % 3], category="+1" if exposure else "-1", exposure=exposure))
    result = compare(data)
    assert result.activation_gate.passed
    assert result.pooled.delta_ls >= 2.0
    assert result.status == "PRACTICAL_SUPPORT_M_B"


def test_empty_template_runner_finishes_without_pretending_result(tmp_path):
    root = Path(__file__).resolve().parents[1]
    output = tmp_path / "result"
    subprocess.run(
        [
            sys.executable,
            str(root / "scripts" / "run_subject6_comparison.py"),
            "--output",
            str(output),
        ],
        check=True,
        cwd=root,
    )
    summary = json.loads((output / "summary.json").read_text(encoding="utf-8"))
    assert summary["status"] == "NO_DATA"
    assert summary["pooled"] is None
    assert (output / "per_ie_predictions.csv").read_text(encoding="utf-8").count("\n") == 1
    assert {path.name for path in output.iterdir()} == {
        "config.json", "per_ie_predictions.csv", "pair_summary.csv", "summary.json", "REPORT.md"
    }


def test_runner_enforces_direction_reliability_gate(tmp_path):
    root = Path(__file__).resolve().parents[1]
    exposures = tmp_path / "exposures.csv"
    outcomes = tmp_path / "outcomes.csv"
    manifest = tmp_path / "manifest.csv"
    exposures.write_text(
        "global_order,pair_ie_order,ie_id,pair,x_shared,source_locator,shared_event_adjudicated,exposure_frozen_at,exposure_commit\n"
        "0,1,IE-0,KM,0,locator-0,true,2026-01-01T00:00:00+09:00,exposure-commit\n",
        encoding="utf-8",
    )
    manifest.write_text(
        "work_id,version_id,edition,volume,qualified_ie_coding_complete,exposure_freeze_commit,outcome_commit,notes\n"
        "S6,v1,comic,5,true,exposure-commit,outcome-commit,complete\n",
        encoding="utf-8",
    )
    outcomes.write_text(
        "ie_id,r_dir,direction_coder_a,direction_coder_b,direction_adjudicated,outcome_revealed_at,outcome_commit\n"
        "IE-0,+1,+1,-1,true,2026-01-02T00:00:00+09:00,outcome-commit\n",
        encoding="utf-8",
    )
    failed_output = tmp_path / "failed"
    subprocess.run(
        [sys.executable, str(root / "scripts" / "run_subject6_comparison.py"),
         "--exposures", str(exposures), "--outcomes", str(outcomes), "--manifest", str(manifest),
         "--output", str(failed_output)],
        check=True,
        cwd=root,
    )
    failed = json.loads((failed_output / "summary.json").read_text(encoding="utf-8"))
    assert failed["status"] == "MEASUREMENT_FAILURE"
    assert failed["pooled"] is None

    outcomes.write_text(
        "ie_id,r_dir,direction_coder_a,direction_coder_b,direction_adjudicated,outcome_revealed_at,outcome_commit\n"
        "IE-0,+1,+1,+1,true,2026-01-02T00:00:00+09:00,outcome-commit\n",
        encoding="utf-8",
    )
    passed_output = tmp_path / "passed"
    subprocess.run(
        [sys.executable, str(root / "scripts" / "run_subject6_comparison.py"),
         "--exposures", str(exposures), "--outcomes", str(outcomes), "--manifest", str(manifest),
         "--output", str(passed_output)],
        check=True,
        cwd=root,
    )
    passed = json.loads((passed_output / "summary.json").read_text(encoding="utf-8"))
    assert passed["status"] == "INSUFFICIENT_SHARED_EVENT_EXPOSURE"
    assert passed["pooled"]["row_count"] == 1
