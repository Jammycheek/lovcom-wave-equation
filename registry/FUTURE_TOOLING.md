# Future tooling backlog

Deferred tool ideas. Entries here are **not** theory candidates (see `V2.1_CANDIDATES.md`), are not part of the v2.0 specification freeze, and produce no evidence. No research resources are allocated to them.

## T-01 Live "ECG-style" channel monitor

**Status:** deferred (recorded 2026-09-23). Revisit only when resources allow; it is not a prerequisite for N-2/N-5 or any validation.

**Idea.** A coder enters each qualified IE's `D/S/C/P` vector on the Codebook 0.25 grid while reading a work. A monitor scrolls the `p_D` trace and the rolling five-IE `P_AC`, like an electrocardiogram strip. The horizontal axis is the IE index, not wall-clock time: one interaction advances the strip one beat. A model forecast band may be overlaid.

**Constraints if it is ever built.** Each follows from rules already frozen in this repository.

1. **The coder never sees the monitor.** The Codebook requires theory-blind coding: no RCWE equations, forecasts, waveforms or `P_AC` in the coder's view. Input and monitor are separate views with separate roles.
2. **Tension Bridge audience raters never see it either.** They may not see annotations, `P_AC` or phase expectations.
3. **Forecasts are frozen before each reveal.** Any forecast overlay follows predict → record → reveal → score → update, as in the Subject 6 probabilistic addendum. Primary open-loop scoring is unchanged; the live display is not a scoring method.
4. **Development material first.** Use it only on corpora already classified as development data (for example Samuwan Herutsu volumes 1–3). Never on prospective, holdout or confirmatory material.
5. **Its entries are not confirmatory data** unless collected under the full protocol: two independent coders, adjudication, provenance and reliability gates.

**Related prototype (outside the repository).** An offline viewer of the minimal `p_D` model, "RCWE Phase Lab", was built during review: time series, `(p_D, v)` phase plane and a `Δ × G` regime map. Its RK4 integration matched the reference DOP853 implementation within `6.3e-11` for `τ = 0..60` in both benchmark scenarios, and its regime labels matched `classify_local_regime` on seven test cases. It simulates only; it takes no observations. Private artifact, owner access only: https://claude.ai/artifact/Jkw4FaVhTW1qQsUyg3VK1v
