# Romantic Tension Bridge v0.1

**Status: hypothesis frozen; confirmatory implementation inactive; human rating data not yet collected.** See `protocols/TENSION_BRIDGE_EXPERIMENT_v1.0.md`, `protocols/TENSION_BRIDGE_RATING_FORM_v1.1.md`, and the fixed-plan discriminant pilot v0.2. No real pilot plan or passing evidence has been supplied.

## External ratings

For each preregistered window, collect independent 0–100 ratings:

- `L_obs`: perceived affection/love;
- `T_obs`: uncertainty or oscillation in what the romantic relationship will do next;
- `D_obs`: general dramatic tension, irrespective of romance.

## Channel dynamics

For window `W`,

\[
\bar{\mathbf p}_W=\frac1N\sum_{n\in W}\mathbf p_n,
\]

\[
P_{AC}(W)=\frac1N\sum_{n\in W}\|\mathbf p_n-\bar{\mathbf p}_W\|_2^2.
\]

The secondary switching metric is

\[
P_{switch}(W)=\frac1{N-1}\sum_{n=2}^{N}\|\mathbf p_n-\mathbf p_{n-1}\|_2^2.
\]

The confirmatory protocol freezes non-overlapping consecutive five-IE windows. Do not select windows around confessions or climaxes.

## Primary hypothesis

\[
T^{obs}\sim\beta_0+\beta_1L^{obs}+\beta_2P_{AC}+\beta_3D^{obs},
\qquad H_T:\beta_2>0.
\]

Compare held-out performance of `T_obs ~ L_obs` against `T_obs ~ L_obs + P_AC`, and then test whether the AC contribution survives control for general drama.

## Failure conditions

- AC has non-positive or no held-out predictive contribution.
- Its contribution vanishes after controlling for general drama.
- Love alone predicts tension equally well.
- Reproducible high romantic tension appears with near-zero channel AC power.

The bridge uses observed channel allocation, not latent gain `G`, so it can be tested independently of the state estimator.
