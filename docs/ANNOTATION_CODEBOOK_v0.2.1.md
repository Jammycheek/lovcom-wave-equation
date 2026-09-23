# Annotation Codebook v0.2.1

## Unit of observation

An Interaction Episode (IE) is a continuous interaction between the same dyad under one scene, purpose, and context. Split at clear time or place changes, purpose changes, or third-party interventions that change the interaction mode.

No interaction is recorded as a gap. It is not coded as `p_D = 0`.

## Required provenance

Record work, version, edition, unit, locator, source type, coder, coding date, future-blind status, and theory-blind status. Store only a locator and short original summary, not source text.

## Channel simplex

\[
\mathbf p=(p_D,p_S,p_C,p_P),\qquad \sum p_k=1.
\]

Use increments from `{0,.25,.50,.75,1}`.

- `D`: pair-specific romantic/intimate content—direct disclosure, explicit date proposal, kiss, or discussion of the relationship itself.
- `S`: ordinary social exchange.
- `C`: conflict, rivalry, argument, or competition; it is not inherently negative affinity.
- `P`: joint work, play, performance, creation, or pursuit of a shared object.

Generic romantic performance carried out as a role is normally `S`, not `D`, unless it becomes pair-specific. Third-party romantic labeling is an event tag, not evidence of `D`.

## Independent attributes

- `M_mask ∈ {0,1}`: concealed identity, proxy voice, or masked persona.
- `R_dir ∈ {+1,0,-1,mixed}`: approach, maintenance, withdrawal, or clear approach and withdrawal within the same IE.
- Event tags: `disclosure`, `concealment`, `correction`, `misunderstanding`, `third-party`, `constraint-change`, `joint-event`, `none`; multiple tags allowed.
- Character belief state: `known`, `believed`, `uncertain`, `false-belief`, or `unknown`, only with explicit dialogue, narration, or action evidence.
- Source quality `Q_src`: 3 original text/video; 2 complete transcript; 1 official synopsis/PV; 0 secondary or fan material.

Do not directly code `psi`, `h`, or `U`. Do not call analyst posterior and character belief by the same name.

## Blind coding and reliability

Use at least two independent coders for formal data. Hide RCWE equations, predictions, later plot, and the other coder’s scores. Preserve both raw ratings and any adjudicated value.

Reliability gates:

\[
\kappa\ge0.70
\]

for categorical or weighted-ordinal fields, and

\[
\operatorname{median}(d_{TV})\le0.25,
\qquad d_{TV}=\frac12\sum_k|p_k^A-p_k^B|,
\]

for channel vectors. If the gate fails, revise and repilot the codebook before analysing the model.

## Character-belief schema

Do not compress a belief into a single context-free cell. Record each supported belief assertion in a linked table with:

`IE_ID, Believer, Proposition, Target, Belief_State, Evidence_Type, Evidence_Locator`

Multiple belief rows may link to one IE. Pair-external observations may update a character belief but are event-layer records, not dyadic IEs.

## Minimum row schema

`IE_ID, Work_ID, Version_ID, Edition, Unit, Locator, Pair, D, S, C, P, Mask, Direction, Event_Tags, Gap_Before, Q_src, Coder_ID, Coding_Date, Future_Blind, Theory_Blind, Short_Summary`
