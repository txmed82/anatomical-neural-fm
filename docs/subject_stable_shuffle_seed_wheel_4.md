# Wheel Target Family Gate

No-spend audit for target definitions derived from cached wheel position, using the same shared-family model-free promotion gate.

- rows: `14`
- candidates: `0`
- positive centered-delta rows: `5`
- max bidirectional recordings: `3`
- max bidirectional recording fraction: `0.750`
- decision: `no_wheel_target_family_candidate`

## Target Balance

| target | trials | eligible recordings | recordings |
|---|---:|---:|---:|
| wheel_active | 16982 | 28 | 28 |
| wheel_displacement | 16967 | 28 | 28 |

## Top Rows

| target | family | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs |
|---|---|---|---|---:|---:|---:|---:|---:|
| wheel_active | broad_named_anatomy | KS014 | reject: shuffle | -0.001 | -0.002 | 0.588 | 0.610 | 3/4 |
| wheel_displacement | broad_named_anatomy | KS014 | reject: shuffle | -0.005 | -0.009 | 0.585 | 0.615 | 3/4 |
| wheel_displacement | broad_named_anatomy | SWC_043 | reject: target0 | +0.014 | +0.010 | 0.527 | 0.627 | 1/4 |
| wheel_active | broad_named_anatomy | NR_0019 | reject: shuffle | -0.000 | +0.000 | 0.495 | 0.563 | 1/4 |
| wheel_displacement | broad_named_anatomy | NR_0019 | reject: shuffle | -0.001 | -0.000 | 0.490 | 0.559 | 1/4 |
| wheel_active | broad_named_anatomy | SWC_038 | reject: shuffle | -0.003 | -0.002 | 0.564 | 0.504 | 1/4 |
| wheel_displacement | broad_named_anatomy | SWC_038 | reject: shuffle | -0.004 | -0.005 | 0.611 | 0.550 | 1/4 |
| wheel_displacement | broad_named_anatomy | MFD_06 | reject: target0 | +0.031 | +0.018 | 0.443 | 0.548 | 0/4 |
| wheel_active | broad_named_anatomy | SWC_043 | reject: target0 | +0.013 | +0.011 | 0.505 | 0.600 | 0/4 |
| wheel_active | broad_named_anatomy | NYU-12 | reject: total baseline | +0.006 | -0.002 | 0.493 | 0.527 | 0/4 |
| wheel_displacement | broad_named_anatomy | NYU-12 | reject: total baseline | +0.005 | -0.002 | 0.549 | 0.498 | 0/4 |
| wheel_active | broad_named_anatomy | CSH_ZAD_019 | reject: shuffle | -0.001 | +0.003 | 0.493 | 0.484 | 0/4 |
| wheel_active | broad_named_anatomy | MFD_06 | reject: shuffle | -0.002 | -0.005 | 0.415 | 0.519 | 0/4 |
| wheel_displacement | broad_named_anatomy | CSH_ZAD_019 | reject: shuffle | -0.003 | -0.004 | 0.480 | 0.477 | 0/4 |

## Decision

A wheel-derived target is only a training trigger if it passes the same local gate as prior audits: nonnegative true-vs-shuffle and true-vs-total deltas, both global target classes >=0.55, and at least 3/4 same-recording bidirectional support.
