# 恋愛的緊張Bridge 確認実験 v1.0

> [英語原本](TENSION_BRIDGE_EXPERIMENT_v1.0.md)の参考訳。凍結Protocol本体ではなく、数式・閾値・状態codeは英語原本を正本とする。後続の[評定除外追補](TENSION_BRIDGE_RATING_EXCLUSION_ADDENDUM_v0.1.ja.md)も併読する。

## 状態と科学的問い

`docs/TENSION_BRIDGE_v0.1.md`の仮説を確認的に検査するProtocol。人間の評定データは未収集。観測した相互作用チャネルの変動`P_AC`が、知覚された好意`L_obs`と一般的劇的緊張`D_obs`を統制しても、恋愛的緊張`T_obs`のholdout予測を改善するかを問う。

主要比較：

```text
M0: T_obs ~ L_obs + D_obs
M1: T_obs ~ L_obs + D_obs + P_AC
```

主要仮説は`beta_PAC>0`かつ`M1`のholdout予測score改善を要求する。二次比較は`ML: T_obs ~ L_obs`と`MLAC: T_obs ~ L_obs + P_AC`。二次結果で主要判定を上書きしない。

## 凍結windowとチャネル指標

各二者について最初の適格IEから、連続する適格IEを５件ずつ、重複しない`1–5`, `6–10`, `11–15`…のwindowとする。余った１～４IEは確認的分析から除く。指標計算・評定収集の前に境界を凍結し、告白、climax、jump、観測上の指標大小でwindowを選ばない。

５IE windowごとに

\[
\bar{\mathbf p}_W=\frac15\sum_{n\in W}\mathbf p_n,\qquad
P_{AC}(W)=\frac15\sum_{n\in W}\|\mathbf p_n-\bar{\mathbf p}_W\|_2^2,
\]

\[
P_{switch}(W)=\frac14\sum_{n=2}^{5}\|\mathbf p_n-\mathbf p_{n-1}\|_2^2.
\]

`P_AC`が主要指標、`P_switch`は二次診断で、後付けで主要modelに入れない。coder A/Bの生vectorと調停済みD/S/C/P vectorはいずれもCodebookの0.25 gridとsimplexに従う。runnerは調停IE行から完全windowと両指標を導出し、提出window値を検証fieldとして照合する。不一致なら分析停止。チャネル信頼性は生coder vector２本のIE別Total Variation距離のmedianで計算し、`median dTV<=.25`のみ合格。不合格corpusは確認分析不可。

生チャネルschema：`work_id, version_id, edition, pair, global_order, ie_id, d_a, s_a, c_a, p_a, d_b, s_b, c_b, p_b, d, s, c, p, channel_coder_ids, adjudicator_id, source_locator`。凍結window manifestは、機械的に導出した完全な５IE windowすべてと、IE ID順、version、版、endpoint locator、`P_AC`、`P_switch`が完全一致しなければならない。

## 役割分離と逐次提示

同一作品で一人がチャネルcoder、調停者、audience raterの複数役を兼ねない。割当を保存し、評定値の分析前に検証する。audience raterにRCWEの式、annotation、`P_AC`、parameter、相の期待、Bridge仮説、他人の評定、未来の物語を見せない。

raterは担当作品を正規の時系列順に読む／視聴する。各５IE endpointに到達後初めて質問を表示し、次の原典単位を開く前に回答する。切り出したwindowを無作為順に提示しない。過去の文脈は可、未来情報は禁止。

## 主要raterの適格性

次の全てを報告するraterのみ募集：

```text
prior_read_or_watch = no
knows_future_pair_outcome = no
uncertain_about_prior_exposure = no
```

適格性判断は評定を見る前。未来を知る人、既知の人、不確かな人は主要datasetから除き、別labelの感度分析にのみ残せる。行ごとにoffset付きISO-8601の`eligibility_decided_at`, `window_endpoint_reached_at`, `rating_timestamp`、必要なら`next_source_opened_at`を記録する。主要未来blind状態は自己申告でなく計算する：適格判定がendpoint以前、endpointが評定以前、評定が次原典の開封より前。

作品当たり適格rater16人を目標とし、windowは有効な`L/T/D`を持つrater12人以上が必要。不足は`INSUFFICIENT_RATERS`で除外。評定後に最低人数を変えない。

## 凍結評定instrument

全回答は整数0–100の連続slider。日本語文言、anchors、実施指示は`TENSION_BRIDGE_RATING_FORM_v1.1.md`でversion管理され、独立pilot開始後に変更不可。pilotと確認的成果物はフォーム全体のSHA-256を記録する。

window/raterごとの`L/T/D`質問順は事前宣言したmaster seedからSHA-256で決定的にrandomizeし、Pythonの`hash()`は使わない。生データに`question_order`を残し、予定順序と異なる行を拒否する。

## 集約とaudience信頼性

主要window値は適格で完全な評定の算術平均。medianは二次診断。結果を改善するためのwinsorize、trim、重み変更、raterの事後除外は禁止。

`L/T/D`ごとに決定的な反復split-halfを1,000回。window内の２群は同人数とし、奇数ならその反復の決定的permutationに従って１人を外す。両群の平均を計算し、各群のwindow平均を作品内でcenterした後poolし、Pearson `r`を求める。

\[
r_{SB}=\frac{2r}{1+r}.
\]

median、2.5/97.5 percentileを報告する。各constructのmedian`r_SB>=.70`が必要。どれかが失敗すれば統制した主要modelを行わず`MEASUREMENT_FAILURE`。計算後に信頼性を上げるためraterを除かない。

## corpus稼働gate

全条件が必要：適格window30以上、独立作品４以上、固有の作品／pair組合せで定義した二者４以上、各採用作品に適格window５以上、各採用windowに適格rater12以上、チャネル信頼性合格、`L/T/D`audience信頼性合格、coder／調停者／rater分離合格、source／version／window manifestが評定前に凍結済み。測定gateの失敗は`MEASUREMENT_FAILURE`、その他の稼働要件不足は`INSUFFICIENT_BRIDGE_DATA`。いずれも記述出力のみ。

## 作品単位のholdout分析

Leave-One-Work-Out交差検証。１作品をholdout、残り全作品をtrainingとし、同作品のwindowを双方に混ぜない。

foldごとにtrainingのみで`L_obs`, `D_obs`, `P_AC`をz標準化し、training平均・母標準偏差`ddof=0`をholdoutに適用する。`T_obs`は0–100尺度のまま。training SDゼロはmodel識別失敗。

通常の線形回帰のみfitし、ridge、lasso、spline、interaction、多項式、後付け項は入れない。training design`X`に対して古典的予測分布は

\[
\hat\beta=(X'X)^{-1}X'y,\qquad s^2=\frac{SSE}{n-p},
\]

\[
T_*\sim t_{n-p}\left(x_*'\hat\beta,
s\sqrt{1+x_*'(X'X)^{-1}x_*}\right).
\]

各holdout windowをStudent-tのlog予測密度で採点。singular design、非正の残差自由度・残差分散はfoldを無効にし、見た後で正則化しない。

４modelすべての合計と

\[
\Delta LS_{primary}=LS_{M1}-LS_{M0},\qquad
\Delta LS_{love}=LS_{MLAC}-LS_{ML}
\]

を報告する。全適格datasetでpredictorをz標準化したfull-data `M1`をfitし、方向検査として`beta_PAC_full`を報告する。p値gateではない。

## 主要判定

- `SUPPORT`：`beta_PAC_full>0`かつ`Delta LS_primary>=2`。
- `INDETERMINATE`：`beta_PAC_full>0`かつ`0<Delta LS_primary<2`。
- `FAIL`：`beta_PAC_full<=0`または`Delta LS_primary<=0`。

`MLAC>ML`でも`M1<=M0`なら、一般的drama統制後にACの独立寄与が消えたと報告し、RCWE支持とは呼ばない。総合点は作らない。

## 静的緊張challenge

５IE・0.25チャネル解像度で、最小の非ゼロ`P_AC`は一度の最小チャネル移動による`.02`。`T_obs>=75`かつ`P_AC<=.02`のwindowを候補とする。独立作品２以上にまたがり候補３以上なら`STATIC_TENSION_CHALLENGE=FAIL`。回帰のみの判定は報告し続けるが、最終Bridge状態は`FAIL_STATIC_TENSION_CHALLENGE`となり、回帰の`SUPPORT`では消せない。

## データ分離、原典方針、倫理

チャネルannotationとaudience評定は別ファイル・別ID名前空間に置き、分析時に`window_id`のみでjoin。locator、endpoint、access metadata、短い独自メモ、hashだけを保存し、page、原典本文、書き起こし、音声／映像、長い引用を置かない。raterは合法的にアクセスできる原典を使う。

稼働前に責任operatorが同意、privacy、倫理上の要件を文書化する。このProtocolは審査／承認が不要だと仮定しない。

## 共通methodの限界

同じraterが一つのendpointで`L_obs/T_obs/D_obs`を答える。質問順randomizationは順序効果を減らすが、同一評定者・同一methodの共分散は除けない。主要分析でこの限界を報告し、正の`P_AC`係数を構成概念の心理測定上の独立性の証明と解釈しない。rater分割／複数methodの再現はv2.1候補で、未登録の救済分析ではない。

`T_obs/D_obs`の弁別妥当性は原本執筆時点の`TENSION_BRIDGE_DISCRIMINANT_PILOT_v0.3.md`で別定義され、後続のv0.4が評定開始前にこれを置換した。最初の確認的評定前に単一の固定計画pilotが`PILOT_PASS`を返し、封印した完全な履歴に不足、失敗、中止を含む全結果を列挙する。確認的作品manifestには採用結果と履歴の正確なSHA-256を入れる。runnerは全列挙結果、フォーム／Protocol／計画hash、作品／rater再利用を検査する。変更計画で失敗を置換しない。通過前は`PILOT_NOT_PASSED`で非稼働。確認的相関をpilot閾値選択・改訂に使わない。空templateは独立性未評価の`NO_DATA`。完全性宣言には外部provenanceが必要で、hashでは隠されたrunを発見できない。

## 再現性と凍結規律

`data/`のtemplateはheaderのみ。window・作品manifestはoffset付きfreeze timestampと空でないfreeze commitを記録し、runnerは最初の評定以前であることを確認する。倫理準備にはstatusと、責任operatorの外部倫理／同意記録へのSHA-256参照が必要。記録自体に私的情報をrepoで公開する必要はない。生成出力は入力hash、Git commit、master seed、除外、信頼性、稼働状態、fold、score、効果方向、静的challenge、warningを記録する。空templateは科学的結果ではなく`NO_DATA`。

corpus、作品、二者、機械的に導出した全window、目標rater数、募集終了規則は最初の評定前にcommitする。確認的status開封後に作品・window・raterを追加できず、後続データは別versionの研究になる。失敗をwindow、rater、統制変数、modelの変更で修復しない。
