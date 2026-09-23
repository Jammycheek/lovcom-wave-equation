# 恋愛的緊張のBridge v0.1

> [英語原本](TENSION_BRIDGE_v0.1.md)の参考訳。数式・評価条件の正本は原本。

**状態：仮説は凍結。確認実験の実装は非稼働。人間の評定データは未収集。** `protocols/TENSION_BRIDGE_EXPERIMENT_v1.0.md`、評定除外の追補、評定フォームv1.1、固定計画の弁別パイロットv0.4を参照。実パイロット計画、外部検証済み締切原票、PASS証拠はない。

## 外部評定

事前登録したwindowごとに独立した0–100評定を集める。

- `L_obs`：知覚された好意・愛情。
- `T_obs`：恋愛関係が次にどう動くかの不確実性・揺れ。
- `D_obs`：恋愛に限定しない、一般的な劇的緊張。

## チャネル力学

window`W`について

\[
\bar{\mathbf p}_W=\frac1N\sum_{n\in W}\mathbf p_n,
\]

\[
P_{AC}(W)=\frac1N\sum_{n\in W}\|\mathbf p_n-\bar{\mathbf p}_W\|_2^2.
\]

二次的なswitching指標は

\[
P_{switch}(W)=\frac1{N-1}\sum_{n=2}^{N}\|\mathbf p_n-\mathbf p_{n-1}\|_2^2.
\]

確認Protocolでは連続する５IEの重複しないwindowを固定する。告白やclimaxを中心に選ばない。

## 主要仮説

\[
T^{obs}\sim\beta_0+\beta_1L^{obs}+\beta_2P_{AC}+\beta_3D^{obs},\qquad H_T:\beta_2>0.
\]

`T_obs ~ L_obs`と`T_obs ~ L_obs + P_AC`のholdout性能を比較し、その後、一般的dramaを統制してもACの寄与が残るか調べる。

## 失敗条件

- ACのholdout予測への寄与が非正またはない。
- 一般的dramaを統制すると寄与が消える。
- 好意のみで緊張を同程度に予測できる。
- チャネルAC powerがほぼゼロでも、高い恋愛的緊張が再現して観測される。

Bridgeは潜在gain`G`ではなく観測されたチャネル配分を使うので、状態推定器から独立して検証できる。
