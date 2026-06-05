# Signed Wheel-Direction Family Gate

No-spend audit for post-stimulus signed wheel-direction targets derived from cached wheel position, using the same shared-family model-free promotion gate.

- rows: `80`
- candidates: `0`
- positive centered-delta rows: `34`
- max bidirectional recordings: `2`
- max bidirectional recording fraction: `0.500`
- decision: `no_signed_wheel_direction_family_candidate`

## Target Balance

| target | trials | eligible recordings | recordings |
|---|---:|---:|---:|
| signed_wheel_direction | 19287 | 31 | 31 |

## Top Rows

| target | family | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs |
|---|---|---|---|---:|---:|---:|---:|---:|
| signed_wheel_direction | basal_ganglia | CSHL045 | reject: shuffle | -0.075 | +0.138 | 0.204 | 0.860 | 2/4 |
| signed_wheel_direction | midbrain | ZFM-01577 | reject: shuffle | -0.219 | +0.058 | 0.121 | 0.903 | 1/3 |
| signed_wheel_direction | brainstem_interbrain | NR_0019 | reject: target1 | +0.153 | +0.197 | 0.752 | 0.400 | 1/4 |
| signed_wheel_direction | brainstem_interbrain | KS014 | reject: target1 | +0.051 | +0.088 | 0.599 | 0.362 | 1/4 |
| signed_wheel_direction | fiber_tracts | KS014 | reject: target0 | +0.032 | +0.176 | 0.456 | 0.618 | 1/4 |
| signed_wheel_direction | broad_named_anatomy | SWC_038 | reject: shuffle | -0.001 | -0.003 | 0.529 | 0.497 | 1/4 |
| signed_wheel_direction | broad_named_anatomy | KS014 | reject: shuffle | -0.013 | +0.136 | 0.453 | 0.511 | 1/4 |
| signed_wheel_direction | cortical_retrosplenial | SWC_038 | reject: target1 | +0.297 | +0.433 | 1.000 | 0.000 | 0/4 |
| signed_wheel_direction | fiber_tracts | CSHL045 | reject: target0 | +0.205 | +0.309 | 0.156 | 0.830 | 0/4 |
| signed_wheel_direction | basal_ganglia | NR_0019 | reject: target1 | +0.118 | +0.098 | 0.771 | 0.331 | 0/4 |
| signed_wheel_direction | brainstem_interbrain | CSHL045 | reject: target1 | +0.115 | +0.182 | 0.611 | 0.446 | 0/4 |
| signed_wheel_direction | fiber_tracts | MFD_06 | reject: target0 | +0.110 | +0.203 | 0.186 | 0.799 | 0/4 |
| signed_wheel_direction | cortical_visual | MFD_06 | reject: target0 | +0.106 | +0.113 | 0.260 | 0.809 | 0/4 |
| signed_wheel_direction | thalamic | NYU-12 | reject: target0 | +0.102 | +0.276 | 0.142 | 0.874 | 0/4 |

## Decision

A wheel-derived target is only a training trigger if it passes the same local gate as prior audits: nonnegative true-vs-shuffle and true-vs-total deltas, both global target classes >=0.55, and at least 3/4 same-recording bidirectional support.
