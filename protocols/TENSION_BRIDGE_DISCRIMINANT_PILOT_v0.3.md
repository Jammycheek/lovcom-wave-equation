# Tension Bridge T/D Discriminant-Validity Pilot v0.3

## Purpose and separation

This pilot must pass before the Tension Bridge confirmatory experiment can activate. It tests whether romantic uncertainty (`T_obs`) and general dramatic tension (`D_obs`) remain empirically distinguishable under the frozen Japanese rating form. It does not test `P_AC`, fit a Bridge model, or provide confirmatory evidence.

Pilot works, windows, and raters may not be reused in the confirmatory study. Before the first rating, freeze one complete manifest per instrument version: exact work IDs/count, window IDs/count per work, pseudonymous rater IDs per work, a single offset-aware recruitment cutoff, version, edition, form hash, freeze timestamp, and commit. The minima below are planning constraints, not sequential stopping rules. Every planned rater/window cell appears exactly once in the submitted roster. An answered cell keeps its actual values and timestamps, including ineligible or late answers; a `NONRESPONSE` cell has no fabricated value or timestamp. No replacement recruits, added works or extended cutoff are allowed. A planned rater who drops out retains `NONRESPONSE` cells for later windows. Run the final analysis only at or after the frozen cutoff. Missing cells prevent a result until the operator supplies honest `NONRESPONSE` rows or formally cancels the plan. A completed verdict or cancellation is final for that instrument. Revised wording requires a new instrument version and an independent pilot; earlier history remains retained.

An explicit cancellation may close a frozen plan before the cutoff, even with no submitted cells. It produces `CANCELLED_PILOT` with a reason, planned membership, input hashes, and completion timestamp. It cannot activate confirmation and must be included in the pilot history. A plan that reaches the cutoff with fewer eligible windows or raters produces `INSUFFICIENT_PILOT_DATA`; the raw roster and nonresponse count are preserved. A new plan under the same instrument cannot replace either result. Plans begun but never finalized require an external audit record; the repository cannot discover an unreported attempt.

## Instrument and administration

Use `TENSION_BRIDGE_RATING_FORM_v1.1.md` unchanged, including all three `L/T/D` questions, canonical sequential presentation, deterministic question-order randomization, and future-blind timestamp audit. `L_obs` is collected to preserve the actual instrument context but is not part of this discriminant gate. The `response_status` field is exactly `ANSWERED` or `NONRESPONSE`. For `NONRESPONSE`, only planned work/window/rater IDs and the status are filled; all ratings, eligibility answers, and timestamps remain empty. An `ANSWERED` row requires actual values and timestamps. Answers after the frozen cutoff are retained but excluded from the primary analysis. The same fixed master seed applies to every run of this protocol version.

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

Estimate uncertainty with 5,000 deterministic work-cluster bootstrap repetitions. In each repetition, sample the frozen works with replacement, retain every centered window from each sampled work, calculate `|r_TD|`, and store valid values. The master seed is `RCWE-TB-DISCRIMINANT-v0.3`. Report the point value and the 95th percentile of the bootstrap distribution as the one-sided upper bound. With four works only 35 distinct cluster-count compositions exist; the bound is discrete and is not a universal raw-correlation cutoff such as .78. Increasing sample size after a failure is prohibited, even if the point correlation is unchanged.

## Frozen verdict

The pilot passes only when both are true:

```text
abs(r_TD) < 0.85
upper_95_abs_r_TD < 0.85
```

Otherwise status is `PILOT_DISCRIMINANT_FAILURE`. The `.85` value is a preregistered practical non-equivalence boundary for this experiment, not a universal claim about construct validity. No lower correlation bound is imposed: `D_obs` is a negative-control covariate, not required to correlate with `T_obs`.

## Reproducibility and confirmatory handoff

The reference runner computes eligibility, minimum counts, split-half reliability, within-work centering, the work-cluster bootstrap, and the verdict from raw pilot ratings. It emits hashes for the ratings, manifest, this protocol, and the entire rating form, plus pilot work IDs and SHA-256 hashes of pseudonymous rater IDs. A header-only run yields `NO_DATA`.

Before the first confirmatory rating, commit and seal the complete pilot-history JSON (template under `data/`). Enumerate every completed result, including insufficient/failed runs and cancelled plans, by path and exact SHA-256; declare completeness explicitly. All entries must belong to the same instrument/protocol and single frozen manifest and must pass. Every confirmatory manifest row must reference both the selected result and the history-file hash. The runner verifies all listed files and their form/protocol hashes, and checks non-reuse against the union of all planned pilot works/raters. Missing, failed, cancelled, changed-plan, or mismatched evidence yields `PILOT_NOT_PASSED`. No data means independence is unassessed, not true.

Hashes cannot discover an unreported external run or prove a claimed timestamp. Before the first rating, publish the plan file hash under a timestamped external registration, with one registered plan per instrument version; retain its locator and receipt outside the repository's copyrighted material. OSF registration or another durable record may be used, but its availability and access conditions must be checked by the operator. The runner cannot verify that an external platform has actually retained the record. Completeness, cancellations and pre-rating freezing require an auditable operator declaration and Git history. Historical instrument versions and their failures must remain available in version control. No real work/rater plan has yet been supplied: collection and activation remain pending.
