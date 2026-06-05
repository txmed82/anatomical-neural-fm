# Contextual Target Family Gate

No-spend audit for trial-context target definitions that use sequence state rather than the direct cached task labels.

- rows: `84`
- candidates: `0`
- positive centered-delta rows: `40`
- max bidirectional recordings: `2`
- max bidirectional recording fraction: `0.500`
- decision: `no_contextual_target_family_candidate`

## Target Balance

| target | trials | eligible recordings | recordings |
|---|---:|---:|---:|
| post_error | 17854 | 28 | 28 |
| prior_block_switch | 7280 | 23 | 28 |
| prior_block_late | 4798 | 28 | 28 |

## Top Rows

| target | family | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs |
|---|---|---|---|---:|---:|---:|---:|---:|
| post_error | fiber_tracts | SWC_043 | reject: shuffle | -0.031 | -0.050 | 0.527 | 0.472 | 2/4 |
| post_error | fiber_tracts | NYU-12 | reject: target0 | +0.083 | +0.130 | 0.411 | 0.679 | 1/4 |
| prior_block_late | thalamic | SWC_038 | reject: target0 | +0.022 | +0.047 | 0.094 | 0.943 | 1/4 |
| post_error | broad_named_anatomy | MFD_06 | reject: target0 | +0.013 | +0.009 | 0.476 | 0.500 | 1/4 |
| post_error | hippocampal_formation | NYU-12 | reject: target0 | +0.003 | +0.119 | 0.426 | 0.651 | 1/4 |
| post_error | broad_named_anatomy | SWC_038 | reject: total baseline | +0.002 | -0.069 | 0.502 | 0.536 | 1/4 |
| post_error | broad_named_anatomy | SWC_043 | reject: total baseline | +0.000 | -0.074 | 0.501 | 0.547 | 1/4 |
| post_error | thalamic | MFD_06 | reject: shuffle | -0.001 | +0.139 | 0.940 | 0.149 | 1/4 |
| prior_block_late | broad_named_anatomy | SWC_043 | reject: shuffle | -0.004 | -0.008 | 0.471 | 0.549 | 1/4 |
| prior_block_late | fiber_tracts | SWC_043 | reject: shuffle | -0.009 | +0.023 | 0.549 | 0.491 | 1/4 |
| prior_block_late | thalamic | MFD_06 | reject: target0 | +0.357 | +0.347 | 0.086 | 0.923 | 0/4 |
| post_error | thalamic | KS014 | reject: target1 | +0.090 | +0.229 | 0.860 | 0.097 | 0/4 |
| prior_block_switch | hippocampal_formation | MFD_06 | reject: target1 | +0.089 | +0.034 | 0.717 | 0.342 | 0/4 |
| post_error | hippocampal_formation | SWC_038 | reject: target1 | +0.079 | +0.070 | 0.934 | 0.109 | 0/4 |

## Decision

A contextual target is only a training trigger if it passes the same local gate as prior audits: nonnegative true-vs-shuffle and true-vs-total deltas, both global target classes >=0.55, and at least 3/4 same-recording bidirectional support.
