#!/usr/bin/env python
"""Run the frozen Subject 6 M_A/M_B prequential comparison."""

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

from rcwe.subject6_compare import ALPHA, CATEGORIES, DIRECTION_KAPPA_GATE, PAIRS, compare, row_from_mapping


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--exposures", type=Path, default=ROOT / "data" / "subject6_exposures_template.csv")
    parser.add_argument("--outcomes", type=Path, default=ROOT / "data" / "subject6_outcomes_template.csv")
    parser.add_argument("--manifest", type=Path, default=ROOT / "data" / "subject6_comparison_manifest_template.csv")
    parser.add_argument("--output", type=Path, default=ROOT / "results" / "subject6_comparison")
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
            raise ValueError(f"{path} requires a CSV header")
        return raw, list(reader)


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def git_sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unavailable"


def dump_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def cohen_kappa(coder_a: list[str], coder_b: list[str]) -> float | None:
    if len(coder_a) != len(coder_b) or not coder_a:
        return None
    if any(value not in CATEGORIES for value in [*coder_a, *coder_b]):
        raise ValueError("raw direction codes must use the frozen four-category vocabulary")
    observed = sum(a == b for a, b in zip(coder_a, coder_b)) / len(coder_a)
    expected = sum((coder_a.count(category) / len(coder_a)) * (coder_b.count(category) / len(coder_b)) for category in CATEGORIES)
    if expected == 1.0:
        return 1.0 if observed == 1.0 else None
    return (observed - expected) / (1.0 - expected)


def parse_and_join(exposure_rows, outcome_rows, manifest_rows):
    if not exposure_rows and not outcome_rows and not manifest_rows:
        return [], None, None
    if len(manifest_rows) != 1:
        raise ValueError("a nonempty run requires exactly one frozen comparison manifest row")
    manifest = manifest_rows[0]
    if not parse_bool(manifest["qualified_ie_coding_complete"], "qualified_ie_coding_complete"):
        raise ValueError("all Volume 5 qualified-IE coding must be complete before outcomes are joined")
    exposure_commit = manifest["exposure_freeze_commit"].strip()
    outcome_commit = manifest["outcome_commit"].strip()
    if not exposure_commit or not outcome_commit or exposure_commit == outcome_commit:
        raise ValueError("distinct exposure-freeze and outcome commits are required")
    exposures = {row["ie_id"].strip(): row for row in exposure_rows}
    outcomes = {row["ie_id"].strip(): row for row in outcome_rows}
    if len(exposures) != len(exposure_rows) or len(outcomes) != len(outcome_rows):
        raise ValueError("duplicate ie_id")
    if set(exposures) != set(outcomes):
        raise ValueError("exposure and outcome files must contain exactly the same IE identifiers")
    rows = []
    coder_a, coder_b = [], []
    for ie_id, exposure in exposures.items():
        outcome = outcomes[ie_id]
        if exposure["exposure_commit"].strip() != exposure_commit or outcome["outcome_commit"].strip() != outcome_commit:
            raise ValueError("row-level commit provenance does not match the manifest")
        frozen_at = parse_timestamp(exposure["exposure_frozen_at"], "exposure_frozen_at")
        revealed_at = parse_timestamp(outcome["outcome_revealed_at"], "outcome_revealed_at")
        if frozen_at >= revealed_at:
            raise ValueError(f"exposure must be frozen before outcome reveal: {ie_id}")
        a = outcome["direction_coder_a"].strip()
        b = outcome["direction_coder_b"].strip()
        coder_a.append(a)
        coder_b.append(b)
        rows.append(row_from_mapping({
            "global_order": exposure["global_order"], "pair_ie_order": exposure["pair_ie_order"],
            "ie_id": ie_id, "pair": exposure["pair"], "r_dir": outcome["r_dir"],
            "x_shared": exposure["x_shared"], "source_locator": exposure["source_locator"],
            "direction_adjudicated": outcome["direction_adjudicated"],
            "shared_event_adjudicated": exposure["shared_event_adjudicated"],
        }))
    for pair in PAIRS:
        orders = sorted(row.pair_ie_order for row in rows if row.pair == pair)
        if orders != list(range(1, len(orders) + 1)):
            raise ValueError(f"{pair} pair_ie_order must be contiguous from 1")
    return rows, cohen_kappa(coder_a, coder_b), manifest


def blank_summary(status: str, row_count: int, kappa: float | None) -> dict[str, object]:
    return {"status": status, "direction_kappa": kappa, "direction_kappa_gate": DIRECTION_KAPPA_GATE, "row_count": row_count, "pooled": None, "pair_summaries": [], "activation_gate": None}


def main() -> int:
    args = parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    exposure_raw, exposure_rows = read_csv(args.exposures.resolve())
    outcome_raw, outcome_rows = read_csv(args.outcomes.resolve())
    manifest_raw, manifest_rows = read_csv(args.manifest.resolve())
    rows, kappa, manifest = parse_and_join(exposure_rows, outcome_rows, manifest_rows)
    hashes = {"exposures_sha256": sha256(exposure_raw), "outcomes_sha256": sha256(outcome_raw), "manifest_sha256": sha256(manifest_raw)}
    command = " ".join([Path(sys.executable).name, *sys.argv])
    config = {
        "command": command,
        "input_files": {"exposures": str(args.exposures.resolve()), "outcomes": str(args.outcomes.resolve()), "manifest": str(args.manifest.resolve())},
        "input_hashes": hashes, "category_order": list(CATEGORIES), "pairs": list(PAIRS), "alpha": ALPHA,
        "pair_ie_cap": 10, "direction_kappa_gate": DIRECTION_KAPPA_GATE,
        "activation_gate": {"total_rows_min": 12, "x_shared_0_min": 4, "x_shared_1_min": 4, "pairs_with_both_exposures_min": 2},
        "models": ["M_A", "M_B"], "M_C_implemented": False,
    }
    dump_json(output / "config.json", config)
    warnings: list[str] = []
    if not rows and manifest is None:
        summary = blank_summary("NO_DATA", 0, None)
        warnings.append("Header-only templates contain no observations; no score or A/B verdict was produced.")
        prediction_rows, pair_rows = [], []
    elif kappa is None:
        summary = blank_summary("DIRECTION_RELIABILITY_NOT_IDENTIFIABLE", len(rows), None)
        warnings.append("Direction reliability could not be identified from the raw double-coded outcomes.")
        prediction_rows, pair_rows = [], []
    elif kappa < DIRECTION_KAPPA_GATE:
        summary = blank_summary("MEASUREMENT_FAILURE", len(rows), kappa)
        warnings.append(f"Computed direction kappa={kappa} is below the frozen {DIRECTION_KAPPA_GATE} gate.")
        prediction_rows, pair_rows = [], []
    else:
        result = compare(rows)
        summary = {**result.as_dict(), "direction_kappa": kappa, "direction_kappa_gate": DIRECTION_KAPPA_GATE, "row_count": len(rows)}
        prediction_rows = [row.as_dict() for row in result.predictions]
        pair_rows = [result.pooled.as_dict(), *[item.as_dict() for item in result.pair_summaries]]
        if not result.activation_gate.passed:
            warnings.append("Activation gate failed; log scores are descriptive and no support verdict was issued.")
    prediction_fields = ["global_order", "pair_ie_order", "ie_id", "pair", "r_dir", "x_shared", "source_locator", "p_a_observed", "p_b_observed", "ls_a", "ls_b", "delta_ls", "p_a_minus1", "p_a_zero", "p_a_plus1", "p_a_mixed", "p_b_minus1", "p_b_zero", "p_b_plus1", "p_b_mixed"]
    write_csv(output / "per_ie_predictions.csv", prediction_fields, prediction_rows)
    write_csv(output / "pair_summary.csv", ["scope", "row_count", "ls_a", "ls_b", "delta_ls", "mean_ls_a", "mean_ls_b"], pair_rows)
    dump_json(output / "summary.json", summary)
    report = [
        "# Subject 6 Probabilistic Comparison Report", "", "Generated by `scripts/run_subject6_comparison.py`; do not edit by hand.", "",
        "## Provenance", "", f"- Git commit: `{git_sha()}`", f"- Input hashes: `{hashes}`", f"- Input rows: `{len(rows)}`", f"- Python: `{platform.python_version()}`", f"- Exact command: `{command}`", "",
        "## Result", "", f"- Status: `{summary['status']}`", f"- Computed Direction kappa: `{kappa}`", f"- Exposure counts: `{summary.get('activation_gate') or 'not scored'}`", f"- Scores: `{summary.get('pooled') or 'not scored'}`", f"- Pair-level scores: `{summary.get('pair_summaries', [])}`", "",
        "## Warnings", "", *([f"- {warning}" for warning in warnings] or ["- None."]), "",
    ]
    (output / "REPORT.md").write_text("\n".join(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
