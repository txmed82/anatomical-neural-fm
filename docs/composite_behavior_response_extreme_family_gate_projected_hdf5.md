# Composite Behavior Target Family Gate

No-spend bounded screen over prospective composite behavior targets. Targets combine low contrast, prior context, previous-trial outcome, correctness, block-switch context, and response-speed labels under the unchanged shared-family model-free promotion gate.

- rows: `64`
- candidates: `4`
- positive centered-delta rows: `26`
- max bidirectional recordings: `3`
- max bidirectional recording fraction: `0.750`
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
| post_error_response_extreme_25_75_le_1 | 32 | 2 | 15 | 0.750 |
| post_error_response_extreme_33_67_le_1 | 32 | 2 | 11 | 0.750 |

## Top Rows

| target | family | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs |
|---|---|---|---|---:|---:|---:|---:|---:|
| post_error_response_extreme_25_75_le_1 | broad_named_anatomy | CSHL045 | candidate | +0.066 | +0.037 | 0.710 | 0.899 | 3/4 |
| post_error_response_extreme_33_67_le_1 | broad_named_anatomy | CSHL045 | candidate | +0.061 | +0.025 | 0.696 | 0.873 | 3/4 |
| post_error_response_extreme_33_67_le_1 | broad_named_anatomy | NR_0019 | candidate | +0.006 | +0.004 | 0.632 | 0.658 | 3/4 |
| post_error_response_extreme_25_75_le_1 | broad_named_anatomy | NR_0019 | candidate | +0.005 | +0.004 | 0.693 | 0.670 | 3/4 |
| post_error_response_extreme_33_67_le_1 | broad_named_anatomy | KS014 | reject: shuffle | -0.001 | -0.003 | 0.738 | 0.795 | 3/4 |
| post_error_response_extreme_25_75_le_1 | broad_named_anatomy | KS014 | reject: shuffle | -0.002 | -0.002 | 0.713 | 0.787 | 3/4 |
| post_error_response_extreme_33_67_le_1 | hippocampal_formation | ZFM-01577 | reject: total baseline | +0.057 | -0.013 | 0.512 | 0.752 | 2/3 |
| post_error_response_extreme_25_75_le_1 | thalamic | CSHL045 | reject: total baseline | +0.112 | -0.008 | 0.471 | 0.957 | 2/4 |
| post_error_response_extreme_33_67_le_1 | thalamic | CSHL045 | reject: total baseline | +0.111 | -0.021 | 0.464 | 0.928 | 2/4 |
| post_error_response_extreme_25_75_le_1 | thalamic | NR_0019 | reject: target0 | +0.065 | +0.063 | 0.352 | 0.909 | 2/4 |
| post_error_response_extreme_25_75_le_1 | thalamic | CSH_ZAD_019 | reject: recording bidirectionality | +0.062 | +0.062 | 0.562 | 0.570 | 2/4 |
| post_error_response_extreme_33_67_le_1 | thalamic | CSH_ZAD_019 | reject: recording bidirectionality | +0.056 | +0.052 | 0.566 | 0.566 | 2/4 |
| post_error_response_extreme_33_67_le_1 | broad_named_anatomy | MFD_06 | reject: recording bidirectionality | +0.046 | +0.033 | 0.551 | 0.612 | 2/4 |
| post_error_response_extreme_25_75_le_1 | hippocampal_formation | KS014 | reject: total baseline | +0.000 | -0.014 | 0.479 | 0.979 | 2/4 |
| post_error_response_extreme_33_67_le_1 | hippocampal_formation | KS014 | reject: shuffle | -0.006 | -0.021 | 0.951 | 0.484 | 2/4 |
| post_error_response_extreme_25_75_le_1 | broad_named_anatomy | CSH_ZAD_019 | reject: shuffle | -0.006 | +0.005 | 0.555 | 0.570 | 2/4 |

## Decision

Validate composite behavior candidates on the projected manifest and across shuffle seeds before GPU training.
