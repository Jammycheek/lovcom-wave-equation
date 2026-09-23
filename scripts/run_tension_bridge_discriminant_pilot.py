#!/usr/bin/env python
"""Run the frozen Tension Bridge T/D discriminant-validity pilot."""

from __future__ import annotations

import argparse
import csv
from dataclasses import replace
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np
import scipy

from rcwe.discriminant_pilot import BOOTSTRAP_REPEATS, DISCRIMINANT_LIMIT, evaluate_discriminant_pilot
from rcwe.pilot_audit import INSTRUMENT_VERSION
from rcwe.tension_bridge import (
    MIN_RATERS,
    RELIABILITY_REPEATS,
    Rating,
    WindowMetric,
    aggregate_ratings,
    split_half_reliability,
    validate_question_orders,
)

PROTOCOL = ROOT / "protocols" / "TENSION_BRIDGE_DISCRIMINANT_PILOT_v0.4.md"
INSTRUMENT = ROOT / "protocols" / "TENSION_BRIDGE_RATING_FORM_v1.1.md"
MASTER_SEED = "RCWE-TB-DISCRIMINANT-v0.4"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ratings", type=Path, default=ROOT / "data" / "tension_bridge_discriminant_pilot_ratings_template.csv")
    parser.add_argument("--cutoff-export", type=Path, default=ROOT / "data" / "tension_bridge_pilot_cutoff_export_template.csv")
    parser.add_argument("--cutoff-receipt", type=Path, default=ROOT / "data" / "tension_bridge_pilot_cutoff_receipt_template.json")
    parser.add_argument("--manifest", type=Path, default=ROOT / "data" / "tension_bridge_discriminant_pilot_manifest_template.csv")
    parser.add_argument("--master-seed", default=MASTER_SEED)
    parser.add_argument("--cancel-reason", help="close this frozen pilot plan without a scientific verdict")
    parser.add_argument("--output", type=Path, default=ROOT / "results" / "tension_bridge_discriminant_pilot")
    return parser.parse_args()


def parse_bool(value: str, field: str) -> bool:
    normalized = value.strip().lower()
    if normalized in ("true", "1", "yes"):
        return True
    if normalized in ("false", "0", "no"):
        return False
    raise ValueError(f"{field} must be an explicit boolean")


def parse_timestamp(value: str, field: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError(f"{field} must be ISO 8601")
    normalized = value.strip().replace("Z", "+00:00")
    if not normalized:
        raise ValueError(f"{field} is required")
    try:
        result = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError(f"{field} must be ISO 8601") from exc
    if result.tzinfo is None or result.utcoffset() is None:
        raise ValueError(f"{field} must include a UTC offset")
    return result


def read_csv(path: Path) -> tuple[bytes, list[dict[str, str]]]:
    raw = path.read_bytes()
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"{path} requires a header")
        return raw, list(reader)


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def git_sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unavailable"


def parse_ratings(rows: list[dict[str, str]]) -> tuple[list[Rating], list[datetime]]:
    ratings, times = [], []
    for row in rows:
        if "valid_pilot" in row or "valid_primary" in row:
            raise ValueError("manual row-level validity overrides are prohibited")
        response_status = row["response_status"].strip()
        if response_status == "NONRESPONSE":
            if any(row[field].strip() for field in (
                "prior_exposure", "knows_future", "exposure_uncertain", "question_order",
                "l_obs", "t_obs", "d_obs", "eligibility_decided_at",
                "window_endpoint_reached_at", "rating_timestamp", "next_source_opened_at",
            )):
                raise ValueError("NONRESPONSE cells must not contain invented ratings or timestamps")
            continue
        if response_status != "ANSWERED":
            raise ValueError("response_status must be ANSWERED or NONRESPONSE")
        eligibility = parse_timestamp(row["eligibility_decided_at"], "eligibility_decided_at")
        endpoint = parse_timestamp(row["window_endpoint_reached_at"], "window_endpoint_reached_at")
        rated = parse_timestamp(row["rating_timestamp"], "rating_timestamp")
        next_raw = row["next_source_opened_at"].strip()
        next_opened = parse_timestamp(next_raw, "next_source_opened_at") if next_raw else None
        future_blind = eligibility <= endpoint <= rated and (next_opened is None or rated < next_opened)
        ratings.append(Rating(
            row["rater_id"].strip(), row["work_id"].strip(), row["window_id"].strip(),
            row["prior_exposure"].strip(), row["knows_future"].strip(), row["exposure_uncertain"].strip(),
            row["question_order"].strip(), int(row["l_obs"]), int(row["t_obs"]), int(row["d_obs"]),
            future_blind, True,
        ))
        times.append(rated)
    return ratings, times


def validate_manifest(
    rows: list[dict[str, str]], response_rows: list[dict[str, str]], rating_times: list[datetime],
    *, cancelled: bool = False, as_of: datetime | None = None,
) -> tuple[bool, datetime | None, int]:
    if not rows and not response_rows:
        return False, None, 0
    if not rows:
        raise ValueError("a frozen pilot work manifest is required")
    works = {row["work_id"].strip() for row in response_rows}
    if len({row["work_id"].strip() for row in rows}) != len(rows):
        raise ValueError("duplicate work_id in pilot manifest")
    if works - {row["work_id"].strip() for row in rows}:
        raise ValueError("pilot manifest works must exactly match rating works")
    first_rating = min(rating_times, default=None)
    now = as_of or datetime.now(timezone.utc)
    closures = set()
    planned_cell_count = 0
    for row in rows:
        work = row["work_id"].strip()
        if int(row["planned_work_count"]) != len(rows):
            raise ValueError("actual work count must equal the frozen planned work count")
        if row["instrument_sha256"] != sha256(INSTRUMENT.read_bytes()):
            raise ValueError("pilot manifest instrument hash mismatch")
        if not all(row[field].strip() for field in ("version_id", "edition", "manifest_freeze_commit")):
            raise ValueError("pilot manifest provenance is incomplete")
        if not parse_bool(row["confirmatory_reuse_prohibited"], "confirmatory_reuse_prohibited"):
            raise ValueError("pilot works and raters cannot be reused in the confirmatory Bridge study")
        frozen_at = parse_timestamp(row["manifest_frozen_at"], "manifest_frozen_at")
        closes_at = parse_timestamp(row["recruitment_closes_at"], "recruitment_closes_at")
        closures.add(closes_at)
        if frozen_at >= closes_at or (first_rating is not None and frozen_at >= first_rating):
            raise ValueError("pilot manifest must be frozen before the first rating")
        window_list = row["planned_window_ids"].split(";")
        rater_list = row["planned_rater_ids"].split(";")
        if any(not value or value != value.strip() for value in window_list + rater_list):
            raise ValueError("planned window/rater IDs must be nonempty semicolon-separated IDs")
        if len(set(window_list)) != len(window_list) or len(set(rater_list)) != len(rater_list):
            raise ValueError("duplicate ID in frozen pilot plan")
        if int(row["planned_window_count"]) != len(window_list):
            raise ValueError(f"planned window count mismatch for {work}")
        actual_cells = [(entry["window_id"].strip(), entry["rater_id"].strip())
                        for entry in response_rows if entry["work_id"].strip() == work]
        expected_cells = {(window, rater) for window in window_list for rater in rater_list}
        planned_cell_count += len(expected_cells)
        if len(actual_cells) != len(set(actual_cells)) or not set(actual_cells) <= expected_cells:
            raise ValueError("pilot ratings must exactly cover the frozen rater/window plan, including exclusions")
        if not cancelled and set(actual_cells) != expected_cells:
            raise ValueError("pilot ratings must exactly cover the frozen rater/window plan, including exclusions")
    if len(closures) != 1:
        raise ValueError("all pilot works must share one frozen recruitment cutoff")
    closes_at = closures.pop()
    if not cancelled and now < closes_at:
        raise ValueError("pilot collection has not reached the frozen recruitment cutoff")
    return True, closes_at, planned_cell_count


def nonresponse_order_violations(
    manifest_rows: list[dict[str, str]], response_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    """A rater may stop, but cannot resume after a planned nonresponse."""
    by_cell = {(row["work_id"].strip(), row["rater_id"].strip(), row["window_id"].strip()): row
               for row in response_rows}
    violations = []
    for plan in manifest_rows:
        work = plan["work_id"].strip()
        for rater in plan["planned_rater_ids"].split(";"):
            stopped = False
            for window in plan["planned_window_ids"].split(";"):
                row = by_cell.get((work, rater, window))
                if row is None:
                    continue  # A cancelled plan may have an incomplete roster.
                if row["response_status"].strip() == "NONRESPONSE":
                    stopped = True
                elif stopped:
                    violations.append({"work_id": work, "rater_id": rater, "resumed_at_window_id": window})
    return violations


def audit_cutoff_export(
    export_raw: bytes, export_rows: list[dict[str, str]], response_rows: list[dict[str, str]],
    manifest_raw: bytes, receipt: dict[str, str], closes_at: datetime,
    *, as_of: datetime | None = None,
) -> list[str]:
    """Check a committed cutoff snapshot against every answer received by cutoff."""
    violations: list[str] = []
    now = as_of or datetime.now(timezone.utc)
    claimed_export_hash = receipt.get("cutoff_export_sha256")
    claimed_manifest_hash = receipt.get("manifest_sha256")
    if not isinstance(claimed_export_hash, str) or claimed_export_hash.lower() != sha256(export_raw):
        violations.append("CUTOFF_EXPORT_HASH_MISMATCH")
    if not isinstance(claimed_manifest_hash, str) or claimed_manifest_hash.lower() != sha256(manifest_raw):
        violations.append("CUTOFF_RECEIPT_PLAN_MISMATCH")
    if not isinstance(receipt.get("registration_locator"), str) or not receipt["registration_locator"].strip():
        violations.append("CUTOFF_EXTERNAL_REGISTRATION_MISSING")
    if not isinstance(receipt.get("export_operator_id"), str) or not receipt["export_operator_id"].strip():
        violations.append("CUTOFF_EXPORT_OPERATOR_MISSING")
    try:
        registered_at = parse_timestamp(receipt.get("registered_at", ""), "registered_at")
        if not closes_at <= registered_at <= now:
            violations.append("CUTOFF_REGISTRATION_TIME_INVALID")
    except ValueError:
        violations.append("CUTOFF_REGISTRATION_TIME_INVALID")

    export_by_cell: dict[tuple[str, str, str], dict[str, str]] = {}
    for row in export_rows:
        if any(not isinstance(row.get(field), str) for field in ("work_id", "rater_id", "window_id", "response_status")):
            violations.append("CUTOFF_EXPORT_MALFORMED_ROW")
            continue
        cell = (row["work_id"].strip(), row["rater_id"].strip(), row["window_id"].strip())
        if cell in export_by_cell:
            violations.append("DUPLICATE_CUTOFF_ANSWER")
        export_by_cell[cell] = row
        if row["response_status"].strip() != "ANSWERED":
            violations.append("CUTOFF_EXPORT_HAS_NONANSWER")
        try:
            if parse_timestamp(row.get("rating_timestamp", ""), "rating_timestamp") > closes_at:
                violations.append("CUTOFF_EXPORT_HAS_LATE_ANSWER")
        except ValueError:
            violations.append("CUTOFF_EXPORT_HAS_INVALID_TIMESTAMP")

    roster_at_cutoff: dict[tuple[str, str, str], dict[str, str]] = {}
    for row in response_rows:
        if row["response_status"].strip() != "ANSWERED":
            continue
        if parse_timestamp(row["rating_timestamp"], "rating_timestamp") <= closes_at:
            cell = (row["work_id"].strip(), row["rater_id"].strip(), row["window_id"].strip())
            roster_at_cutoff[cell] = row
    if set(export_by_cell) != set(roster_at_cutoff):
        violations.append("CUTOFF_ANSWER_MEMBERSHIP_MISMATCH")
    elif any(export_by_cell[cell] != roster_at_cutoff[cell] for cell in export_by_cell):
        violations.append("CUTOFF_ANSWER_CONTENT_MISMATCH")
    return sorted(set(violations))


def main() -> int:
    args = parse_args()
    if args.master_seed != MASTER_SEED:
        raise ValueError("the pilot bootstrap/question-order seed is frozen for this protocol version")
    if args.cancel_reason is not None and not args.cancel_reason.strip():
        raise ValueError("cancellation requires a nonempty reason")
    cancelled = args.cancel_reason is not None
    output = args.output.resolve()
    prior = output / "summary.json"
    if prior.exists() and json.loads(prior.read_bytes()).get("status") != "NO_DATA":
        raise ValueError("completed pilot results cannot be overwritten; retain and register every run")
    rating_raw, rating_rows = read_csv(args.ratings.resolve())
    try:
        export_raw, export_rows = read_csv(args.cutoff_export.resolve())
        export_missing = False
    except FileNotFoundError:
        export_raw, export_rows, export_missing = b"", [], True
    try:
        receipt_raw = args.cutoff_receipt.resolve().read_bytes()
        receipt_missing = False
    except FileNotFoundError:
        receipt_raw, receipt_missing = b"", True
    try:
        receipt = json.loads(receipt_raw)
    except json.JSONDecodeError:
        receipt = {}
    receipt_malformed = not isinstance(receipt, dict)
    if receipt_malformed:
        receipt = {}
    manifest_raw, manifest_rows = read_csv(args.manifest.resolve())
    if cancelled and not manifest_rows:
        raise ValueError("a cancelled pilot must name a frozen plan")
    ratings, rating_times = parse_ratings(rating_rows)
    manifest_ready, closes_at, planned_cell_count = validate_manifest(
        manifest_rows, rating_rows, rating_times, cancelled=cancelled)
    order_violations = nonresponse_order_violations(manifest_rows, rating_rows)
    provenance_violations = (
        audit_cutoff_export(export_raw, export_rows, rating_rows, manifest_raw, receipt, closes_at)
        if manifest_ready and not cancelled and closes_at is not None else []
    )
    if manifest_ready and not cancelled:
        if export_missing:
            provenance_violations.append("CUTOFF_EXPORT_MISSING")
        if receipt_missing or receipt_malformed:
            provenance_violations.append("CUTOFF_RECEIPT_MISSING_OR_MALFORMED")
    output.mkdir(parents=True, exist_ok=True)
    late_count = sum(rated > closes_at for rated in rating_times) if closes_at is not None else 0
    if closes_at is not None:
        ratings = [replace(rating, valid_primary=False) if rated > closes_at else rating
                   for rating, rated in zip(ratings, rating_times)]
    nonresponse_count = sum(row["response_status"].strip() == "NONRESPONSE" for row in rating_rows)
    protocol_hash = sha256(PROTOCOL.read_bytes())
    instrument_hash = sha256(INSTRUMENT.read_bytes())
    hashes = {"ratings_sha256": sha256(rating_raw), "manifest_sha256": sha256(manifest_raw),
              "cutoff_export_sha256": sha256(export_raw), "cutoff_receipt_sha256": sha256(receipt_raw),
              "protocol_sha256": protocol_hash, "instrument_sha256": instrument_hash}
    command = " ".join([Path(sys.executable).name, *sys.argv])
    config = {
        "command": command, "master_seed": args.master_seed, "input_hashes": hashes,
        "minimum_raters": MIN_RATERS, "reliability_repeats": RELIABILITY_REPEATS,
        "bootstrap_repeats": BOOTSTRAP_REPEATS, "discriminant_limit": DISCRIMINANT_LIMIT,
        "recruitment_closes_at": closes_at.isoformat() if closes_at else None,
        "planned_cell_count": planned_cell_count,
        "cutoff_registration_locator": receipt.get("registration_locator") if manifest_ready else None,
    }
    (output / "config.json").write_text(json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    environment = {"git_commit": git_sha(), "python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__}
    (output / "environment.json").write_text(json.dumps(environment, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")

    pilot_works = sorted(row["work_id"].strip() for row in manifest_rows)
    pilot_raters = sorted({rater for row in manifest_rows for rater in row["planned_rater_ids"].split(";")}) if manifest_rows else []
    membership = {
        "pilot_work_ids": pilot_works,
        "pilot_rater_id_hashes": sorted(hashlib.sha256(rater.encode()).hexdigest() for rater in pilot_raters),
    }
    exclusions = {
        "planned_cells": planned_cell_count,
        "answered_cells": len(ratings),
        "nonresponse_cells": nonresponse_count,
        "late_answered_cells": late_count,
    }
    if not manifest_rows and not rating_rows:
        reliability = {}
        summary = {"status": "NO_DATA", "protocol_sha256": protocol_hash, "input_hashes": hashes, "pilot_work_ids": [], "pilot_rater_id_hashes": [], "abs_r_td": None, "upper_95_abs_r_td": None}
        aggregates = []
    elif cancelled:
        reliability = {}
        aggregates = []
        summary = {"status": "CANCELLED_PILOT", "cancel_reason": args.cancel_reason.strip(),
                   "manifest_ready": manifest_ready, "protocol_sha256": protocol_hash,
                   "input_hashes": hashes, **membership, "abs_r_td": None, "upper_95_abs_r_td": None}
    elif order_violations or provenance_violations:
        reliability = {}
        aggregates = []
        summary = {"status": "PILOT_PROTOCOL_DEVIATION" if order_violations else "PILOT_PROVENANCE_FAILURE",
                   "manifest_ready": manifest_ready, "protocol_sha256": protocol_hash,
                   "input_hashes": hashes, **membership, "abs_r_td": None, "upper_95_abs_r_td": None,
                   "nonresponse_order_violations": order_violations,
                   "cutoff_export_violations": provenance_violations}
    else:
        validate_question_orders(ratings, args.master_seed)
        mapping: dict[str, str] = {}
        for row in manifest_rows:
            for window_id in row["planned_window_ids"].split(";"):
                previous = mapping.setdefault(window_id, row["work_id"].strip())
                if previous != row["work_id"].strip():
                    raise ValueError("window_id must be globally unique across pilot works")
        windows = [
            WindowMetric(window_id, work, work, tuple(f"{window_id}::{index}" for index in range(5)), 0.0, 0.0)
            for window_id, work in mapping.items()
        ]
        aggregates, _statuses, eligible = aggregate_ratings(windows, ratings)
        reliability = {key: split_half_reliability(eligible, key, master_seed=args.master_seed) for key in ("T", "D")}
        summary = {
            **evaluate_discriminant_pilot(aggregates, reliability, master_seed=args.master_seed),
            "manifest_ready": manifest_ready, "protocol_sha256": protocol_hash, "input_hashes": hashes,
            **membership,
        }
    summary.update(instrument_version=INSTRUMENT_VERSION, instrument_sha256=instrument_hash,
                   completed_at=datetime.now(timezone.utc).isoformat(),
                   recruitment_closes_at=closes_at.isoformat() if closes_at else None,
                   cutoff_registration_locator=receipt.get("registration_locator") if manifest_ready else None,
                   cutoff_registered_at=receipt.get("registered_at") if manifest_ready else None,
                   cutoff_export_operator_id=receipt.get("export_operator_id") if manifest_ready else None,
                   exclusions=exclusions)
    reliability_json = {key: value.as_dict() for key, value in reliability.items()}
    (output / "reliability.json").write_text(json.dumps(reliability_json, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    (output / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8", newline="\n")
    with (output / "window_aggregates.csv").open("w", encoding="utf-8", newline="") as handle:
        fields = ["window_id", "work_id", "pair", "p_ac", "p_switch", "l_obs", "t_obs", "d_obs", "median_l_obs", "median_t_obs", "median_d_obs", "rating_count"]
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(item.as_dict() for item in aggregates)
    report = [
        "# Tension Bridge Discriminant-Validity Pilot Report", "", "Generated; do not edit by hand.", "",
        f"- Git commit: `{environment['git_commit']}`", f"- Input/protocol hashes: `{hashes}`", f"- Exact command: `{command}`", "",
        f"- Status: `{summary['status']}`", f"- T/D result: `{summary}`", f"- Reliability: `{reliability_json}`", "",
    ]
    (output / "REPORT.md").write_text("\n".join(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
