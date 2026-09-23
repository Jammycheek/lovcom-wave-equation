# Changelog

## Unreleased — fourth-review R-4 safeguard

- Pilot v0.4 enforces suffix-only nonresponse per planned rater/window order. A resumed answer yields terminal `PILOT_PROTOCOL_DEVIATION`; source/roster or cutoff-registration inconsistencies yield terminal `PILOT_PROVENANCE_FAILURE`.
- Require a cutoff snapshot of actual answer rows, externally registered SHA-256 and receipt metadata, exact match to all pre-cutoff roster answers, and independent receipt-verification metadata before confirmatory activation. The runner cannot itself prove the external registration's authenticity.
- Remove analyst-controlled `valid_pilot` and `valid_primary` input columns. The confirmatory exclusion change is a separately versioned addendum; until its source-export commitment is specified, the runner fails closed with `CONFIRMATORY_SOURCE_PROVENANCE_PENDING` rather than a support verdict.
- Independently reran the comparison utility on the supplied Linux artifacts in separate commit `67c4fc0`; pinned-vs-older Linux numerical outputs agree exactly, and both differ from the committed Windows classification on 10/40 exposed cases. No thresholds were changed.

## Unreleased — third-review follow-up (R-1 through R-3)

- R-1: retain the fixed-parameter solver-only `1e-8` agreement check, but label the historical independently refitted `1e-8` comparison as a failed diagnostic rather than an acceptance gate. A distinct refitted-forecast tolerance requires an unexposed development block. Record the reviewer's 12/40 discrepancy as reported evidence, pending the raw reproduction bundle.
- R-2: version the T/D pilot as v0.3. Freeze one recruitment cutoff and represent every planned cell as an actual `ANSWERED` row or a blank-valued `NONRESPONSE`; keep late answers in raw data but out of the primary analysis. Emit insufficient-data or cancelled-plan results without silently replacing the plan.
- R-3: require an external timestamped registration of the plan hash before the first rating, one plan per instrument version. A real plan, receipt, participants and outcomes are still absent.
- N-1, N-3 and N-4 passed the reviewer's mutation and runtime checks. N-2 and N-5 remain open; no freeze tag or scientific pass claim follows from this update.

## Unreleased — second-review safeguards (N-1 through N-5)

- N-1: fix the pilot sampling plan before ratings; require exact work/window/rater cells and a sealed, complete result history. Failed or changed-plan evidence cannot activate confirmation. Real collection remains pending.
- N-3: derive the truth-start guard from every default scenario, ignoring noise scale; mutation regressions now call the intended guard test and catch appended exact/near truths.
- N-4: version the romantic-uncertainty form as v1.1 and bind its complete bytes in pilot and confirmatory artifacts. Add explicit `PILOT_NOT_PASSED` and unassessed no-data independence.
- N-5 partial: pin NumPy/SciPy and the canonical Python/runtime family, capture numerical build provenance, add a non-acceptance three-state diagnostic, and quarantine all 40 exposed cases. Preserve the original benchmark and stationarity gate unchanged.
- N-2 remains open: record the required scientific acceptance decisions and prohibit executable benchmark PASS claims until independently preregistered criteria exist. No new thresholds, validation seed blocks, tags or scientific results were invented.
- Add per-replicate progress/checkpoints and a conservative worker default; reject overwriting existing benchmark or completed pilot results.

## Unreleased — initial research import

- Consolidated the RCWE v2.0 frozen core.
- Separated channel allocation, relationship direction, masking, events, character belief, and analyst posterior.
- Added the E/O/M/L/B phase classification.
- Added Annotation Codebook v0.2.1 and its reliability gates.
- Added Tension Bridge v0.1.
- Added protocols for Subjects 5, 6, 7, and the prospective control.
- Added a failure log and a v2.1 candidate registry.

This import intentionally excludes exploratory parameter estimates, superseded five-channel annotations, post-hoc forcing terms, and copyrighted source text.

## Unreleased — review corrections

- Restored the full conceptual RCWE architecture and separate interaction-event layer.
- Restored the prospective control's C1/C2/C3 tests while leaving unread-boundary metadata unresolved.
- Restored Origin Channel Persistence and Finite-Horizon Effect to the v2.1 registry.
- Added Predictive Scoring Specification v0.1 with open-loop holdout forecasting and discretized-Gaussian log scoring.
- Replaced the contradictory Subject 7 channel-lock condition with Direct-boundary lock definitions.
- Recorded the Subject 7 H7-3 shadow failure without promoting it to formal evidence.
- Split character-belief fields, clarified Subject 6 qualified IEs, and removed the `J` symbol collision.
- Marked Tension Bridge v0.1 as a preregistered concept whose experiment is not frozen.
- Added and implemented the Subject 6 probabilistic-comparison addendum without activating M_C.
- Fixed the Samuwan control's information-exposure boundary at the end of comic volume 3 as of 2026-09-21; exact prospective source-unit identifiers and coder access controls remain pending.
- Wired the Tension Bridge experiment to raw double-coded channels, mechanically derived windows, auditable freeze/future-blind timestamps, within-work reliability, role separation, and static-challenge precedence. Activation remains pending a separately frozen discriminant-validity pilot.
- Replaced truth-matching synthetic starts with four data-independent starts, froze optimizer settings, added cross-start agreement, direct fit/gradient tests, and baseline guard warnings.
- Split Subject 6 exposure and outcome inputs across distinct commits, capped the confirmatory corpus at the first 10 qualified IEs per pair, and compute Direction kappa from raw double coding.
- Closed Samuwan C1/C3 underspecification and added external provenance for the unread-boundary declaration.
- Reran the frozen 40-replicate synthetic benchmark: strict cross-start agreement failed in all 40 fits, recorded as `F-07`; no thresholds or model terms were changed to rescue the result.
- Diagnosed `F-07` as a false-termination defect caused by a flat `1e300` invalid-point penalty; replaced it with a finite quadratic penalty, added an explicit projected-gradient stationarity gate, and preserved the invalidated run in the audit log.
- Added the independent Tension Bridge T/D discriminant-validity pilot, frozen `.85` work-cluster-bootstrap gate, raw runner, data templates, result hashing, and confirmatory non-reuse checks.
- Completed the corrected 40-replicate benchmark: `31/40` met strict convergence and all 31 recovered the generating regime; the remaining nine are retained as `F-08` rather than repaired post hoc.
