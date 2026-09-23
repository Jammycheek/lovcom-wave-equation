# 第２回レビューへの対応：N-1～N-5

> [英語原本](REVIEW_RESPONSE_N1_N5.md)の参考訳。これは各レビュー時点の履歴記録であり、後日判定へ書き換えない。数値・statusは原本を正本とする。

総合判定は仕様freezeには**NOT READY**。実行可能な修正と、科学的承認を待つ決定を分ける。人間の結果や新しい合成validation blockは開いておらず、元の40件benchmarkは不変。

| 項目 | 実装した対応 | 残条件 |
|---|---|---|
| N-1 | pilot v0.3は評定前の正確な作品／window／rater計画と締切を一つ要求。確認実験はseal済みの全結果hash履歴を検査し、失敗・不足・中止があれば稼働不能。完了pilot出力の上書きは禁止。 | reviewerは検査したoptional stopping経路をクローズ。実作品／rater計画、外部timestamp登録、監査可能な完全性宣言は未提出。hashでは隠された外部runを発見できない。 |
| N-3 | 真値起点guardは全`DEFAULT_SCENARIOS`を読み、noise scaleとは独立に５つの力学parameterを検査し、全起点を見る。４つのmutation regressionは正確／２%摂動真値を追加し、意図したguard testを走らせる。 | 第３回reviewでクローズ。正確、摂動、noise-scale variantをguard testが捕捉。 |
| N-4 | 評定フォームをv1.1として改名・version化し、pilot計画／結果／確認実験へbyte全体のhashを拘束。履歴entryはinstrument／Protocol／計画一致が必要。LF規約でcheckout改行の置換を防ぐ。 | 第３回reviewで１語mutationによりクローズ。確認実験前には新しい独立pilotが必要。 |
| N-5 | 数値依存関係の厳密pin、canonical runtime検査、BLAS/build/thread provenance、別の三値感度注記。F-08を環境条件付きに修正し、F-09にplatform間結果を記録。露出済み40件すべて隔離。 | **未解決**：独立開発較正、未開封validation、runtime間membership監査。pinや広い診断bandだけでは解決しない。 |
| N-2 | benchmarkは`acceptance_status: NOT_ASSESSED`を出す。Decision/READMEは過去の`31/40`を事後的PASSにできない。数値受入計画が全未承認fieldと順序を列挙。 | **未解決**：科学的な数値閾値、正確な開発／validation block、事前承認。露出結果から値を選んでいない。 |

追加修正：明示的な`PILOT_NOT_PASSED`、無data時の独立性未評価、独立した役割分離status、正確な`.85`境界test、repo外cwdから使えるimport、保守的worker上限、進捗／checkpoint、benchmark／完了pilot結果の上書き禁止。

## 第３回reviewへの対応

reviewerはN-1/N-3/N-4をクローズし、N-2/N-5以外に新freeze blockerはないとした。R-1では、固定parameter solverには有効な過去のIE別平均`1e-8`照合が、独立再fit platform間経路の40件中12件で失敗したことが分かった（reviewer報告の最大`9.08e-8`）。旧比較は非受入の失敗診断として残し、validation前に独立開発blockから別の再fit許容差を定める。この第３回review時点で生の再現bundleはまだ提供されていなかった。

R-2ではpilot v0.3の明示的`NONRESPONSE` roster、事前凍結締切、遅延回答除外、不足時の完了出力、終局的`CANCELLED_PILOT`に対応。R-3ではinstrument version当たり一つの計画hashを最初の評定前に外部timestamp登録する。参照codeはlocal rosterとhashを確認できても、外部serviceや未申告の試行は検出できない。実登録、人間の評定、経験的pilot結果は主張していない。

三値診断は境界不安定性について有益だが受入には広すぎた（露出40件のうち約26～28件が`MARGINAL`）。当時、pin版Linux再現は進行中であり、結果を推測したり露出件から閾値を選んだりしない。

## 第４回review R-4対応と受領した再現証拠

reviewerはR-1をクローズし、R-2はほぼクローズと評価。回答済み128/512 cellを任意の`NONRESPONSE`へ変更すると、探索的pilotが`PILOT_DISCRIMINANT_FAILURE`（`|r|=.829`, upper`.898`）から`PILOT_PASS`（`|r|=.457`, upper`.628`）へ反転する選択的欠測攻撃を示した。これはreviewer報告の合成敵対的結果で、人間の証拠ではない。末尾のみの反例はそのtestではFAILのままだった。末尾制約は必要だが全選択mechanismへの証明ではない。

pilot v0.4は予定rater／作品全ての末尾制約を検査し、無回答後の再開で終局的`PILOT_PROTOCOL_DEVIATION`、別途hash登録したsource exportとの全cutoff回答照合を行う。欠落、不一致、未申告は終局的`PILOT_PROVENANCE_FAILURE`。手動入力列`valid_pilot/valid_primary`を削除。確認実験側は保存したv1.0 Protocolへの追補とする。pilot履歴は確認実験稼働前にPASS結果の独立receipt検証metadataを要求する。確認的modelは独自のsource-export Protocolが決まるまで`CONFIRMATORY_SOURCE_PROVENANCE_PENDING`でfail closed。外部serviceの真正性はrunnerの証明対象外。実計画、receipt、人間の評定はない。

reviewerは別branchのcommit`67c4fc0`で展開済みLinux再現artifactを提供し、PR #1や`main`はその時点で未変更だった。２つの生Linux CSVとWindows runを再比較：両Linuxは歴史的flagを`10/40`反転、FIT尤度最大差`1.106315039578476e-11`、IE別平均最大差`9.084153679284057e-8`。同一Linux上のpin／旧版は比較した数値がゼロ差。`run.log`のWindows checkout改行変換を考慮した各Git blob hashを確認。元`.tar.gz` hashは未検証。F-09/F-10の監査証拠であり、受入結果や閾値根拠ではない。N-2/N-5は未解決。

## 再現作業の引継ぎ

この歴史的記録作成時のlocal検証は**203 tests passed**。直前の202-test suiteもrepo外cwdから通過。203番目のtestはcommit済み無data成果物と現行form／Protocol／result byteを照合した。headerのみのrunnerは共に`NO_DATA`、独立性未評価。NumPy/SciPy build情報取得時にoptional PyYAML warningが２件あるが、取得とtestは成功。`pip check`は依存破綻なし、`git diff --check`は空白errorなし。commit済みbenchmarkの自己比較はtoolの動作検査で、独立再現ではない。元成果物は変更していない。

repoのPython 3.12環境で：

```text
python -m pytest -q
```

独立再現directoryがある場合：

```text
python scripts/compare_synthetic_runs.py results/synthetic_recovery PATH_TO_REPRODUCED_RUN
```

比較は読み取り専用で、ID、member反転、全FIT尤度、IE別RCWE holdout平均を調べる。総Log ScoreからIE平均許容差を推定しない。数値許容差が一致しても科学的受入とruntime適格性は別reviewなので`NOT_ASSESSED`。後にartifactは上記別commitで提供され、当時のPR branchにはmergeしていない。

## 数値作業再開前の決定

`NUMERICAL_RECOVERY_ACCEPTANCE_PLAN_v0.1.md`に従い、真に未露出の開発blockと固定設計を先に承認。較正後に正確な受入閾値と未開封validation blockを凍結する。事前登録でmarginal／failedの分母、parameter誤差基準、regime回復、runtime間member不一致許容を指定する。現在の40件は回顧的監査専用。

この歴史的対応記録自体には、`main` merge、freeze tag、停留性閾値変更、起点変更、後付け救済は含まれなかった。
