# Composite Behavior Target Family Gate

No-spend bounded screen over prospective composite behavior targets. Targets combine low contrast, prior context, previous-trial outcome, correctness, block-switch context, and response-speed labels under the unchanged shared-family model-free promotion gate.

- rows: `8`
- candidates: `2`
- positive centered-delta rows: `4`
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
| post_error_fast_response_le_1 | 8 | 2 | 4 | 0.750 |

## Top Rows

| target | family | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs |
|---|---|---|---|---:|---:|---:|---:|---:|
| post_error_fast_response_le_1 | broad_named_anatomy | CSHL045 | candidate | +0.068 | +0.039 | 0.618 | 0.835 | 3/4 |
| post_error_fast_response_le_1 | broad_named_anatomy | NR_0019 | candidate | +0.004 | +0.002 | 0.570 | 0.645 | 3/4 |
| post_error_fast_response_le_1 | broad_named_anatomy | KS014 | reject: shuffle | -0.003 | -0.005 | 0.699 | 0.754 | 3/4 |
| post_error_fast_response_le_1 | broad_named_anatomy | SWC_038 | reject: shuffle | -0.007 | -0.007 | 0.596 | 0.567 | 2/4 |
| post_error_fast_response_le_1 | broad_named_anatomy | ZFM-01577 | reject: shuffle | -0.015 | -0.051 | 0.470 | 0.459 | 1/3 |
| post_error_fast_response_le_1 | broad_named_anatomy | MFD_06 | reject: target0 | +0.034 | +0.019 | 0.537 | 0.631 | 1/4 |
| post_error_fast_response_le_1 | broad_named_anatomy | NYU-12 | reject: total baseline | +0.002 | -0.008 | 0.483 | 0.494 | 1/4 |
| post_error_fast_response_le_1 | broad_named_anatomy | CSH_ZAD_019 | reject: shuffle | -0.000 | +0.004 | 0.524 | 0.591 | 1/4 |

## Decision

Validate composite behavior candidates on the projected manifest and across shuffle seeds before GPU training.
