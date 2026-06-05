# Composite Behavior Target Family Gate

No-spend bounded screen over prospective composite behavior targets. Targets combine low contrast, prior context, previous-trial outcome, correctness, block-switch context, and response-speed labels under the unchanged shared-family model-free promotion gate.

- rows: `16`
- candidates: `3`
- positive centered-delta rows: `6`
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
| post_error_response_extreme_25_75_le_1 | 8 | 1 | 3 | 0.750 |
| post_error_response_extreme_33_67_le_1 | 8 | 2 | 3 | 1.000 |

## Top Rows

| target | family | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs |
|---|---|---|---|---:|---:|---:|---:|---:|
| post_error_response_extreme_33_67_le_1 | broad_named_anatomy | NR_0019 | candidate | +0.003 | +0.004 | 0.649 | 0.675 | 4/4 |
| post_error_response_extreme_25_75_le_1 | broad_named_anatomy | CSHL045 | candidate | +0.070 | +0.037 | 0.754 | 0.848 | 3/4 |
| post_error_response_extreme_33_67_le_1 | broad_named_anatomy | CSHL045 | candidate | +0.057 | +0.025 | 0.696 | 0.818 | 3/4 |
| post_error_response_extreme_33_67_le_1 | broad_named_anatomy | KS014 | reject: shuffle | -0.001 | -0.003 | 0.738 | 0.762 | 3/4 |
| post_error_response_extreme_25_75_le_1 | broad_named_anatomy | KS014 | reject: shuffle | -0.001 | -0.002 | 0.777 | 0.819 | 3/4 |
| post_error_response_extreme_25_75_le_1 | broad_named_anatomy | ZFM-01577 | reject: shuffle | -0.026 | -0.103 | 0.489 | 0.457 | 2/3 |
| post_error_response_extreme_25_75_le_1 | broad_named_anatomy | NR_0019 | reject: recording bidirectionality | +0.002 | +0.004 | 0.682 | 0.716 | 2/4 |
| post_error_response_extreme_25_75_le_1 | broad_named_anatomy | CSH_ZAD_019 | reject: shuffle | -0.001 | +0.005 | 0.570 | 0.508 | 2/4 |
| post_error_response_extreme_33_67_le_1 | broad_named_anatomy | ZFM-01577 | reject: shuffle | -0.021 | -0.080 | 0.479 | 0.446 | 1/3 |
| post_error_response_extreme_33_67_le_1 | broad_named_anatomy | MFD_06 | reject: target0 | +0.039 | +0.033 | 0.478 | 0.534 | 1/4 |
| post_error_response_extreme_33_67_le_1 | broad_named_anatomy | CSH_ZAD_019 | reject: shuffle | -0.001 | +0.004 | 0.548 | 0.506 | 1/4 |
| post_error_response_extreme_33_67_le_1 | broad_named_anatomy | SWC_038 | reject: shuffle | -0.009 | -0.007 | 0.613 | 0.554 | 1/4 |
| post_error_response_extreme_25_75_le_1 | broad_named_anatomy | SWC_038 | reject: shuffle | -0.010 | -0.008 | 0.598 | 0.554 | 1/4 |
| post_error_response_extreme_25_75_le_1 | broad_named_anatomy | MFD_06 | reject: target0 | +0.046 | +0.041 | 0.456 | 0.515 | 0/4 |
| post_error_response_extreme_33_67_le_1 | broad_named_anatomy | NYU-12 | reject: shuffle | -0.010 | -0.014 | 0.398 | 0.415 | 0/4 |
| post_error_response_extreme_25_75_le_1 | broad_named_anatomy | NYU-12 | reject: shuffle | -0.014 | -0.015 | 0.352 | 0.374 | 0/4 |

## Decision

Validate composite behavior candidates on the projected manifest and across shuffle seeds before GPU training.
