# 数学モデル

> [英語原本](MATHEMATICAL_MODEL.md)の参考訳。数式と条件は原本を正本とする。

## 最小系

\[
\dot s=\Omega(\Delta-v+R\tanh s),\qquad
\dot v=-v+\sigma(s),\qquad p_D=\sigma(s).
\]

平衡点は

\[
v^*=\sigma(s^*),\qquad \sigma(s^*)=\Delta+R\tanh s^*
\]

を満たす。ヤコビ行列は

\[
J=\begin{pmatrix}
\Omega R\,\mathrm{sech}^2s^*&-\Omega\\
\sigma'(s^*)&-1
\end{pmatrix}.
\]

したがって

\[
\operatorname{tr}J=G\,\mathrm{sech}^2s^*-1,\qquad G=\Omega R.
\]

行列式が正で横断的な交差がある場合、Hopf分岐の候補は

\[
G_H=\cosh^2s^*\ge1.
\]

よく知られた`G=1`は、対称な`s*=0`、同値に`Delta=1/2`の場合に限る。

## 対称なHopf近傍

`Delta=1/2`かつ`0<R<1/4`では、超臨界Hopf直後の小振幅cycleは近似的に

\[
A_s\simeq2\sqrt{\frac{G-1}{G}}.
\]

対称性から離れるとHopfは亜臨界になり得る。Bautin境界の数値は探索的で、普遍定数として凍結していない。

## foldのパラメータ表示

`t=tanh(s/2)`とすると、saddle-node境界は

\[
R=\frac{(1+t^2)^2}{4(1-t^2)},\qquad
\Delta=\frac12-\frac{t^3}{1-t^2}
\]

で、この表示に沿ったHopf面は

\[
G_H=\left(\frac{1+t^2}{1-t^2}\right)^2.
\]

## 観測式

codingされた系列では

\[
p_{D,n}^{obs}=\sigma(s_n)+\epsilon_n.
\]

有界な離散観測分布、数値積分、FITのみの推定、open-loop holdoutの規則は`PREDICTIVE_SCORING_SPEC_v0.1.md`で定義する。
