import csv
import json
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone

import pytest

from rcwe.discriminant_pilot import discriminant_verdict, evaluate_discriminant_pilot
from rcwe.tension_bridge import AggregatedWindow, ReliabilityResult, Rating
from scripts.run_tension_bridge_discriminant_pilot import (
    INSTRUMENT, nonresponse_order_violations, parse_ratings, sha256, validate_manifest,
)
from rcwe.tension_bridge import deterministic_question_order


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
                         recruitment_closes_at="2026-01-03T00:00:00Z",
                         confirmatory_reuse_prohibited="true"))
        ratings.extend({"rater_id": rater, "work_id": work, "window_id": window, "response_status": "ANSWERED"}
                       for window in windows for rater in raters)
    times = [datetime(2026, 1, 2, tzinfo=timezone.utc)] * len(ratings)
    as_of = datetime(2026, 1, 4, tzinfo=timezone.utc)
    assert validate_manifest(rows, ratings, times, as_of=as_of)[0]
    extra_work = {**rows[0], "work_id": "extra"}
    extra_rating = {"rater_id": "rater-0", "work_id": "extra", "window_id": "new", "response_status": "ANSWERED"}
    with pytest.raises(ValueError, match="planned work count"):
        validate_manifest([*rows, extra_work], [*ratings, extra_rating], times, as_of=as_of)
    for rater, window in [("new-rater", "work-0-window-0"), ("rater-0", "new-window")]:
        extra = {"rater_id": rater, "work_id": "work-0", "window_id": window, "response_status": "ANSWERED"}
        with pytest.raises(ValueError, match="exactly cover"):
            validate_manifest(rows, [*ratings, extra], times, as_of=as_of)
    rows[0]["instrument_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="instrument hash"):
        validate_manifest(rows, ratings, times, as_of=as_of)


def test_nonresponse_uses_blank_values_and_closes_at_fixed_cutoff():
    row = dict(work_id="w", version_id="v", edition="e", planned_work_count="1",
               planned_window_count="1", planned_window_ids="w1", planned_rater_ids="r1;r2",
               instrument_sha256=sha256(INSTRUMENT.read_bytes()),
               manifest_freeze_commit="frozen", manifest_frozen_at="2026-01-01T00:00:00Z",
               recruitment_closes_at="2026-01-03T00:00:00Z", confirmatory_reuse_prohibited="true")
    blank = dict(rater_id="r2", work_id="w", window_id="w1", response_status="NONRESPONSE",
                 prior_exposure="", knows_future="", exposure_uncertain="", question_order="",
                 l_obs="", t_obs="", d_obs="", eligibility_decided_at="",
                 window_endpoint_reached_at="", rating_timestamp="", next_source_opened_at="")
    assert parse_ratings([blank]) == ([], [])
    with pytest.raises(ValueError, match="invented"):
        parse_ratings([{**blank, "t_obs": "0"}])
    with pytest.raises(ValueError, match="manual row-level"):
        parse_ratings([{**blank, "valid_pilot": "false"}])
    answer = {"rater_id": "r1", "work_id": "w", "window_id": "w1", "response_status": "ANSWERED"}
    roster = [answer, blank]
    before = datetime(2026, 1, 2, tzinfo=timezone.utc)
    after = datetime(2026, 1, 3, tzinfo=timezone.utc)
    with pytest.raises(ValueError, match="cutoff"):
        validate_manifest([row], roster, [before], as_of=before)
    assert validate_manifest([row], roster, [before], as_of=after)[2] == 2
    with pytest.raises(ValueError, match="exactly cover"):
        validate_manifest([row], [answer], [before], as_of=after)
    assert validate_manifest([row], [], [], cancelled=True, as_of=before)[0]


def test_nonresponse_is_a_terminal_suffix_in_planned_window_order():
    plan = [{"work_id": "w", "planned_window_ids": "w1;w2;w3", "planned_rater_ids": "r1;r2"}]
    rows = [
        {"work_id": "w", "window_id": window, "rater_id": rater, "response_status": status}
        for rater, statuses in (("r1", ("ANSWERED", "NONRESPONSE", "ANSWERED")),
                                ("r2", ("ANSWERED", "NONRESPONSE", "NONRESPONSE")))
        for window, status in zip(("w1", "w2", "w3"), statuses)
    ]
    assert nonresponse_order_violations(plan, rows) == [
        {"work_id": "w", "rater_id": "r1", "resumed_at_window_id": "w3"}
    ]


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


def test_real_runner_records_dropout_and_insufficient_result_without_fake_scores(tmp_path):
    root = Path(__file__).resolve().parents[1]
    template = root / "data"
    manifest_fields = (template / "tension_bridge_discriminant_pilot_manifest_template.csv").read_text().strip().split(",")
    rating_fields = (template / "tension_bridge_discriminant_pilot_ratings_template.csv").read_text().strip().split(",")
    manifest = tmp_path / "manifest.csv"
    ratings = tmp_path / "ratings.csv"
    planned = dict(work_id="work", version_id="v", edition="e", planned_work_count="1",
                   planned_window_count="1", planned_window_ids="window", planned_rater_ids="r1;r2",
                   instrument_sha256=sha256(INSTRUMENT.read_bytes()),
                   manifest_frozen_at="2026-01-01T00:00:00Z", manifest_freeze_commit="frozen",
                   recruitment_closes_at="2026-01-03T00:00:00Z", confirmatory_reuse_prohibited="true", notes="")
    with manifest.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=manifest_fields)
        writer.writeheader()
        writer.writerow(planned)
    answered = dict.fromkeys(rating_fields, "")
    answered.update(rater_id="r1", work_id="work", window_id="window", response_status="ANSWERED",
                    prior_exposure="no", knows_future="no", exposure_uncertain="no",
                    question_order=deterministic_question_order("RCWE-TB-DISCRIMINANT-v0.4", "work", "window", "r1"),
                    l_obs="50", t_obs="60", d_obs="30", eligibility_decided_at="2026-01-01T01:00:00Z",
                    window_endpoint_reached_at="2026-01-02T00:00:00Z",
                    rating_timestamp="2026-01-02T00:01:00Z")
    unanswered = {**dict.fromkeys(rating_fields, ""), "rater_id": "r2", "work_id": "work",
                  "window_id": "window", "response_status": "NONRESPONSE"}
    with ratings.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=rating_fields)
        writer.writeheader()
        writer.writerows([answered, unanswered])
    export = tmp_path / "cutoff_export.csv"
    receipt = tmp_path / "cutoff_receipt.json"
    def freeze_export(rows):
        with export.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=rating_fields)
            writer.writeheader()
            writer.writerows(rows)
        receipt.write_text(json.dumps({
            "cutoff_export_sha256": sha256(export.read_bytes()),
            "manifest_sha256": sha256(manifest.read_bytes()),
            "registered_at": "2026-01-03T00:01:00Z",
            "registration_locator": "urn:test:registered-cutoff",
            "export_operator_id": "operator-one",
        }), encoding="utf-8")
    freeze_export([answered])
    output = tmp_path / "result"
    command = [sys.executable, str(root / "scripts/run_tension_bridge_discriminant_pilot.py"),
               "--manifest", str(manifest), "--ratings", str(ratings),
               "--cutoff-export", str(export), "--cutoff-receipt", str(receipt),
               "--output", str(output)]
    subprocess.run(command, cwd=root, check=True)
    result = json.loads((output / "summary.json").read_text())
    assert result["status"] == "INSUFFICIENT_PILOT_DATA"
    assert result["exclusions"]["nonresponse_cells"] == 1
    assert result["exclusions"]["planned_cells"] == 2
    assert len(result["pilot_rater_id_hashes"]) == 2
    assert result["abs_r_td"] is None
    with pytest.raises(subprocess.CalledProcessError):
        subprocess.run(command, cwd=root, check=True, capture_output=True)
    bad_receipt = tmp_path / "bad_receipt.json"
    bad_receipt.write_text(json.dumps({**json.loads(receipt.read_text()),
                                       "cutoff_export_sha256": "0" * 64}), encoding="utf-8")
    bad_receipt_output = tmp_path / "bad-receipt-result"
    subprocess.run([*command[:-1], str(bad_receipt_output),
                    "--cutoff-receipt", str(bad_receipt)], cwd=root, check=True)
    assert json.loads((bad_receipt_output / "summary.json").read_text())["status"] == "PILOT_PROVENANCE_FAILURE"
    missing_export_output = tmp_path / "missing-export-result"
    subprocess.run([*command[:-1], str(missing_export_output),
                    "--cutoff-export", str(tmp_path / "does-not-exist.csv")], cwd=root, check=True)
    missing_export = json.loads((missing_export_output / "summary.json").read_text())
    assert missing_export["status"] == "PILOT_PROVENANCE_FAILURE"
    assert "CUTOFF_EXPORT_MISSING" in missing_export["cutoff_export_violations"]
    hidden_output = tmp_path / "hidden-answer"
    with ratings.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=rating_fields)
        writer.writeheader()
        writer.writerows([{"rater_id": "r1", "work_id": "work", "window_id": "window",
                          "response_status": "NONRESPONSE"}, unanswered])
    hidden = subprocess.run([*command[:-1], str(hidden_output)], cwd=root, check=True)
    assert hidden.returncode == 0
    hidden_summary = json.loads((hidden_output / "summary.json").read_text())
    assert hidden_summary["status"] == "PILOT_PROVENANCE_FAILURE"
    assert "CUTOFF_ANSWER_MEMBERSHIP_MISMATCH" in hidden_summary["cutoff_export_violations"]
    late_output = tmp_path / "late"
    late_answer = {**answered, "rating_timestamp": "2026-01-04T00:01:00Z"}
    with ratings.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=rating_fields)
        writer.writeheader()
        writer.writerows([late_answer, unanswered])
    freeze_export([])
    subprocess.run([*command[:-1], str(late_output)], cwd=root, check=True)
    late = json.loads((late_output / "summary.json").read_text())
    assert late["status"] == "INSUFFICIENT_PILOT_DATA"
    assert late["exclusions"]["late_answered_cells"] == 1
    assert late["exclusions"]["answered_cells"] == 1
    cancelled_output = tmp_path / "cancelled"
    header_only = tmp_path / "empty_ratings.csv"
    header_only.write_text(",".join(rating_fields) + "\n", encoding="utf-8")
    subprocess.run([*command[:2], "--manifest", str(manifest), "--ratings", str(header_only),
                    "--output", str(cancelled_output), "--cancel-reason", "study stopped"], cwd=root, check=True)
    cancelled = json.loads((cancelled_output / "summary.json").read_text())
    assert cancelled["status"] == "CANCELLED_PILOT"
    assert cancelled["cancel_reason"] == "study stopped"
    assert len(cancelled["pilot_rater_id_hashes"]) == 2


def test_runner_records_resumed_after_nonresponse_as_terminal_protocol_deviation(tmp_path):
    root = Path(__file__).resolve().parents[1]
    manifest_fields = (root / "data/tension_bridge_discriminant_pilot_manifest_template.csv").read_text().strip().split(",")
    rating_fields = (root / "data/tension_bridge_discriminant_pilot_ratings_template.csv").read_text().strip().split(",")
    manifest = tmp_path / "manifest.csv"
    roster = tmp_path / "roster.csv"
    export = tmp_path / "cutoff_export.csv"
    receipt = tmp_path / "receipt.json"
    plan = dict(work_id="work", version_id="v", edition="e", planned_work_count="1",
                planned_window_count="2", planned_window_ids="w1;w2", planned_rater_ids="r1",
                instrument_sha256=sha256(INSTRUMENT.read_bytes()),
                manifest_frozen_at="2026-01-01T00:00:00Z", manifest_freeze_commit="frozen",
                recruitment_closes_at="2026-01-03T00:00:00Z",
                confirmatory_reuse_prohibited="true", notes="")
    with manifest.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=manifest_fields)
        writer.writeheader()
        writer.writerow(plan)
    missing = {**dict.fromkeys(rating_fields, ""), "rater_id": "r1", "work_id": "work",
               "window_id": "w1", "response_status": "NONRESPONSE"}
    answered = {**dict.fromkeys(rating_fields, ""), "rater_id": "r1", "work_id": "work",
                "window_id": "w2", "response_status": "ANSWERED", "prior_exposure": "no",
                "knows_future": "no", "exposure_uncertain": "no", "l_obs": "50",
                "t_obs": "60", "d_obs": "30",
                "question_order": deterministic_question_order("RCWE-TB-DISCRIMINANT-v0.4", "work", "w2", "r1"),
                "eligibility_decided_at": "2026-01-01T00:01:00Z",
                "window_endpoint_reached_at": "2026-01-02T00:00:00Z",
                "rating_timestamp": "2026-01-02T00:01:00Z"}
    for path, rows in ((roster, [missing, answered]), (export, [answered])):
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=rating_fields)
            writer.writeheader()
            writer.writerows(rows)
    receipt.write_text(json.dumps({
        "cutoff_export_sha256": sha256(export.read_bytes()),
        "manifest_sha256": sha256(manifest.read_bytes()),
        "registered_at": "2026-01-03T00:01:00Z",
        "registration_locator": "urn:test:registered-cutoff",
        "export_operator_id": "operator-one",
    }), encoding="utf-8")
    output = tmp_path / "result"
    subprocess.run([sys.executable, str(root / "scripts/run_tension_bridge_discriminant_pilot.py"),
                    "--manifest", str(manifest), "--ratings", str(roster),
                    "--cutoff-export", str(export), "--cutoff-receipt", str(receipt),
                    "--output", str(output)], cwd=root, check=True)
    summary = json.loads((output / "summary.json").read_text())
    assert summary["status"] == "PILOT_PROTOCOL_DEVIATION"
    assert summary["nonresponse_order_violations"] == [
        {"work_id": "work", "rater_id": "r1", "resumed_at_window_id": "w2"}]
    assert summary["abs_r_td"] is None
