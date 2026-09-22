# RCWE v2.0 Predictive-Scoring Reference Implementation v0.1

## Scope

This package implements the primary open-loop path in `PREDICTIVE_SCORING_SPEC_v0.1.md`. It does not revise the research model, protocols, Codebook, or freeze criteria. It implements only the minimal two-state RCWE, five-bin observation distribution, FIT-only estimation, three frozen baselines, scoring, and synthetic characterization.

## Architecture

- `model.py`: minimal ODE, parameter object, derived `G`, and local equilibrium classification.
- `integrate.py`: qualified-interaction clock and reference DOP853 integration.
- `observation.py`: five-bin discretized Gaussian likelihood and stable tail arithmetic.
- `fit.py`: FIT-only multiple-start likelihood estimation and frozen holdout forecasting.
- `baselines.py`: Persistence, AR(1), and Quadratic Narrative Position.
- `scoring.py`: per-IE probability, log probability, absolute error, and aggregates.
- `synthetic.py`: seeded synthetic data and developer-only continuous-trajectory fixtures.
- `scripts/run_synthetic_recovery.py`: generated benchmark tables and report.

## Parameter and clock conventions

`Delta`, positive `R`, positive `Omega`, `s0`, and `v0` are fitted. `G = R * Omega` is derived and is never independently fitted. The first FIT observation is evaluated at `(s0, v0)` (interaction index zero). Each later qualified IE advances the clock by one. Missing, ineligible, or no-interaction rows are removed before assigning this index; they are not zero observations and do not advance the ODE.

The predictive scale is parameterized as `sigma_pred = sigma_coder + exp(eta)`, so the coder lower bound is always respected. When coder disagreement is exactly zero, the specified `1e-6` numerical floor is used and reported.

For Quadratic Narrative Position, the FIT-index standard deviation uses the population convention (`ddof=0`). `PREDICTIVE_SCORING_SPEC_v0.1.md` does not select a sample-versus-population convention; this reference choice is therefore an implementation decision to preserve exactly in independent reproductions.

## Open-loop freeze

The FIT terminal state is the state at the last FIT interaction index. The first HOLDOUT forecast is one complete interaction step after that state. Parameters, terminal state, scale, solver settings, and baseline fits remain frozen. Holdout observations are passed only to scoring; they cannot reset a state or forecast.

## Numerical optimizer guards

The likelihood optimizer uses L-BFGS-B with `maxiter=80`, `ftol=1e-12`, and `gtol=1e-7`, plus the four data-independent starts frozen in the scoring specification. It uses broad finite guards declared as `fit.OPTIMIZER_GUARDS` to avoid exponent overflow and pathological ODE calls. The baseline optimizers use analogous `[-5, 5]` coefficient and scale-transform guards. These are implementation safeguards, not scientific parameter bounds. Every baseline guard hit is emitted into the fit artifact and benchmark warning summary. A solution at a guard is not evidence for a scientific boundary.

`converged` is a cross-start agreement result, not a synonym for one optimizer's `success` flag. It requires at least two successful starts whose two best log likelihoods agree within `1e-6`; per-start status remains available for diagnosis.

## Synthetic benchmark

The developer fixture fits continuous means from non-equilibrium initial state `s0=-1.0, v0=0.20`; it detects ODE, transform, and optimizer errors and is not a validation result. The observation benchmark samples a Gaussian latent observation around the continuous mean, then quantizes it with the frozen Codebook boundaries. Its required strong cases are `Delta=.5, R=.1, Omega=8 (G=.8)` and `Omega=12 (G=1.2)`. Poor recovery remains a reported identifiability result; the implementation must not change the model to improve it.

## Reproduction

From the repository root:

```text
python -m pytest
python scripts/run_synthetic_recovery.py --replicates 20 --seed-base 260901
```

The runner writes `config.json`, `environment.json`, `replicates.csv`, `predictions.csv`, `fit_details.json`, `summary.json`, and `REPORT.md` below `results/synthetic_recovery/`. Fixed seeds and a fixed command produce deterministic numerical content within the recorded frozen Python/NumPy/SciPy/platform environment. Cross-platform reproductions are compared using the numerical tolerances above; byte identity is not promised for JSON formatting, platform metadata, optimizer messages, or floating-point serialization. The files are generated artifacts and must not be hand-edited.
