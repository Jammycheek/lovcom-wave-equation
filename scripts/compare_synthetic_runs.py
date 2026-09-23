#!/usr/bin/env python
"""Read-only replicate/forecast comparison; never infers benchmark acceptance."""

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path


def indexed(path, fields):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    result = {tuple(row[field] for field in fields): row for row in rows}
    if len(result) != len(rows) or not rows:
        raise ValueError(f"empty or duplicate keys: {path}")
    return result


def boolean(value):
    if value.lower() not in {"true", "false"}:
        raise ValueError("converged must be True or False")
    return value.lower() == "true"


def maximum_difference(left, right, field):
    differences = []
    for key in left:
        a, b = float(left[key][field]), float(right[key][field])
        if not math.isfinite(a) or not math.isfinite(b):
            raise ValueError(f"non-finite {field} for {key}")
        differences.append(abs(a - b))
    return max(differences)


def compare(left: Path, right: Path):
    a = indexed(left / "replicates.csv", ("scenario", "seed"))
    b = indexed(right / "replicates.csv", ("scenario", "seed"))
    if a.keys() != b.keys():
        raise ValueError("replicate scenario/seed membership differs")
    flipped = [list(key) for key in sorted(a) if boolean(a[key]["converged"]) != boolean(b[key]["converged"])]
    maxima = {field: maximum_difference(a, b, field) for field in (
        "FIT_log_likelihood", "fitted_Delta", "fitted_R", "fitted_Omega", "holdout_LS_RCWE")}
    forecast_a = indexed(left / "predictions.csv", ("scenario", "seed", "model", "interaction_index"))
    forecast_b = indexed(right / "predictions.csv", ("scenario", "seed", "model", "interaction_index"))
    if forecast_a.keys() != forecast_b.keys():
        raise ValueError("per-IE prediction membership differs")
    forecast_a = {key: row for key, row in forecast_a.items() if key[2] == "rcwe"}
    forecast_b = {key: row for key, row in forecast_b.items() if key[2] == "rcwe"}
    if {key[:2] for key in forecast_a} != set(a):
        raise ValueError("every replicate must have RCWE forecast evidence")
    maxima["holdout_predicted_mu"] = maximum_difference(forecast_a, forecast_b, "predicted_mu")
    hashes = {label: {name: hashlib.sha256((directory / name).read_bytes()).hexdigest()
                      for name in ("replicates.csv", "predictions.csv")}
              for label, directory in (("left", left), ("right", right))}
    return {"replicates": len(a), "input_hashes": hashes, "maximum_absolute_differences": maxima,
            "convergence_flipped_ids": flipped, "convergence_membership_equal": not flipped,
            "numerical_tolerances_met": maxima["FIT_log_likelihood"] <= 1e-6 and maxima["holdout_predicted_mu"] <= 1e-8,
            "refitted_forecast_tolerance_status": "NOT_PREREGISTERED",
            "numerical_tolerances_scope": "historical v0.1 fitted-run diagnostic; not acceptance",
            "acceptance_status": "NOT_ASSESSED",
            "note": "Runtime/build eligibility and scientific acceptance require separate review; matching counts are insufficient."}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("left", type=Path)
    parser.add_argument("right", type=Path)
    args = parser.parse_args()
    print(json.dumps(compare(args.left, args.right), indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
