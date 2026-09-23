# Subject 6 確率的model比較の追補 v0.1

> [英語原本](SUBJECT_6_PROBABILISTIC_COMPARISON_ADDENDUM_v0.1.md)の参考訳。式・入力schema・判定codeは原本を正本とする。

## 状態と対象

Subject 6の二次的な`M_A/M_B`確率比較を凍結する追補。事前登録した`KM`,`KT`,`KB`、persona、H内生性testは変えない。最小RCWEのparameterを検証したり、４チャネル完全modelを実装したり、`M_C`を稼働させたりもしない。

問うのは、真に外生的な共有eventへの曝露をpair自身の観測済みDirection履歴へ加えると、次の適格IEのDirection予測が改善するか、に限る。

## 対象と適格IE

採点対象はblind調停済み`R_dir`で、category順を次に固定する。

```text
[-1, 0, +1, mixed]
```

後退、中立／維持、接近、mixedを示す。結果を見て`mixed`を除かない。

適格IEは親ProtocolとCodebookに従うKotaroと`KM/KT/KB`相手の直接的な二者相互作用。外部からの観測はIEに数えないが、適格eventは次のIEの曝露となり得る。Directionのcategory信頼性が`kappa>=0.70`を下回れば比較せず`MEASUREMENT_FAILURE`。

確認的corpusはpairごとの最初の10適格IE、計30行まで。scoreを見て有利な時点で止められないよう、第５巻の適格IE coding完了を宣言・commitしてから採点する。pairが10件未満なら完了後の全行を使い、通常の稼働判定を報告する。後の巻や見せ場を代入しない。

## 共有eventへの曝露

各対象IE`n`について、Directionを明かす前に`X_shared,n∈{0,1}`を凍結する。そのpairの直前の適格IE終了後、対象IE開始前に適格eventが最低１件起きた場合、厳密に１。

曝露と結果は別々のcommit済みファイル。曝露行にはoffset付きfreeze timestampと曝露freeze commit、結果行にはそれより後のreveal timestampと別の結果commitを記録する。runnerは曝露が結果公開より厳密に先でない行を拒否し、正確なIE-ID照合後のみjoinする。

適格な真の外生的共有eventは、`KM/KT/KB`の最低２pairに共通文脈を与え得る明示eventで、対象pairの先行変化によって生成されず、対象IE開始前に観測可能でなければならない。対象IE内で初めて発生／判明したeventはそのIEを予測できず、次IEの曝露候補になる。pair変化→H観測→H設計介入の内生的H event単独では`X_shared=1`にできない。同じ区間に別の適格外生eventがあれば、その独立した証拠で設定できる。

event表に必要な項目：

`event_id, event_order, event_type, shared_candidate, h_endogenous, eligible_exogenous_shared, source_locator, coder_id, coding_date, future_blind, theory_blind, adjudicated`

表にはlocator、metadata、短い独自要約のみを入れ、著作権のある原典本文を保存しない。

## 時系列と漏洩防止

第５巻の適格IE全件を作品内のglobal時系列順に並べる。各行で次の順序を守る。

```text
predict -> record probability -> reveal R_dir -> score -> update
```

同一場面の複数IEは原典に定義された順序を使う。原典で一意に決まらなければ分析者がtieを解かず、仕様問題として確認的採点を停止する。重複`global_order`は拒否。

第１～４巻の要約をfitに使わない。両modelは第５巻冒頭に全pair・４category（`M_B`は曝露２層の両方）で`alpha=1`からcold-startする。

## `M_A`：pair履歴のみ

pair`i`、category`k`の過去の観測数を`N_A[i,k]`とする。対象`n`の前に

\[
P_A(R_n=k\mid i)=\frac{N_A[i,k]+1}{N_A[i,*]+4}.
\]

予測・採点後に同じpairの観測categoryだけを加算する。priorと観測数を二重に加えない。

## `M_B`：曝露別のpair履歴

pair`i`、曝露`x`、category`k`の過去の観測数を`N_B[i,x,k]`とする。

\[
P_B(R_n=k\mid i,x)=\frac{N_B[i,x,k]+1}{N_B[i,x,*]+4}.
\]

採点後、対応するpair／曝露層のみ更新。固定Dirichlet prior以外のfallback、backoff、階層化、平滑化はしない。文脈でデータを分けたcold-start penaltyをprequential性能が負担する意図である。

## prequential Log Score

自然対数を使う。

\[
LS_{A,n}=\log P_A(R_n),\qquad LS_{B,n}=\log P_B(R_n),
\]

\[
LS_A=\sum_n LS_{A,n},\qquad LS_B=\sum_n LS_{B,n},\qquad \Delta LS=LS_B-LS_A.
\]

稼働gate通過時、poolした判定は`Delta LS>=2`で`PRACTICAL_SUPPORT_M_B`、`-2<Delta LS<2`で`INDETERMINATE`、`Delta LS<=-2`で`PRACTICAL_SUPPORT_M_A`。pool合計、`KM/KT/KB`ごと、IE当たり平均Log Score、IE別確率表を報告する。pair別scoreは診断で、投票や勝敗合算にしない。

## 稼働gate

全条件が必要：採点された適格IEが計12以上、`X_shared=1`が４行以上、`X_shared=0`が４行以上、３pairのうち２pair以上が両曝露層に１行以上。満たさなければ`INSUFFICIENT_SHARED_EVENT_EXPOSURE`。scoreは記述のみ、結果を見て閾値を変えない。

## 主要test／`M_C`との分離

これは二次的経験testで、Subject 6の主要予測を書き換えない。`M_B`支持はNetwork RCWEの証明ではなく、`M_A`支持はMinimal RCWEの失敗ではない。`M_C`は未実装で、親Protocolの候補条件のみで検討する。A/B不良だけでは稼働させられない。

## 確認的入力schema

必要な３ファイル：

- exposure：`global_order, pair_ie_order, ie_id, pair, x_shared, source_locator, shared_event_adjudicated, exposure_frozen_at, exposure_commit`
- outcome：`ie_id, r_dir, direction_coder_a, direction_coder_b, direction_adjudicated, outcome_revealed_at, outcome_commit`
- manifest：`work_id, version_id, edition, volume, qualified_ie_coding_complete, exposure_freeze_commit, outcome_commit, notes`

`pair`は`KM/KT/KB`、`r_dir`と生方向codeは`-1/0/+1/mixed`、`x_shared`は0/1。`pair_ie_order`は１から連続、10以下。両調停fieldは明示的true。invalid category/pair、順序重複、非調停行、commit不一致、corpus完了宣言不足、結果がfreezeより先の時系列は拒否。CohenのDirection kappaは２つの生coder列から計算し、command line入力不可。

## 再現可能な出力

参照runnerは設定、３入力のSHA-256、IE別予測、pool／pair summary、稼働状態、software/Git provenance、warningを出す。headerのみのtemplateは`NO_DATA`、生の信頼性が識別不能なら`DIRECTION_RELIABILITY_NOT_IDENTIFIABLE`、計算した`kappa<0.70`なら`MEASUREMENT_FAILURE`。いずれもA/B判定ではない。
