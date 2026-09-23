import json
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone

import pytest

from rcwe.discriminant_pilot import discriminant_verdict, evaluate_discriminant_pilot
from rcwe.tension_bridge import AggregatedWindow, ReliabilityResult, Rating
from scripts.run_tension_bridge_discriminant_pilot import INSTRUMENT, sha256, validate_manifest


@pytest.mark.parametrize("point,upper,expected", [
    (.84, .849999, "PILOT_PASS"), (.85, .84, "PILOT_DISCRIMINANT_FAILURE"),
    (.84, .85, "PILOT_DISCRIMINANT_FAILURE"), (.85, .85, "PILOT_DISCRIMINANT_FAILURE"),
    (.86, .86, "PILOT_DISCRIMINANT_FAILURE"), (float("nan"), .8, "PILOT_MEASUREMENT_FAILURE"),
])
def test_exact_point_and_confidence_bound_cutoffs(point, upper, expected):
    assert discriminant_verdict(point, upper) == expected


def test_frozen_plan_prevents_added_works_windows_and_raters():
    rows, ratings = [], []
    for index in range(4):
        work = f"work-{index}"
        windows = [f"{work}-window-{n}" for n in range(8)]
        raters = [f"rater-{n}" for n in range(12)]
        rows.append(dict(work_id=work, version_id="v", edition="e", planned_work_count="4",
                         planned_window_count="8", planned_window_ids=";".join(windows),
                         planned_rater_ids=";".join(raters), instrument_sha256=sha256(INSTRUMENT.read_bytes()),
                         manifest_freeze_commit="frozen", manifest_frozen_at="2026-01-01T00:00:00Z",
                         confirmatory_reuse_prohibited="true"))
        ratings.extend(Rating(rater, work, window, "no", "no", "no", "L-T-D", 50, 50, 50, True, True)
                       for window in windows for rater in raters)
    times = [datetime(2026, 1, 2, tzinfo=timezone.utc)] * len(ratings)
    assert validate_manifest(rows, ratings, times)
    extra_work = {**rows[0], "work_id": "extra"}
    extra_rating = Rating("rater-0", "extra", "new", "no", "no", "no", "L-T-D", 50, 50, 50, True, True)
    with pytest.raises(ValueError, match="planned work count"):
        validate_manifest([*rows, extra_work], [*ratings, extra_rating], times)
    for rater, window in [("new-rater", "work-0-window-0"), ("rater-0", "new-window")]:
        extra = Rating(rater, "work-0", window, "no", "no", "no", "L-T-D", 50, 50, 50, True, True)
        with pytest.raises(ValueError, match="exactly cover"):
            validate_manifest(rows, [*ratings, extra], times)
    rows[0]["instrument_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="instrument hash"):
        validate_manifest(rows, ratings, times)


def reliability(passed=True):
    return {
        key: ReliabilityResult(key, 1000, 1000, 0.9 if passed else 0.5, 0.8, 0.95, passed)
        for key in ("T", "D")
    }


def windows(equivalent=False):
    result = []
    t_pattern = [10, 20, 30, 40, 50, 60, 70, 80]
    d_pattern = t_pattern if equivalent else [20, 80, 30, 70, 40, 60, 50, 10]
    for work_index in range(4):
        for index, (t, d) in enumerate(zip(t_pattern, d_pattern)):
            result.append(AggregatedWindow(
                f"W{work_index}-{index}", f"W{work_index}", f"P{work_index}", 0.0, 0.0,
                50.0, float(t), float(d), 50.0, float(t), float(d), 12,
            ))
    return result


def test_independent_patterns_pass_frozen_discriminant_gate():
    result = evaluate_discriminant_pilot(windows(), reliability(), master_seed="fixed", repeats=100)
    assert result["status"] == "PILOT_PASS"
    assert result["upper_95_abs_r_td"] < 0.85


def test_equivalent_patterns_fail_frozen_discriminant_gate():
    result = evaluate_discriminant_pilot(windows(equivalent=True), reliability(), master_seed="fixed", repeats=100)
    assert result["status"] == "PILOT_DISCRIMINANT_FAILURE"
    assert result["abs_r_td"] == 1.0


def test_reliability_failure_cannot_pass():
    assert evaluate_discriminant_pilot(windows(), reliability(False), master_seed="fixed")["status"] == "PILOT_MEASUREMENT_FAILURE"


def test_insufficient_data_cannot_pass():
    assert evaluate_discriminant_pilot(windows()[:29], reliability(), master_seed="fixed")["status"] == "INSUFFICIENT_PILOT_DATA"


def test_empty_pilot_runner_returns_no_data(tmp_path):
    root = Path(__file__).resolve().parents[1]
    output = tmp_path / "pilot"
    subprocess.run(
        [sys.executable, str(root / "scripts" / "run_tension_bridge_discriminant_pilot.py"), "--output", str(output)],
        cwd=root,
        check=True,
    )
    summary = json.loads((output / "summary.json").read_text(encoding="utf-8"))
    assert summary["status"] == "NO_DATA"
    assert summary["abs_r_td"] is None
