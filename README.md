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
- Predictive Scoring Specification v0.1: **NOT READY**; historical `31/40` convergence membership is runtime-dependent (F-08/F-09). Numerical dependencies are pinned, but independent calibration and preregistered acceptance remain unresolved (N-2/N-5).
- Tension Bridge: implementation wired; fixed-plan discriminant pilot v0.3 supports honest nonresponse, a frozen collection cutoff, final insufficient results, cancellation, and complete-history checks. Form v1.1 remains hash-bound. No real pilot plan or human data yet; experiment inactive.
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

Recovery acceptance is currently `NOT_ASSESSED`, not a pass. See [the open numerical acceptance plan](docs/NUMERICAL_RECOVERY_ACCEPTANCE_PLAN_v0.1.md). All 40 exposed benchmark cases are audit-only, never threshold-development data. Original benchmark artifacts are retained unchanged. Replays must use a new output directory; exact package pins alone do not establish cross-platform classification reproducibility.
