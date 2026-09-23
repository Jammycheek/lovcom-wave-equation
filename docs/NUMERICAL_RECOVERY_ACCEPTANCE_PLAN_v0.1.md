# Numerical recovery acceptance plan v0.1

Status: **DRAFT / NOT ASSESSED / FREEZE BLOCKED**. This is a preregistration checklist, not a declaration that recovery passed. No new scientific acceptance thresholds or seed blocks have been selected. Decisions 17 and 23 do not make the historical `31/40` run a pass.

## Immutable historical evidence

Keep `results/synthetic_recovery/` and its generating revision unchanged. Its `converged` boolean is the v0.1 runtime-conditional rule. The exposed block comprises both default scenarios and seeds 260901 through 260920 (40 scenario/seed pairs). Quarantine the entire block across environments. Neither the original nine rejected IDs nor a reproduction's rejected IDs define a fresh holdout.

The reviewer supplied two Linux reproduction runs separately at commit `67c4fc0` under `review/reproduction_2026-09-23/`. The comparison utility was rerun locally on those raw CSV files against the committed Windows artifacts: both Linux runs flip the same 10/40 historical convergence flags and reach maximum per-IE forecast-mean difference `9.084153679284057e-8`; pinned-vs-older Linux fits and predictions agree numerically exactly. This verifies the supplied artifacts and comparisons, not an independent rerun of either Linux optimization on this host. The original archive SHA-256 was not checked because only expanded files were pushed; per-file Git-blob hashes were checked. Total holdout Log Score agreement remains no substitute for per-IE comparison. All 40 cases remain exposed audit data, not calibration data.

## Runtime contract and replay

- Canonical family: CPython 3.12.14, NumPy 2.5.3, SciPy 1.18.1, Windows AMD64. `pyproject.toml` pins the numerical dependencies and Python minor family. The benchmark also checks the exact runtime family before fitting.
- Record OS, architecture, library build/BLAS configuration, thread environment, worker count, code commit, all initial/final values, raw optimizer flags, projected gradients and likelihoods. Same versions do not imply identical builds or bitwise replay.
- Another family requires `--allow-nonreference-runtime`; no cross-family run is silently called canonical. Diagnostic replay must use a new output directory, never overwrite historical results.
- Compare exact `(scenario, seed)` membership and per-IE predictions. Preserve the historical FIT-likelihood absolute tolerance `1e-6` as a diagnostic. The solver-only `1e-8` forecast-mean tolerance applies with fixed parameters and initial state. Independently refitted forecasts need a **separate, not yet selected** equivalence tolerance calibrated on the development block. Parameter differences, holdout scores and classification differences remain separately reported. The reviewer reported a `9.08e-8` maximum per-IE mean difference, with 12/40 exposed replicates beyond the historical `1e-8` fitted-run test; these numbers are audit observations, not calibration data.
- Use `python scripts/compare_synthetic_runs.py results/synthetic_recovery PATH_TO_REPRODUCED_RUN` for a read-only comparison. It checks duplicate/missing IDs, raw flags, FIT likelihoods and each RCWE holdout mean; matching totals cannot hide membership swaps. Its `numerical_tolerances_met` field applies the **historical** fitted-run `1e-8` diagnostic and does not determine future acceptance. A self-comparison tests the tool only, not independent reproducibility. Missing/non-finite fit evidence raises an error rather than silently excluding cases.
- New benchmark runs checkpoint each completed replicate and report progress. Default workers are capped at four and at the detected logical CPU count; operators may lower the explicit worker count for quota-limited hosts.

## Three-state annotation, not a rescued gate

The reviewer-requested factor-ten neighborhood of the existing gradient cutoff is reported as `MARGINAL`; see `PREDICTIVE_SCORING_SPEC_v0.1.md` for exact implementation. `CONVERGED`/`MARGINAL`/`FAILED` are additional diagnostics. They do not change the v0.1 selected fit, boolean or summary subset. The label `CONVERGED` here does not certify benchmark acceptance. Boundaries of any discrete rule can still be runtime-sensitive.

Do not delete stationarity checking: that would reopen F-07. Do not lower standards until exposed results pass. N-5 is still open after dependency pinning and this annotation.

## Required decision order

1. Before generating development observations, approve and commit its exact seed/scenario list, fixed sample sizes, parameter transformations, diagnostic metrics and allowable numerical changes. Check disjointness from every previously opened block, including test/developer runs.
2. On that development block only, investigate numerical derivative accuracy, termination and sparse regions of the gradient distribution across the intended runtime/build matrix. Any changed optimizer is separately versioned v0.2. Preserve all trials, including failed choices; no optional stopping by enlarging the block.
3. Before opening validation, approve and commit numeric acceptance criteria and one exact untouched validation block. If no defensible stable cutoff emerges, report that result rather than forcing a binary classification.
4. Validate once using the frozen algorithm, runtime policy, block and criteria. A failed validation remains failed. Further redesign requires another version and genuinely fresh validation data; the old block becomes audit-only.
5. Only after independent review of this evidence may `v2.0-spec-freeze` be considered. No tag or merge is authorized by this document.

## Numeric acceptance fields still requiring scientific approval

These must be filled before validation, not inferred from the existing 31/40 result:

- accepted three-state policy and exact stationarity/agreement thresholds;
- minimum convergence rate **per scenario**, denominator including all attempted replicates, errors and marginal cases (never just successful fits);
- minimum correct regime fraction per scenario over all attempted replicates, with failures/marginals counted as not recovered;
- maximum parameter-recovery error for each named parameter, metric/quantile, and handling of non-identifiability;
- maximum between-runtime membership disagreement and the declared runtime/build matrix;
- refitted-forecast per-IE mean equivalence tolerance, independently of the fixed-parameter solver tolerance, and an explicit policy for failed equivalence;
- reference runtime/build matrix for independent Linux or container reproduction, if cross-platform confirmation is required;
- fixed development and validation sample sizes, seed lists and closure rules;
- whether predictive performance is a separate characterization or an acceptance criterion; if the latter, exact baseline comparisons and thresholds.

Until these decisions are approved, the executable benchmark unconditionally reports `acceptance_status: NOT_ASSESSED`. No synthetic recovery claim, empirical Bridge pilot pass, or successful unit test substitutes for these scientific decisions. This is the remaining N-2/N-5 handoff to the research owner and reviewer.
