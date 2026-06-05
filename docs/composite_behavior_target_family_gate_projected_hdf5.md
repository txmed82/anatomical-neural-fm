# Composite Behavior Target Family Gate

No-spend bounded screen over prospective composite behavior targets. Targets combine low contrast, prior context, previous-trial outcome, correctness, block-switch context, and response-speed labels under the unchanged shared-family model-free promotion gate.

- rows: `256`
- candidates: `2`
- positive centered-delta rows: `119`
- max bidirectional recordings: `3`
- max bidirectional recording fraction: `0.750`
- decision: `composite_behavior_target_family_candidate`
- gpu training ready: `False`

## Target Balance

| target | trials | eligible recordings | recordings |
|---|---:|---:|---:|
| low_contrast_fast_response_le_0.25 | 16116 | 31 | 31 |
| neutral_prior_fast_response_le_1 | 2790 | 31 | 31 |
| post_error_choice_le_1 | 3768 | 24 | 31 |
| post_error_low_contrast_choice_le_0.25 | 2953 | 15 | 31 |
| biased_prior_choice_le_0.25 | 13842 | 31 | 31 |
| prior_switch_choice_le_1 | 1962 | 4 | 31 |
| post_error_fast_response_le_1 | 3820 | 28 | 31 |
| correct_low_contrast_fast_response_le_0.25 | 12432 | 31 | 31 |

## Target Summary

| target | rows | candidates | positive centered delta | max bidir frac |
|---|---:|---:|---:|---:|
| biased_prior_choice_le_0.25 | 32 | 0 | 15 | 0.333 |
| correct_low_contrast_fast_response_le_0.25 | 32 | 0 | 13 | 0.750 |
| low_contrast_fast_response_le_0.25 | 32 | 0 | 15 | 0.750 |
| neutral_prior_fast_response_le_1 | 32 | 0 | 10 | 0.750 |
| post_error_choice_le_1 | 32 | 0 | 20 | 0.500 |
| post_error_fast_response_le_1 | 32 | 2 | 13 | 0.750 |
| post_error_low_contrast_choice_le_0.25 | 32 | 0 | 16 | 0.500 |
| prior_switch_choice_le_1 | 32 | 0 | 17 | 0.500 |

## Top Rows

| target | family | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs |
|---|---|---|---|---:|---:|---:|---:|---:|
| post_error_fast_response_le_1 | broad_named_anatomy | CSHL045 | candidate | +0.068 | +0.039 | 0.618 | 0.835 | 3/4 |
| post_error_fast_response_le_1 | broad_named_anatomy | NR_0019 | candidate | +0.004 | +0.002 | 0.570 | 0.645 | 3/4 |
| neutral_prior_fast_response_le_1 | broad_named_anatomy | KS014 | reject: shuffle | -0.000 | -0.002 | 0.606 | 0.650 | 3/4 |
| post_error_fast_response_le_1 | broad_named_anatomy | KS014 | reject: shuffle | -0.003 | -0.005 | 0.699 | 0.754 | 3/4 |
| correct_low_contrast_fast_response_le_0.25 | broad_named_anatomy | KS014 | reject: shuffle | -0.005 | -0.005 | 0.708 | 0.725 | 3/4 |
| low_contrast_fast_response_le_0.25 | broad_named_anatomy | KS014 | reject: shuffle | -0.008 | -0.008 | 0.710 | 0.678 | 3/4 |
| low_contrast_fast_response_le_0.25 | hippocampal_formation | ZFM-01577 | reject: total baseline | +0.252 | -0.017 | 0.448 | 0.739 | 2/3 |
| correct_low_contrast_fast_response_le_0.25 | hippocampal_formation | ZFM-01577 | reject: total baseline | +0.018 | -0.001 | 0.696 | 0.519 | 2/3 |
| post_error_fast_response_le_1 | hippocampal_formation | KS014 | reject: total baseline | +0.496 | -0.122 | 0.891 | 0.470 | 2/4 |
| low_contrast_fast_response_le_0.25 | hippocampal_formation | KS014 | reject: target0 | +0.104 | +0.008 | 0.505 | 0.897 | 2/4 |
| correct_low_contrast_fast_response_le_0.25 | hippocampal_formation | KS014 | reject: target1 | +0.097 | +0.000 | 0.911 | 0.462 | 2/4 |
| post_error_fast_response_le_1 | thalamic | CSHL045 | reject: total baseline | +0.085 | -0.002 | 0.706 | 0.607 | 2/4 |
| post_error_choice_le_1 | fiber_tracts | NYU-12 | reject: target1 | +0.059 | +0.037 | 0.667 | 0.398 | 2/4 |
| post_error_low_contrast_choice_le_0.25 | fiber_tracts | SWC_038 | reject: target0 | +0.042 | +0.081 | 0.435 | 0.670 | 2/4 |
| low_contrast_fast_response_le_0.25 | broad_named_anatomy | CSHL045 | reject: target0 | +0.042 | +0.012 | 0.506 | 0.753 | 2/4 |
| neutral_prior_fast_response_le_1 | broad_named_anatomy | SWC_038 | reject: shuffle | -0.001 | -0.000 | 0.483 | 0.478 | 2/4 |

## Decision

Validate composite behavior candidates on the projected manifest and across shuffle seeds before GPU training.
