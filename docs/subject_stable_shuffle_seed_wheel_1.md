# Wheel Target Family Gate

No-spend audit for target definitions derived from cached wheel position, using the same shared-family model-free promotion gate.

- rows: `14`
- candidates: `0`
- positive centered-delta rows: `7`
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
| wheel_displacement | broad_named_anatomy | NR_0019 | reject: total baseline | +0.002 | -0.000 | 0.541 | 0.577 | 3/4 |
| wheel_displacement | broad_named_anatomy | KS014 | reject: shuffle | -0.006 | -0.009 | 0.545 | 0.588 | 3/4 |
| wheel_displacement | broad_named_anatomy | SWC_043 | reject: target0 | +0.011 | +0.010 | 0.522 | 0.602 | 1/4 |
| wheel_active | broad_named_anatomy | SWC_043 | reject: target0 | +0.010 | +0.011 | 0.510 | 0.581 | 1/4 |
| wheel_active | broad_named_anatomy | KS014 | reject: shuffle | -0.001 | -0.002 | 0.539 | 0.575 | 1/4 |
| wheel_active | broad_named_anatomy | SWC_038 | reject: shuffle | -0.002 | -0.002 | 0.545 | 0.512 | 1/4 |
| wheel_displacement | broad_named_anatomy | MFD_06 | reject: target0 | +0.020 | +0.018 | 0.456 | 0.501 | 0/4 |
| wheel_active | broad_named_anatomy | NYU-12 | reject: total baseline | +0.005 | -0.002 | 0.458 | 0.552 | 0/4 |
| wheel_displacement | broad_named_anatomy | NYU-12 | reject: total baseline | +0.003 | -0.002 | 0.524 | 0.503 | 0/4 |
| wheel_active | broad_named_anatomy | NR_0019 | reject: target0 | +0.000 | +0.000 | 0.491 | 0.525 | 0/4 |
| wheel_active | broad_named_anatomy | CSH_ZAD_019 | reject: shuffle | -0.001 | +0.003 | 0.475 | 0.528 | 0/4 |
| wheel_displacement | broad_named_anatomy | CSH_ZAD_019 | reject: shuffle | -0.002 | -0.004 | 0.459 | 0.532 | 0/4 |
| wheel_displacement | broad_named_anatomy | SWC_038 | reject: shuffle | -0.005 | -0.005 | 0.580 | 0.499 | 0/4 |
| wheel_active | broad_named_anatomy | MFD_06 | reject: shuffle | -0.010 | -0.005 | 0.440 | 0.492 | 0/4 |

## Decision

A wheel-derived target is only a training trigger if it passes the same local gate as prior audits: nonnegative true-vs-shuffle and true-vs-total deltas, both global target classes >=0.55, and at least 3/4 same-recording bidirectional support.
