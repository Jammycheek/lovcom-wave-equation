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
