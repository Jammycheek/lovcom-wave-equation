#!/usr/bin/env python
"""Run the frozen Tension Bridge confirmatory analysis."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
DISCRIMINANT_PROTOCOL = ROOT / "protocols" / "TENSION_BRIDGE_DISCRIMINANT_PILOT_v0.2.md"
INSTRUMENT = ROOT / "protocols" / "TENSION_BRIDGE_RATING_FORM_v1.1.md"

import numpy as np
import scipy
from rcwe.pilot_audit import INSTRUMENT_VERSION, audit_pilot_history

from rcwe.tension_bridge import (
    ChannelIE,
    MIN_RATERS,
    ModelIdentificationError,
    RELIABILITY_GATE,
    RELIABILITY_REPEATS,
    Rating,
    WindowMetric,
    activation_gate,
    aggregate_ratings,
    build_windows,
    bridge_verdict,
    channel_reliability,
    leave_one_work_out,
    split_half_reliability,
    static_tension_challenge,
    validate_question_orders,
    validate_role_separation,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--channels", type=Path, default=ROOT / "data" / "tension_bridge_channels_template.csv")
    parser.add_argument("--windows", type=Path, default=ROOT / "data" / "tension_bridge_windows_template.csv")
    parser.add_argument("--ratings", type=Path, default=ROOT / "data" / "tension_bridge_ratings_template.csv")
    parser.add_argument("--manifest", type=Path, default=ROOT / "data" / "tension_bridge_work_manifest_template.csv")
    parser.add_argument("--pilot-result", type=Path, default=ROOT / "results" / "tension_bridge_discriminant_pilot" / "summary.json")
    parser.add_argument("--pilot-history", type=Path, default=ROOT / "data" / "tension_bridge_pilot_history_template.json")
    parser.add_argument("--master-seed", default="RCWE-TB-v1.0")
    parser.add_argument("--output", type=Path, default=ROOT / "results" / "tension_bridge")
    return parser.parse_args()


def parse_bool(value: str, field: str) -> bool:
    normalized = value.strip().lower()
    if normalized in ("true", "1", "yes"):
        return True
    if normalized in ("false", "0", "no"):
        return False
    raise ValueError(f"{field} must be an explicit boolean")


def read_csv(path: Path) -> tuple[bytes, list[dict[str, str]]]:
    raw = path.read_bytes()
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"{path} requires a CSV header")
        return raw, list(reader)


def file_hash(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def git_sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unavailable"


def dump_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8", newline="\n")


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def parse_channels(rows: list[dict[str, str]]):
    ies: list[ChannelIE] = []
    coder_a: list[tuple[float, float, float, float]] = []
    coder_b: list[tuple[float, float, float, float]] = []
    metadata: dict[str, dict[str, str]] = {}
    coders: dict[str, set[str]] = {}
    adjudicators: dict[str, set[str]] = {}
    for row in rows:
        work = row["work_id"].strip()
        pair = row["pair"].strip()
        ie_id = row["ie_id"].strip()
        version_id = row["version_id"].strip()
        edition = row["edition"].strip()
        locator = row["source_locator"].strip()
        coder_ids = split_ids(row["channel_coder_ids"])
        adjudicator_id = row["adjudicator_id"].strip()
        if not all((work, pair, ie_id, version_id, edition, locator, adjudicator_id)) or len(coder_ids) != 2:
            raise ValueError("each channel row requires provenance, exactly two coder IDs, and one adjudicator")
        if ie_id in metadata:
            raise ValueError(f"duplicate ie_id: {ie_id}")
        raw_a = tuple(float(row[f"{name}_a"]) for name in "dscp")
        raw_b = tuple(float(row[f"{name}_b"]) for name in "dscp")
        adjudicated = tuple(float(row[name]) for name in "dscp")
        # ChannelIE validates the frozen simplex and 0.25 grid for every vector.
        ChannelIE(work, pair, int(row["global_order"]), f"{ie_id}::coder-a", raw_a)
        ChannelIE(work, pair, int(row["global_order"]), f"{ie_id}::coder-b", raw_b)
        ies.append(ChannelIE(work, pair, int(row["global_order"]), ie_id, adjudicated))
        coder_a.append(raw_a)
        coder_b.append(raw_b)
        metadata[ie_id] = {
            "work_id": work,
            "pair": pair,
            "version_id": version_id,
            "edition": edition,
            "source_locator": locator,
        }
        coders.setdefault(work, set()).update(coder_ids)
        adjudicators.setdefault(work, set()).add(adjudicator_id)
    reliability = channel_reliability(coder_a, coder_b) if rows else {"median_d_tv": None, "row_count": 0, "passed": False}
    return ies, metadata, coders, adjudicators, reliability


def parse_windows(
    rows: list[dict[str, str]],
    derived_windows: list[WindowMetric],
    channel_metadata: dict[str, dict[str, str]],
) -> tuple[list[WindowMetric], list[datetime]]:
    submitted = {row["window_id"].strip(): row for row in rows}
    derived = {window.window_id: window for window in derived_windows}
    if len(submitted) != len(rows):
        raise ValueError("duplicate window_id")
    if set(submitted) != set(derived):
        raise ValueError("submitted window manifest must exactly match mechanically derived complete windows")
    frozen_times = []
    for window_id, window in derived.items():
        row = submitted[window_id]
        ie_ids = tuple(row[f"ie_{index}"].strip() for index in range(1, 6))
        if ie_ids != window.ie_ids:
            raise ValueError(f"window IE membership/order mismatch: {window_id}")
        if row["work_id"].strip() != window.work_id or row["pair"].strip() != window.pair:
            raise ValueError(f"window work/pair mismatch: {window_id}")
        first = channel_metadata[ie_ids[0]]
        last = channel_metadata[ie_ids[-1]]
        if any(channel_metadata[ie_id]["version_id"] != first["version_id"] or channel_metadata[ie_id]["edition"] != first["edition"] for ie_id in ie_ids):
            raise ValueError(f"window crosses version or edition boundaries: {window_id}")
        if row["version_id"].strip() != first["version_id"] or row["edition"].strip() != first["edition"]:
            raise ValueError(f"window provenance mismatch: {window_id}")
        if row["window_end_locator"].strip() != last["source_locator"]:
            raise ValueError(f"window endpoint locator mismatch: {window_id}")
        if not np.isclose(float(row["p_ac"]), window.p_ac, atol=1e-12, rtol=0.0):
            raise ValueError(f"submitted p_ac is not the mechanically derived value: {window_id}")
        if not np.isclose(float(row["p_switch"]), window.p_switch, atol=1e-12, rtol=0.0):
            raise ValueError(f"submitted p_switch is not the mechanically derived value: {window_id}")
        if not row["window_freeze_commit"].strip():
            raise ValueError(f"window freeze commit is required: {window_id}")
        frozen_times.append(parse_timestamp(row["window_frozen_at"], "window_frozen_at"))
    return derived_windows, frozen_times


def parse_timestamp(value: str, field: str) -> datetime:
    normalized = value.strip().replace("Z", "+00:00")
    if not normalized:
        raise ValueError(f"{field} is required for future-blind audit")
    try:
        result = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError(f"{field} must be ISO 8601") from exc
    if result.tzinfo is None or result.utcoffset() is None:
        raise ValueError(f"{field} must include a UTC offset")
    return result


def parse_ratings(rows: list[dict[str, str]]) -> list[Rating]:
    ratings = []
    for row in rows:
        eligibility = parse_timestamp(row["eligibility_decided_at"], "eligibility_decided_at")
        endpoint = parse_timestamp(row["window_endpoint_reached_at"], "window_endpoint_reached_at")
        rated = parse_timestamp(row["rating_timestamp"], "rating_timestamp")
        next_opened_raw = row["next_source_opened_at"].strip()
        next_opened = parse_timestamp(next_opened_raw, "next_source_opened_at") if next_opened_raw else None
        audit_passed = eligibility <= endpoint <= rated and (next_opened is None or rated < next_opened)
        ratings.append(Rating(
            rater_id=row["rater_id"].strip(),
            work_id=row["work_id"].strip(),
            window_id=row["window_id"].strip(),
            prior_exposure=row["prior_exposure"].strip(),
            knows_future=row["knows_future"].strip(),
            exposure_uncertain=row["exposure_uncertain"].strip(),
            question_order=row["question_order"].strip(),
            l_obs=int(row["l_obs"]),
            t_obs=int(row["t_obs"]),
            d_obs=int(row["d_obs"]),
            future_blind=audit_passed,
            valid_primary=parse_bool(row["valid_primary"], "valid_primary"),
        ))
    return ratings


def split_ids(value: str) -> set[str]:
    return {item.strip() for item in value.replace(",", ";").split(";") if item.strip()}


def parse_manifest(rows: list[dict[str, str]]):
    coders: dict[str, set[str]] = {}
    adjudicators: dict[str, set[str]] = {}
    frozen_times = []
    ethics_ready = []
    pilot_result_hashes = set()
    for row in rows:
        work = row["work_id"].strip()
        coders.setdefault(work, set()).update(split_ids(row["channel_coder_ids"]))
        adjudicators.setdefault(work, set()).update(split_ids(row["adjudicator_ids"]))
        if not row["manifest_freeze_commit"].strip():
            raise ValueError("manifest_freeze_commit is required")
        frozen_times.append(parse_timestamp(row["manifest_frozen_at"], "manifest_frozen_at"))
        if parse_bool(row["copyright_content_stored"], "copyright_content_stored"):
            raise ValueError("repository manifest indicates copyrighted source content was stored")
        ethics_hash = row["ethics_record_sha256"].strip().lower()
        pilot_hash = row["discriminant_pilot_result_sha256"].strip().lower()
        pilot_result_hashes.add(pilot_hash)
        ethics_ready.append(
            row["ethics_status"].strip().lower() not in ("", "pending", "unassessed", "unknown")
            and len(ethics_hash) == 64 and all(character in "0123456789abcdef" for character in ethics_hash)
            and len(pilot_hash) == 64 and all(character in "0123456789abcdef" for character in pilot_hash)
        )
    return coders, adjudicators, frozen_times, pilot_result_hashes, bool(rows) and all(ethics_ready)


def validate_discriminant_pilot(
    pilot_result: dict[str, object],
    *,
    result_hash: str | None,
    protocol_hash: str,
    instrument_hash: str,
    manifest_hashes: set[str],
    confirmatory_work_ids: set[str],
    confirmatory_rater_ids: set[str],
) -> tuple[bool, bool | None]:
    pilot_work_ids = set(pilot_result.get("pilot_work_ids", []))
    pilot_rater_hashes = set(pilot_result.get("pilot_rater_id_hashes", []))
    if not pilot_work_ids or not pilot_rater_hashes or pilot_result.get("status") == "NO_DATA":
        return False, None
    confirmatory_rater_hashes = {hashlib.sha256(rater_id.encode()).hexdigest() for rater_id in confirmatory_rater_ids}
    independent = not (pilot_work_ids & confirmatory_work_ids) and not (pilot_rater_hashes & confirmatory_rater_hashes)
    ready = (
        pilot_result.get("status") == "PILOT_PASS"
        and pilot_result.get("protocol_sha256") == protocol_hash
        and pilot_result.get("instrument_sha256") == instrument_hash
        and pilot_result.get("instrument_version") == INSTRUMENT_VERSION
        and result_hash is not None
        and manifest_hashes == {result_hash}
        and independent
    )
    return ready, independent


def main() -> int:
    args = parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    channel_raw, channel_rows = read_csv(args.channels.resolve())
    window_raw, window_rows = read_csv(args.windows.resolve())
    rating_raw, rating_rows = read_csv(args.ratings.resolve())
    manifest_raw, manifest_rows = read_csv(args.manifest.resolve())
    pilot_result_path = args.pilot_result.resolve()
    pilot_result_raw = pilot_result_path.read_bytes() if pilot_result_path.exists() else b""
    pilot_result = json.loads(pilot_result_raw) if pilot_result_raw else {"status": "NO_DATA"}
    pilot_result_hash = file_hash(pilot_result_raw) if pilot_result_raw else None
    discriminant_protocol_hash = file_hash(DISCRIMINANT_PROTOCOL.read_bytes())
    instrument_hash = file_hash(INSTRUMENT.read_bytes())
    input_hashes = {
        "channels_sha256": file_hash(channel_raw),
        "windows_sha256": file_hash(window_raw),
        "ratings_sha256": file_hash(rating_raw),
        "manifest_sha256": file_hash(manifest_raw),
        "pilot_result_sha256": pilot_result_hash,
        "instrument_sha256": instrument_hash,
        "discriminant_protocol_sha256": discriminant_protocol_hash,
    }
    channel_ies, channel_metadata, raw_coders, raw_adjudicators, channel_reliability_result = parse_channels(channel_rows)
    windows, window_freeze_times = parse_windows(window_rows, build_windows(channel_ies), channel_metadata)
    ratings = parse_ratings(rating_rows)
    coders, adjudicators, manifest_freeze_times, pilot_result_hashes, ethics_ready = parse_manifest(manifest_rows)
    if raw_coders != coders or raw_adjudicators != adjudicators:
        raise ValueError("work manifest role assignments must exactly match raw channel rows")
    first_rating_time = min((parse_timestamp(row["rating_timestamp"], "rating_timestamp") for row in rating_rows), default=None)
    freeze_ready = bool(first_rating_time) and all(
        frozen_at < first_rating_time for frozen_at in [*window_freeze_times, *manifest_freeze_times]
    )
    confirmatory_work_ids = set(coders) | {rating.work_id for rating in ratings}
    pilot_ready, pilot_independence_passed = validate_discriminant_pilot(
        pilot_result,
        result_hash=pilot_result_hash,
        protocol_hash=discriminant_protocol_hash,
        instrument_hash=instrument_hash,
        manifest_hashes=pilot_result_hashes,
        confirmatory_work_ids=confirmatory_work_ids,
        confirmatory_rater_ids={rating.rater_id for rating in ratings},
    )
    history_audit = audit_pilot_history(
        args.pilot_history.resolve(),
        expected_history_hashes={row.get("discriminant_pilot_history_sha256", "").strip() for row in manifest_rows},
        selected_result_hash=pilot_result_hash, instrument_hash=instrument_hash,
        protocol_hash=discriminant_protocol_hash, first_confirmatory_rating=first_rating_time,
        confirmatory_works=confirmatory_work_ids,
        confirmatory_raters={rating.rater_id for rating in ratings},
    )
    pilot_ready = pilot_ready and bool(history_audit["ready"])
    input_hashes["pilot_history_sha256"] = history_audit["history_sha256"]
    command = " ".join([Path(sys.executable).name, *sys.argv])
    config = {
        "command": command,
        "master_seed": args.master_seed,
        "input_files": {
            "channels": str(args.channels.resolve()),
            "windows": str(args.windows.resolve()),
            "ratings": str(args.ratings.resolve()),
            "manifest": str(args.manifest.resolve()),
            "pilot_result": str(pilot_result_path),
            "pilot_history": str(args.pilot_history.resolve()),
        },
        "input_hashes": input_hashes,
        "window_size": 5,
        "minimum_raters": MIN_RATERS,
        "reliability_repeats": RELIABILITY_REPEATS,
        "reliability_gate": RELIABILITY_GATE,
        "cross_validation": "Leave-One-Work-Out",
        "models": ["ML", "MLAC", "M0", "M1"],
    }
    environment = {"git_commit": git_sha(), "python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__}
    dump_json(output / "config.json", config)
    dump_json(output / "environment.json", environment)

    warnings = []
    pilot_audit = {
        "ready": pilot_ready,
        "status": pilot_result.get("status"),
        "protocol_sha256": discriminant_protocol_hash,
        "result_sha256": pilot_result_hash,
        "selected_result_independence_passed": pilot_independence_passed,
        "independence_passed": history_audit["independence_passed"],
        "instrument_sha256": instrument_hash,
        "instrument_version": INSTRUMENT_VERSION,
        "history": history_audit,
    }
    exclusions = {"non_primary_ratings": 0, "window_status": {}}
    fold_rows: list[dict[str, object]] = []
    reliability = {}
    model_summary: dict[str, object]
    window_output_rows: list[dict[str, object]] = []

    if not channel_ies and not windows and not ratings and not manifest_rows:
        status = "NO_DATA"
        model_summary = {
            "status": status,
            "channel_reliability": channel_reliability_result,
            "discriminant_pilot": pilot_audit,
            "scores": None,
            "delta_ls_primary": None,
            "delta_ls_love": None,
            "beta_pac_full": None,
            "static_tension_challenge": None,
        }
        warnings.append("Header-only templates contain no human or work data; no scientific result was produced.")
    else:
        validate_question_orders(ratings, args.master_seed)
        role_separation_passed = validate_role_separation(coders, adjudicators, ratings)
        aggregates, window_statuses, eligible_ratings = aggregate_ratings(windows, ratings)
        exclusions = {"non_primary_ratings": len(ratings) - len(eligible_ratings), "window_status": window_statuses}
        reliability = {
            construct: split_half_reliability(eligible_ratings, construct, master_seed=args.master_seed)
            for construct in ("L", "T", "D")
        }
        gate = activation_gate(
            aggregates,
            reliability,
            channel_reliability_passed=bool(channel_reliability_result["passed"]),
            manifest_frozen=freeze_ready and ethics_ready,
            role_separation_passed=role_separation_passed,
        )
        static = static_tension_challenge(aggregates)
        aggregate_map = {item.window_id: item for item in aggregates}
        for window in windows:
            aggregate = aggregate_map.get(window.window_id)
            window_output_rows.append({
                **window.as_dict(),
                "rating_status": window_statuses[window.window_id],
                "rating_count": aggregate.rating_count if aggregate else 0,
                "l_obs": aggregate.l_obs if aggregate else "",
                "t_obs": aggregate.t_obs if aggregate else "",
                "d_obs": aggregate.d_obs if aggregate else "",
            })
        if not pilot_ready:
            status = "PILOT_NOT_PASSED"
            model_summary = {"status": status, "activation_gate": gate.as_dict(),
                             "discriminant_pilot": pilot_audit, "scores": None,
                             "channel_reliability": channel_reliability_result,
                             "delta_ls_primary": None, "delta_ls_love": None,
                             "beta_pac_full": None, "static_tension_challenge": None}
            warnings.append("Pilot evidence did not pass; confirmatory models were not fitted.")
        elif gate.passed:
            try:
                analysis = leave_one_work_out(aggregates)
                fold_rows = analysis.pop("predictions")
                primary_model_status = str(analysis.pop("primary_status"))
                status = bridge_verdict(
                    float(analysis["beta_pac_full"]),
                    float(analysis["delta_ls_primary"]),
                    static_tension_failed=static["status"] == "FAIL",
                )
                model_summary = {
                    "status": status,
                    "primary_model_status": primary_model_status,
                    "channel_reliability": channel_reliability_result,
                    "discriminant_pilot": pilot_audit,
                    "activation_gate": gate.as_dict(),
                    **analysis,
                    "static_tension_challenge": static,
                }
            except ModelIdentificationError as exc:
                status = "MODEL_IDENTIFICATION_FAILURE"
                model_summary = {"status": status, "channel_reliability": channel_reliability_result, "discriminant_pilot": pilot_audit, "activation_gate": gate.as_dict(), "scores": None, "delta_ls_primary": None, "delta_ls_love": None, "beta_pac_full": None, "static_tension_challenge": static, "identification_error": str(exc)}
                warnings.append(f"Frozen linear model could not be identified: {exc}")
        else:
            status = gate.status
            model_summary = {"status": status, "channel_reliability": channel_reliability_result, "discriminant_pilot": pilot_audit, "activation_gate": gate.as_dict(), "scores": None, "delta_ls_primary": None, "delta_ls_love": None, "beta_pac_full": None, "static_tension_challenge": static}
            warnings.append(f"Confirmatory analysis was not activated: {status}.")

    reliability_json = {key: value.as_dict() for key, value in reliability.items()}
    dump_json(output / "rater_reliability.json", reliability_json)
    dump_json(output / "model_summary.json", model_summary)
    window_fields = ["window_id", "work_id", "pair", "ie_ids", "p_ac", "p_switch", "rating_status", "rating_count", "l_obs", "t_obs", "d_obs"]
    write_csv(output / "window_metrics.csv", window_fields, window_output_rows)
    fold_fields = ["holdout_work", "window_id", "model", "observed_t", "predicted_t", "predictive_scale", "df", "log_predictive_density", "train_work_count", "train_works", "train_predictor_means", "train_predictor_sds", "coefficients"]
    write_csv(output / "fold_predictions.csv", fold_fields, fold_rows)

    gate_report = model_summary.get("activation_gate")
    report = [
        "# Romantic Tension Bridge Analysis Report", "",
        "Generated by `scripts/run_tension_bridge_analysis.py`; do not edit by hand.", "",
        "## Provenance", "",
        f"- Git commit: `{environment['git_commit']}`",
        f"- Input hashes: `{input_hashes}`",
        f"- Master seed: `{args.master_seed}`",
        f"- Exact command: `{command}`", "",
        "## Corpus and reliability", "",
        f"- Works / dyads / eligible windows: `{gate_report if gate_report is not None else 'no data'}`",
        f"- Ratings per window and exclusions: `{exclusions}`",
        f"- Channel reliability: `{channel_reliability_result}`",
        f"- Rater reliability: `{reliability_json}`", "",
        "## Models and challenges", "",
        f"- Model summary: `{model_summary}`",
        f"- Final primary status: `{model_summary['status']}`", "",
        "## Warnings", "",
        *([f"- {warning}" for warning in warnings] or ["- None."]), "",
    ]
    (output / "REPORT.md").write_text("\n".join(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
