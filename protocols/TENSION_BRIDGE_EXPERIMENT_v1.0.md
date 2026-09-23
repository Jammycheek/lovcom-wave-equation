# Romantic Tension Bridge Confirmatory Experiment v1.0

## Status and scientific question

This protocol freezes the confirmatory experiment for the hypothesis in `docs/TENSION_BRIDGE_v0.1.md`. Human rating data have not been collected. It asks whether observed interaction-channel variation `P_AC` improves held-out prediction of romantic tension `T_obs` after controlling for perceived affection `L_obs` and general dramatic tension `D_obs`.

Primary comparison:

```text
M0: T_obs ~ L_obs + D_obs
M1: T_obs ~ L_obs + D_obs + P_AC
```

The primary hypothesis requires `beta_PAC > 0` and better held-out predictive score for `M1`. The secondary comparison retains `ML: T_obs ~ L_obs` versus `MLAC: T_obs ~ L_obs + P_AC`. Secondary results cannot overwrite the primary verdict.

## Frozen windows and channel metrics

For each dyad, begin at the first eligible IE and form non-overlapping windows of exactly five consecutive qualified IEs: `1–5`, `6–10`, `11–15`, and so on. Discard a remainder of one to four IEs from confirmatory analysis. Freeze boundaries before calculating metrics and before collecting ratings. Never select a window because of a confession, climax, jump, or observed high/low metric.

For each five-IE window:

\[
\bar{\mathbf p}_W=\frac15\sum_{n\in W}\mathbf p_n,
\qquad
P_{AC}(W)=\frac15\sum_{n\in W}\|\mathbf p_n-\bar{\mathbf p}_W\|_2^2,
\]

\[
P_{switch}(W)=\frac14\sum_{n=2}^{5}\|\mathbf p_n-\mathbf p_{n-1}\|_2^2.
\]

`P_AC` is primary; `P_switch` is a secondary diagnostic and may not be added post hoc to a primary model. Raw coder-A, coder-B, and adjudicated D/S/C/P vectors must all use the Codebook's 0.25 grid and simplex. The runner derives complete windows and both metrics from adjudicated IE rows; submitted window values are verification fields and any mismatch stops analysis. Channel reliability is computed from the two raw coder vectors as median per-IE total-variation distance and passes only at `median dTV <= .25`. A corpus failing this gate is unavailable for confirmatory analysis.

The raw channel schema is `work_id, version_id, edition, pair, global_order, ie_id, d_a, s_a, c_a, p_a, d_b, s_b, c_b, p_b, d, s, c, p, channel_coder_ids, adjudicator_id, source_locator`. The frozen window manifest must exactly match every mechanically derived complete five-IE window, including ordered IE IDs, version, edition, endpoint locator, `P_AC`, and `P_switch`.

## Role separation and sequential presentation

For the same work, no person may serve as more than one of channel coder, adjudicator, or audience rater. Store these assignments and validate them before rating values are analysed. Audience raters may not see RCWE equations, annotations, `P_AC`, parameters, phase expectations, the Bridge hypothesis, other ratings, or future story content.

Raters consume their assigned work in canonical chronology. At each five-IE endpoint, reveal the questions only after the endpoint is reached and require answers before the next source unit is opened. Do not present isolated windows in random order. Past context is allowed; future information is forbidden.

## Primary rater eligibility

Recruit only raters who report all of:

```text
prior_read_or_watch = no
knows_future_pair_outcome = no
uncertain_about_prior_exposure = no
```

Make eligibility decisions before inspecting ratings. Future-aware, previously familiar, or uncertain participants are excluded from the primary dataset and may be retained only for separately labelled sensitivity analysis. Each row records offset-aware ISO-8601 timestamps for `eligibility_decided_at`, `window_endpoint_reached_at`, `rating_timestamp`, and (when applicable) `next_source_opened_at`. Primary future-blind status is computed, not self-declared: eligibility must precede or equal the endpoint, the endpoint must precede or equal the rating, and the rating must precede the next source opening.

Target 16 eligible raters per work. A window requires at least 12 raters with valid `L/T/D` values. Otherwise it is excluded with `INSUFFICIENT_RATERS`; the minimum may not be changed after ratings are seen.

## Frozen rating instrument

All responses use an integer 0–100 continuous slider. Japanese wording, anchors, and administration instructions are versioned in `TENSION_BRIDGE_RATING_FORM_v1.1.md` and may not change after its independent pilot begins. Both pilot and confirmatory artifacts record the entire form's SHA-256.

For each window/rater, deterministically randomize the order of `L/T/D` from a predeclared master seed using SHA-256. Never use Python `hash()`. Preserve `question_order` in raw data and reject a row that does not match its planned order.

## Aggregation and audience reliability

Primary window aggregates are arithmetic means of eligible complete ratings. Medians are secondary diagnostics. Do not winsorize, trim, reweight, or exclude raters post hoc to improve results.

For each of `L`, `T`, and `D`, run 1,000 deterministic repeated split halves. Within each window, use two equal halves; if the count is odd, discard one rater according to the deterministic permutation for that repeat. Calculate the two half means, center each half's window means within work, pool the centered values, correlate half A with half B using Pearson `r`, and apply:

\[
r_{SB}=\frac{2r}{1+r}.
\]

Report median, 2.5th percentile, and 97.5th percentile. Each construct must have median `r_SB >= .70`. Failure of any construct prevents the controlled primary model and produces `MEASUREMENT_FAILURE`. Raters may not be removed after this calculation to raise reliability.

## Corpus activation gate

All conditions are required:

- at least 30 eligible windows;
- at least four independent works;
- at least four dyads, defined as unique work/pair combinations;
- every included work contributes at least five eligible windows;
- every included window has at least 12 eligible raters;
- channel reliability passes;
- audience reliability passes for `L/T/D`;
- coder/adjudicator/rater separation passes; and
- source, version, and window manifests were frozen before ratings.

If measurement gates fail, status is `MEASUREMENT_FAILURE`. If other activation requirements fail, status is `INSUFFICIENT_BRIDGE_DATA`. Only descriptive outputs are permitted in either state.

## Work-level held-out analysis

Use Leave-One-Work-Out cross-validation. A work is the holdout and every other work is training; no window from one work may occur in both partitions.

Within each fold, z-standardize `L_obs`, `D_obs`, and `P_AC` from training data only, then apply the training means and population standard deviations (`ddof=0`) to holdout data. Keep `T_obs` on its 0–100 scale. Zero training SD is a model-identification failure.

Fit ordinary linear regression only: no ridge, lasso, spline, interaction, polynomial, or post-hoc terms. For training design `X`, use the classical predictive distribution:

\[
\hat\beta=(X'X)^{-1}X'y,
\qquad s^2=\frac{SSE}{n-p},
\]

\[
T_*\sim t_{n-p}\left(x_*'\hat\beta,
s\sqrt{1+x_*'(X'X)^{-1}x_*}\right).
\]

Score each holdout window with its Student-t log predictive density. A singular design, non-positive residual degrees of freedom, or non-positive residual variance invalidates the fold; do not add regularization after seeing this failure.

Report all four totals and:

\[
\Delta LS_{primary}=LS_{M1}-LS_{M0},
\qquad
\Delta LS_{love}=LS_{MLAC}-LS_{ML}.
\]

Fit full-data `M1` after z-standardizing its predictors over the full eligible dataset and report `beta_PAC_full` as a direction check. It is not a p-value gate.

## Primary verdict

- `SUPPORT`: `beta_PAC_full > 0` and `Delta LS_primary >= 2`;
- `INDETERMINATE`: `beta_PAC_full > 0` and `0 < Delta LS_primary < 2`;
- `FAIL`: `beta_PAC_full <= 0` or `Delta LS_primary <= 0`.

If `MLAC > ML` but `M1 <= M0`, report that the AC signal loses independent contribution after controlling for general dramatic tension. Do not call that RCWE support. There is no overall point score.

## Static-tension challenge

With five IEs and 0.25 channel resolution, the smallest non-zero `P_AC` from one minimal channel transfer is `.02`. A window is a candidate when `T_obs >= 75` and `P_AC <= .02`. If at least three candidates occur across at least two independent works, record `STATIC_TENSION_CHALLENGE = FAIL`. The regression-only verdict remains reported, but the final Bridge status becomes `FAIL_STATIC_TENSION_CHALLENGE`; a regression `SUPPORT` result cannot erase it.

## Data separation, source policy, and ethics

Keep channel annotations and audience ratings in separate files and ID namespaces. Join only by `window_id` at analysis. Store locators, endpoints, access metadata, short original notes, and hashes; do not store pages, source text, transcripts, audio/video, or long quotations. Raters use lawfully accessible originals.

Before activation, the responsible study operator must document applicable consent, privacy, and ethics requirements. This protocol does not presume that review or approval is unnecessary.

## Common-method limitation

The same rater supplies `L_obs`, `T_obs`, and `D_obs` at one endpoint. Question-order randomization reduces order effects but does not eliminate shared-rater/common-method covariance. The primary analysis must report this limitation and must not interpret a positive `P_AC` coefficient as proof that the constructs are psychometrically independent. Split-rater or multi-method replication is a v2.1 candidate, not an unregistered rescue analysis.

`T_obs` / `D_obs` discriminant validity is specified separately in `TENSION_BRIDGE_DISCRIMINANT_PILOT_v0.3.md`. Before the first confirmatory rating, the single fixed-plan pilot must return `PILOT_PASS`; a complete, sealed history must enumerate all results including insufficient, failed, and cancelled plans. The confirmatory work manifest stores the exact selected-result SHA-256 and history SHA-256. The runner checks every listed result, requires every status to pass, verifies unchanged form/protocol/plan hashes, and rejects pilot work/rater reuse. A changed plan cannot replace a failed pilot. Until these checks pass, status is `PILOT_NOT_PASSED` and this experiment remains inactive; the implementation must not use the confirmatory correlation to choose or revise the threshold. Empty templates remain `NO_DATA` with unassessed independence. The completeness declaration requires external provenance: hashes cannot detect concealed external runs.

## Reproducibility and freeze discipline

The templates under `data/` contain headers only. Window and work manifests record offset-aware freeze timestamps and nonempty freeze commits; the runner verifies that every freeze predates the first rating. Ethics readiness requires a status plus a SHA-256 reference to the responsible operator's external ethics/consent record; the record itself need not expose private participant information in this repository. Generated outputs record input hashes, Git commit, master seed, exclusions, reliability, activation, folds, scores, effect direction, static challenge, and warnings. Empty templates yield `NO_DATA`, never a scientific result. The corpus, work list, dyads, all mechanically derived windows, target rater count, and recruitment closure rule must be committed before the first rating is opened. Works, windows, or raters may not be added after confirmatory status is opened; later data constitute a separately versioned study. Failed results may not be repaired by changing windows, raters, controls, or models.
