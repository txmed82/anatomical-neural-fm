# Composite Behavior Target Family Gate

No-spend bounded screen over prospective composite behavior targets. Targets combine low contrast, prior context, previous-trial outcome, correctness, block-switch context, and response-speed labels under the unchanged shared-family model-free promotion gate.

- rows: `8`
- candidates: `2`
- positive centered-delta rows: `5`
- max bidirectional recordings: `3`
- max bidirectional recording fraction: `0.750`
- decision: `composite_behavior_target_family_candidate`
- gpu training ready: `False`

## Target Balance

| target | trials | eligible recordings | recordings |
|---|---:|---:|---:|
| post_error_fast_response_le_1 | 3820 | 28 | 31 |

## Target Summary

| target | rows | candidates | positive centered delta | max bidir frac |
|---|---:|---:|---:|---:|
| post_error_fast_response_le_1 | 8 | 2 | 5 | 0.750 |

## Top Rows

| target | family | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs |
|---|---|---|---|---:|---:|---:|---:|---:|
| post_error_fast_response_le_1 | broad_named_anatomy | CSHL045 | candidate | +0.061 | +0.039 | 0.647 | 0.757 | 3/4 |
| post_error_fast_response_le_1 | broad_named_anatomy | NR_0019 | candidate | +0.004 | +0.002 | 0.564 | 0.657 | 3/4 |
| post_error_fast_response_le_1 | broad_named_anatomy | KS014 | reject: shuffle | -0.001 | -0.005 | 0.716 | 0.814 | 3/4 |
| post_error_fast_response_le_1 | broad_named_anatomy | SWC_038 | reject: shuffle | -0.006 | -0.007 | 0.618 | 0.554 | 2/4 |
| post_error_fast_response_le_1 | broad_named_anatomy | ZFM-01577 | reject: shuffle | -0.028 | -0.051 | 0.530 | 0.464 | 1/3 |
| post_error_fast_response_le_1 | broad_named_anatomy | MFD_06 | reject: target0 | +0.024 | +0.019 | 0.530 | 0.608 | 1/4 |
| post_error_fast_response_le_1 | broad_named_anatomy | CSH_ZAD_019 | reject: target0 | +0.004 | +0.004 | 0.532 | 0.615 | 1/4 |
| post_error_fast_response_le_1 | broad_named_anatomy | NYU-12 | reject: total baseline | +0.007 | -0.008 | 0.528 | 0.483 | 0/4 |

## Decision

Validate composite behavior candidates on the projected manifest and across shuffle seeds before GPU training.
