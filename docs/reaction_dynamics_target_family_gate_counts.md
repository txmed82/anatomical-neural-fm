# Reaction-Dynamics Target Family Gate

No-spend audit for wheel-derived reaction dynamics around stimulus onset, using the same shared-family model-free promotion gate.

- rows: `84`
- candidates: `0`
- positive centered-delta rows: `39`
- max bidirectional recordings: `1`
- max bidirectional recording fraction: `0.250`
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
| pre_stim_quiescence | fiber_tracts | KS014 | reject: target1 | +0.029 | +0.016 | 0.750 | 0.330 | 1/4 |
| post_stim_speedup | broad_named_anatomy | MFD_06 | reject: shuffle | -0.001 | -0.005 | 0.451 | 0.616 | 1/4 |
| post_stim_speedup | broad_named_anatomy | KS014 | reject: shuffle | -0.004 | -0.002 | 0.426 | 0.695 | 1/4 |
| wheel_reaction_latency | thalamic | MFD_06 | reject: target1 | +0.378 | +0.524 | 1.000 | 0.000 | 0/4 |
| post_stim_speedup | thalamic | NYU-12 | reject: target1 | +0.195 | +0.251 | 0.740 | 0.260 | 0/4 |
| wheel_reaction_latency | thalamic | KS014 | reject: target1 | +0.178 | +0.381 | 0.668 | 0.332 | 0/4 |
| post_stim_speedup | thalamic | KS014 | reject: target1 | +0.145 | +0.031 | 0.991 | 0.012 | 0/4 |
| wheel_reaction_latency | hippocampal_formation | SWC_038 | reject: target1 | +0.139 | +0.171 | 1.000 | 0.000 | 0/4 |
| wheel_reaction_latency | thalamic | NYU-12 | reject: target1 | +0.125 | +0.299 | 0.722 | 0.278 | 0/4 |
| pre_stim_quiescence | thalamic | SWC_038 | reject: target0 | +0.119 | +0.118 | 0.007 | 0.988 | 0/4 |
| pre_stim_quiescence | hippocampal_formation | MFD_06 | reject: target0 | +0.106 | +0.148 | 0.394 | 0.669 | 0/4 |
| pre_stim_quiescence | thalamic | SWC_043 | reject: target0 | +0.079 | +0.098 | 0.247 | 0.754 | 0/4 |
| wheel_reaction_latency | fiber_tracts | KS014 | reject: target0 | +0.076 | +0.186 | 0.338 | 0.662 | 0/4 |
| pre_stim_quiescence | broad_named_anatomy | MFD_06 | reject: target0 | +0.053 | +0.067 | 0.341 | 0.719 | 0/4 |

## Decision

A reaction-dynamics target is only a training trigger if it passes the same local gate as prior audits: nonnegative true-vs-shuffle and true-vs-total deltas, both global target classes >=0.55, and at least 3/4 same-recording bidirectional support.
