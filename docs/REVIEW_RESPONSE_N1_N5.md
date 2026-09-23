# Second-review response: N-1 through N-5

Overall verdict remains **NOT READY for spec freeze**. This response separates executable corrections from scientific decisions still requiring approval. No human outcomes or new synthetic validation block were opened, and the original 40-case benchmark is unchanged.

| Item | Implemented response | Remaining condition |
|---|---|---|
| N-1 | Pilot v0.2 requires one pre-rating exact work/window/rater plan. Confirmation checks a complete sealed history of result hashes; any failed run or changed plan blocks activation. Completed pilot output cannot be overwritten. | Actual work/rater plan and auditable completeness declaration have not been supplied. Hashes cannot prove that an external run was not concealed. |
| N-3 | Truth-start guard reads all `DEFAULT_SCENARIOS`, tests the five dynamical parameters independently of noise scale, and examines every start. Four mutation regressions append exact or 2%-perturbed truths and execute the intended guard test. | Reviewer rerun. No dependency on another optimizer mock failing accidentally. |
| N-4 | Rating form renamed/versioned v1.1; its entire byte hash is bound in the pilot plan, pilot results and confirmation. History entries must match the same instrument/protocol/plan. LF evidence-file convention prevents checkout newline substitution. | New independent pilot required before confirmation; no grandfathered v1.0 result. |
| N-5 | Exact numerical dependency pins, canonical runtime check, BLAS/build/thread provenance, and a separate three-state sensitivity annotation. F-08 corrected to an environment-conditional finding; F-09 attributes the reviewer's cross-platform result. Entire exposed 40-case block quarantined. | **Still open:** independent development calibration, untouched validation and cross-runtime membership audit. Pins or a wider diagnostic band alone do not solve the gate. |
| N-2 | Benchmark emits `acceptance_status: NOT_ASSESSED`; Decisions/README no longer allow retrospective interpretation of 31/40 as a pass. A numerical acceptance plan lists every unresolved approval field and ordering constraint. | **Still open:** scientific numeric thresholds, exact development/validation blocks and their prior approval. No values inferred from the exposed results. |

Additional corrections: explicit `PILOT_NOT_PASSED`, unassessed no-data independence, separate role-separation status, exact `.85` boundary tests, imports usable outside the repository cwd, capped default worker count, progress/checkpoints, and no benchmark-result overwrite.

## Reproduction handoff

Local verification: **202 tests passed**, including a full run invoked from outside the repository cwd. Two optional-PyYAML display warnings occur while capturing NumPy/SciPy build configuration; the capture and tests succeed. `pip check` reports no broken installed requirements and `git diff --check` reports no whitespace errors. The committed benchmark was self-compared to exercise the comparison tool only; this is not an independent reproduction. The original benchmark files were not modified.

Run the suite from the repository using its Python 3.12 environment:

```text
python -m pytest -q
```

With the independent reproduction directory available:

```text
python scripts/compare_synthetic_runs.py results/synthetic_recovery PATH_TO_REPRODUCED_RUN
```

The comparison is read-only. It checks replicate and prediction IDs, membership flips, all FIT likelihoods and per-IE RCWE forecast means. The per-IE mean tolerance is not inferred from total Log Score. It reports `NOT_ASSESSED` even if numeric tolerances match, because scientific acceptance and runtime eligibility require separate review. The reviewer's Linux artifact bundle has not yet been provided to this checkout.

## Decisions requested before numerical work resumes

Use `NUMERICAL_RECOVERY_ACCEPTANCE_PLAN_v0.1.md` to approve a genuinely unexposed development block and its fixed design first. After calibration, freeze exact acceptance thresholds and an untouched validation block before opening validation. The preregistration must specify how marginal/failed fits enter the denominator, parameter-error criteria, regime-recovery criteria, and allowed between-runtime membership disagreement. The current 40 cases are retrospective audits only.

No `main` merge, freeze tag, stationarity-threshold change, start-set change, or post-hoc rescue is part of this response.
