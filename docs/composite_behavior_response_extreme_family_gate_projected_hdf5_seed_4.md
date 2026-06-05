# Composite Behavior Target Family Gate

No-spend bounded screen over prospective composite behavior targets. Targets combine low contrast, prior context, previous-trial outcome, correctness, block-switch context, and response-speed labels under the unchanged shared-family model-free promotion gate.

- rows: `16`
- candidates: `4`
- positive centered-delta rows: `11`
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
| post_error_response_extreme_25_75_le_1 | 8 | 2 | 6 | 1.000 |
| post_error_response_extreme_33_67_le_1 | 8 | 2 | 5 | 1.000 |

## Top Rows

| target | family | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs |
|---|---|---|---|---:|---:|---:|---:|---:|
| post_error_response_extreme_33_67_le_1 | broad_named_anatomy | NR_0019 | candidate | +0.005 | +0.004 | 0.667 | 0.667 | 4/4 |
| post_error_response_extreme_25_75_le_1 | broad_named_anatomy | NR_0019 | candidate | +0.005 | +0.004 | 0.727 | 0.693 | 4/4 |
| post_error_response_extreme_33_67_le_1 | broad_named_anatomy | CSHL045 | candidate | +0.028 | +0.025 | 0.691 | 0.751 | 3/4 |
| post_error_response_extreme_25_75_le_1 | broad_named_anatomy | CSHL045 | candidate | +0.024 | +0.037 | 0.681 | 0.746 | 3/4 |
| post_error_response_extreme_25_75_le_1 | broad_named_anatomy | KS014 | reject: total baseline | +0.000 | -0.002 | 0.777 | 0.819 | 3/4 |
| post_error_response_extreme_33_67_le_1 | broad_named_anatomy | KS014 | reject: shuffle | -0.000 | -0.003 | 0.762 | 0.795 | 3/4 |
| post_error_response_extreme_25_75_le_1 | broad_named_anatomy | CSH_ZAD_019 | reject: recording bidirectionality | +0.001 | +0.005 | 0.578 | 0.578 | 2/4 |
| post_error_response_extreme_33_67_le_1 | broad_named_anatomy | SWC_038 | reject: shuffle | -0.008 | -0.007 | 0.625 | 0.580 | 2/4 |
| post_error_response_extreme_25_75_le_1 | broad_named_anatomy | SWC_038 | reject: shuffle | -0.008 | -0.008 | 0.603 | 0.588 | 2/4 |
| post_error_response_extreme_33_67_le_1 | broad_named_anatomy | NYU-12 | reject: total baseline | +0.009 | -0.014 | 0.483 | 0.466 | 1/4 |
| post_error_response_extreme_33_67_le_1 | broad_named_anatomy | CSH_ZAD_019 | reject: recording bidirectionality | +0.001 | +0.004 | 0.566 | 0.584 | 1/4 |
| post_error_response_extreme_25_75_le_1 | broad_named_anatomy | MFD_06 | reject: target0 | +0.056 | +0.041 | 0.390 | 0.500 | 0/4 |
| post_error_response_extreme_33_67_le_1 | broad_named_anatomy | MFD_06 | reject: target0 | +0.047 | +0.033 | 0.388 | 0.528 | 0/4 |
| post_error_response_extreme_25_75_le_1 | broad_named_anatomy | NYU-12 | reject: total baseline | +0.008 | -0.015 | 0.451 | 0.429 | 0/4 |
| post_error_response_extreme_33_67_le_1 | broad_named_anatomy | ZFM-01577 | reject: shuffle | -0.022 | -0.080 | 0.413 | 0.421 | 0/3 |
| post_error_response_extreme_25_75_le_1 | broad_named_anatomy | ZFM-01577 | reject: shuffle | -0.025 | -0.103 | 0.380 | 0.435 | 0/3 |

## Decision

Validate composite behavior candidates on the projected manifest and across shuffle seeds before GPU training.
