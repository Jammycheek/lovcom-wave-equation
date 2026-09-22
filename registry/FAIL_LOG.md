# Failure and observation log

Failures are retained even when they motivate later revisions.

| ID | Status | Observation |
|---|---|---|
| F-01 | failed generalization | `C` increasing does not universally imply `p_D` decreasing; conflict may coexist with affinity or intimacy. |
| F-02 | measurement failure | Direct intimacy was initially conflated with relationship approach. They are now separate. |
| F-03 | measurement failure | Absence of interaction was initially at risk of being treated as `p_D = 0`; it is a gap. |
| F-04 | sampling failure | Salient-scene sampling inflated Direct allocation. Full Interaction Census is required. |
| F-05 | freeze violation avoided | A post-hoc additive forcing term was explored after inspecting Subject 5. It is excluded from confirmatory v2.0 evidence. |
| F-06 | identification warning | Self-only gain estimates were highly sensitive to clipping of `p_D = 1`; those numerical values are not frozen results. |
| F-07 | optimizer-identification failure | After removing truth-matching starts and requiring the top two successful starts to agree within `1e-6`, the frozen synthetic benchmark achieved `0/40` strict-converged fits. All four starts terminated successfully in 39 replicates (three in one), but top-two FIT log-likelihood gaps ranged from `0.8127993492760339` to `89.25444727938093`. Holdout recovery summaries are therefore withheld rather than used to rescue v2.0. |
| O-01 | observation | Constraints can suppress relationship transition without reducing interaction frequency. |
| O-02 | observation | Objective constraints and a character’s belief about constraints can move separately. |
| O-03 | observation | A pair-external observed event can update character belief without a dyadic interaction. |
| O-04 | observation | Narrative forcing omitted from analysis can masquerade as self-excitation. |
| O-05 | observation | Character emotional volatility need not imply dyadic channel volatility. |
| SHADOW-S7-01 | non-blind exploratory failure | Subject 7 H7-3 predicted `N_+ - N_- >= 2`; the shadow holdout was unsupported / FAIL-leaning. This is not a formal result; blind validation remains pending. |

New entries should state the frozen prediction, eligible data, observed contradiction, impact, and whether a v2.1 proposal was registered.
