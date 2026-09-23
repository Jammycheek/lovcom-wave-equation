#!/usr/bin/env python
"""Run the frozen Tension Bridge T/D discriminant-validity pilot."""

from __future__ import annotations

import argparse
import csv
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

PROTOCOL = ROOT / "protocols" / "TENSION_BRIDGE_DISCRIMINANT_PILOT_v0.2.md"
INSTRUMENT = ROOT / "protocols" / "TENSION_BRIDGE_RATING_FORM_v1.1.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ratings", type=Path, default=ROOT / "data" / "tension_bridge_discriminant_pilot_ratings_template.csv")
    parser.add_argument("--manifest", type=Path, default=ROOT / "data" / "tension_bridge_discriminant_pilot_manifest_template.csv")
    parser.add_argument("--master-seed", default="RCWE-TB-DISCRIMINANT-v0.2")
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
            future_blind, parse_bool(row["valid_pilot"], "valid_pilot"),
        ))
        times.append(rated)
    return ratings, times


def validate_manifest(rows: list[dict[str, str]], ratings: list[Rating], rating_times: list[datetime]) -> bool:
    if not rows and not ratings:
        return False
    if not rows or not ratings:
        raise ValueError("pilot ratings and a frozen work manifest are both required")
    works = {rating.work_id for rating in ratings}
    if len({row["work_id"].strip() for row in rows}) != len(rows):
        raise ValueError("duplicate work_id in pilot manifest")
    if {row["work_id"].strip() for row in rows} != works:
        raise ValueError("pilot manifest works must exactly match rating works")
    first_rating = min(rating_times)
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
        if parse_timestamp(row["manifest_frozen_at"], "manifest_frozen_at") >= first_rating:
            raise ValueError("pilot manifest must be frozen before the first rating")
        window_list = row["planned_window_ids"].split(";")
        rater_list = row["planned_rater_ids"].split(";")
        if any(not value or value != value.strip() for value in window_list + rater_list):
            raise ValueError("planned window/rater IDs must be nonempty semicolon-separated IDs")
        if len(set(window_list)) != len(window_list) or len(set(rater_list)) != len(rater_list):
            raise ValueError("duplicate ID in frozen pilot plan")
        if int(row["planned_window_count"]) != len(window_list):
            raise ValueError(f"planned window count mismatch for {work}")
        actual_cells = [(rating.window_id, rating.rater_id) for rating in ratings if rating.work_id == work]
        expected_cells = {(window, rater) for window in window_list for rater in rater_list}
        if len(actual_cells) != len(expected_cells) or set(actual_cells) != expected_cells:
            raise ValueError("pilot ratings must exactly cover the frozen rater/window plan, including exclusions")
    return True


def main() -> int:
    args = parse_args()
    output = args.output.resolve()
    prior = output / "summary.json"
    if prior.exists() and json.loads(prior.read_bytes()).get("status") != "NO_DATA":
        raise ValueError("completed pilot results cannot be overwritten; retain and register every run")
    output.mkdir(parents=True, exist_ok=True)
    rating_raw, rating_rows = read_csv(args.ratings.resolve())
    manifest_raw, manifest_rows = read_csv(args.manifest.resolve())
    ratings, rating_times = parse_ratings(rating_rows)
    manifest_ready = validate_manifest(manifest_rows, ratings, rating_times)
    protocol_hash = sha256(PROTOCOL.read_bytes())
    instrument_hash = sha256(INSTRUMENT.read_bytes())
    hashes = {"ratings_sha256": sha256(rating_raw), "manifest_sha256": sha256(manifest_raw), "protocol_sha256": protocol_hash, "instrument_sha256": instrument_hash}
    command = " ".join([Path(sys.executable).name, *sys.argv])
    config = {
        "command": command, "master_seed": args.master_seed, "input_hashes": hashes,
        "minimum_raters": MIN_RATERS, "reliability_repeats": RELIABILITY_REPEATS,
        "bootstrap_repeats": BOOTSTRAP_REPEATS, "discriminant_limit": DISCRIMINANT_LIMIT,
    }
    (output / "config.json").write_text(json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    environment = {"git_commit": git_sha(), "python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__}
    (output / "environment.json").write_text(json.dumps(environment, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")

    if not ratings and not manifest_rows:
        reliability = {}
        summary = {"status": "NO_DATA", "protocol_sha256": protocol_hash, "input_hashes": hashes, "pilot_work_ids": [], "pilot_rater_id_hashes": [], "abs_r_td": None, "upper_95_abs_r_td": None}
        aggregates = []
    else:
        validate_question_orders(ratings, args.master_seed)
        mapping: dict[str, str] = {}
        for rating in ratings:
            previous = mapping.setdefault(rating.window_id, rating.work_id)
            if previous != rating.work_id:
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
            "pilot_work_ids": sorted({rating.work_id for rating in ratings}),
            "pilot_rater_id_hashes": sorted({hashlib.sha256(rating.rater_id.encode()).hexdigest() for rating in ratings}),
        }
    summary.update(instrument_version=INSTRUMENT_VERSION, instrument_sha256=instrument_hash,
                   completed_at=datetime.now(timezone.utc).isoformat())
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
