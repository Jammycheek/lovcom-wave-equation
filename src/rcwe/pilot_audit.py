"""Fail-closed checks for the declared complete, instrument-bound pilot history.

This checks submitted evidence, not the truth of an operator's completeness claim.
"""

from datetime import datetime
import hashlib
import json
from pathlib import Path

INSTRUMENT_VERSION = "1.1"


def timestamp(value: str) -> datetime:
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None or result.utcoffset() is None:
        raise ValueError("audit timestamps require a UTC offset")
    return result


def audit_pilot_history(
    path: Path, *, expected_history_hashes: set[str], selected_result_hash: str | None,
    instrument_hash: str, protocol_hash: str, first_confirmatory_rating: datetime | None,
    confirmatory_works: set[str], confirmatory_raters: set[str],
) -> dict[str, object]:
    result = {"ready": False, "independence_passed": None, "history_sha256": None,
              "reason": "NO_DECLARED_HISTORY", "result_hashes": []}
    if not path.exists():
        return result
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    result["history_sha256"] = digest
    history = json.loads(raw)
    entries = history.get("runs", [])
    if not entries:
        return result
    if (history.get("declared_complete") is not True
            or history.get("instrument_version") != INSTRUMENT_VERSION
            or history.get("instrument_sha256") != instrument_hash
            or history.get("protocol_sha256") != protocol_hash
            or expected_history_hashes != {digest}
            or not history.get("freeze_commit")):
        return {**result, "reason": "HISTORY_PROVENANCE_MISMATCH"}
    sealed = timestamp(history["sealed_at"])
    if first_confirmatory_rating is None or sealed >= first_confirmatory_rating:
        return {**result, "reason": "HISTORY_NOT_FROZEN_BEFORE_RATINGS"}
    plan = history.get("manifest_sha256", "")
    if len(plan) != 64 or any(char not in "0123456789abcdef" for char in plan):
        return {**result, "reason": "MISSING_FIXED_PLAN"}
    works, raters, hashes = set(), set(), set()
    all_passed = True
    for entry in entries:
        artifact = path.parent / entry["path"]
        if not artifact.is_file():
            return {**result, "reason": "MISSING_RESULT_FILE"}
        contents = artifact.read_bytes()
        actual_hash = hashlib.sha256(contents).hexdigest()
        if actual_hash != entry["sha256"] or actual_hash in hashes:
            return {**result, "reason": "RESULT_HASH_MISMATCH_OR_DUPLICATE"}
        hashes.add(actual_hash)
        pilot = json.loads(contents)
        if (pilot.get("instrument_version") != INSTRUMENT_VERSION
                or pilot.get("instrument_sha256") != instrument_hash
                or pilot.get("protocol_sha256") != protocol_hash
                or pilot.get("input_hashes", {}).get("manifest_sha256") != plan
                or pilot.get("manifest_ready") is not True
                or not pilot.get("completed_at")
                or timestamp(pilot["completed_at"]) > sealed):
            return {**result, "reason": "RESULT_INSTRUMENT_OR_PLAN_MISMATCH"}
        if not pilot.get("pilot_work_ids") or not pilot.get("pilot_rater_id_hashes"):
            return {**result, "reason": "MISSING_PILOT_MEMBERSHIP"}
        works.update(pilot["pilot_work_ids"])
        raters.update(pilot["pilot_rater_id_hashes"])
        if pilot.get("status") == "PILOT_PASS":
            verification = entry.get("cutoff_receipt_verification") or {}
            export_hash = pilot.get("input_hashes", {}).get("cutoff_export_sha256")
            if (not isinstance(export_hash, str)
                    or len(export_hash) != 64
                    or any(char not in "0123456789abcdef" for char in export_hash)
                    or not pilot.get("cutoff_registration_locator")
                    or not pilot.get("cutoff_export_operator_id")
                    or not verification.get("verifier_id")
                    or verification.get("verifier_id") == pilot.get("cutoff_export_operator_id")
                    or verification.get("registration_locator") != pilot.get("cutoff_registration_locator")
                    or verification.get("cutoff_export_sha256") != export_hash):
                return {**result, "reason": "UNVERIFIED_CUTOFF_EXPORT"}
            try:
                if not (timestamp(pilot.get("cutoff_registered_at", ""))
                        <= timestamp(verification.get("verified_at", "")) <= sealed):
                    return {**result, "reason": "UNVERIFIED_CUTOFF_EXPORT"}
            except (AttributeError, TypeError, ValueError):
                return {**result, "reason": "UNVERIFIED_CUTOFF_EXPORT"}
        all_passed = all_passed and pilot.get("status") == "PILOT_PASS"
    independent = not (works & confirmatory_works) and not (
        raters & {hashlib.sha256(rater.encode()).hexdigest() for rater in confirmatory_raters})
    ready = all_passed and independent and selected_result_hash in hashes
    return {**result, "ready": ready, "independence_passed": independent,
            "result_hashes": sorted(hashes),
            "reason": "READY" if ready else "FAILED_HISTORY_OR_REUSE_OR_UNLISTED_RESULT"}
