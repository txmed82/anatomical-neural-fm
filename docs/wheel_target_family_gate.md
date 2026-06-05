# Wheel Target Family Gate

No-spend audit for target definitions derived from cached wheel position, using the same shared-family model-free promotion gate.

- rows: `84`
- candidates: `0`
- positive centered-delta rows: `39`
- max bidirectional recordings: `3`
- max bidirectional recording fraction: `0.750`
- decision: `no_wheel_target_family_candidate`

## Target Balance

| target | trials | eligible recordings | recordings |
|---|---:|---:|---:|
| wheel_active | 16982 | 28 | 28 |
| wheel_displacement | 16967 | 28 | 28 |
| choice_aligned_wheel | 16549 | 23 | 28 |

## Top Rows

| target | family | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs |
|---|---|---|---|---:|---:|---:|---:|---:|
| wheel_active | broad_named_anatomy | KS014 | reject: shuffle | -0.002 | -0.002 | 0.587 | 0.598 | 3/4 |
| wheel_displacement | broad_named_anatomy | KS014 | reject: shuffle | -0.008 | -0.009 | 0.556 | 0.593 | 3/4 |
| choice_aligned_wheel | broad_named_anatomy | SWC_043 | reject: recording bidirectionality | +0.008 | +0.007 | 0.558 | 0.584 | 2/4 |
| wheel_displacement | hippocampal_formation | KS014 | reject: shuffle | -0.019 | -0.009 | 0.788 | 0.370 | 2/4 |
| wheel_displacement | thalamic | MFD_06 | reject: target0 | +0.216 | +0.198 | 0.097 | 0.958 | 1/4 |
| wheel_displacement | thalamic | SWC_038 | reject: target0 | +0.211 | +0.039 | 0.111 | 0.955 | 1/4 |
| choice_aligned_wheel | hippocampal_formation | KS014 | reject: total baseline | +0.200 | -0.023 | 0.357 | 0.795 | 1/4 |
| wheel_active | thalamic | SWC_038 | reject: target0 | +0.191 | +0.229 | 0.109 | 0.954 | 1/4 |
| wheel_active | thalamic | NR_0019 | reject: target1 | +0.023 | +0.100 | 0.771 | 0.327 | 1/4 |
| wheel_displacement | broad_named_anatomy | SWC_043 | reject: target0 | +0.011 | +0.010 | 0.538 | 0.635 | 1/4 |
| wheel_active | broad_named_anatomy | SWC_043 | reject: target0 | +0.011 | +0.011 | 0.539 | 0.622 | 1/4 |
| wheel_active | fiber_tracts | SWC_038 | reject: total baseline | +0.006 | -0.047 | 0.352 | 0.598 | 1/4 |
| wheel_active | broad_named_anatomy | NYU-12 | reject: total baseline | +0.003 | -0.002 | 0.517 | 0.541 | 1/4 |
| wheel_active | hippocampal_formation | KS014 | reject: target1 | +0.002 | +0.016 | 0.785 | 0.355 | 1/4 |

## Decision

A wheel-derived target is only a training trigger if it passes the same local gate as prior audits: nonnegative true-vs-shuffle and true-vs-total deltas, both global target classes >=0.55, and at least 3/4 same-recording bidirectional support.
