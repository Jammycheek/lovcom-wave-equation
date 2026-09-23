# Second-review response: N-1 through N-5

Overall verdict remains **NOT READY for spec freeze**. This response separates executable corrections from scientific decisions still requiring approval. No human outcomes or new synthetic validation block were opened, and the original 40-case benchmark is unchanged.

| Item | Implemented response | Remaining condition |
|---|---|---|
| N-1 | Pilot v0.3 requires one pre-rating exact work/window/rater plan and cutoff. Confirmation checks a complete sealed history of result hashes; any failed, insufficient or cancelled run blocks activation. Completed pilot output cannot be overwritten. | The reviewer closed the tested optional-stopping paths. Actual work/rater plan, external timestamped registration and auditable completeness declaration have not been supplied. Hashes cannot prove that an external run was not concealed. |
| N-3 | Truth-start guard reads all `DEFAULT_SCENARIOS`, tests the five dynamical parameters independently of noise scale, and examines every start. Four mutation regressions append exact or 2%-perturbed truths and execute the intended guard test. | Closed in the third review: the intended guard test caught exact, perturbed and noise-scale variants. |
| N-4 | Rating form renamed/versioned v1.1; its entire byte hash is bound in the pilot plan, pilot results and confirmation. History entries must match the same instrument/protocol/plan. LF evidence-file convention prevents checkout newline substitution. | Closed in the third review by a one-word mutation; a new independent pilot remains required before confirmation. |
| N-5 | Exact numerical dependency pins, canonical runtime check, BLAS/build/thread provenance, and a separate three-state sensitivity annotation. F-08 corrected to an environment-conditional finding; F-09 attributes the reviewer's cross-platform result. Entire exposed 40-case block quarantined. | **Still open:** independent development calibration, untouched validation and cross-runtime membership audit. Pins or a wider diagnostic band alone do not solve the gate. |
| N-2 | Benchmark emits `acceptance_status: NOT_ASSESSED`; Decisions/README no longer allow retrospective interpretation of 31/40 as a pass. A numerical acceptance plan lists every unresolved approval field and ordering constraint. | **Still open:** scientific numeric thresholds, exact development/validation blocks and their prior approval. No values inferred from the exposed results. |

Additional corrections: explicit `PILOT_NOT_PASSED`, unassessed no-data independence, separate role-separation status, exact `.85` boundary tests, imports usable outside the repository cwd, capped default worker count, progress/checkpoints, and no benchmark-result overwrite.

## Third-review follow-up

The reviewer closed N-1/N-3/N-4 and found no new freeze blocker beyond N-2/N-5. R-1 exposed that the historical `1e-8` per-IE mean check, valid for a fixed-parameter solver comparison, failed for 12 of 40 independently refitted cross-platform paths (reviewer-reported maximum `9.08e-8`). The old comparison remains visible but is explicitly non-acceptance; an independent development block must set the separate refitted tolerance before validation. At the time of this third review, the raw reproduction bundle had not been supplied.

R-2 is addressed by pilot v0.3's explicit `NONRESPONSE` roster cells, pre-frozen cutoff, late-answer exclusion, completed insufficient-data output, and terminal `CANCELLED_PILOT` record. R-3 now requires a durable external timestamped record of one plan hash per instrument version before any rating. The reference code can check local roster and hashes but cannot verify an external service or detect an undeclared attempt. No registration, human ratings or empirical pilot result has been claimed.

The reviewer also found the three-state diagnostic informative about boundary instability but too broad for acceptance (`MARGINAL` for roughly 26–28 of 40 exposed cases). Pinned-library Linux reproduction was still in progress at the time of that review. Do not infer its outcome or choose a threshold from those exposed cases.

## Fourth-review R-4 response and received reproduction evidence

The reviewer closed R-1, found R-2 nearly closed, and demonstrated a selective-missingness attack: changing 128/512 already-answered cells to arbitrary `NONRESPONSE` changed an exploratory pilot from `PILOT_DISCRIMINANT_FAILURE` (`|r|=.829`, upper `.898`) to `PILOT_PASS` (`|r|=.457`, upper `.628`). These are reviewer-reported synthetic adversarial results, not human evidence. A terminal-suffix-only counterexample remained a failure in that test; suffix restriction is necessary but not proof against all selection mechanisms.

Pilot v0.4 now checks the suffix for every planned rater/work, emits terminal `PILOT_PROTOCOL_DEVIATION` on resume-after-nonresponse, and compares every cutoff answer row with a separately hash-registered source export. A missing, mismatched or undeclared cutoff record emits terminal `PILOT_PROVENANCE_FAILURE`. The analyst-controlled `valid_pilot` and confirmatory `valid_primary` input columns are removed. The confirmatory exclusion change is an addendum to the preserved v1.0 protocol. The pilot history requires independently recorded verification metadata for the passing result before it can activate confirmation. Confirmatory models remain fail-closed as `CONFIRMATORY_SOURCE_PROVENANCE_PENDING` until their own source-export protocol is specified. External service authenticity remains outside the runner's proof; no real plan, receipt, or human rating exists.

The reviewer pushed expanded Linux reproduction artifacts at commit `67c4fc0` on a separate branch, without altering PR #1 or `main`. We reran the repository comparison tool on its two raw Linux CSV pairs and the committed Windows run: Windows-to-either-Linux flips `10/40` historical flags, maximum FIT-likelihood difference `1.106315039578476e-11`, maximum per-IE mean difference `9.084153679284057e-8`; Linux-pinned-to-Linux-older has zero numeric difference in the compared fields. File hashes match the Git blobs, including `run.log` after accounting for Windows checkout newline conversion. The original `.tar.gz` archive hash was not checked. These observations update F-09/F-10 as audit evidence, **not** as an acceptance result or a basis for thresholds. N-2/N-5 remain open.

## Reproduction handoff

Local verification: **203 tests passed**; the preceding 202-test suite also passed when invoked from outside the repository cwd. The added 203rd test verifies committed no-data artifacts against current form/protocol/result bytes. Both header-only runners report `NO_DATA` and unassessed independence. Two optional-PyYAML display warnings occur while capturing NumPy/SciPy build configuration; the capture and tests succeed. `pip check` reports no broken installed requirements and `git diff --check` reports no whitespace errors. The committed benchmark was self-compared to exercise the comparison tool only; this is not an independent reproduction. The original benchmark files were not modified.

Run the suite from the repository using its Python 3.12 environment:

```text
python -m pytest -q
```

With the independent reproduction directory available:

```text
python scripts/compare_synthetic_runs.py results/synthetic_recovery PATH_TO_REPRODUCED_RUN
```

The comparison is read-only. It checks replicate and prediction IDs, membership flips, all FIT likelihoods and per-IE RCWE forecast means. The per-IE mean tolerance is not inferred from total Log Score. It reports `NOT_ASSESSED` even if numeric tolerances match, because scientific acceptance and runtime eligibility require separate review. The artifacts were subsequently supplied on the separate commit identified above; they are not merged into this PR branch.

## Decisions requested before numerical work resumes

Use `NUMERICAL_RECOVERY_ACCEPTANCE_PLAN_v0.1.md` to approve a genuinely unexposed development block and its fixed design first. After calibration, freeze exact acceptance thresholds and an untouched validation block before opening validation. The preregistration must specify how marginal/failed fits enter the denominator, parameter-error criteria, regime-recovery criteria, and allowed between-runtime membership disagreement. The current 40 cases are retrospective audits only.

No `main` merge, freeze tag, stationarity-threshold change, start-set change, or post-hoc rescue is part of this response.
