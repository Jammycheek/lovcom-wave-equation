# Tension Bridge評定除外の追補 v0.1

> [英語原本](TENSION_BRIDGE_RATING_EXCLUSION_ADDENDUM_v0.1.md)の参考訳。Protocol hashは英語原本のbyte列に基づく。

確認的人間評定の収集前に`TENSION_BRIDGE_EXPERIMENT_v1.0.md`を補足する。元ファイルは監査のため変更しない。確認runnerはこの**英語追補**のSHA-256を出力へ拘束する。

確認評定CSVには分析者が操作する`valid_primary`/`valid_pilot`列を設けない。提出された回答はすべて保持する。主要適格性は凍結した曝露回答（`prior_exposure`, `knows_future`, `exposure_uncertain`）、offset付きの適格判定／endpoint／評定／次の開封timestamp、既存の役割分離・信頼性gateから計算する。自由形式の行別有効性スイッチはない。これらの項目で説明できない技術的無効化を黙って除外行として符号化できない。確認実験を稼働する前に、将来に向けた別versionの理由code Protocolと、独立にtimestampされたsource記録が必要。

手動除外スイッチをなくしても、rating systemが生成した全回答が提出された証明にはならない。確認的募集前に、operatorはpilot v0.4同様の正確なrosterとsource exportのcommit手順も凍結しなければならない。そのprovenance経路が実装され外部検証できるまでは、参照runnerは他の点でpilotがPASSしても`CONFIRMATORY_SOURCE_PROVENANCE_PENDING`を出し、確認modelをfitしない。この追補だけでは人間のデータ収集準備は整わない。
