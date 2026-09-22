# Rom-Com Wave Equation (RCWE)

RCWE is a falsifiable research program for modelling how a fictional pair allocates interaction among four channels over time:

\[
\mathbf p=(p_D,p_S,p_C,p_P),\qquad \sum_k p_k=1.
\]

- `D`: pair-specific direct romantic or intimate interaction
- `S`: ordinary social interaction
- `C`: conflict or rivalry
- `P`: joint work, play, or co-creation

The working slogan is **Love is DC; Rom-Com is AC**. It does not claim that affection itself oscillates. It asks whether romantic tension is better predicted by changes in interaction-channel allocation than by perceived affection alone.

## Status

- RCWE v2.0 mathematical core: frozen
- Annotation Codebook v0.2.1: frozen candidate; reliability pilot still required
- Predictive Scoring Specification v0.1: reference implementation and synthetic recovery completed
- Tension Bridge v0.1: preregistered concept; experiment not frozen
- Subject 5: retrospective blind-validation protocol
- Subject 6: prospective protocol; probabilistic model-comparison addendum frozen
- Control: information-exposure boundary frozen; inactive pending exact source-unit identifiers and coder access controls
- Subject 7: shadow holdout completed; formal blind replication remains

No quoted scripts, transcripts, manga pages, novel text, or other copyrighted source text are stored here. Data should contain only locators, short summaries, annotations, provenance, and derived values.

## Repository map

- `docs/`: frozen theory, mathematics, phase diagram, codebook, predictive scoring, tension bridge
- `protocols/`: validation and control protocols
- `registry/`: failures, observations, and post-freeze candidates
- `data/`: data policy and future schemas
- `paper/`: manuscript outline and notes

## Freeze discipline

Do not change v2.0 to rescue a failed validation. Record failures in `registry/FAIL_LOG.md`; place possible revisions in `registry/V2.1_CANDIDATES.md`. Do not create `v2.0-freeze`. A future `v2.0-spec-freeze` tag may be created only after review, a scoring reference implementation, and synthetic recovery verification; it denotes a specification freeze, not completed validation.
