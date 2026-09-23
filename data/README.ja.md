# データ方針とschema

> [英語原本](README.md)の参考訳。実入力列名・hash手順・状態codeは英語原本を正本とする。

著作権のある原典本文、screenshot、全文書き起こし、漫画・小説page、映像・音声を保存しない。locator、短い独自要約、annotation、provenance、派生値のみを保存する。

推奨表：

- `interactions.csv`：Codebook v0.2.1の最小schemaでIE当たり１行。
- `events.csv`：event ID、区間、種類、pairとの関連、内生／外生、影響／観測する人物、短い要約、provenance。pair外部の観測はここに置き、dyadic IEには数えない。
- `character_beliefs.csv`：IE/eventとのlink、believer、proposition、target、belief状態、証拠種類、evidence locator。
- `coder_ratings.csv`：coder別の生値。不一致を上書きしない。
- `adjudication.csv`：調停値、理由、生行へのlink。
- `windows.csv`：事前登録した緊張windowと外部評定。
- `predictions.csv`：予測timestamp、model/code version、training境界、target、５bin全分布、予測mode、reveal timestamp。

推奨directory：

```text
data/
  annotations/
  derived/
```

派生fileには原典commitと生成方法を記録し、個人を特定できるcoder情報はcommitしない。

## Tension Bridge pilot監査

収集前にpilot manifestへ、正確な`planned_work_count`、順序付き`planned_window_ids`と件数、作品ごとの`planned_rater_ids`、共通のoffset付き`recruitment_closes_at`、v1.1フォーム**全体**のSHA-256を入れる。仮名のみ使用。計画hashを事前登録し外部timestamp receiptを保持する。pilot v0.4では各予定cellがrosterに１回現れ、実値・timestampのある`ANSWERED`か値が空の`NONRESPONSE`とする。各raterの無回答は予定window順で末尾連続のみ。再開は黙った除外でなく非合格Protocol逸脱。`valid_pilot`入力列はない。

締切時にrating systemから、締切までに受領した**実回答のみ**を`tension_bridge_pilot_cutoff_export_template.csv`と同じ列で直接exportする。

結果分析前に正確なexport SHA-256を外部登録する。`--cutoff-export`と`--cutoff-receipt`を指定。JSON receiptは`cutoff_export_sha256`, `manifest_sha256`, offset付き`registered_at`, `registration_locator`, 仮名化`export_operator_id`を持つ。runnerはhashとrosterとの全回答行一致を検査する。実名や著作物を公開repoへ入れない。遅延回答はrosterに残すが主要分析から除く。別の監査者が外部記録を検証し、一致するreceipt検証metadataをseal済みpilot履歴へ書くまで確認実験は稼働しない。架空のlocal receiptだけではcodeが検出できない。templateには実登録・実評定データがない。

凍結締切後、最低数不足でも１回実行する。中止は`--cancel-reason`で最終非合格とする。source不一致や末尾でない無回答も終局的非合格。同instrument versionの代替計画は禁止。

JSON履歴templateは意図的に未承認／空。確認的評定前に、失敗、不足、Protocol/provenance失敗、中止を含む全pilot結果を`runs`へ`{"path":"relative/path/to/summary.json","sha256":"exact file hash"}`として列挙する。PASS entryには`cutoff_receipt_verification`の`verifier_id`, offset付き`verified_at`, `registration_locator`, `cutoff_export_sha256`も必要。後２者はPASS結果と一致し、検証はsealより先。凍結した単一manifest／form／Protocol hashを設定し、完全性を宣言し、offset付き`sealed_at`と`freeze_commit`を残す。確認的作品manifestの各行は選択結果と履歴hashを記録する。runnerは選択PASSだけでなく全列挙fileを検査する。申告verifier IDでは外部監査の実在を証明できないので、独立receiptをrepo外に保存する。

正確なUTF-8 byte列をLF改行でhashする。`.gitattributes`がcheckout間で守り、新JSON成果物も明示的にLFで書く。過去結果は生成revisionに結びついたままにし、新hash規約へ遡及的に書き換えない。templateがpilot結果や計画を捏造することはない。
