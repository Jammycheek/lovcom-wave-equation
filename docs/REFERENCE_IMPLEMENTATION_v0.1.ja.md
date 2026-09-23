# RCWE v2.0 予測スコア参照実装 v0.1

> [英語原本](REFERENCE_IMPLEMENTATION_v0.1.md)の参考訳。実行可能な仕様・設定は英語原本とコードを正本とする。

## 対象

このpackageは`PREDICTIVE_SCORING_SPEC_v0.1.md`の主要open-loop経路を実装する。研究モデル、Protocol、Codebook、凍結基準は改訂しない。実装対象は最小２状態RCWE、５bin観測分布、FITのみの推定、３baseline、scoring、合成characterization。

## 構成

- `model.py`：最小ODE、parameter object、派生量`G`、局所平衡分類。
- `integrate.py`：適格相互作用時計と参照DOP853積分。
- `observation.py`：５bin離散化Gaussian尤度と安定なtail計算。
- `fit.py`：FITのみの複数起点尤度推定、凍結holdout予測。
- `baselines.py`：Persistence、AR(1)、Quadratic Narrative Position。
- `scoring.py`：IE別確率・log確率・絶対誤差・集計。
- `synthetic.py`：seed付き合成データとdeveloper専用の連続軌道fixture。
- `scripts/run_synthetic_recovery.py`：生成benchmark表とreport。

## parameterと時計の規約

`Delta`、正の`R`、正の`Omega`、`s0`、`v0`をfitする。`G=R*Omega`は派生値で独立にはfitしない。最初のFIT観測は相互作用indexゼロの`(s0,v0)`で評価する。その後の適格IEごとに時計を１進める。欠測、不適格、相互作用のない行はindex割当前に除き、ゼロ観測にもODEの時間進行にも使わない。

予測scaleは`sigma_pred=sigma_coder+exp(eta)`で表し、coder下限を保証する。不一致が厳密にゼロなら指定された数値floor`1e-6`を使い報告する。

Quadratic Narrative PositionのFIT index標準偏差は母集団規約`ddof=0`。採点仕様が標本／母集団のどちらかを選んでいないため、独立再現で厳密に保持すべき実装判断である。

## open-loop凍結

FIT終端状態は最後のFIT相互作用indexでの状態。最初のHOLDOUT予測はその１相互作用step後。parameter、終端状態、scale、solver設定、baseline fitは凍結する。HOLDOUT観測はscoringにのみ渡し、状態や予測をresetできない。

## 数値optimizerのguard

尤度optimizerはL-BFGS-B、`maxiter=80`, `ftol=1e-12`, `gtol=1e-7`と、採点仕様のデータ非依存４起点。`fit.OPTIMIZER_GUARDS`の広い有限guardで指数overflowや病的なODE callを避ける。baseline optimizerにも同様の係数・scale変換guard`[-5,5]`を使う。これらは実装上の安全策で、科学的parameter境界ではない。全baseline guard hitをfit成果物とbenchmark警告summaryへ出す。guard上の解を科学的境界の証拠にしない。

`converged`は起点間一致で、単一optimizerの`success`と同義ではない。起点ごとに成功flagと射影勾配無限大norm`<=1e-4`の両方が必要で、最低２起点がlog likelihood`1e-6`以内で一致する。各起点の生status、停留性、勾配normを残す。無効なODE試行点には勾配と整合する有限二次penaltyを使う。旧来のflatな`1e300` sentinelはline-search補間を壊して初期点から動かず偽の成功を出し得るため禁止。

## 合成benchmark

developer fixtureは非平衡初期状態`s0=-1.0,v0=0.20`から連続平均をfitする。ODE、変換、optimizerの誤り検出用で、validation結果ではない。観測benchmarkは連続平均周辺のGaussian潜在観測をsampleし、Codebookの凍結境界で量子化する。必須の強いcaseは`Delta=.5,R=.1,Omega=8 (G=.8)`と`Omega=12 (G=1.2)`。回復不良は識別性の結果として報告し、改善のためにmodelを変えない。

## 再現

repo rootから：

```text
python -m pytest
python scripts/run_synthetic_recovery.py --replicates 20 --seed-base 260901 --workers 8
```

runnerは`results/synthetic_recovery/`以下に`config.json`, `environment.json`, `replicates.csv`, `predictions.csv`, `fit_details.json`, `summary.json`, `REPORT.md`を出力する。固定seedとcommandは、記録された凍結Python/NumPy/SciPy/platform環境内で決定的な数値内容を作る。cross-platform再現は上記数値許容差で比較し、JSON整形、platform metadata、optimizer message、浮動小数点serializationのbyte一致は約束しない。生成成果物は手編集しない。
