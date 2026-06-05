# Reaction-Dynamics Target Family Gate

No-spend audit for wheel-derived reaction dynamics around stimulus onset, using the same shared-family model-free promotion gate.

- rows: `84`
- candidates: `0`
- positive centered-delta rows: `45`
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
| post_stim_speedup | thalamic | NYU-12 | reject: target1 | +0.335 | +0.237 | 0.770 | 0.239 | 0/4 |
| post_stim_speedup | thalamic | MFD_06 | reject: target1 | +0.332 | +0.342 | 0.862 | 0.149 | 0/4 |
| wheel_reaction_latency | thalamic | NYU-12 | reject: target0 | +0.251 | +0.375 | 0.205 | 0.820 | 0/4 |
| pre_stim_quiescence | hippocampal_formation | SWC_043 | reject: target1 | +0.206 | +0.203 | 0.971 | 0.016 | 0/4 |
| post_stim_speedup | hippocampal_formation | KS014 | reject: total baseline | +0.182 | -0.136 | 0.152 | 0.912 | 0/4 |
| post_stim_speedup | thalamic | KS014 | reject: total baseline | +0.139 | -0.089 | 0.995 | 0.003 | 0/4 |
| wheel_reaction_latency | hippocampal_formation | KS014 | reject: target0 | +0.138 | +0.407 | 0.112 | 0.930 | 0/4 |
| wheel_reaction_latency | fiber_tracts | MFD_06 | reject: target1 | +0.135 | +0.276 | 0.934 | 0.040 | 0/4 |
| post_stim_speedup | fiber_tracts | NYU-12 | reject: target1 | +0.134 | +0.056 | 0.590 | 0.518 | 0/4 |
| pre_stim_quiescence | hippocampal_formation | NYU-12 | reject: total baseline | +0.115 | -0.103 | 0.470 | 0.569 | 0/4 |
| wheel_reaction_latency | hippocampal_formation | SWC_043 | reject: target1 | +0.100 | +0.196 | 0.987 | 0.008 | 0/4 |
| post_stim_speedup | fiber_tracts | KS014 | reject: total baseline | +0.097 | -0.205 | 0.606 | 0.477 | 0/4 |
| pre_stim_quiescence | hippocampal_formation | MFD_06 | reject: target0 | +0.088 | +0.146 | 0.379 | 0.687 | 0/4 |
| post_stim_speedup | thalamic | SWC_043 | reject: target1 | +0.083 | +0.085 | 0.787 | 0.238 | 0/4 |

## Decision

A reaction-dynamics target is only a training trigger if it passes the same local gate as prior audits: nonnegative true-vs-shuffle and true-vs-total deltas, both global target classes >=0.55, and at least 3/4 same-recording bidirectional support.
