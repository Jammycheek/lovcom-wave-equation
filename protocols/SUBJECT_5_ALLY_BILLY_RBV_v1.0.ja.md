# Subject 5-RBV — アリー・マクビール／ビリー・トーマス

> [英語原本](SUBJECT_5_ALLY_BILLY_RBV_v1.0.md)の参考訳。区間・閾値・式は原本を正本とする。

## 設計

完全な前向き検証ではなく、回顧的なblind validation。

- version：TV seriesのみ。
- FIT：S1E1–S2E23。
- HOLDOUT-N：S3E1–E14。
- HOLDOUT-A：S3E15の異常challenge。
- 外部label：S3E16の診断／死。通常の予測scoreから除外。
- S3E17以降は除外。

blind coderは放送順に進み、後のepisode、要約、RCWE予測、結末を知らない。

## 主要modelとbaseline

主要対象は凍結最小系の`p_D`。FITだけから`Delta,R,Omega,s0,v0`と予測誤差を推定し、`R,Omega>0`とする。主要評価は`docs/PREDICTIVE_SCORING_SPEC_v0.1.md`に従う。FIT境界で全parameter、終端状態、予測scale、数値設定、baseline fitを凍結し、S3全体をopen-loop予測する。holdoutによる状態更新、再fit、再較正、resetは禁止。

比較するopen-loop予測はPersistence、AR(1)、二次式の物語位置。予測Log Score差を個別に報告する。

\[
\Delta LS\ge2:\ RCWE\ support;\quad -2<\Delta LS<2:\ indeterminate;\quad \Delta LS\le-2:\ baseline\ support.
\]

MAEも報告する。Directionは観測するが、RCWE予測としては採点しない。

## 強制された力学と内在的力学

明瞭な介在eventを`X_n`として標識する。

\[
J_n^{TV}=\frac12\sum_k|p_{k,n}-p_{k,n-1}|;
\]

を用い、event連動jumpとeventのないjumpの分布をpermutation testで比較する。内在的力学はeventのないwindowだけでfitし、v2.0へ新しいforce項を挿入しない。

## 異常challenge

FIT上で予測innovationを標準化する。FITの絶対innovationの97.5 percentileを閾値として凍結。連続３IE中２IE以上が超えればalarm。S3E1–E13のalarmはfalse positive、S3E14–E15はchallenge window。S3E16は外部labelのみ。
