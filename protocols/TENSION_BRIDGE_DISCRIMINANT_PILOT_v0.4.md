# Tension Bridge T/D Discriminant-Validity Pilot v0.4

## Purpose and separation

This pilot must pass before the Tension Bridge confirmatory experiment can activate. It tests whether romantic uncertainty (`T_obs`) and general dramatic tension (`D_obs`) remain empirically distinguishable under the frozen Japanese rating form. It does not test `P_AC`, fit a Bridge model, or provide confirmatory evidence. No human ratings have been collected under this version.

Pilot works, windows, and raters may not be reused in confirmation. Before the first rating, freeze one complete manifest per instrument version: exact work IDs/count, ordered window IDs/count per work, pseudonymous rater IDs per work, one offset-aware recruitment cutoff, version, edition, form hash, freeze timestamp, and commit. Externally timestamp the manifest hash before the first rating; retain the locator and receipt. The minimum sample sizes below are planning constraints, not sequential stopping rules. No replacement recruits, added works, or extended cutoff are allowed.

Every planned rater/window cell appears exactly once in the submitted roster. An `ANSWERED` cell contains the actual response and timestamps, even when ineligible or late. A `NONRESPONSE` cell contains only planned IDs and the status; all response, eligibility, and timestamp fields are blank. For each rater within a work, `NONRESPONSE` may occur only as a contiguous suffix of the manifest's ordered windows. An answer after a nonresponse is a protocol deviation, not a selectively ignorable row: the runner records `PILOT_PROTOCOL_DEVIATION` as a terminal nonpassing result. This rule also covers a participant who skips one window and resumes. The runner does not silently drop the skipped cell or treat it as ordinary attrition.

At the frozen cutoff, export the rating system's unmodified answer rows, including all answers timestamped at or before the cutoff. This **cutoff export** has the same columns as the roster but contains only `ANSWERED` rows. Register its byte-level SHA-256 in an external timestamped record before viewing any pilot statistic. Supply a JSON receipt with `cutoff_export_sha256`, `manifest_sha256`, offset-aware `registered_at`, `registration_locator`, and pseudonymous `export_operator_id`. The runner checks the two hashes, that the declared time is at/after cutoff and no later than analysis, and one-to-one equality of every cutoff answer's cell and full row in the roster. Absent or mismatched evidence produces terminal `PILOT_PROVENANCE_FAILURE`, never a pass. Answers received after cutoff remain in the roster, marked late and excluded from primary analysis; they are not retroactively inserted into the registered cutoff snapshot.

The receipt is an operator claim. Local code cannot verify that an external service actually retained it at the claimed time, or that the rating system export was not altered before registration. Independent verification of the external locator/receipt and source-system controls is required before treating a numerical `PILOT_PASS` as activation evidence. The verifier ID must differ from the export operator ID, and verification must occur after registration but before pilot-history sealing; the code checks these declarations but not real-world independence. Publish only hashes and non-sensitive locators, not participant identities or copyrighted work content. The reference repository contains header-only templates, not a real registration.

Run the final analysis only at or after the frozen cutoff. If minima fail after honest nonresponse and exclusion accounting, record `INSUFFICIENT_PILOT_DATA`. Explicit cancellation may close a frozen plan early; `CANCELLED_PILOT` preserves a reason, membership, input hashes, and completion timestamp. Both are terminal for the instrument version and must enter the sealed pilot history. Missing planned cells or a malformed input prevent a result until corrected against the registered raw export, or the operator cancels the plan. A completed result cannot be overwritten. Changed scientific wording requires a new instrument version and independent pilot; prior attempts remain in history.

## Instrument and administration

Use `TENSION_BRIDGE_RATING_FORM_v1.1.md` unchanged, including all three `L/T/D` questions, canonical sequential presentation, deterministic question-order randomization, and future-blind timestamp audit. `L_obs` is collected to preserve the instrument context but is not part of this discriminant gate. There is no analyst-controlled `valid_pilot` or `valid_primary` input column. Eligibility follows only the frozen exposure answers, timestamp order, and cutoff. The fixed master seed is `RCWE-TB-DISCRIMINANT-v0.4`.

Use at least:

- 30 eligible five-IE windows;
- four independent pilot works;
- five eligible windows per work; and
- 12 eligible future-blind ratings per window.

The same exclusion rules and `T/D` repeated split-half reliability gate (`median r_SB >= .70`) as the confirmatory protocol apply. Insufficient data produce `INSUFFICIENT_PILOT_DATA`; reliability failure produces `PILOT_MEASUREMENT_FAILURE`. Neither is a pass.

## Frozen discriminant statistic

Aggregate eligible ratings by arithmetic mean within each window. For each work separately, subtract that work's mean from its window-level `T_obs` values and separately from its `D_obs` values. Pool the centered values and calculate:

\[
r_{TD}=\operatorname{cor}(T_{centered},D_{centered}).
\]

This removes between-work level differences from the discriminant check. Use `|r_TD|`; negative near-equivalence is as problematic as positive near-equivalence.

Estimate uncertainty with 5,000 deterministic work-cluster bootstrap repetitions. In each repetition, sample the frozen works with replacement, retain every centered window from each sampled work, calculate `|r_TD|`, and store valid values. Report the point value and the 95th percentile of the bootstrap distribution as the one-sided upper bound. With four works only 35 distinct cluster-count compositions exist; the bound is discrete and is not a universal raw-correlation cutoff. Increasing sample size after a failure is prohibited.

## Frozen verdict

The pilot passes only when both are true:

```text
abs(r_TD) < 0.85
upper_95_abs_r_TD < 0.85
```

Otherwise status is `PILOT_DISCRIMINANT_FAILURE`. The `.85` value is a preregistered practical non-equivalence boundary for this experiment, not a universal claim about construct validity. No lower correlation bound is imposed: `D_obs` is a negative-control covariate, not required to correlate with `T_obs`.

## Reproducibility and confirmatory handoff

The runner computes eligibility, counts, reliability, within-work centering, bootstrap, and verdict from the registered-source-matched roster. It emits hashes for roster, manifest, cutoff export, receipt, this protocol, and the entire rating form, plus planned work IDs and hashes of pseudonymous rater IDs. A header-only run yields `NO_DATA`.

Before the first confirmatory rating, seal the complete pilot-history JSON. Enumerate every completed result, including insufficient, failed, protocol-deviation, provenance-failure and cancelled attempts, by path and SHA-256; declare completeness. Every entry must belong to the same instrument/protocol and single frozen manifest and must pass. The confirmatory manifest binds selected-result and history hashes. Missing, failed, cancelled, changed-plan, or mismatched evidence yields `PILOT_NOT_PASSED`. Pilot works/raters cannot be reused.

Hashes cannot discover an unreported external run. The external plan registration and cutoff-export registration must be independently inspected. No real work/rater plan, registration, or human rating data have yet been supplied. This experiment remains inactive.
