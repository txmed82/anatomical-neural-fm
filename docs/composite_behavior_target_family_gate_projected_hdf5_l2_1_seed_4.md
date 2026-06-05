# Composite Behavior Target Family Gate

No-spend bounded screen over prospective composite behavior targets. Targets combine low contrast, prior context, previous-trial outcome, correctness, block-switch context, and response-speed labels under the unchanged shared-family model-free promotion gate.

- rows: `8`
- candidates: `1`
- positive centered-delta rows: `5`
- max bidirectional recordings: `4`
- max bidirectional recording fraction: `1.000`
- decision: `composite_behavior_target_family_candidate`
- gpu training ready: `False`

## Target Balance

| target | trials | eligible recordings | recordings |
|---|---:|---:|---:|
| post_error_fast_response_le_1 | 3820 | 28 | 31 |

## Target Summary

| target | rows | candidates | positive centered delta | max bidir frac |
|---|---:|---:|---:|---:|
| post_error_fast_response_le_1 | 8 | 1 | 5 | 1.000 |

## Top Rows

| target | family | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs |
|---|---|---|---|---:|---:|---:|---:|---:|
| post_error_fast_response_le_1 | broad_named_anatomy | NR_0019 | candidate | +0.002 | +0.002 | 0.593 | 0.645 | 4/4 |
| post_error_fast_response_le_1 | broad_named_anatomy | KS014 | reject: shuffle | -0.002 | -0.005 | 0.705 | 0.754 | 3/4 |
| post_error_fast_response_le_1 | broad_named_anatomy | CSHL045 | reject: recording bidirectionality | +0.043 | +0.039 | 0.621 | 0.713 | 2/4 |
| post_error_fast_response_le_1 | broad_named_anatomy | CSH_ZAD_019 | reject: target0 | +0.003 | +0.004 | 0.528 | 0.571 | 2/4 |
| post_error_fast_response_le_1 | broad_named_anatomy | SWC_038 | reject: shuffle | -0.006 | -0.007 | 0.621 | 0.569 | 2/4 |
| post_error_fast_response_le_1 | broad_named_anatomy | NYU-12 | reject: total baseline | +0.006 | -0.008 | 0.511 | 0.438 | 1/4 |
| post_error_fast_response_le_1 | broad_named_anatomy | MFD_06 | reject: target0 | +0.032 | +0.019 | 0.474 | 0.549 | 0/4 |
| post_error_fast_response_le_1 | broad_named_anatomy | ZFM-01577 | reject: shuffle | -0.014 | -0.051 | 0.431 | 0.492 | 0/3 |

## Decision

Validate composite behavior candidates on the projected manifest and across shuffle seeds before GPU training.
