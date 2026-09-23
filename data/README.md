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

Before collection, fill the pilot manifest's exact `planned_work_count`, ordered `planned_window_ids`/count, `planned_rater_ids` for each work, common offset-aware `recruitment_closes_at`, and entire v1.1 form SHA-256. Use pseudonyms only. Pre-register the plan hash and retain its external timestamped receipt. Under pilot v0.4, every planned cell appears once in the analysis roster: `ANSWERED` with actual values/timestamps, or blank-valued `NONRESPONSE`. For each rater, nonresponse is allowed only as a terminal suffix in planned-window order; resumption is a nonpassing protocol deviation, not a silently excluded observation. There is no `valid_pilot` input column.

At cutoff, export **only actual answers received by cutoff** directly from the rating system using the columns of `tension_bridge_pilot_cutoff_export_template.csv`. Register the exact export SHA-256 externally before analysing outcomes. Supply `--cutoff-export` and `--cutoff-receipt`; the JSON receipt carries `cutoff_export_sha256`, `manifest_sha256`, offset-aware `registered_at`, `registration_locator`, and pseudonymous `export_operator_id`. The runner checks the hash and full answer-row equality with the roster. Do not put participant identities or copyrighted content into the public repo. Late answers remain in the roster but are excluded from primary analysis. A different auditor must verify the external record and enter matching receipt-verification metadata in the sealed pilot history before confirmation can activate. A fabricated local receipt cannot be detected by code alone. No real registration or rating data are in these templates.

After the frozen cutoff, run once even if minima fail; cancellation uses `--cancel-reason` and is a final nonpassing result. Source mismatch or nonterminal nonresponse also produces a terminal nonpassing result. No replacement plan under the same instrument version is allowed.

The JSON history template is deliberately unapproved/empty. Before confirmatory ratings, enumerate every completed pilot result (including failures, insufficient data, protocol/provenance failures and cancellation) in `runs` as `{"path": "relative/path/to/summary.json", "sha256": "exact file hash"}`. For a passing entry, also supply `cutoff_receipt_verification` with `verifier_id`, offset-aware `verified_at`, `registration_locator`, and `cutoff_export_sha256`; the latter two must match the passing result and verification must predate sealing. Set the one frozen manifest/form/protocol hashes, declare completeness, and record offset-aware `sealed_at` and `freeze_commit`. Every confirmatory work-manifest row records selected-result and history hashes. The runner checks every listed file, not just the selected pass. A declared verifier ID cannot prove that an external audit actually happened; preserve the independent receipt outside the repository.

Hash exact UTF-8 file bytes using LF newlines. `.gitattributes` preserves this convention across checkouts; new JSON artifacts are written with LF explicitly. Historical results remain tied to their original revision and must not be rewritten to retroactively match a new hash convention. No pilot result or plan is fabricated by these templates.
