# Data policy and schema

Do not store copyrighted source text, screenshots, full transcripts, manga pages, novel pages, or video/audio. Store locators, short original summaries, annotations, provenance, and derived values only.

Recommended tables:

- `interactions.csv`: one row per IE using the Codebook v0.2.1 minimum schema.
- `events.csv`: event ID, interval, type, pair relevance, endogenous/exogenous status, short summary, provenance.
- `coder_ratings.csv`: raw coder-specific values; never overwrite disagreement.
- `adjudication.csv`: adjudicated values plus rationale and links to raw rows.
- `windows.csv`: preregistered tension windows and external ratings.
- `predictions.csv`: prediction timestamp, model version, training boundary, target, distribution, and reveal timestamp.

Suggested directories:

```text
data/
  annotations/
  derived/
```

Derived files must record the source commit and generation method. Personally identifying coder information should not be committed.
