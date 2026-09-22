#!/usr/bin/env python
"""Run the frozen Tension Bridge confirmatory analysis."""

from __future__ import annotations

import argparse
import csv
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

from rcwe.tension_bridge import (
    MIN_RATERS,
    RELIABILITY_GATE,
    RELIABILITY_REPEATS,
    Rating,
    WindowMetric,
    activation_gate,
    aggregate_ratings,
    leave_one_work_out,
    split_half_reliability,
    static_tension_challenge,
    validate_question_orders,
    validate_role_separation,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--windows", type=Path, default=ROOT / "data" / "tension_bridge_windows_template.csv")
    parser.add_argument("--ratings", type=Path, default=ROOT / "data" / "tension_bridge_ratings_template.csv")
    parser.add_argument("--manifest", type=Path, default=ROOT / "data" / "tension_bridge_work_manifest_template.csv")
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
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def parse_windows(rows: list[dict[str, str]]) -> tuple[list[WindowMetric], bool, bool]:
    windows = []
    channel_passes = []
    frozen_flags = []
    for row in rows:
        ie_ids = tuple(row[f"ie_{index}"].strip() for index in range(1, 6))
        if len(set(ie_ids)) != 5 or not all(ie_ids):
            raise ValueError("every frozen window requires five distinct IE identifiers")
        p_ac = float(row["p_ac"])
        p_switch = float(row["p_switch"])
        if p_ac < 0 or p_switch < 0:
            raise ValueError("P_AC and P_switch cannot be negative")
        windows.append(WindowMetric(row["window_id"].strip(), row["work_id"].strip(), row["pair"].strip(), ie_ids, p_ac, p_switch))
        channel_passes.append(parse_bool(row["channel_reliability_passed"], "channel_reliability_passed"))
        frozen_flags.append(parse_bool(row["frozen_before_ratings"], "frozen_before_ratings"))
    if len({window.window_id for window in windows}) != len(windows):
        raise ValueError("duplicate window_id")
    return windows, bool(windows) and all(channel_passes), bool(windows) and all(frozen_flags)


def parse_ratings(rows: list[dict[str, str]]) -> list[Rating]:
    return [
        Rating(
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
            future_blind=parse_bool(row["future_blind"], "future_blind"),
            valid_primary=parse_bool(row["valid_primary"], "valid_primary"),
        )
        for row in rows
    ]


def split_ids(value: str) -> set[str]:
    return {item.strip() for item in value.replace(",", ";").split(";") if item.strip()}


def parse_manifest(rows: list[dict[str, str]]):
    coders: dict[str, set[str]] = {}
    adjudicators: dict[str, set[str]] = {}
    frozen = []
    ethics_ready = []
    for row in rows:
        work = row["work_id"].strip()
        coders.setdefault(work, set()).update(split_ids(row["channel_coder_ids"]))
        adjudicators.setdefault(work, set()).update(split_ids(row["adjudicator_ids"]))
        frozen.append(parse_bool(row["manifest_frozen"], "manifest_frozen"))
        if parse_bool(row["copyright_content_stored"], "copyright_content_stored"):
            raise ValueError("repository manifest indicates copyrighted source content was stored")
        ethics_ready.append(row["ethics_status"].strip().lower() not in ("", "pending", "unassessed", "unknown"))
    return coders, adjudicators, bool(rows) and all(frozen) and all(ethics_ready)


def main() -> int:
    args = parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    window_raw, window_rows = read_csv(args.windows.resolve())
    rating_raw, rating_rows = read_csv(args.ratings.resolve())
    manifest_raw, manifest_rows = read_csv(args.manifest.resolve())
    input_hashes = {
        "windows_sha256": file_hash(window_raw),
        "ratings_sha256": file_hash(rating_raw),
        "manifest_sha256": file_hash(manifest_raw),
    }
    windows, channel_passed, windows_frozen = parse_windows(window_rows)
    ratings = parse_ratings(rating_rows)
    coders, adjudicators, manifest_ready = parse_manifest(manifest_rows)
    command = " ".join([Path(sys.executable).name, *sys.argv])
    config = {
        "command": command,
        "master_seed": args.master_seed,
        "input_files": {"windows": str(args.windows.resolve()), "ratings": str(args.ratings.resolve()), "manifest": str(args.manifest.resolve())},
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
    exclusions = {"non_primary_ratings": 0, "window_status": {}}
    fold_rows: list[dict[str, object]] = []
    reliability = {}
    model_summary: dict[str, object]
    window_output_rows: list[dict[str, object]] = []

    if not windows and not ratings and not manifest_rows:
        status = "NO_DATA"
        model_summary = {"status": status, "scores": None, "delta_ls_primary": None, "delta_ls_love": None, "beta_pac_full": None, "static_tension_challenge": None}
        warnings.append("Header-only templates contain no human or work data; no scientific result was produced.")
    else:
        validate_question_orders(ratings, args.master_seed)
        validate_role_separation(coders, adjudicators, ratings)
        aggregates, window_statuses, eligible_ratings = aggregate_ratings(windows, ratings)
        exclusions = {"non_primary_ratings": len(ratings) - len(eligible_ratings), "window_status": window_statuses}
        reliability = {
            construct: split_half_reliability(eligible_ratings, construct, master_seed=args.master_seed)
            for construct in ("L", "T", "D")
        }
        gate = activation_gate(
            aggregates,
            reliability,
            channel_reliability_passed=channel_passed,
            manifest_frozen=windows_frozen and manifest_ready,
            role_separation_passed=True,
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
        if gate.passed:
            try:
                analysis = leave_one_work_out(aggregates)
                fold_rows = analysis.pop("predictions")
                status = str(analysis["primary_status"])
                model_summary = {"status": status, "activation_gate": gate.as_dict(), **analysis, "static_tension_challenge": static}
            except ValueError as exc:
                status = "MODEL_IDENTIFICATION_FAILURE"
                model_summary = {"status": status, "activation_gate": gate.as_dict(), "scores": None, "delta_ls_primary": None, "delta_ls_love": None, "beta_pac_full": None, "static_tension_challenge": static, "identification_error": str(exc)}
                warnings.append(f"Frozen linear model could not be identified: {exc}")
        else:
            status = gate.status
            model_summary = {"status": status, "activation_gate": gate.as_dict(), "scores": None, "delta_ls_primary": None, "delta_ls_love": None, "beta_pac_full": None, "static_tension_challenge": static}
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
