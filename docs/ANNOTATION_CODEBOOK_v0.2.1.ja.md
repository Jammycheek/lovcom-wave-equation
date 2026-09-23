# Annotation Codebook v0.2.1

> [英語原本](ANNOTATION_CODEBOOK_v0.2.1.md)の参考訳。値域・schema・閾値は原本を正本とする。

## 観測単位

Interaction Episode（IE）は、同じ二者が一つの場面・目的・文脈のもとで行う連続した相互作用。明瞭な時間・場所の変化、目的の変化、相互作用modeを変える第三者介入で分割する。相互作用がないことはgapであり、`p_D=0`とはcodingしない。

## 必須provenance

作品、version、版、単位、locator、資料種別、coder、coding日、未来に対するblind状態、理論に対するblind状態を記録する。原典本文ではなく、locatorと短い独自要約のみを保存する。

## チャネル単体

\[
\mathbf p=(p_D,p_S,p_C,p_P),\qquad \sum p_k=1.
\]

値は`{0,.25,.50,.75,1}`刻みで付ける。

- `D`：その二者固有の恋愛・親密さ。直接の告白、明示的なdateの提案、kiss、関係そのものについての話など。
- `S`：通常の社会的交流。
- `C`：対立、ライバル、口論、競争。親和性が負であることを必ずしも意味しない。
- `P`：共同作業、遊び、演技、創作、共通の対象を追うこと。

役割として行う一般的な恋愛演技は、二者固有のものにならない限り通常`D`ではなく`S`。第三者による恋愛ラベルはeventタグであり、`D`の証拠ではない。

## 独立した属性

- `M_mask ∈ {0,1}`：隠された身元、代理の声、仮面の人格。
- `R_dir ∈ {+1,0,-1,mixed}`：接近、維持、後退、または同一IE内で明瞭な接近と後退。
- eventタグ：`disclosure`, `concealment`, `correction`, `misunderstanding`, `third-party`, `constraint-change`, `joint-event`, `none`。複数可。
- 人物のbelief状態：`known`, `believed`, `uncertain`, `false-belief`, `unknown`。明示的な台詞、叙述、行動の証拠がある場合のみ。
- 資料品質`Q_src`：3=原文／映像、2=完全な書き起こし、1=公式あらすじ／PV、0=二次資料／fan資料。

`psi`、`h`、`U`を直接codingしない。分析者のposteriorと登場人物のbeliefを同じ名称で呼ばない。

## blind codingと信頼性

正式データには独立したcoderを最低２人使う。RCWEの式・予測・後の展開・他coderの得点を隠す。両者の生評定と、調停値を保持する。

カテゴリ変数／重み付き順序変数は

\[
\kappa\ge0.70
\]

チャネルvectorは

\[
\operatorname{median}(d_{TV})\le0.25,\qquad
d_{TV}=\frac12\sum_k|p_k^A-p_k^B|,
\]

をgateとする。満たさなければモデル分析前にcodebookを修訂し、pilotをやり直す。

## 人物beliefのschema

beliefを文脈のない単一cellに圧縮しない。証拠のある主張ごとに、連結した表へ

`IE_ID, Believer, Proposition, Target, Belief_State, Evidence_Type, Evidence_Locator`

を記録する。一つのIEに複数行を結べる。二者の外からの観測は人物のbeliefを更新し得るが、dyadic IEではなくevent層の記録である。

## 最小行schema

`IE_ID, Work_ID, Version_ID, Edition, Unit, Locator, Pair, D, S, C, P, Mask, Direction, Event_Tags, Gap_Before, Q_src, Coder_ID, Coding_Date, Future_Blind, Theory_Blind, Short_Summary`
