# Predictive Scoring Specification v0.1

**Freeze blocked (N-2/N-5):** the v0.1 binary convergence rule below is retained for historical reproduction, not yet a reproducible acceptance gate. The canonical runtime family is Windows x86-64 (AMD64), CPython 3.12.14, NumPy 2.5.3 and SciPy 1.18.1; package pins are in `pyproject.toml`. A version match alone does not guarantee identical BLAS builds or convergence membership. New benchmark artifacts also retain build configuration and thread environment. Cross-family runs require `--allow-nonreference-runtime` and remain diagnostic. See `NUMERICAL_RECOVERY_ACCEPTANCE_PLAN_v0.1.md` for unresolved calibration and acceptance requirements.

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

An implementation using another solver is acceptable only if its forecast means agree with the reference settings to an absolute tolerance of `1e-8` at every scored IE, using the **same fixed parameters and initial state**. This is a solver-only comparison; it does not assess independently fitted parameter estimates.

## FIT estimation and freeze boundary

Estimate `Delta, R, Omega, s0, v0` and predictive scale `sigma_pred` using FIT only, with `R > 0`, `Omega > 0`, and `sigma_pred > 0`. Use the discretized observation likelihood defined below. The frozen reference optimizer is L-BFGS-B with `maxiter=80`, `ftol=1e-12`, and `gtol=1e-7`, using four data-independent starts in `(Delta,R,Omega,s0,v0,sigma_pred)` coordinates: `(0.25,.03,3,-2,.8,.20)`, `(.75,.30,20,2,.2,.05)`, `(.40,.05,15,1.5,.8,.15)`, and `(.60,.25,5,-1.5,.2,.30)`. The implementation converts positive coordinates to its logged parameterization and adjusts the scale coordinate for the coder lower bound. An optimizer-reported success counts as a successful start only when the infinity norm of its projected objective gradient is at most `1e-4`; preserve both the raw optimizer flag and this stationarity check.

Retain the successful solution with the largest FIT likelihood and preserve every start, termination code, projected-gradient norm, fitted value, software version, and seed. A fit is marked `converged` only when at least two stationary successful starts have FIT log likelihoods differing by no more than `1e-6`. Otherwise forecasts may be retained for diagnosis, but the run is an optimizer-agreement failure and cannot count as confirmatory evidence. The historical v0.1 test called two fitted implementations numerically equivalent when maximum FIT log likelihoods agreed within `1e-6` and holdout forecast means agreed within `1e-8` under the same frozen dependency/runtime family. This second `1e-8` application is **not a defensible cross-platform acceptance gate for refitted forecasts**: reviewer-reported comparison of the exposed 40 cases found a maximum per-IE mean difference of `9.08e-8` and 12/40 replicates beyond `1e-8` (raw reproduction artifacts pending import). Preserve and report the historical result as a failed diagnostic. Calibrate a distinct refitted-forecast tolerance only on a separately frozen development block, then approve it before untouched validation. The solver-only fixed-parameter `1e-8` tolerance above remains unchanged.

For audit visibility, each new fit additionally reports `convergence_diagnostic` using the two highest-likelihood raw optimizer-successful starts. If fewer than two exist, their likelihood gap exceeds `1e-6`, or either gradient norm is non-finite or exceeds `10 * 1e-4`, report `FAILED`. With likelihood agreement, report `CONVERGED` only if both norms are strictly below `1e-4 / 10`; otherwise report `MARGINAL` (including band endpoints). This reviewer-requested factor-ten annotation does not replace the historical boolean, change selected parameters, or provide an acceptance rule. Its new boundaries can also be runtime-sensitive; it is not evidence that N-5 is solved. No threshold or start was retuned on the exposed 40 cases.

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
