# Subject 7 — 藤岡ハルヒ／須王環

> [英語原本](SUBJECT_7_HARUHI_TAMAKI_BLIND_v1.0.md)の参考訳。区間・閾値は原本を正本とする。

## versionと分割

- version：2006年TV animeのみ。
- pilot：E1–E2、採点から除外。
- FIT：E3–E17。
- HOLDOUT：E18–E26。

pilotでCodebook規則を２つ追加した。一般的な恋愛演技は`D`ではなく、第三者の恋愛ラベルも`D`ではない。E3で規則を凍結する。

既存作業は一部二次的書き起こしに依存する非盲検shadow runで、pipelineの証拠に過ぎない。正式な主張には対象versionの原典から新たに未来blind・理論blindでcodingする必要がある。

## 凍結holdout予測

1. **内在的な反復反転なし**：eventのない`+ -> - -> +`または`- -> + -> -`はない。１回で失敗。
2. **大きなjumpはevent連動**：`J_n^TV>=.5`が、そのIEまたは直前IEのeventなしに起きたら失敗。`J_n^TV`は凍結仕様のTotal Variation jump。
3. **接近優位**：`N_+-N_->=2`。`N_+<=N_-`で失敗、差１は不確定。
4. **Directの独占なし**：平均`p_D<.5`。`.5`以上で失敗。
5. **Direct境界lockなし**：D飽和lock（`p_D>=.90`が３IE連続）もD抑制lock（`p_D<=.10`が３IE連続）も起きない。どちらでも失敗。抑制caseでの`S/C/P`配分は問わない。

事前登録した相：**強制されたexcursionを伴うE領域**。

## 解釈上のguard

夢や内的表象はdyadic相互作用ではない。人物一人の嫉妬、意図、感情的変動はpairチャネルの観測ではない。人物の変動と二者の変動を分ける。
