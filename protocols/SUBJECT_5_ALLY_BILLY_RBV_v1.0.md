# Subject 5-RBV — Ally McBeal / Billy Thomas

## Design

This is retrospective blind validation, not fully prospective validation.

- Version: television series only
- FIT: S1E1–S2E23
- HOLDOUT-N: S3E1–E14
- HOLDOUT-A: S3E15 anomaly challenge
- External label: S3E16 diagnosis/death; excluded from ordinary prediction score
- Exclude: S3E17 onward

Blind coders proceed in broadcast order without later episodes, summaries, RCWE predictions, or knowledge of the outcome.

## Primary model and baselines

The primary target is `p_D` under the frozen minimal system. Estimate only `Delta, R, Omega, s0, v0` and observation error from FIT, with positive `R` and `Omega`. After opening S3, parameters cannot be re-estimated; state updating only is allowed.

Compare prequential predictions with:

1. persistence;
2. AR(1);
3. quadratic narrative position.

Report predictive log-score differences separately:

\[
\Delta LS\ge2:\ RCWE\ support;
\quad -2<\Delta LS<2:\ indeterminate;
\quad \Delta LS\le-2:\ baseline\ support.
\]

Also report MAE. Direction is observed but not scored as an RCWE prediction.

## Forced versus intrinsic dynamics

Mark clear intervening events `X_n`. Compare event-linked and event-free jump distributions using `J_n`; use permutation testing. Fit intrinsic dynamics only to event-free windows. Do not insert a new force term into v2.0.

## Anomaly challenge

Standardize prediction innovations using FIT. Freeze the 97.5th percentile of FIT absolute innovations as the threshold. Trigger an alarm when at least two of three consecutive IEs exceed it. Treat alarms in S3E1–E13 as false positives and S3E14–E15 as the challenge window. S3E16 is only the external label.
