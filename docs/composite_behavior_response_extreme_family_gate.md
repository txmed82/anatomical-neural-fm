# Composite Behavior Target Family Gate

No-spend bounded screen over prospective composite behavior targets. Targets combine low contrast, prior context, previous-trial outcome, correctness, block-switch context, and response-speed labels under the unchanged shared-family model-free promotion gate.

- rows: `56`
- candidates: `2`
- positive centered-delta rows: `28`
- max bidirectional recordings: `3`
- max bidirectional recording fraction: `0.750`
- decision: `composite_behavior_target_family_candidate`
- gpu training ready: `False`

## Target Balance

| target | trials | eligible recordings | recordings |
|---|---:|---:|---:|
| post_error_response_extreme_33_67_le_1 | 2182 | 10 | 28 |
| post_error_response_extreme_25_75_le_1 | 1672 | 4 | 28 |

## Target Summary

| target | rows | candidates | positive centered delta | max bidir frac |
|---|---:|---:|---:|---:|
| post_error_response_extreme_25_75_le_1 | 28 | 1 | 15 | 0.750 |
| post_error_response_extreme_33_67_le_1 | 28 | 1 | 13 | 0.750 |

## Top Rows

| target | family | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs |
|---|---|---|---|---:|---:|---:|---:|---:|
| post_error_response_extreme_33_67_le_1 | broad_named_anatomy | NR_0019 | candidate | +0.006 | +0.004 | 0.632 | 0.649 | 3/4 |
| post_error_response_extreme_25_75_le_1 | broad_named_anatomy | NR_0019 | candidate | +0.005 | +0.004 | 0.693 | 0.670 | 3/4 |
| post_error_response_extreme_33_67_le_1 | broad_named_anatomy | KS014 | reject: shuffle | -0.001 | -0.003 | 0.713 | 0.762 | 3/4 |
| post_error_response_extreme_25_75_le_1 | broad_named_anatomy | KS014 | reject: shuffle | -0.001 | -0.002 | 0.702 | 0.787 | 3/4 |
| post_error_response_extreme_25_75_le_1 | hippocampal_formation | KS014 | reject: total baseline | +0.705 | -0.020 | 0.479 | 0.989 | 2/4 |
| post_error_response_extreme_33_67_le_1 | hippocampal_formation | KS014 | reject: total baseline | +0.688 | -0.026 | 0.451 | 0.992 | 2/4 |
| post_error_response_extreme_25_75_le_1 | thalamic | CSH_ZAD_019 | reject: recording bidirectionality | +0.062 | +0.062 | 0.562 | 0.578 | 2/4 |
| post_error_response_extreme_33_67_le_1 | thalamic | CSH_ZAD_019 | reject: recording bidirectionality | +0.056 | +0.052 | 0.566 | 0.566 | 2/4 |
| post_error_response_extreme_25_75_le_1 | broad_named_anatomy | SWC_043 | reject: recording bidirectionality | +0.018 | +0.023 | 0.579 | 0.642 | 2/4 |
| post_error_response_extreme_25_75_le_1 | thalamic | NR_0019 | reject: total baseline | +0.014 | -0.017 | 0.352 | 0.943 | 2/4 |
| post_error_response_extreme_33_67_le_1 | broad_named_anatomy | SWC_043 | reject: recording bidirectionality | +0.010 | +0.012 | 0.573 | 0.629 | 2/4 |
| post_error_response_extreme_33_67_le_1 | thalamic | NR_0019 | reject: shuffle | -0.005 | -0.084 | 0.298 | 0.895 | 2/4 |
| post_error_response_extreme_25_75_le_1 | broad_named_anatomy | CSH_ZAD_019 | reject: shuffle | -0.006 | +0.005 | 0.562 | 0.570 | 2/4 |
| post_error_response_extreme_33_67_le_1 | broad_named_anatomy | SWC_038 | reject: shuffle | -0.008 | -0.007 | 0.613 | 0.591 | 2/4 |
| post_error_response_extreme_25_75_le_1 | broad_named_anatomy | SWC_038 | reject: shuffle | -0.008 | -0.008 | 0.598 | 0.583 | 2/4 |
| post_error_response_extreme_25_75_le_1 | fiber_tracts | SWC_043 | reject: shuffle | -0.048 | -0.026 | 0.400 | 0.474 | 2/4 |

## Decision

Validate composite behavior candidates on the projected manifest and across shuffle seeds before GPU training.
