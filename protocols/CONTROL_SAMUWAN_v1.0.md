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

Remove `0` directions and treat `mixed` as ineligible for this test unless its internal order was fixed during blind coding. In the first 12 qualified IEs, predict at most one sign reversal. Two or more reversals fail C1.

### C2 — Perturbation response

After a preregistered misunderstanding, third-party intervention, constraint change, or comparable perturbation, examine the next four qualified IEs. A `+ -> - -> +` or `- -> + -> -` double reversal within that response window fails C2. If no eligible perturbation occurs, C2 is not tested.

### C3 — AC comparison

As a secondary, cross-work hypothesis, predict lower channel AC power than Subject 6 in equal 12-IE windows. This comparison is descriptive until a cross-work normalization and uncertainty procedure are frozen. Failure of C3 does not overwrite C1 or C2.

If strong oscillation is reproducibly observed, record control failure rather than redefining the work as a non-control. Report C1, C2, and C3 separately.

## Boundary status and remaining activation metadata

The user-declared unread boundary and freeze date are now fixed. Before this protocol is activated, commit the exact edition/work version, the first eligible source-unit identifier after volume 3, the resulting eligible-unit list, an exposure/contamination log, and coder access controls. No result may be called prospective until those remaining fields are committed.

The C1/C2/C3 predictions remain preserved while the protocol is inactive. Missing source-unit metadata must not be inferred from publication dates, conversation timestamps, another edition, or assumptions about chapter numbering.
