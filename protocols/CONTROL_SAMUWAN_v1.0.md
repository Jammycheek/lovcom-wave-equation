# Prospective control — Samuwan Herutsu v1.0

## Purpose

This control asks whether RCWE can correctly avoid detecting oscillation when a relationship is comparatively stable. Only material unread at the freeze date is eligible for prospective scoring; previously discussed material is development data.

## Frozen information-exposure boundary

```yaml
freeze_date: 2026-09-21
user_declared_last_read_boundary: "コミック単行本 第3巻の最後まで"
development_corpus:
  - "コミック単行本 第1巻〜第3巻"
  - "第3巻より後を含め、ユーザーがfreeze以前に内容を知っていた範囲"
prospective_eligible_material: "コミック単行本 第3巻より後の内容のうち、2026-09-21時点でユーザーが未読・未確認だったもの"
exact_first_prospective_chapter: "未確認。publication structureから推測しない。"
```

Eligibility is defined by information exposure, not publication date. Material published before the freeze date may remain prospectively eligible if it was unread and unconfirmed at freeze. Conversely, any post-volume-3 content known before freeze is `CONTAMINATED` and cannot be scored prospectively. If prior exposure cannot be established, classify the unit as `UNRESOLVED` rather than eligible.

The declaration above fixes the conceptual boundary but does not identify the exact chapter or other source-unit identifier that follows volume 3. Verify that identifier from the actual edition metadata before opening or coding prospective material. Do not infer it from publication structure, a different edition, or an online chapter sequence.

## Procedure

1. Record the exact work version and source-unit identifier before opening new material, then confirm that the unit lies after the declared volume-3 boundary and was unread at freeze. The calendar date and publication order alone do not establish eligibility.
2. Use the same IE definition, four-channel codebook, provenance fields, two-coder blind process, and reliability gates as the main studies.
3. Analyse consecutive IEs rather than selecting romantic highlights.
4. Freeze the expected phase as stable-equilibrium/low-AC (`E`). Do not change the label after holdout access.
5. Use the first 12 qualified dyadic IEs as the primary window. If fewer than 12 eligible IEs exist, report the control as pending rather than shortening the threshold after inspection.
6. Report channel AC power. Romantic-tension ratings may be reported only after the Tension Bridge experiment is frozen.

## Control prediction

### C1 — Direction reversals

Remove `0` directions; `mixed` is always ineligible for C1 and is never decomposed into a hidden internal order. In the first 12 qualified IEs, at least six valid signed (`+1` or `-1`) Direction observations are required. With six or more, predict at most one sign reversal; two or more reversals fail C1. With fewer than six, report `INSUFFICIENT_DIRECTIONAL_EVENTS`, not support.

### C2 — Perturbation response

After a preregistered misunderstanding, third-party intervention, constraint change, or comparable perturbation, examine the next four qualified IEs. A `+ -> - -> +` or `- -> + -> -` double reversal within that response window fails C2. If no eligible perturbation occurs, C2 is not tested.

### C3 — AC comparison

As a secondary, cross-work hypothesis, compare the first 10 qualified Samuwan dyadic IEs with the arithmetic mean of three separately computed Subject 6 values: the first 10 qualified `KM`, `KT`, and `KB` dyadic IEs. Each value uses the same frozen channel AC definition. C3 predicts that the Samuwan value is lower than that three-pair mean. All four sequences must contain 10 qualified IEs; otherwise report C3 as `NOT_TESTED_INCOMPLETE_WINDOWS`. No substitution, shortening, highlight selection, or pooled 30-IE recomputation is allowed. Failure of C3 does not overwrite C1 or C2.

If strong oscillation is reproducibly observed, record control failure rather than redefining the work as a non-control. Report C1, C2, and C3 separately.

## Boundary status and remaining activation metadata

The user-declared unread boundary and freeze date are now fixed. Before this protocol is activated, commit the exact edition/work version, the first eligible source-unit identifier after volume 3, the resulting eligible-unit list, an exposure/contamination log, and coder access controls. Also record a SHA-256 hash and externally timestamped or independently witnessed reference for the boundary declaration artifact. The public repository need not contain private reading history, but it must contain enough provenance to audit that the declaration existed before eligible material was opened. No result may be called prospective until those remaining fields are committed.

The C1/C2/C3 predictions remain preserved while the protocol is inactive. Missing source-unit metadata must not be inferred from publication dates, conversation timestamps, another edition, or assumptions about chapter numbering.
