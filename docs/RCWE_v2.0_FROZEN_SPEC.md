# RCWE v2.0 — Frozen specification

## Scope

RCWE models interaction-channel dynamics for a fictional dyad. It is not a mind reader, a universal relationship score, or a claim that every romance is periodic.

## Layers

### Observation layer

Each qualified Interaction Episode (IE) produces:

- channel allocation `p = (p_D,p_S,p_C,p_P)`;
- transition direction `R_dir`;
- masking flag `M_mask`;
- event tags and provenance;
- character-belief evidence, when explicit.

### Latent layer

The model may infer affinity `psi`, defensive or inhibitory memory `h`, uncertainty `U`, and other latent state from observations. These are not hand-scored.

### Minimal closed dynamics

\[
\frac{ds}{d\tau}=\Omega\,[\Delta-v+R\tanh s],
\qquad
\frac{dv}{d\tau}=-v+\sigma(s),
\]

\[
p_D=\sigma(s),\qquad \sigma(s)=\frac{1}{1+e^{-s}}.
\]

Here `tau` is normally the interaction index, not fictional days. `Omega > 0` is the effective response rate, `R > 0` is reinforcement, `Delta` is net bias, and `v` is delayed inhibition.

The effective loop gain is

\[
G=\Omega R.
\]

The broader conceptual layer allows channel values

\[
Q_k=V_k(\psi,H,C,\mathcal B^{char})-g_kh+\rho_kp_k,
\]

but v2.0 does not freeze a unique implementable `V_k` for all four channels. Therefore primary numerical validation is restricted to the closed minimal `p_D` model.

## Event handling

Events are marked inputs or covariates, not permission to add a post-hoc force term. Define channel jump

\[
J_n=\frac12\sum_k |p_{k,n}-p_{k,n-1}|.
\]

Compare `E[J|X=1]` with `E[J|X=0]`, where `X` marks a clear intervening external or narrative event. Event-free windows may be used to estimate intrinsic dynamics.

## Freeze constraints

- No new state, channel, subject-specific parameter, or forcing term may be added during a frozen validation.
- No refitting after a holdout is opened, except state updating explicitly allowed by the protocol.
- Failures go to the failure log; proposed repairs go to the v2.1 registry.
