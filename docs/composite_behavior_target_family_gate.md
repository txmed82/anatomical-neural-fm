# Composite Behavior Target Family Gate

No-spend bounded screen over prospective composite behavior targets. Targets combine low contrast, prior context, previous-trial outcome, correctness, block-switch context, and response-speed labels under the unchanged shared-family model-free promotion gate.

- rows: `224`
- candidates: `1`
- positive centered-delta rows: `102`
- max bidirectional recordings: `3`
- max bidirectional recording fraction: `0.750`
- decision: `composite_behavior_target_family_candidate`
- gpu training ready: `False`

## Target Balance

| target | trials | eligible recordings | recordings |
|---|---:|---:|---:|
| low_contrast_fast_response_le_0.25 | 13872 | 28 | 28 |
| neutral_prior_fast_response_le_1 | 2520 | 28 | 28 |
| post_error_choice_le_1 | 3250 | 20 | 28 |
| post_error_low_contrast_choice_le_0.25 | 2553 | 12 | 28 |
| biased_prior_choice_le_0.25 | 11832 | 28 | 28 |
| prior_switch_choice_le_1 | 1714 | 2 | 28 |
| post_error_fast_response_le_1 | 3286 | 24 | 28 |
| correct_low_contrast_fast_response_le_0.25 | 10702 | 28 | 28 |

## Target Summary

| target | rows | candidates | positive centered delta | max bidir frac |
|---|---:|---:|---:|---:|
| biased_prior_choice_le_0.25 | 28 | 0 | 16 | 0.500 |
| correct_low_contrast_fast_response_le_0.25 | 28 | 0 | 15 | 0.750 |
| low_contrast_fast_response_le_0.25 | 28 | 0 | 11 | 0.750 |
| neutral_prior_fast_response_le_1 | 28 | 0 | 10 | 0.750 |
| post_error_choice_le_1 | 28 | 0 | 11 | 0.500 |
| post_error_fast_response_le_1 | 28 | 1 | 13 | 0.750 |
| post_error_low_contrast_choice_le_0.25 | 28 | 0 | 10 | 0.500 |
| prior_switch_choice_le_1 | 28 | 0 | 16 | 0.500 |

## Top Rows

| target | family | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs |
|---|---|---|---|---:|---:|---:|---:|---:|
| post_error_fast_response_le_1 | broad_named_anatomy | NR_0019 | candidate | +0.004 | +0.002 | 0.570 | 0.622 | 3/4 |
| neutral_prior_fast_response_le_1 | broad_named_anatomy | KS014 | reject: shuffle | -0.000 | -0.002 | 0.578 | 0.611 | 3/4 |
| post_error_fast_response_le_1 | broad_named_anatomy | KS014 | reject: shuffle | -0.003 | -0.005 | 0.678 | 0.721 | 3/4 |
| correct_low_contrast_fast_response_le_0.25 | broad_named_anatomy | KS014 | reject: shuffle | -0.005 | -0.005 | 0.713 | 0.726 | 3/4 |
| low_contrast_fast_response_le_0.25 | broad_named_anatomy | KS014 | reject: shuffle | -0.008 | -0.008 | 0.711 | 0.674 | 3/4 |
| correct_low_contrast_fast_response_le_0.25 | hippocampal_formation | KS014 | reject: total baseline | +0.680 | -0.000 | 0.930 | 0.535 | 2/4 |
| low_contrast_fast_response_le_0.25 | hippocampal_formation | KS014 | reject: target0 | +0.644 | +0.006 | 0.501 | 0.928 | 2/4 |
| post_error_fast_response_le_1 | hippocampal_formation | KS014 | reject: total baseline | +0.580 | -0.045 | 0.410 | 0.967 | 2/4 |
| post_error_low_contrast_choice_le_0.25 | fiber_tracts | MFD_06 | reject: target1 | +0.177 | +0.109 | 0.805 | 0.287 | 2/4 |
| prior_switch_choice_le_1 | fiber_tracts | CSH_ZAD_019 | reject: target0 | +0.158 | +0.197 | 0.546 | 0.597 | 2/4 |
| post_error_choice_le_1 | fiber_tracts | CSH_ZAD_019 | reject: recording bidirectionality | +0.131 | +0.169 | 0.553 | 0.601 | 2/4 |
| post_error_low_contrast_choice_le_0.25 | fiber_tracts | CSH_ZAD_019 | reject: target0 | +0.109 | +0.137 | 0.542 | 0.563 | 2/4 |
| prior_switch_choice_le_1 | fiber_tracts | SWC_038 | reject: target1 | +0.064 | +0.134 | 0.745 | 0.377 | 2/4 |
| post_error_fast_response_le_1 | broad_named_anatomy | SWC_043 | reject: recording bidirectionality | +0.013 | +0.012 | 0.559 | 0.629 | 2/4 |
| biased_prior_choice_le_0.25 | broad_named_anatomy | SWC_043 | reject: total baseline | +0.007 | -0.157 | 0.533 | 0.582 | 2/4 |
| neutral_prior_fast_response_le_1 | broad_named_anatomy | SWC_038 | reject: shuffle | -0.001 | -0.000 | 0.472 | 0.456 | 2/4 |

## Decision

Validate composite behavior candidates on the projected manifest and across shuffle seeds before GPU training.
