# Reaction-Dynamics Target Family Gate

No-spend audit for wheel-derived reaction dynamics around stimulus onset, using the same shared-family model-free promotion gate.

- rows: `14`
- candidates: `0`
- positive centered-delta rows: `6`
- max bidirectional recordings: `3`
- max bidirectional recording fraction: `0.750`
- decision: `no_reaction_dynamics_target_family_candidate`

## Target Balance

| target | trials | eligible recordings | recordings |
|---|---:|---:|---:|
| post_stim_speedup | 16754 | 28 | 28 |
| wheel_reaction_latency | 12014 | 28 | 28 |

## Top Rows

| target | family | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs |
|---|---|---|---|---:|---:|---:|---:|---:|
| post_stim_speedup | broad_named_anatomy | KS014 | reject: shuffle | -0.001 | -0.002 | 0.607 | 0.618 | 3/4 |
| wheel_reaction_latency | broad_named_anatomy | KS014 | reject: shuffle | -0.001 | +0.003 | 0.681 | 0.684 | 3/4 |
| wheel_reaction_latency | broad_named_anatomy | NR_0019 | reject: target1 | +0.001 | +0.002 | 0.555 | 0.541 | 1/4 |
| post_stim_speedup | broad_named_anatomy | CSH_ZAD_019 | reject: shuffle | -0.002 | +0.000 | 0.503 | 0.510 | 1/4 |
| post_stim_speedup | broad_named_anatomy | SWC_038 | reject: shuffle | -0.003 | -0.003 | 0.564 | 0.502 | 1/4 |
| wheel_reaction_latency | broad_named_anatomy | MFD_06 | reject: shuffle | -0.014 | +0.009 | 0.600 | 0.440 | 1/4 |
| post_stim_speedup | broad_named_anatomy | SWC_043 | reject: target0 | +0.015 | +0.012 | 0.493 | 0.589 | 0/4 |
| post_stim_speedup | broad_named_anatomy | NYU-12 | reject: total baseline | +0.005 | -0.001 | 0.470 | 0.555 | 0/4 |
| wheel_reaction_latency | broad_named_anatomy | NYU-12 | reject: target0 | +0.005 | +0.004 | 0.489 | 0.377 | 0/4 |
| wheel_reaction_latency | broad_named_anatomy | CSH_ZAD_019 | reject: target0 | +0.002 | +0.000 | 0.405 | 0.494 | 0/4 |
| wheel_reaction_latency | broad_named_anatomy | SWC_043 | reject: target0 | +0.001 | +0.004 | 0.442 | 0.409 | 0/4 |
| post_stim_speedup | broad_named_anatomy | NR_0019 | reject: shuffle | -0.000 | +0.000 | 0.468 | 0.562 | 0/4 |
| wheel_reaction_latency | broad_named_anatomy | SWC_038 | reject: shuffle | -0.002 | -0.003 | 0.488 | 0.476 | 0/4 |
| post_stim_speedup | broad_named_anatomy | MFD_06 | reject: shuffle | -0.004 | -0.005 | 0.409 | 0.515 | 0/4 |

## Decision

A reaction-dynamics target is only a training trigger if it passes the same local gate as prior audits: nonnegative true-vs-shuffle and true-vs-total deltas, both global target classes >=0.55, and at least 3/4 same-recording bidirectional support.
