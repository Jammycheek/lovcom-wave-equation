# 将来のtool backlog

> [英語原本](FUTURE_TOOLING.md)の参考訳。理論候補や証拠ではない。

先送りしたtool案。`V2.1_CANDIDATES.md`の理論候補ではなく、v2.0仕様freezeの対象でもなく、証拠も生まない。研究資源はまだ割り当てない。

## T-01 生の「心電図風」チャネルmonitor

**状態：先送り（2026-09-23記録）。** 資源があるときのみ再検討し、N-2/N-5や検証の前提にはしない。

**案**：coderが作品を読みながら適格IEごとの`D/S/C/P` vectorをCodebookの0.25 gridで入力する。monitorは心電図stripのように`p_D`の軌跡とrolling５IEの`P_AC`をスクロール表示する。横軸は壁時計時刻ではなくIE indexで、相互作用１回が１拍。model予測帯のoverlayも候補。

**もし構築するなら守る制約**（repoの既存凍結規則から導かれる）：

1. **coderにmonitorを見せない**。Codebookは理論blindを要求し、coder画面にRCWEの式、予測、波形、`P_AC`を表示しない。入力とmonitorは役割分離した別view。
2. **Bridge audience raterにも見せない**。annotation、`P_AC`、相の期待を見せない。
3. **予測は公開前に凍結**。overlayはSubject 6確率追補の`predict -> record -> reveal -> score -> update`に従う。主要open-loop採点は不変。live表示自体は採点法ではない。
4. **最初は開発資料のみ**。例えば『さむわんへるつ』第１～３巻。前向き、holdout、確認的資料では使わない。
5. **入力自体は確認的データではない**。２人の独立coder、調停、provenance、信頼性gateを備えた完全Protocolの下で集めた場合を除く。

**関連prototype（repo外）**：review中に最小`p_D` modelのoffline viewer「RCWE Phase Lab」を構築。時系列、`(p_D,v)`相平面、`Δ × G`相領域mapを表示する。RK4積分は両benchmark scenarioの`τ=0..60`で参照DOP853と`6.3e-11`以内で一致し、７test caseで領域labelが`classify_local_regime`と一致した。simulationのみで観測は入力しない。private artifact／ownerのみ：https://claude.ai/artifact/Jkw4FaVhTW1qQsUyg3VK1v
