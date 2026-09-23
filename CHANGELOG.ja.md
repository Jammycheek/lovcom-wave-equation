# 変更履歴

> [英語原本](CHANGELOG.md)の参考訳。過去の判定・数値は原本を正本とし、ここで改訂しない。

## 未release — 第４回review R-4への保護策

- pilot v0.4は予定rater/window順の末尾のみの無回答を強制。再開回答は終局的`PILOT_PROTOCOL_DEVIATION`、source/rosterまたは締切登録の不整合は終局的`PILOT_PROVENANCE_FAILURE`。
- 実際の回答行のcutoff snapshot、外部登録したSHA-256とreceipt metadata、締切前roster回答全件との完全一致、確認実験稼働前の独立receipt検証metadataを要求。runner単独では外部登録の真正性を証明できない。
- 分析者が制御する`valid_pilot/valid_primary`入力列を削除。確認実験の除外変更は別versionの追補。source exportのcommit方法が決まるまでrunnerは支持判定ではなく`CONFIRMATORY_SOURCE_PROVENANCE_PENDING`でfail closed。
- 別commit`67c4fc0`で提供されたLinux成果物の比較toolを独立に再実行。同一Linux hostのpin版／旧版の数値出力は完全一致、どちらもWindowsと露出済み40件中10件の分類が異なった。閾値は変更していない。

## 未release — 第３回review後（R-1～R-3）

- R-1：固定parameter solver専用の`1e-8`一致検査を保持し、独立再fitへの歴史的な`1e-8`適用は受入gateでなく失敗診断とする。再fit許容差には未露出開発blockが必要。当時はreviewer報告の`12/40`不一致を生bundle待ちの報告証拠として記録。
- R-2：T/D pilotをv0.3とし、一つの募集締切を凍結。各予定cellを実際の`ANSWERED`か値空欄の`NONRESPONSE`として表す。遅延回答は生データに残し主要分析から除外。不足・中止の結果を出し、黙って計画を置換しない。
- R-3：最初の評定前に計画hashを外部timestamp登録。instrument version当たり一計画。実計画、receipt、参加者、結果はまだない。
- N-1/N-3/N-4はreviewerのmutation・runtime検査を通過。N-2/N-5は未解決。この更新からfreeze tagや科学的PASSを主張しない。

## 未release — 第２回reviewへの保護策（N-1～N-5）

- N-1：評定前に作品／window／rater cellを正確に計画し、seal済み完全結果履歴を要求。失敗や変更計画は確認実験を稼働させない。実収集は保留。
- N-3：真値起点guardは全default scenarioから導出し、noise scaleを無視。意図したguard testをmutation regressionが実行し、正確／近傍真値の追加を捕捉。
- N-4：恋愛的不確実性フォームをv1.1とし、全byteをpilotと確認的成果物のhashへ拘束。`PILOT_NOT_PASSED`と無dataの独立性未評価を明示。
- N-5の一部：NumPy/SciPyとcanonical Python/runtime familyをpinし、数値build provenance、非受入の三値診断を追加し、露出済み40件を隔離。元benchmarkと停留性gateは不変。
- N-2は未解決：科学的受入決定を列挙し、独立事前登録基準まで実行benchmarkのPASSを禁止。新閾値、validation seed block、tag、科学的結果は作っていない。
- replicateごとの進捗／checkpointと保守的worker defaultを追加。既存benchmarkや完了pilot結果の上書きを拒否。

## 未release — 初期研究投入

- RCWE v2.0の凍結中核を統合。
- チャネル配分、関係Direction、Masking、event、人物belief、分析者posteriorを分離。
- E/O/M/L/B相分類を追加。
- Annotation Codebook v0.2.1と信頼性gateを追加。
- Tension Bridge v0.1を追加。
- Subject 5/6/7および前向きcontrolのProtocolを追加。
- FAIL logとv2.1候補registryを追加。

探索的parameter推定、旧５チャネルannotation、後付けforce項、著作物本文は意図して投入しなかった。

## 未release — レビュー修正

- 完全な概念的RCWE構造と独立した相互作用event層を復元。
- 前向きcontrolのC1/C2/C3を復元し、未読境界metadataは当時未解決のままにした。
- Origin Channel PersistenceとFinite-Horizon Effectをv2.1 registryへ復元。
- open-loop holdoutと離散化Gaussian Log Scoreの予測スコア仕様v0.1を追加。
- Subject 7の矛盾したchannel-lock条件をDirect-boundary lockへ変更。
- Subject 7 H7-3のshadow失敗を、正式証拠へ昇格させず記録。
- 人物belief fieldの分割、Subject 6適格IEの明確化、`J`記号衝突の解消。
- Tension Bridge v0.1を事前登録した概念とし、実験自体は未凍結と明記。
- Subject 6確率比較追補を追加・実装し、`M_C`は非稼働。
- 『さむわんへるつ』の情報曝露境界を2026-09-21時点のcomic第３巻末に固定。正確な前向き原典単位IDとcoderアクセス制御は保留。
- Tension Bridge実験に生の二重codingチャネル、機械的window、監査可能なfreeze／未来blind timestamp、作品内信頼性、役割分離、静的challenge優先順位を配線。別途凍結する弁別妥当性pilotまで非稼働。
- 真値と一致する合成起点をデータ非依存４起点へ変更。optimizer設定、起点間一致、直接的なfit／勾配test、baseline guard warningを固定。
- Subject 6曝露と結果入力を別commitに分割、確認的corpusをpairごとの最初の10適格IEに限定、生の二重codingからDirection kappaを計算。
- さむわんC1/C3の仕様不足を解決し、未読境界宣言の外部provenanceを追加。
- 凍結40-replicate合成benchmarkを再実行し、厳密な起点間一致が40件すべてで失敗した結果を`F-07`と記録。救済目的で閾値やmodel項を変えず。
- `F-07`をflatな`1e300`無効点penaltyによる偽の終了と診断。有限二次penaltyと明示的射影勾配gateに変更し、無効化されたrunをaudit logに保持。
- 独立したBridge T/D弁別妥当性pilot、凍結`.85`作品cluster bootstrap gate、生runner、data template、結果hash、確認実験での再利用禁止検査を追加。
- 修正後40-replicate benchmarkでは厳密収束`31/40`、その31件は生成相を回復。残り９件は事後修復せず`F-08`に保持。
