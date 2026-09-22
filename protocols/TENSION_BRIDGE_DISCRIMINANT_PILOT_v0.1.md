# Tension Bridge T/D Discriminant-Validity Pilot v0.1

## Purpose and separation

This pilot must pass before the Tension Bridge confirmatory experiment can activate. It tests whether romantic uncertainty (`T_obs`) and general dramatic tension (`D_obs`) remain empirically distinguishable under the frozen Japanese rating form. It does not test `P_AC`, fit a Bridge model, or provide confirmatory evidence.

Pilot works, windows, and raters may not be reused in the confirmatory study. The pilot manifest is frozen before the first rating and records version, edition, planned window count, freeze timestamp, and commit. A failed pilot cannot be repaired by deleting windows or raters; revised wording requires a new instrument version and a new independent pilot.

## Instrument and administration

Use `TENSION_BRIDGE_RATING_FORM_v1.0.md` unchanged, including all three `L/T/D` questions, canonical sequential presentation, deterministic question-order randomization, and future-blind timestamp audit. `L_obs` is collected to preserve the actual instrument context but is not part of this discriminant gate.

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

Estimate uncertainty with 5,000 deterministic work-cluster bootstrap repetitions. In each repetition, sample the frozen works with replacement, retain every centered window from each sampled work, calculate `|r_TD|`, and store valid values. The master seed is `RCWE-TB-DISCRIMINANT-v0.1`. Report the point value and the 95th percentile of the bootstrap distribution as the one-sided upper bound.

## Frozen verdict

The pilot passes only when both are true:

```text
abs(r_TD) < 0.85
upper_95_abs_r_TD < 0.85
```

Otherwise status is `PILOT_DISCRIMINANT_FAILURE`. The `.85` value is a preregistered practical non-equivalence boundary for this experiment, not a universal claim about construct validity. No lower correlation bound is imposed: `D_obs` is a negative-control covariate, not required to correlate with `T_obs`.

## Reproducibility and confirmatory handoff

The reference runner computes eligibility, minimum counts, split-half reliability, within-work centering, the work-cluster bootstrap, and the verdict from raw pilot ratings. It emits hashes for the ratings, manifest, and this protocol, plus pilot work IDs and SHA-256 hashes of pseudonymous rater IDs. The confirmatory runner accepts a pilot only when its generated result is `PILOT_PASS`, its protocol hash matches this file, the work manifest references the exact result-file SHA-256, and no pilot work or rater hash appears in the confirmatory inputs. A header-only run yields `NO_DATA`.
