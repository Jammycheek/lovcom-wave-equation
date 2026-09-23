# Tension Bridge T/D弁別妥当性pilot v0.3（履歴版）

> [英語原本](TENSION_BRIDGE_DISCRIMINANT_PILOT_v0.3.md)の参考訳。v0.4が評定開始前に後継版となった。履歴の意味を保持するための訳であり、実施には使わない。原本の条件を正本とする。

## 目的と分離

このpilotのPASSはBridge確認実験の稼働前提。凍結した日本語評定フォームで`T_obs`（恋愛的不確実性）と`D_obs`（一般的劇的緊張）が経験的に区別できるかを検査する。`P_AC`の検査、Bridge modelのfit、確認的証拠の提供はしない。

pilotの作品、window、raterは確認研究で再利用禁止。最初の評定前にinstrument versionごとに完全manifestを一つ凍結する：正確な作品ID／件数、作品ごとのwindow ID／件数、仮名化rater ID、offset付きの単一募集締切、version、版、form hash、freeze timestamp、commit。以下の最低数は計画制約で逐次停止規則ではない。全予定rater/window cellをrosterに一度ずつ置く。回答済みcellには不適格・遅延を含む実値とtimestampを残し、`NONRESPONSE`には架空の値・時刻を入れない。補充、作品追加、締切延長は禁止。離脱した予定raterの後続windowは`NONRESPONSE`にする。最終分析は締切以後のみ。cellが欠ければ誠実な`NONRESPONSE`行を補うか正式中止まで結果を出せない。完了判定・中止は同instrumentで最終。文言改訂には新versionと独立pilotを要し、旧履歴を残す。

明示中止は締切前・cell未提出でも可能で、理由、予定member、入力hash、完了timestampを含む`CANCELLED_PILOT`を生成する。確認実験は稼働せず、履歴に含める。締切時に適格window/rater不足なら`INSUFFICIENT_PILOT_DATA`とし、生roster・無回答数を保持する。同instrumentの新計画では置換不可。開始後未完了の計画には外部監査記録が必要で、repoは未報告試行を発見できない。

## instrumentと実施

`TENSION_BRIDGE_RATING_FORM_v1.1.md`を変更せず使う。３問`L/T/D`、正規時系列提示、決定的な質問順randomization、未来blind timestamp監査を含む。`L_obs`はinstrument文脈のため集めるが弁別gateには使わない。`response_status`は`ANSWERED`か`NONRESPONSE`のみ。後者は予定IDとstatus以外の評定、適格性回答、timestampを空欄にする。`ANSWERED`は実値・実時刻が必要。締切後回答は保持し主要分析から除く。master seedはこのProtocol versionで共通。

最低値は、適格５IE window30、独立pilot作品４、作品ごとに適格window５、windowごとに適格な未来blind評定12。除外規則と`T/D`反復split-half信頼性gate（`median r_SB>=.70`）は確認Protocolと同じ。データ不足は`INSUFFICIENT_PILOT_DATA`、信頼性不良は`PILOT_MEASUREMENT_FAILURE`。どちらもPASSでない。

## 凍結した弁別統計量

適格評定をwindow内で算術平均する。各作品について、その作品のwindow levelの`T_obs`平均を引き、`D_obs`も別に平均を引く。centered値をpoolして

\[
r_{TD}=\operatorname{cor}(T_{centered},D_{centered})
\]

を計算する。作品間水準差を除き、負のほぼ同等性も問題とするため`|r_TD|`を使う。

不確実性は決定的な作品cluster bootstrap 5,000回。各回で凍結作品を復元抽出し、抽出作品のcentered windowを全て保持して`|r_TD|`を計算し、有効値を保存する。master seedは`RCWE-TB-DISCRIMINANT-v0.3`。点推定とbootstrap分布95 percentileを片側上限として報告する。４作品では異なるcluster件数構成が35種類だけで、上限は離散的。`.78`のような普遍的な生相関cutoffではない。失敗後にsampleを増やさない。

## 凍結判定

両方が真の場合だけPASS：

```text
abs(r_TD) < 0.85
upper_95_abs_r_TD < 0.85
```

それ以外は`PILOT_DISCRIMINANT_FAILURE`。`.85`はこの実験用に事前登録した実務的な非同等性境界で、構成概念妥当性についての普遍的主張ではない。下限相関は課さない。`D_obs`はnegative-control共変量で、`T_obs`との相関を要求しない。

## 再現性と確認研究への引継ぎ

参照runnerは生pilot評定から適格性、最低数、split-half信頼性、作品内center、作品cluster bootstrap、判定を計算する。評定、manifest、本Protocol、フォーム全体のhash、pilot作品ID、仮名化rater IDのSHA-256を出す。headerのみなら`NO_DATA`。

最初の確認的評定前に完全なpilot履歴JSONをcommit・sealし、不足／失敗runと中止計画を含む全完了結果をpathと正確なSHA-256で列挙し、完全性を宣言する。全entryは同一instrument／Protocol／単一凍結manifestでPASSしなければならない。確認manifestの各行は採用結果と履歴hashを参照する。runnerは全列挙ファイル、form／Protocol hash、全予定pilot作品／raterとの非再利用を検査する。欠落、失敗、中止、変更計画、不一致なら`PILOT_NOT_PASSED`。無データは独立性が真ではなく未評価。

hashで未報告外部runや主張されたtimestampの真偽は分からない。最初の評定前に計画ファイルhashをinstrument version当たり一つ、外部のtimestamp付き登録へ公開し、locatorとreceiptをrepo外で保持する。OSF等の永続記録を使う場合、利用条件・access条件をoperatorが確認する。runnerは外部platformで本当に保持されたか検証できない。完全性、中止、評定前凍結は監査可能なoperator宣言とGit履歴を要する。過去versionと失敗をversion管理に残す。実際の作品／rater計画は未提出で、収集・稼働は保留。
