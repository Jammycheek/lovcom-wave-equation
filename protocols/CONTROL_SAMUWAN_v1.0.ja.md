# 前向きcontrol — さむわんへるつ v1.0

> [英語原本](CONTROL_SAMUWAN_v1.0.md)の参考訳。適格性・閾値の正本は原本。原典の未確認chapterを補完しない。

## 目的

比較的安定した関係に対してRCWEが誤って振動を検出しないかを調べるcontrol。freeze日時点で未読の資料のみ前向き採点に適格で、以前に内容を話した資料は開発データとする。

## 凍結した情報曝露境界

```yaml
freeze_date: 2026-09-21
user_declared_last_read_boundary: "コミック単行本 第3巻の最後まで"
development_corpus:
  - "コミック単行本 第1巻〜第3巻"
  - "第3巻より後を含め、ユーザーがfreeze以前に内容を知っていた範囲"
prospective_eligible_material: "コミック単行本 第3巻より後の内容のうち、2026-09-21時点でユーザーが未読・未確認だったもの"
exact_first_prospective_chapter: "未確認。publication structureから推測しない。"
```

適格性は出版日ではなく情報曝露で決まる。freeze以前に出版済みでも未読・未確認なら候補となる。逆に第３巻より後でもfreeze以前に知っていた内容は`CONTAMINATED`で前向き採点不可。事前曝露を確認できなければ`UNRESOLVED`とし、適格とはしない。

この宣言は概念的な境界を固定するが、第３巻の次の正確なchapter等の原典単位IDは特定しない。前向き資料を開く／codingする前に、実際の版のmetadataで確認する。出版構造、別版、online連載順から推測しない。

## 手順

1. 新資料を開く前に正確な作品versionと原典単位IDを記録し、宣言済み第３巻境界より後でfreeze時未読であることを確認する。日付と出版順だけでは足りない。
2. 主研究と同じIE定義、４チャネルCodebook、provenance項目、２coderのblind手順、信頼性gateを使う。
3. 恋愛的な見せ場だけを選ばず、連続IEを解析する。
4. 期待相を安定平衡／低ACの`E`として凍結し、holdoutを見てから変えない。
5. 最初の適格なdyadic IEを12件、主要windowとする。12件未満なら事後的に閾値を縮めずpendingと報告する。
6. チャネルAC powerを報告する。恋愛的緊張の評定はTension Bridge実験が凍結された後に限る。

## control予測

### C1 — Direction反転

`0`方向を除く。`mixed`は常にC1不適格で、隠れた内部順序へ分解しない。最初の12適格IEには符号付き（`+1`/`-1`）Directionが６件以上必要。６件以上なら符号反転は最大１回と予測し、２回以上でC1失敗。６件未満は支持ではなく`INSUFFICIENT_DIRECTIONAL_EVENTS`。

### C2 — 外乱への応答

事前登録した誤解、第三者介入、制約変更等の外乱後、次の４適格IEを調べる。この応答window内で`+ -> - -> +`または`- -> + -> -`の二重反転があればC2失敗。適格な外乱がなければC2未検査。

### C3 — AC比較

二次的な作品間仮説として、さむわんの最初の10適格dyadic IEの値を、Subject 6の`KM`,`KT`,`KB`それぞれの最初の10適格dyadic IEから別々に計算した３値の算術平均と比較する。すべて同じ凍結チャネルAC定義を使い、さむわん値が３pair平均より低いと予測する。４系列すべてに10適格IEが必要で、足りなければ`NOT_TESTED_INCOMPLETE_WINDOWS`。代替、短縮、見せ場選択、30 IEをpoolした再計算は禁止。C3失敗はC1/C2を書き換えない。

強い振動が再現して観測されたら、作品をcontrolでないと再定義せずcontrol失敗を記録する。C1/C2/C3を別々に報告する。

## 境界の状態と稼働前の残項目

ユーザー申告の未読境界とfreeze日は固定済み。稼働前に、正確な版／作品version、第３巻後の最初の適格原典単位ID、適格単位list、曝露／汚染log、coderアクセス制御をcommitする。境界宣言artifactのSHA-256と、外部timestamp付きまたは独立立会いの参照も残す。公開repoに私的な読書履歴は不要だが、適格資料を開く前に宣言が存在したと監査できるprovenanceは必要。残項目のcommit前にprospective結果と呼ばない。

C1/C2/C3予測はProtocol非稼働中も保持する。欠けた原典単位metadataを出版日、会話timestamp、別版、chapter番号の推測で埋めない。
