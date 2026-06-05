# Reaction-Dynamics Target Family Gate

No-spend audit for wheel-derived reaction dynamics around stimulus onset, using the same shared-family model-free promotion gate.

- rows: `84`
- candidates: `0`
- positive centered-delta rows: `39`
- max bidirectional recordings: `3`
- max bidirectional recording fraction: `0.750`
- decision: `no_reaction_dynamics_target_family_candidate`

## Target Balance

| target | trials | eligible recordings | recordings |
|---|---:|---:|---:|
| pre_stim_quiescence | 16910 | 28 | 28 |
| post_stim_speedup | 16754 | 28 | 28 |
| wheel_reaction_latency | 12014 | 28 | 28 |

## Top Rows

| target | family | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs |
|---|---|---|---|---:|---:|---:|---:|---:|
| wheel_reaction_latency | broad_named_anatomy | KS014 | reject: shuffle | -0.001 | +0.003 | 0.667 | 0.715 | 3/4 |
| post_stim_speedup | broad_named_anatomy | KS014 | reject: shuffle | -0.004 | -0.002 | 0.608 | 0.584 | 3/4 |
| pre_stim_quiescence | hippocampal_formation | NYU-12 | reject: target1 | +0.010 | +0.015 | 0.719 | 0.476 | 2/4 |
| wheel_reaction_latency | hippocampal_formation | KS014 | reject: target0 | +0.007 | +0.141 | 0.376 | 0.824 | 2/4 |
| pre_stim_quiescence | broad_named_anatomy | NYU-12 | reject: recording bidirectionality | +0.004 | +0.008 | 0.645 | 0.571 | 2/4 |
| post_stim_speedup | thalamic | SWC_038 | reject: target1 | +0.202 | +0.030 | 0.924 | 0.143 | 1/4 |
| pre_stim_quiescence | hippocampal_formation | MFD_06 | reject: target1 | +0.106 | +0.148 | 0.667 | 0.445 | 1/4 |
| pre_stim_quiescence | fiber_tracts | KS014 | reject: target0 | +0.029 | +0.016 | 0.378 | 0.674 | 1/4 |
| wheel_reaction_latency | hippocampal_formation | MFD_06 | reject: target0 | +0.014 | +0.103 | 0.367 | 0.616 | 1/4 |
| post_stim_speedup | broad_named_anatomy | SWC_043 | reject: target0 | +0.011 | +0.012 | 0.520 | 0.603 | 1/4 |
| post_stim_speedup | broad_named_anatomy | NYU-12 | reject: total baseline | +0.003 | -0.001 | 0.479 | 0.576 | 1/4 |
| post_stim_speedup | fiber_tracts | SWC_038 | reject: total baseline | +0.003 | -0.070 | 0.342 | 0.611 | 1/4 |
| wheel_reaction_latency | broad_named_anatomy | NR_0019 | reject: target0 | +0.001 | +0.002 | 0.550 | 0.538 | 1/4 |
| post_stim_speedup | broad_named_anatomy | MFD_06 | reject: shuffle | -0.001 | -0.005 | 0.464 | 0.566 | 1/4 |

## Decision

A reaction-dynamics target is only a training trigger if it passes the same local gate as prior audits: nonnegative true-vs-shuffle and true-vs-total deltas, both global target classes >=0.55, and at least 3/4 same-recording bidirectional support.
