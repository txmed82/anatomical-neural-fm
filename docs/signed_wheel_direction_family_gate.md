# Signed Wheel-Direction Family Gate

No-spend audit for post-stimulus signed wheel-direction targets derived from cached wheel position, using the same shared-family model-free promotion gate.

- rows: `70`
- candidates: `0`
- positive centered-delta rows: `31`
- max bidirectional recordings: `2`
- max bidirectional recording fraction: `0.500`
- decision: `no_signed_wheel_direction_family_candidate`

## Target Balance

| target | trials | eligible recordings | recordings |
|---|---:|---:|---:|
| signed_wheel_direction | 16615 | 28 | 28 |

## Top Rows

| target | family | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs |
|---|---|---|---|---:|---:|---:|---:|---:|
| signed_wheel_direction | fiber_tracts | CSH_ZAD_019 | reject: target1 | +0.198 | +0.186 | 0.628 | 0.533 | 2/4 |
| signed_wheel_direction | broad_named_anatomy | SWC_043 | reject: total baseline | +0.009 | -0.142 | 0.612 | 0.541 | 2/4 |
| signed_wheel_direction | brainstem_interbrain | NR_0019 | reject: target1 | +0.119 | +0.174 | 0.756 | 0.397 | 1/4 |
| signed_wheel_direction | basal_ganglia | NR_0019 | reject: target1 | +0.110 | +0.095 | 0.785 | 0.366 | 1/4 |
| signed_wheel_direction | fiber_tracts | KS014 | reject: target0 | +0.054 | +0.186 | 0.450 | 0.620 | 1/4 |
| signed_wheel_direction | brainstem_interbrain | KS014 | reject: target1 | +0.042 | +0.089 | 0.599 | 0.362 | 1/4 |
| signed_wheel_direction | broad_named_anatomy | SWC_038 | reject: shuffle | -0.001 | -0.003 | 0.531 | 0.507 | 1/4 |
| signed_wheel_direction | fiber_tracts | SWC_038 | reject: shuffle | -0.013 | +0.093 | 0.387 | 0.646 | 1/4 |
| signed_wheel_direction | broad_named_anatomy | KS014 | reject: shuffle | -0.013 | +0.136 | 0.485 | 0.472 | 1/4 |
| signed_wheel_direction | basal_ganglia | SWC_043 | reject: shuffle | -0.071 | +0.003 | 0.265 | 0.739 | 1/4 |
| signed_wheel_direction | cortical_visual | CSH_ZAD_019 | reject: target0 | +0.335 | +0.536 | 0.000 | 1.000 | 0/4 |
| signed_wheel_direction | thalamic | MFD_06 | reject: target0 | +0.251 | +0.298 | 0.088 | 0.936 | 0/4 |
| signed_wheel_direction | cortical_retrosplenial | SWC_038 | reject: target1 | +0.241 | +0.382 | 1.000 | 0.000 | 0/4 |
| signed_wheel_direction | basal_ganglia | KS014 | reject: target1 | +0.219 | +0.537 | 1.000 | 0.000 | 0/4 |

## Decision

A wheel-derived target is only a training trigger if it passes the same local gate as prior audits: nonnegative true-vs-shuffle and true-vs-total deltas, both global target classes >=0.55, and at least 3/4 same-recording bidirectional support.
