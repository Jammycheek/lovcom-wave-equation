# Tension Bridge T/D弁別妥当性pilot v0.4

> [英語原本](TENSION_BRIDGE_DISCRIMINANT_PILOT_v0.4.md)の参考訳。実験条件・CSV列・判定codeは原本を正本とする。この訳は新しいinstrumentではない。

## 目的と分離

Tension Bridge確認実験の稼働前に、このpilotがPASSする必要がある。凍結した日本語評定フォームの恋愛的不確実性`T_obs`と一般的な劇的緊張`D_obs`を経験的に区別できるかを検査する。`P_AC`は検査せず、Bridge modelをfitせず、確認的証拠も与えない。このversionで人間の評定は未収集。

pilotの作品、window、評定者は確認実験で再利用しない。最初の評定前に、instrument versionごとの完全なmanifestを１件凍結する：正確な作品ID／件数、作品ごとの順序付きwindow ID／件数、仮名化した評定者ID、offset付きの一つの募集締切、version、版、form hash、freeze timestamp、commit。最初の評定前にmanifest hashを外部timestamp登録し、locatorと受領記録を保持する。以下のsample size最低値は計画制約で、逐次停止規則ではない。評定者の補充、作品追加、締切延長は禁止。

予定した評定者×windowの各cellは提出rosterに正確に１回現れる。`ANSWERED`は不適格・遅延回答を含め実値とtimestampを保持する。`NONRESPONSE`は予定IDとstatusのみで、回答・適格性・timestampはすべて空欄。各作品内の各評定者について、`NONRESPONSE`はmanifestのwindow順序の連続した**末尾**にしか置けない。無回答後に回答が再開すれば、選択的に無視できる行ではなくProtocol逸脱であり、runnerは終局的な非合格`PILOT_PROTOCOL_DEVIATION`を記録する。途中のwindowを飛ばして再開する場合も含む。飛ばしたcellを黙って除外したり通常の離脱として扱ったりしない。

凍結締切時に、締切以前のtimestampを持つ全回答を含むrating systemの未変更回答行をexportする。この**cutoff export**はrosterと同じ列を持ち、`ANSWERED`行だけを含む。pilot統計量を見る前にbyte単位SHA-256を外部timestamp記録へ登録する。JSON receiptに`cutoff_export_sha256`, `manifest_sha256`, offset付き`registered_at`, `registration_locator`, 仮名化した`export_operator_id`を記録する。runnerは両hash、宣言時刻が締切以後・分析以前であること、cutoff回答の各cellと完全行がrosterに一対一対応することを検査する。欠落・不一致なら終局的な`PILOT_PROVENANCE_FAILURE`で、PASSにはならない。締切後の回答はrosterに残し、lateとして主要分析から除き、登録済みsnapshotへ遡及挿入しない。

receiptはoperatorの主張である。local codeは外部serviceがその時刻に本当に保持したか、登録前にrating-system exportが改変されなかったかを証明できない。数値上の`PILOT_PASS`を稼働根拠にする前に、外部locator／receiptとsource-system管理を独立検証する。verifier IDはexport operator IDと異なり、検証は登録後・pilot履歴seal前。codeは申告の整合性を調べるが現実の独立性は確認できない。公開するのはhashと非機密locatorのみで、参加者の実名や著作物本文は載せない。repoのtemplateはheaderのみで、実登録ではない。

最終分析は凍結締切以後に１回行う。誠実な無回答と除外を計上して最低値を満たさなければ`INSUFFICIENT_PILOT_DATA`。明示的な中止は凍結計画を早期に閉じられ、`CANCELLED_PILOT`が理由、member、入力hash、完了時刻を残す。どちらもそのinstrument versionで終局的で、seal済み履歴へ入れる。予定cellの欠落や不正形式は、登録原票に従った訂正または計画中止まで結果を阻む。完了結果の上書きは禁止。科学的な文言変更には新instrument versionと独立pilotが必要で、以前の試行も履歴に残す。

## instrumentと実施

`TENSION_BRIDGE_RATING_FORM_v1.1.md`を３つの`L/T/D`質問、時系列順の提示、決定的な質問順randomization、未来blindのtimestamp監査も含めて変更せず使う。`L_obs`は実際のinstrument文脈の保持のため集めるが、この弁別gateには使わない。分析者が制御する`valid_pilot`/`valid_primary`入力列はない。適格性は凍結曝露回答、timestamp順、締切のみで決まる。固定master seedは`RCWE-TB-DISCRIMINANT-v0.4`。

最低条件：適格５IE windowが30、独立pilot作品が４、作品ごとに適格window５、windowごとに適格な未来blind評定12。確認Protocolと同じ除外規則および`T/D`反復split-half信頼性gate（`median r_SB>=.70`）を使う。不足は`INSUFFICIENT_PILOT_DATA`、信頼性不合格は`PILOT_MEASUREMENT_FAILURE`。いずれもPASSではない。

## 凍結した弁別統計量

適格評定をwindow内で算術平均する。作品ごとに、その作品のwindowレベル`T_obs`平均を引き、`D_obs`についても別に平均との差を取る。centered値をpoolし、

\[
r_{TD}=\operatorname{cor}(T_{centered},D_{centered})
\]

を計算する。作品間の水準差を弁別検査から取り除く。`|r_TD|`を使い、負のほぼ同等性も正の場合と同様に問題とする。

不確実性は決定的な作品cluster bootstrap 5,000回で推定する。各回、凍結作品を復元抽出し、抽出作品の全centered windowを残して`|r_TD|`を計算、有効値を保存する。点推定とbootstrap分布の95 percentileを片側上限として報告する。４作品ではcluster件数構成が35種類のみで、上限は離散的。失敗後のsample追加は禁止。

## 凍結判定

両方を満たす場合だけPASS：

```text
abs(r_TD) < 0.85
upper_95_abs_r_TD < 0.85
```

それ以外は`PILOT_DISCRIMINANT_FAILURE`。`.85`はこの実験用に事前登録された実務上の非同等性境界で、構成概念妥当性についての普遍的主張ではない。下限相関は課さない。`D_obs`はnegative-control共変量であり、`T_obs`との相関を要求しない。

## 再現性と確認実験への引継ぎ

runnerは登録原票と一致したrosterから、適格性、件数、信頼性、作品内center、bootstrap、判定を計算する。roster、manifest、cutoff export、receipt、このProtocol、評定フォーム全体のhash、予定作品ID、仮名化評定者IDのhashを出す。headerのみなら`NO_DATA`。

最初の確認的評定前に完全なpilot-history JSONをsealする。不足、失敗、Protocol逸脱、provenance失敗、中止を含む全完了試行をpath/SHA-256で列挙し、完全性を宣言する。全entryは同一instrument／Protocol／単一凍結manifestに属し、PASSでなければならない。確認manifestは採用結果と履歴のhashを拘束する。欠落、失敗、中止、変更計画、不一致なら`PILOT_NOT_PASSED`。pilot作品／評定者の再利用は禁止。

hashでは未報告の外部runを発見できない。外部の計画登録とcutoff export登録を独立に調べる。実際の作品／評定者計画、登録、人間の評定データはまだないため、この実験は非稼働。
