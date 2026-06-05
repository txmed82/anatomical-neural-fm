# Subject-Stable Local Gate Prospectus

Searches current local-gate artifacts for rows that are stable across multiple recordings in the held-out subject.

- rows: `2428`
- subject-stable rows: `5`
- subject-stable candidates: `0`
- subject-stable one-failure rows: `1`
- subject-stable holdouts: `KS014`
- decision: `no_subject_stable_local_gate_candidate`

## Stable Rows

| source | target | feature | holdout | failures | delta shuffle | delta total | target0 | target1 | bidir recs |
|---|---|---|---|---|---:|---:|---:|---:|---:|
| reaction_recording_centered | wheel_reaction_latency | broad_named_anatomy | KS014 | shuffle | -0.001 | 0.003 | 0.667 | 0.715 | 3/4 |
| wheel_targets | wheel_active | broad_named_anatomy | KS014 | shuffle, total_baseline | -0.002 | -0.002 | 0.587 | 0.598 | 3/4 |
| reaction_recording_centered | post_stim_speedup | broad_named_anatomy | KS014 | shuffle, total_baseline | -0.004 | -0.002 | 0.608 | 0.584 | 3/4 |
| derived_recording_centered | response_latency | broad_named_anatomy | KS014 | shuffle, total_baseline | -0.004 | -0.005 | 0.714 | 0.745 | 3/4 |
| wheel_targets | wheel_displacement | broad_named_anatomy | KS014 | shuffle, total_baseline | -0.008 | -0.009 | 0.556 | 0.593 | 3/4 |

## Decision

Do not train yet: subject-stable near misses exist, but they fail the unchanged local gate.
