#!/usr/bin/env python
"""Run the frozen Subject 6 M_A/M_B prequential comparison."""

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

from rcwe.subject6_compare import (
    ALPHA,
    CATEGORIES,
    DIRECTION_KAPPA_GATE,
    PAIRS,
    compare,
    row_from_mapping,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=Path,
        default=ROOT / "data" / "subject6_comparison_template.csv",
        help="adjudicated Subject 6 CSV",
    )
    parser.add_argument("--direction-kappa", type=float, default=None)
    parser.add_argument("--output", type=Path, default=ROOT / "results" / "subject6_comparison")
    return parser.parse_args()


def git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unavailable"


def dump_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def read_input(path: Path):
    raw = path.read_bytes()
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("input CSV must contain a header")
        rows = [row_from_mapping(row) for row in reader]
    return raw, rows


def blank_summary(status: str, row_count: int, kappa: float | None) -> dict[str, object]:
    return {
        "status": status,
        "direction_kappa": kappa,
        "direction_kappa_gate": DIRECTION_KAPPA_GATE,
        "row_count": row_count,
        "pooled": None,
        "pair_summaries": [],
        "activation_gate": None,
    }


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    args = parse_args()
    input_path = args.input.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    raw, rows = read_input(input_path)
    input_hash = hashlib.sha256(raw).hexdigest()
    command = " ".join([Path(sys.executable).name, *sys.argv])
    config = {
        "command": command,
        "input_path": str(input_path),
        "input_sha256": input_hash,
        "category_order": list(CATEGORIES),
        "pairs": list(PAIRS),
        "alpha": ALPHA,
        "direction_kappa": args.direction_kappa,
        "direction_kappa_gate": DIRECTION_KAPPA_GATE,
        "activation_gate": {
            "total_rows_min": 12,
            "x_shared_0_min": 4,
            "x_shared_1_min": 4,
            "pairs_with_both_exposures_min": 2,
        },
        "models": ["M_A", "M_B"],
        "M_C_implemented": False,
    }
    dump_json(output / "config.json", config)

    warnings = []
    if not rows:
        summary = blank_summary("NO_DATA", 0, args.direction_kappa)
        warnings.append("Template input contains no observations; no score or A/B verdict was produced.")
        prediction_rows = []
        pair_rows = []
    elif args.direction_kappa is None:
        summary = blank_summary("DIRECTION_RELIABILITY_NOT_ASSESSED", len(rows), None)
        warnings.append("Direction reliability kappa was not supplied; confirmatory comparison was not run.")
        prediction_rows = []
        pair_rows = []
    elif args.direction_kappa < DIRECTION_KAPPA_GATE:
        summary = blank_summary("MEASUREMENT_FAILURE", len(rows), args.direction_kappa)
        warnings.append(
            f"Direction reliability kappa={args.direction_kappa} is below the frozen {DIRECTION_KAPPA_GATE} gate."
        )
        prediction_rows = []
        pair_rows = []
    else:
        result = compare(rows)
        summary = {
            **result.as_dict(),
            "direction_kappa": args.direction_kappa,
            "direction_kappa_gate": DIRECTION_KAPPA_GATE,
            "row_count": len(rows),
        }
        prediction_rows = [row.as_dict() for row in result.predictions]
        pair_rows = [result.pooled.as_dict(), *[item.as_dict() for item in result.pair_summaries]]
        if not result.activation_gate.passed:
            warnings.append("Activation gate failed; log scores are descriptive and no support verdict was issued.")

    prediction_fields = [
        "global_order", "ie_id", "pair", "r_dir", "x_shared", "source_locator",
        "p_a_observed", "p_b_observed", "ls_a", "ls_b", "delta_ls",
        "p_a_minus1", "p_a_zero", "p_a_plus1", "p_a_mixed",
        "p_b_minus1", "p_b_zero", "p_b_plus1", "p_b_mixed",
    ]
    summary_fields = ["scope", "row_count", "ls_a", "ls_b", "delta_ls", "mean_ls_a", "mean_ls_b"]
    write_csv(output / "per_ie_predictions.csv", prediction_fields, prediction_rows)
    write_csv(output / "pair_summary.csv", summary_fields, pair_rows)
    dump_json(output / "summary.json", summary)

    pooled = summary.get("pooled")
    gate = summary.get("activation_gate")
    report = [
        "# Subject 6 Probabilistic Comparison Report",
        "",
        "Generated by `scripts/run_subject6_comparison.py`; do not edit by hand.",
        "",
        "## Provenance",
        "",
        f"- Git commit: `{git_sha()}`",
        f"- Input SHA-256: `{input_hash}`",
        f"- Input rows: `{len(rows)}`",
        f"- Python: `{platform.python_version()}`",
        f"- Exact command: `{command}`",
        "",
        "## Result",
        "",
        f"- Status: `{summary['status']}`",
        f"- Exposure counts: `{gate if gate is not None else 'not scored'}`",
        f"- LS_A / LS_B / Delta_LS: `{pooled if pooled is not None else 'not scored'}`",
        f"- Pair-level scores: `{summary.get('pair_summaries', [])}`",
        "",
        "## Warnings",
        "",
        *([f"- {warning}" for warning in warnings] or ["- None."]),
        "",
    ]
    (output / "REPORT.md").write_text("\n".join(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
