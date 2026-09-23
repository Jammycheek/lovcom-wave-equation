# Subject 6 — 『あそびのかんけい』前向きProtocol

> [英語原本](SUBJECT_6_ASOBI_PROSPECTIVE_v1.0.md)の参考訳。区間・判定は原本を正本とする。

## 凍結設定

既知資料は第４巻まで。第５巻を前向きholdoutとする。主要edgeはKotaro–Mifuru `KM`、Kotaro–Tsukino `KT`、Kotaro–Bushi `KB`。Hangui `H`はまず介入nodeとし、`KH`は恋愛的証拠が稼働させるまで休止する。固有名詞は英語原本の表記を保持し、未確認の漢字表記を補わない。

各pairの主要windowは第５巻の最初の10適格IE、10件未満なら全適格IE。適格IEはCodebookに従うKotaroと該当人物の直接の相互作用。二者の外の情報・観測eventは10件に数えず、次の適格IEの文脈としてevent層に記録する。coderは先の展開を知らずに順にcodingする。

## 事前登録した予測

- `KM`：`N_approach-N_withdrawal<=0`。値が２以上で失敗、１は不確定。
- `KT`：`N_approach-N_withdrawal>=1`。値が−１以下で失敗、０は不確定。
- `KB`：平均`p_P+p_S>p_D`。平均`p_D>p_P+p_S`で失敗、等しい場合は不確定。
- persona観測：`princess` modeと通常modeがそれぞれ３IE以上なら、`E[p_D+p_S|princess]-E[p_D+p_S|ordinary]>=.25`と予測。非正なら失敗、その間は不確定。

## 介入分類

各`H`介入をpair test前に分類する。内生的：Hが特定pairの変化を観測して介入を設計。外生的／共有：先行するpair変化に起因せず、H自身の計画や一般方針から発生。H介入の50%以上が内生的なら「主に外生的なcommon input」仮説は失敗。内生的H eventを共有外部入力として条件付け除外しない。

## model比較

- `M_A`：各pair固有の履歴のみ。
- `M_B`：`M_A`に真に外生的な共有eventを追加。
- `M_C`：pair間の直接結合。v2.1候補のみ。

上記pair別事前登録予測がSubject 6の主要test。`M_A/M_B`の確率比較は二次的で、対象分布とprequential更新は追補v0.1で凍結する。`M_B`は`Delta LS>=2`で`M_A`に対する実用的支持、`(-2,2)`で不確定、`Delta LS<=-2`で敗れる。

`M_C`は、同符号のcross-lagが最低２回あり、別pairをsample外予測し、共有eventや内生的H媒介で説明できない場合に限って検討する。全testを個別に報告し、勝敗合算しない。
