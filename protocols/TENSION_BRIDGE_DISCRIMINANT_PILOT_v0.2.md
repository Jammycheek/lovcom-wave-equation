# Tension Bridge T/D Discriminant-Validity Pilot v0.2

## Purpose and separation

This pilot must pass before the Tension Bridge confirmatory experiment can activate. It tests whether romantic uncertainty (`T_obs`) and general dramatic tension (`D_obs`) remain empirically distinguishable under the frozen Japanese rating form. It does not test `P_AC`, fit a Bridge model, or provide confirmatory evidence.

Pilot works, windows, and raters may not be reused in the confirmatory study. Before the first rating, freeze one complete manifest per instrument version: exact work IDs/count, window IDs/count per work, and pseudonymous rater IDs per work, plus version, edition, form hash, timestamp, and commit. The minima below are planning constraints, not sequential stopping rules. Actual works and every planned rater/window cell must exactly match this plan; ineligible ratings remain as excluded rows, not replacement recruits. Missing cells prevent analysis. No adding works, windows, or raters after results are opened, and no replacing a completed failed pilot with a larger passing pilot under the same instrument. A completed verdict is final for that instrument. Revised wording requires a new instrument version and an independent pilot; earlier history remains retained.

## Instrument and administration

Use `TENSION_BRIDGE_RATING_FORM_v1.1.md` unchanged, including all three `L/T/D` questions, canonical sequential presentation, deterministic question-order randomization, and future-blind timestamp audit. `L_obs` is collected to preserve the actual instrument context but is not part of this discriminant gate.

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

Estimate uncertainty with 5,000 deterministic work-cluster bootstrap repetitions. In each repetition, sample the frozen works with replacement, retain every centered window from each sampled work, calculate `|r_TD|`, and store valid values. The master seed is `RCWE-TB-DISCRIMINANT-v0.2`. Report the point value and the 95th percentile of the bootstrap distribution as the one-sided upper bound. With four works only 35 distinct cluster-count compositions exist; the bound is discrete and is not a universal raw-correlation cutoff such as .78. Increasing sample size after a failure is prohibited, even if the point correlation is unchanged.

## Frozen verdict

The pilot passes only when both are true:

```text
abs(r_TD) < 0.85
upper_95_abs_r_TD < 0.85
```

Otherwise status is `PILOT_DISCRIMINANT_FAILURE`. The `.85` value is a preregistered practical non-equivalence boundary for this experiment, not a universal claim about construct validity. No lower correlation bound is imposed: `D_obs` is a negative-control covariate, not required to correlate with `T_obs`.

## Reproducibility and confirmatory handoff

The reference runner computes eligibility, minimum counts, split-half reliability, within-work centering, the work-cluster bootstrap, and the verdict from raw pilot ratings. It emits hashes for the ratings, manifest, this protocol, and the entire rating form, plus pilot work IDs and SHA-256 hashes of pseudonymous rater IDs. A header-only run yields `NO_DATA`.

Before the first confirmatory rating, commit and seal the complete pilot-history JSON (template under `data/`). Enumerate every completed result, including insufficient/failed runs, by path and exact SHA-256; declare completeness explicitly. All entries must belong to the same instrument/protocol and single frozen manifest and must pass. Every confirmatory manifest row must reference both the selected result and the history-file hash. The runner verifies all listed files and their form/protocol hashes, and checks non-reuse against the union of all pilot works/raters. Missing, failed, changed-plan, or mismatched evidence yields `PILOT_NOT_PASSED`, never a generic sample-size failure. No data means independence is unassessed, not true.

Hashes cannot discover an unreported external run or prove a claimed timestamp. Completeness and pre-rating freezing require an auditable operator declaration and Git history; they are not guaranteed by hashing. Historical instrument versions and their failures must remain available in version control. No real work/rater plan has yet been supplied: collection and activation remain pending.
