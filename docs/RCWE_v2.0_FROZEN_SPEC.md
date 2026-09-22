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

### Frozen conceptual architecture

The full conceptual state is

\[
X=(\psi,h,\mathbf p).
\]

Slow affinity and dynamic inhibition are represented by

\[
\tau_\psi\dot\psi
=-\delta(\psi-\psi_0)+\sum_k r_kA_k+\xi,
\]

\[
\tau_h\dot h
=-h+h_0+\kappa F(A_D,\mathcal B^{char}).
\]

Channel values and allocation are

\[
Q_k=V_k(\psi,H,C,\mathcal B^{char})-g_kh+\rho_kp_k,
\]

\[
p_k^*=\frac{e^{Q_k/T_c}}{\sum_l e^{Q_l/T_c}},
\qquad
\tau_p\dot p_k=p_k^*-p_k.
\]

Interaction occurrence is a separate event layer with rate `lambda_e(t)`. Observations are a marked sequence

\[
\{t_n,E_n,\mathbf p_n\}.
\]

Thus `psi`, `p_D`, and interaction occurrence are distinct. No interaction is a gap in the marked sequence, not `p_D = 0`. The conceptual architecture is frozen, but v2.0 does not specify an implementable universal family for `V_k`; it is therefore not the primary numerical predictor.

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

Primary numerical validation is restricted to this closed minimal `p_D` model. Its numerical integration and predictive scoring rules are fixed separately in `PREDICTIVE_SCORING_SPEC_v0.1.md`.

## Event handling

Events are marked inputs or covariates, not permission to add a post-hoc force term. Define channel jump

\[
J_n^{TV}=\frac12\sum_k |p_{k,n}-p_{k,n-1}|.
\]

Compare `E[J^TV|X=1]` with `E[J^TV|X=0]`, where `X` marks a clear intervening external or narrative event. Event-free windows may be used to estimate intrinsic dynamics.

## Freeze constraints

- No new state, channel, subject-specific parameter, or forcing term may be added during a frozen validation.
- No refitting after a holdout is opened. Primary validation is open-loop; any filtering or state-updating analysis is secondary and requires its own preregistered specification.
- Failures go to the failure log; proposed repairs go to the v2.1 registry.
