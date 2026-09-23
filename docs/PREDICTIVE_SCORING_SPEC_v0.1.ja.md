# 予測スコア仕様 v0.1

> [英語原本](PREDICTIVE_SCORING_SPEC_v0.1.md)の参考訳。計算条件・数値・状態名は原本を正本とする。

**凍結阻害中（N-2/N-5）**：以下のv0.1二値収束規則は過去の再現のために保持し、再現可能な受入gateとしてはまだ認めない。canonical runtimeはWindows x86-64（AMD64）、CPython 3.12.14、NumPy 2.5.3、SciPy 1.18.1。依存関係は`pyproject.toml`で固定する。versionが一致してもBLAS buildや収束memberの一致は保証されない。新しいbenchmark成果物にはbuild設定とthread環境も残す。別runtimeは`--allow-nonreference-runtime`が必要で、診断扱い。未解決の較正・受入要件は`NUMERICAL_RECOVERY_ACCEPTANCE_PLAN_v0.1.md`を参照。

## 対象と予測mode

凍結された最小`p_D`モデルの主要な数値スコア経路を定義する。主要holdout評価は**open-loop forecast**。holdoutを開く前に全パラメータとFIT終端状態を固定する。holdout観測による状態更新、再fit、不確実性の再較正、予測のresetは禁止。

filtering、prequentialな状態更新、particle/Kalman filter分析は二次手法で、使用前に別仕様を凍結する。

## 相互作用時計と数値積分

\[
\tau=n,\qquad \Delta\tau=1.
\]

連続する適格IE間をDOP853で積分し、設定を次のように固定する。

```text
rtol = 1e-9
atol = 1e-11
max_step = 0.05
```

予測平均は

\[
\mu_n=\sigma(s_n).
\]

別solverは、**同じ固定パラメータと初期状態**を使い、各採点IEの予測平均が参照設定と絶対許容差`1e-8`以内で一致する場合のみ認める。これはsolverのみの照合であり、独立にfitした推定値の照合ではない。

## FIT推定と凍結境界

FITのみから`Delta,R,Omega,s0,v0,sigma_pred`を推定する。`R>0`, `Omega>0`, `sigma_pred>0`。後述の離散観測尤度を使う。参照optimizerはL-BFGS-B、`maxiter=80`, `ftol=1e-12`, `gtol=1e-7`。`(Delta,R,Omega,s0,v0,sigma_pred)`座標のデータ非依存の４起点は、`(0.25,.03,3,-2,.8,.20)`, `(.75,.30,20,2,.2,.05)`, `(.40,.05,15,1.5,.8,.15)`, `(.60,.25,5,-1.5,.2,.30)`。実装では正値座標を対数パラメータ化し、coder由来の下限に合わせてscale座標を調整する。optimizerが成功を報告しても、目的関数の射影勾配の無限大normが`1e-4`以下の場合にのみ成功起点と数える。生の成功フラグと停留性検査を両方残す。

成功解のうちFIT尤度が最大のものを採用し、全起点、終了code、射影勾配norm、fit値、software version、seedを保存する。停留した成功起点が２つ以上あり、FIT log likelihood差が`1e-6`以内の場合のみ`converged`とする。それ以外の予測は診断用に残せるが、optimizer一致失敗であり確認的証拠にはできない。歴史的v0.1検査は、同一の凍結依存/runtime familyで、最大FIT log likelihoodが`1e-6`以内、holdout予測平均が`1e-8`以内なら２実装を数値同等とした。ただし後者の`1e-8`は**独立再fit予測のplatform間受入gateとして不適切**。レビューで露出済み40件のIE別予測平均最大差`9.08e-8`、`12/40`件で`1e-8`超が報告された（英語原本執筆時点では生の再現成果物の取り込み待ち）。歴史的な失敗診断として保持・報告する。別の再fit許容差は、独立して凍結した開発ブロックだけで較正し、未開封validation前に承認する。上記の固定パラメータsolver照合の`1e-8`は変えない。

新規fitでは、最も尤度が高い生のoptimizer成功起点２つによる`convergence_diagnostic`も報告する。２つ未満、尤度差`>1e-6`、またはどちらかの勾配normが非有限か`10*1e-4`超なら`FAILED`。尤度が一致し両normが厳密に`1e-4/10`未満なら`CONVERGED`、それ以外は端点も含め`MARGINAL`。これは依頼されたfactor-tenの注記で、過去のboolean、採用値、受入規則を置き換えない。新境界もruntime依存になり得る。露出済み40件から閾値・起点を調整していない。

coder間不一致による測定scaleの下限は

\[
\sigma_{coder}^2=\frac{1}{2N}\sum_{n=1}^{N}(y_n^A-y_n^B)^2,\qquad
\sigma_{pred}\ge\sigma_{coder}.
\]

`sigma_coder=0`なら数値floor`1e-6`を使い、下限が非activeだったと報告する。採点対象は調停済み`p_D`。生のcoder値も保存する。

holdout開封前にFIT data commit、code commit、fit済みパラメータ、終端状態、`sigma_pred`、solver設定、baseline fitを記録する。開封後は変更できない。

## 離散化Gaussian観測分布

結果は

\[
y_n\in\{0,.25,.50,.75,1\}.
\]

bin境界は`.125,.375,.625,.875`。内部値のbinを`(a_y,b_y]`として

\[
P(y\mid\mu,\sigma_{pred})=\Phi\!\left(\frac{b_y-\mu}{\sigma_{pred}}\right)-\Phi\!\left(\frac{a_y-\mu}{\sigma_{pred}}\right).
\]

`y=0`には`(-infinity,.125]`、`y=1`には`(.875,infinity)`を割り当てる。これで５つの有効なCodebook結果に全確率質量を配り、予測平均のclipを避ける。holdout Log Scoreは

\[
LS=\sum_{n\in HOLDOUT}\log P(y_n\mid\mu_n,\sigma_{pred}).
\]

IE当たり平均Log Score、`mu_n`のMAE、全IEの確率、丸めない合計も報告する。結果を見てからゼロや微小確率を置換しない。数値計算には安定なnormal-CDFのlog差を使う。

## 主要baseline

全baselineはFITのみで推定し、holdout全体をopen-loop予測する。

1. **Persistence**：holdout全IEで`mu_n=p_D,lastFIT`。予測scaleはFIT上の１段先persistence予測`mu_n=p_D,n-1`から推定し、同じcoder不一致下限を課して凍結する。
2. **AR(1)**：`p_{D,n}=alpha+phi p_{D,n-1}+epsilon_n`とscaleをFITの同じ離散尤度でfitし、holdout更新なしで再帰予測する。
3. **二次式の物語位置**：`p_{D,n}=a+bz_n+cz_n^2+epsilon_n`とscaleを同じ尤度でFITする。`z_n=(n-mean(n_FIT))/sd(n_FIT)`。holdoutでもglobalな相互作用indexをresetせず、再fitなしで外挿する。

各baselineについて`Delta LS=LS_RCWE-LS_baseline`を別々に報告する。閾値解釈は個別Protocolに従う。勝敗を合算しない。

## 欠測とgap

gapは採点されるゼロではなく、相互作用indexを進めない。欠測・不適格IEはmodel fit前に特定する。予測が悪いことを理由にholdout行を除外しない。

## 状態

この仕様は採点規則と主要open-loop予測modeを定める。`v2.0-spec-freeze`タグ前に、参照実装と合成回復試験で再現する必要がある。
