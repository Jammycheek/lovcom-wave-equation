# 数値回復の受入計画 v0.1

> [英語原本](NUMERICAL_RECOVERY_ACCEPTANCE_PLAN_v0.1.md)の参考訳。英語原本が正本。数値基準を新たに選んだ文書ではない。

状態：**DRAFT / NOT ASSESSED / FREEZE BLOCKED**。事前登録のchecklistであり、回復の合格宣言ではない。新しい科学的受入閾値やseed blockは選んでいない。Decision 17・23によって過去の`31/40`が合格になることはない。

## 変更しない過去の証拠

`results/synthetic_recovery/`と生成時のrevisionを変更しない。その`converged` booleanはv0.1のruntime依存の規則である。露出済みblockは２つのdefault scenario、seed`260901`–`260920`の40組。全環境で隔離する。元の９失敗IDも再実行の失敗IDも、新規holdoutにはならない。

reviewer提供のLinux再現run２本は別commit`67c4fc0`の`review/reproduction_2026-09-23/`にある。生CSVをWindows成果物と再比較したところ、両Linux runで過去の収束フラグが同じ`10/40`反転し、IE当たり予測平均の最大差は`9.084153679284057e-8`。同一Linux上の固定版と旧版のfit・予測は数値的に完全一致した。これは提供成果物と比較の検証であり、このhostでの独立したLinux最適化再実行ではない。元のarchive SHA-256は未照合（展開ファイルのみ提供）。各ファイルのGit blob hashは照合した。holdout Log Score総量の一致はIE別比較の代用にならない。40件は較正ではなく監査データである。

## runtime契約と再実行

- canonical familyはCPython 3.12.14、NumPy 2.5.3、SciPy 1.18.1、Windows AMD64。`pyproject.toml`で数値依存関係とPython minor familyを固定し、benchmarkはfit前にruntimeを厳密確認する。
- OS、architecture、library build/BLAS設定、thread環境、worker数、code commit、全初期／最終値、生optimizer flag、射影勾配、尤度を記録する。同versionでも同build・bit単位の再現とは限らない。
- 別familyでは`--allow-nonreference-runtime`が必要で、canonicalとは呼ばない。診断再実行は新規出力先へ保存し、歴史的結果を上書きしない。
- `(scenario,seed)`の完全なmemberとIE別予測を比較する。FIT尤度の絶対許容差`1e-6`は歴史的診断として保持する。固定パラメータ・初期状態のsolverのみの予測平均許容差は`1e-8`。独立再fitには、開発blockで較正する**別の未選定**同等性許容差が必要。パラメータ差、holdout score、分類差は個別に報告する。露出済み比較で最大`9.08e-8`、`12/40`件が過去の再fit照合`1e-8`を超えたという観察は、較正には使わない。
- `python scripts/compare_synthetic_runs.py results/synthetic_recovery PATH_TO_REPRODUCED_RUN`は読み取り専用。IDの重複／欠落、生flag、FIT尤度、各RCWE holdout平均を調べる。`numerical_tolerances_met`は過去の再fit用`1e-8`診断だけに対応し、将来の受入を決めない。自己比較はtool検査で独立再現ではない。fit証拠の欠落や非有限値は黙って除外せずerrorにする。
- 新benchmarkは完了replicateごとにcheckpointと進捗を記録する。default workerは４以下かつ検出されたlogical CPU以下。資源制限時は明示的に減らせる。

## 三値注記は救済gateではない

既存勾配cutoffの10倍近傍は`MARGINAL`として報告する。正確な実装は`PREDICTIVE_SCORING_SPEC_v0.1.md`を参照。`CONVERGED/MARGINAL/FAILED`は追加診断であり、v0.1の採用fit、boolean、summary対象は変えない。ここでの`CONVERGED`はbenchmark受入を保証しない。離散規則の境界はruntime依存になり得る。

停留性検査を外してはならない（F-07再発）。露出結果を合格させるために基準を緩めない。pinと三値注記だけではN-5は未解決。

## 必須の意思決定順序

1. 開発観測を生成する**前**に、正確なseed/scenario list、固定sample size、パラメータ変換、診断指標、許される数値変更を承認・commitする。test／developer runを含む全開封済みblockとの非重複を確認する。
2. その開発blockだけで、数値微分精度、終了条件、実行予定runtime/build matrixでの勾配分布の疎な領域を検討する。変更したoptimizerは別version v0.2。失敗した選択肢も含む全試行を保持し、block増量によるoptional stoppingはしない。
3. validation開封前に数値受入基準と正確な未開封validation blockを承認・commitする。安定したcutoffを擁護できなければ、二値分類を強行せず、その結果を報告する。
4. 凍結したalgorithm、runtime方針、block、基準で１回検証する。失敗は失敗として残す。改訂には別versionと真に新しいvalidation dataが必要で、旧blockは監査専用になる。
5. 独立レビュー後にのみ`v2.0-spec-freeze`を検討できる。この文書自体はtagやmergeを許可しない。

## 科学的承認がまだ必要な数値項目

validation前に確定し、既存の`31/40`から逆算しない。

- 三値判定の方針と正確な停留性・起点一致閾値。
- scenario**別**の最低収束率。全試行（errorとmarginalを含む）を分母にする。
- scenario別の正しいregime回復率。failed/marginalを未回復と数える。
- 各パラメータの最大回復誤差、指標／分位数、非識別性の扱い。
- runtime間member不一致の最大値と宣言したruntime/build matrix。
- 固定パラメータsolver許容差とは独立した再fit後IE平均の同等性許容差と不一致時の方針。
- cross-platform確認が必要なら、独立Linux/container再現の参照runtime/build matrix。
- 開発・validationの固定sample size、seed list、閉鎖規則。
- 予測性能を別の特性記述とするか受入基準に含めるか。後者ならbaseline比較と正確な閾値。

承認までは実行可能benchmarkは無条件に`acceptance_status: NOT_ASSESSED`を報告する。合成回復の主張、Bridge pilotの経験的PASS、unit test成功はこの科学的判断の代わりにならない。これは研究責任者とreviewerへのN-2/N-5の引き継ぎである。
