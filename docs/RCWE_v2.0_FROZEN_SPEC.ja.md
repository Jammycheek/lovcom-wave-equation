# RCWE v2.0 — 凍結仕様

> [英語原本](RCWE_v2.0_FROZEN_SPEC.md)の参考訳。式・識別子・判定条件は英語原本を正本とする。

## 対象

RCWEは架空の二者の相互作用チャネルの力学をモデル化する。心を読む装置でも、万能の関係スコアでも、すべての恋愛が周期的だという主張でもない。

## 層

### 観測層

適格なInteraction Episode（IE）ごとに、チャネル配分`p=(p_D,p_S,p_C,p_P)`、遷移方向`R_dir`、マスキングフラグ`M_mask`、eventタグとprovenance、明示的な場合の人物のbeliefの証拠を記録する。

### 凍結済みの概念構造

完全な概念状態は

\[
X=(\psi,h,\mathbf p).
\]

緩やかな親和性と動的な抑制は

\[
\tau_\psi\dot\psi=-\delta(\psi-\psi_0)+\sum_k r_kA_k+\xi,
\]

\[
\tau_h\dot h=-h+h_0+\kappa F(A_D,\mathcal B^{char}).
\]

チャネル価値と配分は

\[
Q_k=V_k(\psi,H,C,\mathcal B^{char})-g_kh+\rho_kp_k,
\]

\[
p_k^*=\frac{e^{Q_k/T_c}}{\sum_l e^{Q_l/T_c}},\qquad
\tau_p\dot p_k=p_k^*-p_k.
\]

相互作用の発生は発生率`lambda_e(t)`を持つ独立したevent層であり、観測は標識付き列

\[
\{t_n,E_n,\mathbf p_n\}
\]

である。したがって`psi`、`p_D`、相互作用の発生は別物。相互作用がないことは標識付き列の空白であり、`p_D=0`ではない。この概念構造は凍結済みだが、v2.0には実装可能な普遍的`V_k`の族が未指定なので、主要な数値予測器にはしない。

### 最小の閉じた力学系

\[
\frac{ds}{d\tau}=\Omega\,[\Delta-v+R\tanh s],\qquad
\frac{dv}{d\tau}=-v+\sigma(s),
\]

\[
p_D=\sigma(s),\qquad \sigma(s)=\frac{1}{1+e^{-s}}.
\]

通常`tau`は作中の日数ではなく相互作用index。`Omega>0`は有効応答速度、`R>0`は強化、`Delta`は正味のbias、`v`は遅延抑制である。有効なloop gainは

\[
G=\Omega R.
\]

主要な数値検証対象は、この閉じた最小`p_D`モデルに限定する。数値積分と予測スコアの規則は`PREDICTIVE_SCORING_SPEC_v0.1.md`で別に固定する。

## eventの扱い

eventは標識付き入力または共変量であり、後付けの強制項を加える許可ではない。チャネルのjumpを

\[
J_n^{TV}=\frac12\sum_k|p_{k,n}-p_{k,n-1}|
\]

と定義する。明確な介在する外的・物語的eventを`X`で示し、`E[J^TV|X=1]`と`E[J^TV|X=0]`を比較する。eventのないwindowは内在的力学の推定に使える。

## 凍結上の制約

- 凍結済み検証の途中で、新しい状態、チャネル、対象固有のパラメータ、強制項を追加しない。
- holdout開封後は再fitしない。主要検証はopen-loopであり、filteringや状態更新は別途事前登録した二次分析とする。
- 失敗はFAIL logへ、修正案はv2.1 registryへ記録する。
