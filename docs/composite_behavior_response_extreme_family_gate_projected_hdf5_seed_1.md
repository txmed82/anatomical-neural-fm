# Composite Behavior Target Family Gate

No-spend bounded screen over prospective composite behavior targets. Targets combine low contrast, prior context, previous-trial outcome, correctness, block-switch context, and response-speed labels under the unchanged shared-family model-free promotion gate.

- rows: `16`
- candidates: `3`
- positive centered-delta rows: `8`
- max bidirectional recordings: `4`
- max bidirectional recording fraction: `1.000`
- decision: `composite_behavior_target_family_candidate`
- gpu training ready: `False`

## Target Balance

| target | trials | eligible recordings | recordings |
|---|---:|---:|---:|
| post_error_response_extreme_33_67_le_1 | 2538 | 14 | 31 |
| post_error_response_extreme_25_75_le_1 | 1942 | 7 | 31 |

## Target Summary

| target | rows | candidates | positive centered delta | max bidir frac |
|---|---:|---:|---:|---:|
| post_error_response_extreme_25_75_le_1 | 8 | 2 | 4 | 1.000 |
| post_error_response_extreme_33_67_le_1 | 8 | 1 | 4 | 1.000 |

## Top Rows

| target | family | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs |
|---|---|---|---|---:|---:|---:|---:|---:|
| post_error_response_extreme_33_67_le_1 | broad_named_anatomy | NR_0019 | candidate | +0.004 | +0.004 | 0.640 | 0.684 | 4/4 |
| post_error_response_extreme_25_75_le_1 | broad_named_anatomy | NR_0019 | candidate | +0.003 | +0.004 | 0.716 | 0.739 | 4/4 |
| post_error_response_extreme_25_75_le_1 | broad_named_anatomy | CSHL045 | candidate | +0.035 | +0.037 | 0.616 | 0.703 | 3/4 |
| post_error_response_extreme_25_75_le_1 | broad_named_anatomy | KS014 | reject: shuffle | -0.002 | -0.002 | 0.713 | 0.777 | 3/4 |
| post_error_response_extreme_33_67_le_1 | broad_named_anatomy | KS014 | reject: shuffle | -0.002 | -0.003 | 0.672 | 0.746 | 3/4 |
| post_error_response_extreme_33_67_le_1 | broad_named_anatomy | CSHL045 | reject: recording bidirectionality | +0.034 | +0.025 | 0.591 | 0.696 | 2/4 |
| post_error_response_extreme_33_67_le_1 | broad_named_anatomy | CSH_ZAD_019 | reject: shuffle | -0.000 | +0.004 | 0.536 | 0.614 | 2/4 |
| post_error_response_extreme_25_75_le_1 | broad_named_anatomy | CSH_ZAD_019 | reject: shuffle | -0.003 | +0.005 | 0.523 | 0.617 | 2/4 |
| post_error_response_extreme_33_67_le_1 | broad_named_anatomy | SWC_038 | reject: shuffle | -0.007 | -0.007 | 0.621 | 0.546 | 2/4 |
| post_error_response_extreme_25_75_le_1 | broad_named_anatomy | SWC_038 | reject: shuffle | -0.008 | -0.008 | 0.598 | 0.544 | 2/4 |
| post_error_response_extreme_25_75_le_1 | broad_named_anatomy | ZFM-01577 | reject: shuffle | -0.018 | -0.103 | 0.391 | 0.391 | 1/3 |
| post_error_response_extreme_33_67_le_1 | broad_named_anatomy | ZFM-01577 | reject: shuffle | -0.024 | -0.080 | 0.405 | 0.388 | 1/3 |
| post_error_response_extreme_25_75_le_1 | broad_named_anatomy | MFD_06 | reject: target0 | +0.036 | +0.041 | 0.456 | 0.529 | 0/4 |
| post_error_response_extreme_33_67_le_1 | broad_named_anatomy | MFD_06 | reject: target0 | +0.031 | +0.033 | 0.466 | 0.556 | 0/4 |
| post_error_response_extreme_33_67_le_1 | broad_named_anatomy | NYU-12 | reject: total baseline | +0.008 | -0.014 | 0.441 | 0.458 | 0/4 |
| post_error_response_extreme_25_75_le_1 | broad_named_anatomy | NYU-12 | reject: total baseline | +0.008 | -0.015 | 0.396 | 0.484 | 0/4 |

## Decision

Validate composite behavior candidates on the projected manifest and across shuffle seeds before GPU training.
