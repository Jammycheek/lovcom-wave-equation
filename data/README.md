# Data policy and schema

Do not store copyrighted source text, screenshots, full transcripts, manga pages, novel pages, or video/audio. Store locators, short original summaries, annotations, provenance, and derived values only.

Recommended tables:

- `interactions.csv`: one row per IE using the Codebook v0.2.1 minimum schema.
- `events.csv`: event ID, interval, type, pair relevance, endogenous/exogenous status, affected or observing character, short summary, provenance. Pair-external observations live here and do not count as dyadic IEs.
- `character_beliefs.csv`: IE/event link, believer, proposition, target, belief state, evidence type, and evidence locator.
- `coder_ratings.csv`: raw coder-specific values; never overwrite disagreement.
- `adjudication.csv`: adjudicated values plus rationale and links to raw rows.
- `windows.csv`: preregistered tension windows and external ratings.
- `predictions.csv`: prediction timestamp, model/code version, training boundary, target, full five-bin distribution, forecast mode, and reveal timestamp.

Suggested directories:

```text
data/
  annotations/
  derived/
```

Derived files must record the source commit and generation method. Personally identifying coder information should not be committed.

## Tension Bridge pilot audit

Before collection, fill the pilot manifest's exact `planned_work_count`, `planned_window_count`, semicolon-separated `planned_window_ids` and `planned_rater_ids` for each work, the common offset-aware `recruitment_closes_at`, and the entire v1.1 form's SHA-256. Use pseudonyms only. Pre-register the plan hash and retain the external timestamped receipt. Every planned rater/window cell appears exactly once in raw ratings: `ANSWERED` with actual numeric responses/timestamps, or `NONRESPONSE` with all response and timestamp fields blank. Excluded and late answers remain in raw data; no replacements or additions after results. After the frozen cutoff, run once even if minima fail; a cancelled plan uses `--cancel-reason` and is registered as a final failed result. Counts remain subject to the protocol minima.

The JSON history template is deliberately unapproved/empty. Before confirmatory ratings, an accountable operator must enumerate every completed pilot result (including failures, insufficient data and cancellation) in `runs` as `{"path": "relative/path/to/summary.json", "sha256": "exact file hash"}`, set the one frozen manifest/form/protocol hashes, declare completeness, and record offset-aware `sealed_at` and `freeze_commit`. Paths are resolved relative to the history file. Every confirmatory work-manifest row records the selected result hash and `discriminant_pilot_history_sha256`. Commit the history and retain all listed files; the runner checks every one, not just the selected passing file. A declaration cannot establish completeness without external audit provenance.

Hash exact UTF-8 file bytes using LF newlines. `.gitattributes` preserves this convention across checkouts; new JSON artifacts are written with LF explicitly. Historical results remain tied to their original revision and must not be rewritten to retroactively match a new hash convention. No pilot result or plan is fabricated by these templates.
