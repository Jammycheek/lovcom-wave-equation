# Predictive Scoring Specification v0.1

## Scope and forecast mode

This document defines the primary numerical scoring path for the frozen minimal `p_D` model. Primary holdout evaluation is an **open-loop forecast**. All model parameters and the terminal FIT state are frozen before the holdout is opened. Holdout observations do not update a state, refit a parameter, recalibrate uncertainty, or reset a forecast.

Filtering, prequential state updating, and particle- or Kalman-filter analyses are secondary methods and require a separately frozen specification before use.

## Interaction clock and numerical integration

Use interaction index time:

\[
\tau=n,\qquad \Delta\tau=1.
\]

Integrate the minimal system between consecutive qualified IEs with DOP853 using:

```text
rtol = 1e-9
atol = 1e-11
max_step = 0.05
```

The forecast mean is

\[
\mu_n=\sigma(s_n).
\]

An implementation using another solver is acceptable only if its forecast means agree with the reference settings to an absolute tolerance of `1e-8` at every scored IE.

## FIT estimation and freeze boundary

Estimate `Delta, R, Omega, s0, v0` and predictive scale `sigma_pred` using FIT only, with `R > 0`, `Omega > 0`, and `sigma_pred > 0`. Use the discretized observation likelihood defined below. Optimizers must use multiple starting points; retain the converged solution with the largest FIT likelihood and preserve all starts, convergence codes, fitted values, software versions, and random seeds. Independent implementations are considered numerically equivalent only when their maximum FIT log likelihoods agree within `1e-6` and their holdout forecast means agree within `1e-8`.

Coder disagreement provides a measurement-scale lower bound:

\[
\sigma_{coder}^2
=\frac{1}{2N}\sum_{n=1}^{N}(y_n^A-y_n^B)^2,
\qquad
\sigma_{pred}\ge\sigma_{coder}.
\]

If `sigma_coder = 0`, use a numerical floor of `1e-6` and report that the lower bound was inactive. Adjudicated `p_D` is the scored target; raw coder values remain preserved.

Before opening a holdout, record the FIT data commit, code commit, fitted parameters, terminal state, `sigma_pred`, solver configuration, and baseline fits. No quantity in this record may be changed after holdout access.

## Discretized Gaussian observation distribution

The scored outcome is

\[
y_n\in\{0,.25,.50,.75,1\}.
\]

Place bin boundaries at `.125`, `.375`, `.625`, and `.875`. For an interior value with bin `(a_y,b_y]`,

\[
P(y\mid\mu,\sigma_{pred})
=\Phi\!\left(\frac{b_y-\mu}{\sigma_{pred}}\right)
-\Phi\!\left(\frac{a_y-\mu}{\sigma_{pred}}\right).
\]

For `y = 0`, use `(-infinity,.125]`; for `y = 1`, use `(.875,infinity)`. This assigns all probability mass to the five valid Codebook outcomes and avoids clipping predicted means.

The holdout log score is

\[
LS=\sum_{n\in HOLDOUT}\log P(y_n\mid\mu_n,\sigma_{pred}).
\]

Also report mean log score per IE, MAE of `mu_n`, every per-IE probability, and the unrounded total. Do not replace zero or very small probabilities after seeing results; numerical evaluation must use stable normal-CDF log-difference routines.

## Primary baselines

All baselines use FIT only and forecast the full holdout open-loop.

1. **Persistence:** `mu_n = p_D,lastFIT` for every holdout IE. Estimate its predictive scale on FIT from one-step persistence forecasts `mu_n = p_D,n-1`, subject to the same coder-disagreement lower bound, then freeze it.
2. **AR(1):** fit `p_{D,n}=alpha+phi p_{D,n-1}+epsilon_n` and its predictive scale on FIT using the same discretized likelihood, then forecast recursively without holdout updates.
3. **Quadratic narrative position:** fit `p_{D,n}=a+bz_n+cz_n^2+epsilon_n` and its predictive scale on FIT using the same discretized likelihood. Define `z_n=(n-mean(n_FIT))/sd(n_FIT)` and continue the unreset global interaction index through the holdout. Extrapolate without refitting.

Report `Delta LS = LS_RCWE - LS_baseline` separately for each baseline. Threshold interpretation remains protocol-specific. Do not combine baseline comparisons into a win/loss total.

## Missing observations and gaps

A gap is not a scored zero and does not advance the interaction index. Missing or ineligible IEs must be identified before model fitting. No holdout row may be removed because its prediction is poor.

## Status

This specification closes the scoring rule and primary open-loop forecast mode. A reference implementation and synthetic recovery test must reproduce this document before a `v2.0-spec-freeze` tag is created.
