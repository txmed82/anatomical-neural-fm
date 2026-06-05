# Reaction-Dynamics Target Family Gate

No-spend audit for wheel-derived reaction dynamics around stimulus onset, using the same shared-family model-free promotion gate.

- rows: `14`
- candidates: `0`
- positive centered-delta rows: `4`
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
| wheel_reaction_latency | broad_named_anatomy | KS014 | reject: shuffle | -0.000 | +0.003 | 0.664 | 0.716 | 3/4 |
| post_stim_speedup | broad_named_anatomy | SWC_043 | reject: target0 | +0.014 | +0.012 | 0.518 | 0.621 | 2/4 |
| wheel_reaction_latency | broad_named_anatomy | NR_0019 | reject: target1 | +0.002 | +0.002 | 0.551 | 0.537 | 1/4 |
| post_stim_speedup | broad_named_anatomy | CSH_ZAD_019 | reject: shuffle | -0.000 | +0.000 | 0.519 | 0.511 | 1/4 |
| post_stim_speedup | broad_named_anatomy | KS014 | reject: shuffle | -0.001 | -0.002 | 0.599 | 0.539 | 1/4 |
| post_stim_speedup | broad_named_anatomy | SWC_038 | reject: shuffle | -0.003 | -0.003 | 0.562 | 0.503 | 1/4 |
| wheel_reaction_latency | broad_named_anatomy | NYU-12 | reject: target0 | +0.008 | +0.004 | 0.485 | 0.422 | 0/4 |
| wheel_reaction_latency | broad_named_anatomy | SWC_043 | reject: target0 | +0.001 | +0.004 | 0.446 | 0.404 | 0/4 |
| post_stim_speedup | broad_named_anatomy | NR_0019 | reject: shuffle | -0.001 | +0.000 | 0.479 | 0.527 | 0/4 |
| post_stim_speedup | broad_named_anatomy | NYU-12 | reject: shuffle | -0.002 | -0.001 | 0.493 | 0.491 | 0/4 |
| post_stim_speedup | broad_named_anatomy | MFD_06 | reject: shuffle | -0.002 | -0.005 | 0.439 | 0.510 | 0/4 |
| wheel_reaction_latency | broad_named_anatomy | CSH_ZAD_019 | reject: shuffle | -0.003 | +0.000 | 0.399 | 0.483 | 0/4 |
| wheel_reaction_latency | broad_named_anatomy | SWC_038 | reject: shuffle | -0.004 | -0.003 | 0.490 | 0.473 | 0/4 |
| wheel_reaction_latency | broad_named_anatomy | MFD_06 | reject: shuffle | -0.006 | +0.009 | 0.510 | 0.463 | 0/4 |

## Decision

A reaction-dynamics target is only a training trigger if it passes the same local gate as prior audits: nonnegative true-vs-shuffle and true-vs-total deltas, both global target classes >=0.55, and at least 3/4 same-recording bidirectional support.
