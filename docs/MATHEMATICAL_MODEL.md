# Mathematical model

## Minimal system

\[
\dot s=\Omega(\Delta-v+R\tanh s),\qquad
\dot v=-v+\sigma(s),\qquad p_D=\sigma(s).
\]

An equilibrium satisfies

\[
v^*=\sigma(s^*),\qquad
\sigma(s^*)=\Delta+R\tanh s^*.
\]

The Jacobian is

\[
J=
\begin{pmatrix}
\Omega R\,\mathrm{sech}^2s^* & -\Omega\\
\sigma'(s^*) & -1
\end{pmatrix}.
\]

Hence

\[
\operatorname{tr}J=G\,\mathrm{sech}^2s^*-1,
\qquad G=\Omega R,
\]

and, where the determinant is positive and the crossing is transversal, a Hopf candidate occurs at

\[
G_H=\cosh^2s^*\ge1.
\]

The familiar `G = 1` threshold is only the symmetric case `s* = 0`, equivalently `Delta = 1/2`.

## Symmetric near-Hopf result

At `Delta = 1/2` with `0 < R < 1/4`, the small-cycle amplitude immediately beyond the supercritical Hopf is approximated by

\[
A_s\simeq2\sqrt{\frac{G-1}{G}}.
\]

Away from symmetry, the Hopf may become subcritical. Numerical Bautin-boundary values are exploratory and are not frozen as universal constants.

## Fold parameterization

With `t = tanh(s/2)`, saddle-node boundaries can be written

\[
R=\frac{(1+t^2)^2}{4(1-t^2)},
\qquad
\Delta=\frac12-\frac{t^3}{1-t^2},
\]

and the Hopf surface along this parameterization is

\[
G_H=\left(\frac{1+t^2}{1-t^2}\right)^2.
\]

## Observation equation

For a coded series,

\[
p_{D,n}^{obs}=\sigma(s_n)+\epsilon_n.
\]

The bounded discrete observation distribution, numerical integration, FIT-only estimation, and open-loop holdout rules are defined in `PREDICTIVE_SCORING_SPEC_v0.1.md`.
