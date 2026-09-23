# 失敗・観察log

> [英語原本](FAIL_LOG.md)の参考訳。ID・数値・証拠statusは英語原本を正本とする。

後の改訂の動機となった失敗も保持する。

| ID | 状態 | 観察 |
|---|---|---|
| F-01 | 一般化失敗 | `C`の増加は普遍的に`p_D`減少を意味しない。対立は親和性や親密さと共存し得る。 |
| F-02 | 測定失敗 | 直接的親密さと関係への接近を当初混同した。現在は分離した。 |
| F-03 | 測定失敗 | 相互作用の欠如を`p_D=0`と扱う危険があった。これはgapである。 |
| F-04 | sampling失敗 | 目立つsceneだけの選択でDirect比率が膨らんだ。完全なInteraction Censusが必要。 |
| F-05 | freeze違反を回避 | Subject 5を見た後に後付け加算force項を探索した。v2.0の確認的証拠には含めない。 |
| F-06 | 識別性の警告 | self-only gain推定は`p_D=1`のclippingに強く依存した。その数値は凍結結果でない。 |
| F-07 | 修正された数値実装の失敗 | 真値起点を外した最初のbenchmarkは厳密収束`0/40`を報告。無効ODE試行がflatな`1e300`目的penaltyを返し、L-BFGS-Bのline-search補間が崩壊。大勾配で非停留の初期点を偽の成功と報告した。無効化された`0/40`を履歴に残し、RCWE modelは変えず有限二次penaltyと明示的射影勾配gateで修正した。 |
| F-08 | runtime依存のoptimizer分類／受入未解決 | commit済みWindows / Python 3.12.14 / NumPy 2.5.3 / SciPy 1.18.1 runではv0.1厳密収束`31/40`（安定`19/20`、振動`12/20`）で、31件は生成時の局所相classを回復した。そのrunのみで、reject８件には最高尤度で別の生の成功終了があったが勾配gateに届かず、振動seed`260913`には別々の停留尤度basinがあった。reject IDは安定`260904`、振動`260904,260905,260911,260913,260916,260918,260919,260920`。内在的・platform非依存の失敗IDではない。元の成果物とsubset summaryは変更・合格昇格せず保持。F-09参照。 |
| F-09 | 収束membershipの再現性失敗／生artifact比較済み | 別commit`67c4fc0`のLinux再現run２本を、repoの読み取り専用比較toolでWindows runと比較。各Linux runは40組のFIT尤度で最大差`1.106315039578476e-11`以内だが、同じ`10/40`の厳密収束flagが反転。双方の総数は`31/40`でreject IDの重なりは`4/9`のみ。同一Linux hostでNumPy/SciPy versionを変えても比較したfit値・予測に数値差はゼロ。package pinだけでplatform間分類差は解消せず、OS、Python patch、CPU、数値buildの寄与は未分離。提供artifactを検証したのであり、このhostでLinux最適化を新規実行したのではない。生fileは別branch上でPR branch外。v0.1の閾値・起点・選択と元成果物は不変。露出済み40組は調整禁止。N-2/N-5未解決。 |
| F-10 | 再fit予測の同等性診断失敗／生artifact比較済み | Linux fileとWindowsのholdout IE別平均の最大差は`9.084153679284057e-8`。`12/40`組が歴史的な再fit実装test`1e-8`を超えた。この値は固定parameter ODE solver検査由来で、独立再fitの受入gateには適さない。solverのみの検査は保持し、独立開発dataで別の再fit同等性許容差をvalidation前に指定する。露出組で較正していない。 |
| F-11 | 敵対的欠測の脆弱性／reviewer報告の合成test | reviewerは回答済み128/512 cellを任意の`NONRESPONSE`に変え、window当たり12評定以上を保持したところ、simulationのpilot判定が`PILOT_DISCRIMINANT_FAILURE`（`\|r\|=.829`、上限`.898`）から`PILOT_PASS`（`\|r\|=.457`、上限`.628`）へ反転。人間の結果ではない。pilot v0.4は内部の無回答を禁止し、分析rosterと一致する登録済み締切原票を要求する。末尾のみの欠測でも選択riskは数学的に消えず、外部登録とsource-systemの完全性には独立監査が必要。 |
| O-01 | 観察 | 制約は相互作用頻度を減らさず関係の遷移を抑え得る。 |
| O-02 | 観察 | 客観的制約と人物が信じる制約は別々に動き得る。 |
| O-03 | 観察 | pair外部の観測eventはdyadic相互作用なしでも人物beliefを更新し得る。 |
| O-04 | 観察 | 分析から抜けた物語的強制は自己励起に見え得る。 |
| O-05 | 観察 | 人物個人の感情変動は二者チャネルの変動を意味しない。 |
| SHADOW-S7-01 | 非盲検の探索的失敗 | Subject 7 H7-3は`N_+-N_->=2`を予測したが、shadow holdoutは支持されずFAIL寄り。正式結果ではなく、blind validationは保留。 |

新entryには凍結予測、適格data、観測した矛盾、影響、v2.1案登録の有無を記す。
