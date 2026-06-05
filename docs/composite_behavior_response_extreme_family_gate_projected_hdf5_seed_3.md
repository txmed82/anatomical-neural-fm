# Composite Behavior Target Family Gate

No-spend bounded screen over prospective composite behavior targets. Targets combine low contrast, prior context, previous-trial outcome, correctness, block-switch context, and response-speed labels under the unchanged shared-family model-free promotion gate.

- rows: `16`
- candidates: `4`
- positive centered-delta rows: `10`
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
| post_error_response_extreme_25_75_le_1 | 8 | 2 | 5 | 1.000 |
| post_error_response_extreme_33_67_le_1 | 8 | 2 | 5 | 1.000 |

## Top Rows

| target | family | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs |
|---|---|---|---|---:|---:|---:|---:|---:|
| post_error_response_extreme_33_67_le_1 | broad_named_anatomy | NR_0019 | candidate | +0.008 | +0.004 | 0.693 | 0.737 | 4/4 |
| post_error_response_extreme_25_75_le_1 | broad_named_anatomy | NR_0019 | candidate | +0.006 | +0.004 | 0.750 | 0.807 | 4/4 |
| post_error_response_extreme_25_75_le_1 | broad_named_anatomy | CSHL045 | candidate | +0.058 | +0.037 | 0.739 | 0.804 | 3/4 |
| post_error_response_extreme_33_67_le_1 | broad_named_anatomy | CSHL045 | candidate | +0.045 | +0.025 | 0.713 | 0.790 | 3/4 |
| post_error_response_extreme_25_75_le_1 | broad_named_anatomy | KS014 | reject: shuffle | -0.001 | -0.002 | 0.787 | 0.840 | 3/4 |
| post_error_response_extreme_33_67_le_1 | broad_named_anatomy | KS014 | reject: shuffle | -0.001 | -0.003 | 0.746 | 0.820 | 3/4 |
| post_error_response_extreme_33_67_le_1 | broad_named_anatomy | ZFM-01577 | reject: shuffle | -0.041 | -0.080 | 0.521 | 0.463 | 2/3 |
| post_error_response_extreme_25_75_le_1 | broad_named_anatomy | ZFM-01577 | reject: shuffle | -0.042 | -0.103 | 0.543 | 0.489 | 2/3 |
| post_error_response_extreme_33_67_le_1 | broad_named_anatomy | MFD_06 | reject: target0 | +0.031 | +0.033 | 0.534 | 0.607 | 2/4 |
| post_error_response_extreme_33_67_le_1 | broad_named_anatomy | CSH_ZAD_019 | reject: recording bidirectionality | +0.010 | +0.004 | 0.572 | 0.602 | 2/4 |
| post_error_response_extreme_25_75_le_1 | broad_named_anatomy | CSH_ZAD_019 | reject: recording bidirectionality | +0.010 | +0.005 | 0.570 | 0.602 | 2/4 |
| post_error_response_extreme_33_67_le_1 | broad_named_anatomy | SWC_038 | reject: shuffle | -0.006 | -0.007 | 0.625 | 0.569 | 2/4 |
| post_error_response_extreme_25_75_le_1 | broad_named_anatomy | SWC_038 | reject: shuffle | -0.007 | -0.008 | 0.608 | 0.569 | 2/4 |
| post_error_response_extreme_25_75_le_1 | broad_named_anatomy | MFD_06 | reject: target0 | +0.034 | +0.041 | 0.515 | 0.596 | 1/4 |
| post_error_response_extreme_33_67_le_1 | broad_named_anatomy | NYU-12 | reject: total baseline | +0.010 | -0.014 | 0.525 | 0.525 | 1/4 |
| post_error_response_extreme_25_75_le_1 | broad_named_anatomy | NYU-12 | reject: total baseline | +0.005 | -0.015 | 0.527 | 0.505 | 0/4 |

## Decision

Validate composite behavior candidates on the projected manifest and across shuffle seeds before GPU training.
