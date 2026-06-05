# Reaction-Dynamics Target Family Gate

No-spend audit for wheel-derived reaction dynamics around stimulus onset, using the same shared-family model-free promotion gate.

- rows: `84`
- candidates: `0`
- positive centered-delta rows: `46`
- max bidirectional recordings: `0`
- max bidirectional recording fraction: `0.000`
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
| post_stim_speedup | thalamic | SWC_038 | reject: target1 | +0.243 | +0.034 | 0.815 | 0.185 | 0/4 |
| pre_stim_quiescence | thalamic | NYU-12 | reject: target0 | +0.207 | +0.080 | 0.260 | 0.740 | 0/4 |
| wheel_reaction_latency | hippocampal_formation | SWC_038 | reject: target1 | +0.205 | +0.312 | 0.887 | 0.059 | 0/4 |
| pre_stim_quiescence | thalamic | SWC_043 | reject: target0 | +0.190 | +0.193 | 0.257 | 0.743 | 0/4 |
| wheel_reaction_latency | hippocampal_formation | KS014 | reject: target1 | +0.154 | +0.438 | 1.000 | 0.000 | 0/4 |
| post_stim_speedup | fiber_tracts | NYU-12 | reject: target0 | +0.145 | +0.064 | 0.116 | 0.934 | 0/4 |
| pre_stim_quiescence | thalamic | MFD_06 | reject: target0 | +0.138 | +0.155 | 0.152 | 0.848 | 0/4 |
| wheel_reaction_latency | thalamic | MFD_06 | reject: target1 | +0.137 | +0.211 | 0.928 | 0.072 | 0/4 |
| pre_stim_quiescence | hippocampal_formation | NYU-12 | reject: total baseline | +0.099 | -0.106 | 0.457 | 0.543 | 0/4 |
| post_stim_speedup | thalamic | NYU-12 | reject: target1 | +0.091 | +0.047 | 0.740 | 0.260 | 0/4 |
| pre_stim_quiescence | fiber_tracts | MFD_06 | reject: target1 | +0.089 | +0.155 | 0.701 | 0.293 | 0/4 |
| post_stim_speedup | broad_named_anatomy | NYU-12 | reject: total baseline | +0.068 | -0.041 | 0.308 | 0.712 | 0/4 |
| pre_stim_quiescence | hippocampal_formation | MFD_06 | reject: target1 | +0.059 | +0.121 | 0.606 | 0.435 | 0/4 |
| pre_stim_quiescence | fiber_tracts | NYU-12 | reject: total baseline | +0.058 | -0.054 | 0.941 | 0.080 | 0/4 |

## Decision

A reaction-dynamics target is only a training trigger if it passes the same local gate as prior audits: nonnegative true-vs-shuffle and true-vs-total deltas, both global target classes >=0.55, and at least 3/4 same-recording bidirectional support.
