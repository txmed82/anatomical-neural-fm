# Wheel Target Family Gate

No-spend audit for target definitions derived from cached wheel position, using the same shared-family model-free promotion gate.

- rows: `14`
- candidates: `0`
- positive centered-delta rows: `8`
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
| wheel_active | broad_named_anatomy | KS014 | reject: shuffle | -0.001 | -0.002 | 0.586 | 0.612 | 3/4 |
| wheel_displacement | broad_named_anatomy | KS014 | reject: shuffle | -0.004 | -0.009 | 0.578 | 0.647 | 3/4 |
| wheel_displacement | broad_named_anatomy | SWC_043 | reject: target0 | +0.014 | +0.010 | 0.544 | 0.657 | 2/4 |
| wheel_displacement | broad_named_anatomy | MFD_06 | reject: target0 | +0.025 | +0.018 | 0.509 | 0.583 | 1/4 |
| wheel_displacement | broad_named_anatomy | NR_0019 | reject: total baseline | +0.002 | -0.000 | 0.522 | 0.593 | 1/4 |
| wheel_active | broad_named_anatomy | NR_0019 | reject: target0 | +0.001 | +0.000 | 0.529 | 0.604 | 1/4 |
| wheel_active | broad_named_anatomy | MFD_06 | reject: total baseline | +0.000 | -0.005 | 0.490 | 0.557 | 1/4 |
| wheel_active | broad_named_anatomy | SWC_038 | reject: shuffle | -0.002 | -0.002 | 0.577 | 0.523 | 1/4 |
| wheel_displacement | broad_named_anatomy | SWC_038 | reject: shuffle | -0.005 | -0.005 | 0.587 | 0.544 | 1/4 |
| wheel_active | broad_named_anatomy | SWC_043 | reject: target0 | +0.012 | +0.011 | 0.505 | 0.623 | 0/4 |
| wheel_active | broad_named_anatomy | CSH_ZAD_019 | reject: target0 | +0.003 | +0.003 | 0.532 | 0.502 | 0/4 |
| wheel_active | broad_named_anatomy | NYU-12 | reject: total baseline | +0.002 | -0.002 | 0.510 | 0.518 | 0/4 |
| wheel_displacement | broad_named_anatomy | NYU-12 | reject: shuffle | -0.001 | -0.002 | 0.547 | 0.530 | 0/4 |
| wheel_displacement | broad_named_anatomy | CSH_ZAD_019 | reject: shuffle | -0.002 | -0.004 | 0.501 | 0.534 | 0/4 |

## Decision

A wheel-derived target is only a training trigger if it passes the same local gate as prior audits: nonnegative true-vs-shuffle and true-vs-total deltas, both global target classes >=0.55, and at least 3/4 same-recording bidirectional support.
