#!/usr/bin/env python
"""Generate the frozen RCWE synthetic-recovery benchmark outputs."""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import csv
import json
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np
import scipy

from rcwe.baselines import (
    fit_ar1,
    fit_narrative_position,
    fit_persistence,
    forecast_ar1,
    forecast_narrative_position,
    forecast_persistence,
)
from rcwe.fit import FROZEN_OPTIMIZER, OPTIMIZER_GUARDS, fit_rcwe, forecast_holdout
from rcwe.integrate import REFERENCE_SOLVER
from rcwe.model import classify_local_regime
from rcwe.scoring import score_predictions
from rcwe.synthetic import DEFAULT_SCENARIOS, generate_synthetic


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--replicates", type=int, default=20, help="replicates per scenario")
    parser.add_argument("--seed-base", type=int, default=260901)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--output", type=Path, default=ROOT / "results" / "synthetic_recovery")
    return parser.parse_args()


def git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unavailable"


def json_dump(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def regime_group(classification: str) -> str:
    if classification.startswith("stable"):
        return "stable"
    if classification == "unstable_focus":
        return "oscillatory"
    return classification


def summarize(rows: list[dict[str, object]], scenarios) -> dict[str, object]:
    summary: dict[str, object] = {"replicate_count": len(rows), "scenarios": {}}
    for scenario in scenarios:
        subset = [row for row in rows if row["scenario"] == scenario.name]
        converged = [row for row in subset if row["converged"]]
        recovered = [row for row in converged if row["regime_recovered"]]
        numeric = lambda key: [float(row[key]) for row in converged]
        summary["scenarios"][scenario.name] = {
            "replicates": len(subset),
            "converged": len(converged),
            "convergence_rate": len(converged) / len(subset) if subset else None,
            "regime_recovery_rate_among_converged": len(recovered) / len(converged) if converged else None,
            "median_absolute_error_Delta": float(np.median(numeric("absolute_error_Delta"))) if converged else None,
            "median_absolute_error_R": float(np.median(numeric("absolute_error_R"))) if converged else None,
            "median_absolute_error_G": float(np.median(numeric("absolute_error_G"))) if converged else None,
            "mean_holdout_LS_RCWE": float(np.mean(numeric("holdout_LS_RCWE"))) if converged else None,
            "mean_delta_LS_persistence": float(np.mean(numeric("delta_LS_persistence"))) if converged else None,
            "mean_delta_LS_ar1": float(np.mean(numeric("delta_LS_ar1"))) if converged else None,
            "mean_delta_LS_narrative": float(np.mean(numeric("delta_LS_narrative"))) if converged else None,
        }
    return summary


def run_one(task):
    """Run one independent replicate; top-level for Windows process spawning."""
    scenario, seed = task
    truth_regime = regime_group(str(classify_local_regime(scenario.parameters)["classification"]))
    prediction_rows = []
    fit_detail = None
    series = generate_synthetic(scenario, seed)
    fit_y = series.coded_observation[: scenario.fit_count]
    holdout_y = series.coded_observation[scenario.fit_count :]
    try:
        fitted = fit_rcwe(fit_y, seed=seed)
        rcwe_mu = forecast_holdout(fitted, scenario.holdout_count)
        rcwe_score = score_predictions(holdout_y, rcwe_mu, fitted.sigma_pred, start_index=scenario.fit_count)
        persistence = fit_persistence(fit_y)
        ar1 = fit_ar1(fit_y)
        narrative = fit_narrative_position(fit_y)
        baseline_items = [
            (persistence, forecast_persistence(persistence, scenario.holdout_count)),
            (ar1, forecast_ar1(ar1, scenario.holdout_count, last_fit=float(fit_y[-1]))),
            (narrative, forecast_narrative_position(narrative, scenario.holdout_count)),
        ]
        baseline_scores = {
            item.name: score_predictions(holdout_y, means, item.sigma_pred, start_index=scenario.fit_count)
            for item, means in baseline_items
        }
        local = classify_local_regime(fitted.parameters)
        fitted_regime = regime_group(str(local["classification"]))
        row = {
            "scenario": scenario.name,
            "seed": seed,
            "converged": fitted.converged,
            "successful_starts": fitted.successful_starts,
            "optimizer_agreement": fitted.optimizer_agreement,
            "top_two_log_likelihood_gap": fitted.top_two_log_likelihood_gap,
            "truth_Delta": scenario.parameters.Delta,
            "fitted_Delta": fitted.parameters.Delta,
            "truth_R": scenario.parameters.R,
            "fitted_R": fitted.parameters.R,
            "truth_Omega": scenario.parameters.Omega,
            "fitted_Omega": fitted.parameters.Omega,
            "truth_G": scenario.parameters.G,
            "fitted_G": fitted.parameters.G,
            "truth_regime": truth_regime,
            "fitted_local_regime": fitted_regime,
            "regime_recovered": truth_regime == fitted_regime,
            "absolute_error_Delta": abs(fitted.parameters.Delta - scenario.parameters.Delta),
            "absolute_error_R": abs(fitted.parameters.R - scenario.parameters.R),
            "absolute_error_Omega": abs(fitted.parameters.Omega - scenario.parameters.Omega),
            "absolute_error_G": abs(fitted.parameters.G - scenario.parameters.G),
            "FIT_log_likelihood": fitted.fit_log_likelihood,
            "holdout_LS_RCWE": rcwe_score.LS_total,
            "holdout_MAE_RCWE": rcwe_score.MAE,
            "delta_LS_persistence": rcwe_score.LS_total - baseline_scores["persistence"].LS_total,
            "delta_LS_ar1": rcwe_score.LS_total - baseline_scores["ar1"].LS_total,
            "delta_LS_narrative": rcwe_score.LS_total - baseline_scores["quadratic_narrative_position"].LS_total,
            "baseline_guard_hit_count": sum(len(item.guard_hits) for item, _ in baseline_items),
            "baseline_guard_hits": ";".join(f"{item.name}:{','.join(item.guard_hits)}" for item, _ in baseline_items if item.guard_hits),
            "error": "",
        }
        fit_detail = {
            "scenario": scenario.name,
            "seed": seed,
            "rcwe": fitted.as_dict(),
            "local_regime": local,
            "baselines": [item.as_dict() for item, _ in baseline_items],
        }
        score_sets = [("rcwe", rcwe_score), *baseline_scores.items()]
        for model_name, score in score_sets:
            for score_row in score.rows:
                prediction_rows.append(
                    {"scenario": scenario.name, "seed": seed, "model": model_name, **score_row.as_dict()}
                )
    except Exception as exc:  # Preserve failed replicate as a result.
        row = {
            "scenario": scenario.name,
            "seed": seed,
            "converged": False,
            "truth_Delta": scenario.parameters.Delta,
            "truth_R": scenario.parameters.R,
            "truth_Omega": scenario.parameters.Omega,
            "truth_G": scenario.parameters.G,
            "truth_regime": truth_regime,
            "error": f"{type(exc).__name__}: {exc}",
        }
    return row, fit_detail, prediction_rows


def main() -> int:
    args = parse_args()
    if args.replicates < 1:
        raise SystemExit("--replicates must be at least 1")
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    seeds = [args.seed_base + index for index in range(args.replicates)]
    exact_command = " ".join([Path(sys.executable).name, *sys.argv])
    scenarios = DEFAULT_SCENARIOS
    config = {
        "command": exact_command,
        "replicates_per_scenario": args.replicates,
        "seed_base": args.seed_base,
        "seeds": seeds,
        "optimizer": FROZEN_OPTIMIZER,
        "workers": args.workers,
        "scenarios": [scenario.as_dict() for scenario in scenarios],
        "solver": REFERENCE_SOLVER.as_dict(),
        "optimizer_guards_are_numerical_not_scientific": OPTIMIZER_GUARDS,
    }
    environment = {
        "git_commit": git_sha(),
        "python": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
    }
    json_dump(output / "config.json", config)
    json_dump(output / "environment.json", environment)

    tasks = [(scenario, seed) for scenario in scenarios for seed in seeds]
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        completed = list(executor.map(run_one, tasks))
    rows = [result[0] for result in completed]
    fit_details = [result[1] for result in completed if result[1] is not None]
    prediction_rows = [item for result in completed for item in result[2]]

    fieldnames = sorted({key for row in rows for key in row})
    with (output / "replicates.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    prediction_fields = ["scenario", "seed", "model", "interaction_index", "observed", "predicted_mu", "probability", "log_probability", "absolute_error"]
    with (output / "predictions.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=prediction_fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(prediction_rows)
    json_dump(output / "fit_details.json", fit_details)
    summary = summarize(rows, scenarios)
    json_dump(output / "summary.json", summary)

    warnings = [
        "The observation-model benchmark is characterization, not scientific validation.",
        "Broad optimizer guards prevent numerical overflow and are not scientific parameter bounds.",
        "Poor parameter or regime recovery is reported without changing the frozen model.",
    ]
    convergence_failures = [row for row in rows if not row["converged"]]
    baseline_guard_failures = [row for row in rows if int(row.get("baseline_guard_hit_count", 0)) > 0]
    regime_failures = [row for row in rows if row.get("converged") and not row.get("regime_recovered")]
    warnings.append(
        f"Convergence failures: {len(convergence_failures)} of {len(rows)} replicates."
    )
    warnings.append(
        f"Baseline optimizer guard hits: {len(baseline_guard_failures)} of {len(rows)} replicates; affected comparisons require caution."
    )
    if regime_failures:
        failures = "; ".join(
            f"{row['scenario']} seed={row['seed']} truth={row['truth_regime']} "
            f"fitted={row['fitted_local_regime']} fitted_G={float(row['fitted_G']):.12g}"
            for row in regime_failures
        )
        warnings.append(f"Regime-recovery failures: {failures}.")
    else:
        warnings.append("Regime-recovery failures: none.")
    report = [
        "# RCWE Synthetic Recovery Report",
        "",
        "This file is generated by `scripts/run_synthetic_recovery.py`; do not edit it by hand.",
        "",
        "## Provenance",
        "",
        f"- Exact command: `{exact_command}`",
        f"- Git commit: `{environment['git_commit']}`",
        f"- Python: `{environment['python']}`",
        f"- NumPy: `{environment['numpy']}`",
        f"- SciPy: `{environment['scipy']}`",
        f"- Seeds: `{', '.join(map(str, seeds))}`",
        f"- Solver: `{REFERENCE_SOLVER.as_dict()}`",
        "",
        "## Scenario definitions",
        "",
    ]
    for scenario in scenarios:
        report.append(f"- `{scenario.name}`: `{scenario.as_dict()}`")
    report.extend(["", "## Recovery summary", ""])
    for name, values in summary["scenarios"].items():
        report.append(f"- `{name}`: `{values}`")
    report.extend(["", "## Known failures and warnings", "", *[f"- {warning}" for warning in warnings], ""])
    (output / "REPORT.md").write_text("\n".join(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
