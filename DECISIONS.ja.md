# 決定記録

> [英語原本](DECISIONS.md)の参考訳。番号・識別子・閾値は原本を正本とする。

## 凍結済み決定

1. 主要観測は４チャネル単体`D/S/C/P`。旧「間接」チャネルは廃止。
2. Maskingはチャネルではなく属性。
3. 直接的親密さは関係の接近と同義ではない。Directionは別にcodingする。
4. 相互作用がないことはgapであり、`p_D=0`ではない。
5. 人物のbeliefと分析者のposteriorは別の対象。
6. 潜在変数`psi,h,U`は推定対象であり、直接annotationしない。
7. 検証では未来をblind codingした観測と予測を比較する。推定した潜在状態と主観的な「真値」は比較しない。
8. 媒体間比較のdefault時計は相互作用時間。
9. 凍結した最小検証対象は`p_D`。一意の４チャネル価値関数はまだ未指定。
10. 対象を見てから発見した外部強制を凍結微分方程式へ挿入しない。代わりにevent-triggered jump testを使う。
11. Network結合はv2.1候補で、共有介入と内生的介入による説明が失敗した後に限り検討する。
12. 失敗を可視のまま残し、成功へ書き換えない。
13. 主要holdout採点はopen-loop。holdout観測で状態やparameterを更新しない。
14. `J_n^TV`はIE間のTotal Variation jump、`P_switch(W)`はTension Bridgeの二乗L2 switching指標。
15. 二者外部の情報更新はevent層であり、dyadic IEではない。
16. Tension Bridge v0.1は概念と指標を凍結する。配線済み確認実験は、別versionの`T_obs/D_obs`弁別妥当性pilot仕様とPASS判定がcommitされるまで非稼働。
17. 最初に適格なtagは`v2.0-spec-freeze`。参照採点実装と独立に事前登録した回復受入基準が未開封validationでPASSした後に限る。数値基準は未承認で、既存benchmarkは`NOT_ASSESSED`、事後的PASSではない。`docs/NUMERICAL_RECOVERY_ACCEPTANCE_PLAN_v0.1.md`参照。
18. 前向きcontrolの適格性は出版日でなく情報曝露で決める。さむわんへるつでは、2026-09-21 freeze時のユーザー申告最終既読はcomic第３巻末。後の内容でもfreeze以前に既知なら汚染。最初の前向きchapterは原典単位IDの確認まで未確定。
19. Bridge確認実験は、機械的に導出する重複なし５IE window、未来blind raterのtimestamp監査、決定的な質問順randomization、作品内centerの反復split-half信頼性、Leave-One-Work-Out予測検証を使う。人間の評定は未収集。
20. Static Tension Challenge失敗は最終Bridge判定を上書きし、回帰のみの判定は診断として残す。
21. Subject 6の曝露labelとDirection結果は別commitで凍結し、正確なID・時系列監査後のみjoinする。確認的corpusはpairごとの最初の10適格IEに制限。
22. Bridge弁別pilotは、作品内centerした`|r(T,D)|`点推定と決定的作品cluster bootstrapの95%上限が両方`.85`未満のときのみPASS。pilot作品とraterはID/hash比較により確認実験から除外。
23. optimizer起点は、L-BFGS-Bが成功を報告し、射影勾配の無限大normが`1e-4`以下のときのみ成功。無効ODE試行はflatな極大sentinelではなく有限二次penaltyを使う。
24. 23は歴史的v0.1規則であり、runtime非依存の受入gateではない。成果物を保持し、canonical familyをpinし、build provenanceと別の三値感度注記を報告する。露出済み40件で再調整しない。N-2/N-5は未解決。
25. pilotの正確な作品、window、仮名rater IDは評定前に固定。判定後のsample増加、同instrumentでの失敗pilotの置換は禁止。確認実験は１計画に対する完全な宣言済み結果履歴とv1.1フォーム全体のhashを検査する。hashは提出された証拠を検証できても、operatorの完全性主張を証明しない。
26. T/D pilot v0.3は評定前に単一募集締切を凍結。予定rater/window cellは実際の回答または値が空の`NONRESPONSE`。遅延回答は生データに残すが主要分析から除く。不足・中止は完了した非合格結果で、同instrument versionでは置換不可。最初の評定前に外部の永続的timestamp登録で計画hashを残す必要があり、まだ実登録はない。
27. IE別予測平均の`1e-8`許容差は固定parameter solverの置換に限る。独立再fitへ適用した歴史的使用は受入規則でなく監査診断として残す。N-2/N-5には別の開発blockでの較正と事前承認、runtime間方針が必要。
28. R-4は人間の評定前にpilot v0.3をv0.4へ置換。無回答はraterの予定window順で末尾連続のみ。無回答後の再開は非合格のProtocol逸脱。締切時の実回答exportを外部hash登録し、締切以前のroster回答とcell単位で照合する。provenance欠落・不一致は非合格。確認実験前には外部receiptの独立した人間による検証が必要で、自己申告locatorは証明ではない。
29. 行別の手動`valid_pilot`/`valid_primary`入力は禁止。主要適格性は曝露回答、timestamp順、締切から導出する。確認runnerは評定除外追補のhashを拘束し、source-systemの完全性管理が指定されるまで、pilotがPASSしても`CONFIRMATORY_SOURCE_PROVENANCE_PENDING`を返す。その間に支持判定を出さない。提供されたLinux再現データは回顧的監査で、N-2/N-5を解決しない。
