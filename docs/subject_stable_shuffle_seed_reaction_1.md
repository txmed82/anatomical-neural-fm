# Reaction-Dynamics Target Family Gate

No-spend audit for wheel-derived reaction dynamics around stimulus onset, using the same shared-family model-free promotion gate.

- rows: `14`
- candidates: `1`
- positive centered-delta rows: `8`
- max bidirectional recordings: `3`
- max bidirectional recording fraction: `0.750`
- decision: `reaction_dynamics_target_family_candidate`

## Target Balance

| target | trials | eligible recordings | recordings |
|---|---:|---:|---:|
| post_stim_speedup | 16754 | 28 | 28 |
| wheel_reaction_latency | 12014 | 28 | 28 |

## Top Rows

| target | family | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs |
|---|---|---|---|---:|---:|---:|---:|---:|
| wheel_reaction_latency | broad_named_anatomy | KS014 | candidate | +0.001 | +0.003 | 0.678 | 0.745 | 3/4 |
| post_stim_speedup | broad_named_anatomy | SWC_043 | reject: target0 | +0.013 | +0.012 | 0.500 | 0.573 | 1/4 |
| wheel_reaction_latency | broad_named_anatomy | NR_0019 | reject: target1 | +0.001 | +0.002 | 0.551 | 0.540 | 1/4 |
| post_stim_speedup | broad_named_anatomy | KS014 | reject: shuffle | -0.002 | -0.002 | 0.539 | 0.481 | 1/4 |
| post_stim_speedup | broad_named_anatomy | SWC_038 | reject: shuffle | -0.003 | -0.003 | 0.541 | 0.502 | 1/4 |
| wheel_reaction_latency | broad_named_anatomy | MFD_06 | reject: shuffle | -0.015 | +0.009 | 0.544 | 0.462 | 1/4 |
| wheel_reaction_latency | broad_named_anatomy | NYU-12 | reject: target0 | +0.006 | +0.004 | 0.478 | 0.383 | 0/4 |
| post_stim_speedup | broad_named_anatomy | NYU-12 | reject: total baseline | +0.005 | -0.001 | 0.453 | 0.575 | 0/4 |
| wheel_reaction_latency | broad_named_anatomy | CSH_ZAD_019 | reject: target0 | +0.003 | +0.000 | 0.405 | 0.493 | 0/4 |
| wheel_reaction_latency | broad_named_anatomy | SWC_043 | reject: target0 | +0.002 | +0.004 | 0.441 | 0.412 | 0/4 |
| post_stim_speedup | broad_named_anatomy | NR_0019 | reject: target0 | +0.000 | +0.000 | 0.480 | 0.486 | 0/4 |
| wheel_reaction_latency | broad_named_anatomy | SWC_038 | reject: shuffle | -0.002 | -0.003 | 0.488 | 0.476 | 0/4 |
| post_stim_speedup | broad_named_anatomy | CSH_ZAD_019 | reject: shuffle | -0.002 | +0.000 | 0.490 | 0.528 | 0/4 |
| post_stim_speedup | broad_named_anatomy | MFD_06 | reject: shuffle | -0.013 | -0.005 | 0.446 | 0.490 | 0/4 |

## Decision

A reaction-dynamics target is only a training trigger if it passes the same local gate as prior audits: nonnegative true-vs-shuffle and true-vs-total deltas, both global target classes >=0.55, and at least 3/4 same-recording bidirectional support.
