# Local Gate Meta-Failure Audit

Aggregates closed no-spend target/control gates and ranks near misses against the unchanged GPU promotion criteria.

- artifacts present: `11`
- rows audited: `1924`
- candidates: `0`
- one-failure rows: `11`
- two-or-fewer-failure rows: `609`
- max bidirectional recording fraction: `0.750`
- decision: `no_local_gate_candidate`

## Failure Counts

| failure | rows | one-failure rows |
|---|---:|---:|
| recording_bidirectionality | 1919 | 10 |
| target1 | 1247 | 0 |
| target0 | 1069 | 0 |
| shuffle | 1004 | 1 |
| total_baseline | 681 | 0 |

## Source Summary

| source | rows | <=1 fail | <=2 fails | best score | max bidir |
|---|---:|---:|---:|---:|---:|
| cell_type_priors | 112 | 2 | 14 | -0.250 | 0.500 |
| contextual_targets | 84 | 0 | 24 | -0.250 | 0.500 |
| derived_targets | 84 | 1 | 23 | -0.005 | 0.750 |
| projected_support80_all_families | 320 | 0 | 132 | -0.250 | 0.500 |
| projected_support80_counts | 320 | 2 | 113 | -0.500 | 0.250 |
| projected_support80_fractions | 320 | 0 | 110 | -0.500 | 0.250 |
| projected_support80_unit_residuals | 320 | 0 | 98 | -0.500 | 0.250 |
| reaction_dynamics | 84 | 2 | 30 | -0.001 | 0.750 |
| shared_family | 112 | 2 | 35 | -0.250 | 0.500 |
| waveform | 84 | 1 | 6 | -0.250 | 0.500 |
| wheel_targets | 84 | 1 | 24 | -0.002 | 0.750 |

## Top Near Misses

| fails | source | target | feature | holdout | failures | delta shuffle | delta total | target0 | target1 | bidir |
|---:|---|---|---|---|---|---:|---:|---:|---:|---:|
| 1 | reaction_dynamics | wheel_reaction_latency | broad_named_anatomy | KS014 | shuffle | -0.001 | 0.003 | 0.667 | 0.715 | 3/4 |
| 1 | waveform | choice | depth | CSH_ZAD_019 | recording_bidirectionality | 0.092 | 0.039 | 0.551 | 0.568 | 2/4 |
| 1 | cell_type_priors | choice | modulatory | SWC_038 | recording_bidirectionality | 0.083 | 0.081 | 0.565 | 0.566 | 2/4 |
| 1 | cell_type_priors | choice | gabaergic | NR_0019 | recording_bidirectionality | 0.047 | 0.047 | 0.567 | 0.589 | 2/4 |
| 1 | wheel_targets | choice_aligned_wheel | broad_named_anatomy | SWC_043 | recording_bidirectionality | 0.008 | 0.007 | 0.558 | 0.584 | 2/4 |
| 1 | reaction_dynamics | pre_stim_quiescence | broad_named_anatomy | NYU-12 | recording_bidirectionality | 0.004 | 0.008 | 0.645 | 0.571 | 2/4 |
| 1 | shared_family | choice | fiber_tracts | CSH_ZAD_019 | recording_bidirectionality | 0.199 | 0.221 | 0.558 | 0.614 | 1/4 |
| 1 | derived_targets | prior_engaged | broad_named_anatomy | MFD_06 | recording_bidirectionality | 0.022 | 0.041 | 0.550 | 0.583 | 1/4 |
| 1 | shared_family | feedback | broad_named_anatomy | SWC_043 | recording_bidirectionality | 0.003 | 0.007 | 0.554 | 0.559 | 1/4 |
| 1 | projected_support80_counts | stimulus_side | broad_named_anatomy | CSHL045 | recording_bidirectionality | 0.024 | 0.031 | 0.566 | 0.574 | 0/4 |
| 1 | projected_support80_counts | prior_side | broad_named_anatomy | CSHL045 | recording_bidirectionality | 0.012 | 0.019 | 0.567 | 0.565 | 0/4 |
| 2 | wheel_targets | wheel_active | broad_named_anatomy | KS014 | shuffle, total_baseline | -0.002 | -0.002 | 0.587 | 0.598 | 3/4 |
| 2 | reaction_dynamics | post_stim_speedup | broad_named_anatomy | KS014 | shuffle, total_baseline | -0.004 | -0.002 | 0.608 | 0.584 | 3/4 |
| 2 | derived_targets | response_latency | broad_named_anatomy | KS014 | shuffle, total_baseline | -0.004 | -0.005 | 0.714 | 0.745 | 3/4 |
| 2 | wheel_targets | wheel_displacement | broad_named_anatomy | KS014 | shuffle, total_baseline | -0.008 | -0.009 | 0.556 | 0.593 | 3/4 |
| 2 | derived_targets | prior_engaged | fiber_tracts | KS014 | target1, recording_bidirectionality | 0.263 | 0.220 | 0.850 | 0.473 | 2/4 |

## Redesign Rule

Do not run GPU training until a prospectively defined target/control produces same-recording bidirectional support, not just global centered deltas. The next target should be designed around within-recording target0+target1 evidence and must pass the unchanged local true-vs-shuffle, total-baseline, global target, and bidirectional-recording gate before training.
