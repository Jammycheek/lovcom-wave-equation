from datetime import datetime, timezone
import hashlib
import json

import pytest

from rcwe.pilot_audit import audit_pilot_history
from scripts.run_tension_bridge_analysis import validate_discriminant_pilot


def save(path, value):
    raw = json.dumps(value, sort_keys=True).encode()
    path.write_bytes(raw)
    return hashlib.sha256(raw).hexdigest()


@pytest.fixture
def evidence(tmp_path):
    pilot = {
        "status": "PILOT_PASS", "instrument_version": "1.1",
        "instrument_sha256": "a" * 64, "protocol_sha256": "b" * 64,
        "input_hashes": {"manifest_sha256": "c" * 64}, "manifest_ready": True,
        "completed_at": "2026-01-02T00:00:00Z", "pilot_work_ids": ["pilot-work"],
        "pilot_rater_id_hashes": [hashlib.sha256(b"pilot-rater").hexdigest()],
    }
    digest = save(tmp_path / "pass.json", pilot)
    history = {"instrument_version": "1.1", "instrument_sha256": "a" * 64,
               "protocol_sha256": "b" * 64, "manifest_sha256": "c" * 64,
               "declared_complete": True, "freeze_commit": "frozen-test-commit",
               "sealed_at": "2026-01-03T00:00:00Z",
               "runs": [{"path": "pass.json", "sha256": digest}]}
    return tmp_path, pilot, history, digest


def audit(evidence, **overrides):
    path, _pilot, history, selected = evidence
    history_hash = save(path / "history.json", history)
    kwargs = dict(expected_history_hashes={history_hash}, selected_result_hash=selected,
                  instrument_hash="a" * 64, protocol_hash="b" * 64,
                  first_confirmatory_rating=datetime(2026, 1, 4, tzinfo=timezone.utc),
                  confirmatory_works={"new-work"}, confirmatory_raters={"new-rater"})
    return audit_pilot_history(path / "history.json", **{**kwargs, **overrides})


def test_complete_pass_history_activates(evidence):
    assert audit(evidence)["ready"] is True


@pytest.mark.parametrize("status", ["PILOT_DISCRIMINANT_FAILURE", "PILOT_MEASUREMENT_FAILURE", "INSUFFICIENT_PILOT_DATA"])
def test_failed_run_cannot_be_hidden_behind_later_pass(evidence, status):
    path, pilot, history, _ = evidence
    digest = save(path / "failed.json", {**pilot, "status": status})
    history["runs"].insert(0, {"path": "failed.json", "sha256": digest})
    assert audit(evidence)["ready"] is False


def test_enlarged_manifest_cannot_replace_failed_plan(evidence):
    path, pilot, history, _ = evidence
    enlarged = {**pilot, "input_hashes": {"manifest_sha256": "d" * 64}}
    digest = save(path / "enlarged.json", enlarged)
    history["runs"].append({"path": "enlarged.json", "sha256": digest})
    assert audit(evidence)["reason"] == "RESULT_INSTRUMENT_OR_PLAN_MISMATCH"


@pytest.mark.parametrize("change", [
    {"instrument_hash": "d" * 64}, {"protocol_hash": "d" * 64},
    {"expected_history_hashes": {"d" * 64}}, {"selected_result_hash": "d" * 64},
    {"confirmatory_works": {"pilot-work"}}, {"confirmatory_raters": {"pilot-rater"}},
    {"first_confirmatory_rating": datetime(2026, 1, 2, tzinfo=timezone.utc)},
])
def test_mismatched_hashes_reuse_and_late_seal_block_activation(evidence, change):
    assert audit(evidence, **change)["ready"] is False


def test_result_bytes_are_verified(evidence):
    path, pilot, _, _ = evidence
    save(path / "pass.json", {**pilot, "status": "changed"})
    assert audit(evidence)["reason"] == "RESULT_HASH_MISMATCH_OR_DUPLICATE"


def test_unlisted_selected_result_is_rejected(evidence):
    assert audit(evidence, selected_result_hash="e" * 64)["ready"] is False


def test_incomplete_declaration_blocks_activation(evidence):
    evidence[2]["declared_complete"] = False
    assert audit(evidence)["ready"] is False


def test_no_data_independence_is_unassessed(tmp_path):
    path = tmp_path / "history.json"
    save(path, {"runs": []})
    result = audit_pilot_history(path, expected_history_hashes=set(), selected_result_hash=None,
                                instrument_hash="a", protocol_hash="b", first_confirmatory_rating=None,
                                confirmatory_works=set(), confirmatory_raters=set())
    assert result["ready"] is False and result["independence_passed"] is None
    ready, independent = validate_discriminant_pilot(
        {"status": "NO_DATA"}, result_hash=None, protocol_hash="b", instrument_hash="a",
        manifest_hashes=set(), confirmatory_work_ids=set(), confirmatory_rater_ids=set())
    assert ready is False and independent is None
