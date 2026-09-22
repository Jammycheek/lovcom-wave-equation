import json
from pathlib import Path
import subprocess
import sys

from rcwe.discriminant_pilot import evaluate_discriminant_pilot
from rcwe.tension_bridge import AggregatedWindow, ReliabilityResult


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
