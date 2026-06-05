# Neutral-Prior Low-Contrast Choice Family Gate

Prospective no-spend target redesign: restrict trials by absolute stimulus contrast and neutral block prior, then classify left-vs-right choice under the unchanged shared-family model-free promotion gate.

- rows: `280`
- candidates: `0`
- positive centered-delta rows: `109`
- max bidirectional recordings: `2`
- max bidirectional recording fraction: `0.500`
- decision: `no_neutral_prior_low_contrast_choice_family_candidate`
- gpu training ready: `False`

## Target Balance

| target | trials | eligible recordings | recordings |
|---|---:|---:|---:|
| neutral_prior_low_contrast_choice_le_0.0625 | 840 | 0 | 28 |
| neutral_prior_low_contrast_choice_le_0.125 | 1400 | 0 | 28 |
| neutral_prior_low_contrast_choice_le_0.25 | 1960 | 0 | 28 |
| neutral_prior_low_contrast_choice_le_1 | 2520 | 10 | 28 |

## Top Rows

| target | family | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs |
|---|---|---|---|---:|---:|---:|---:|---:|
| neutral_prior_low_contrast_choice_le_0.25 | broad_named_anatomy | CSH_ZAD_019 | reject: recording bidirectionality | +0.432 | +0.424 | 0.606 | 0.695 | 2/4 |
| neutral_prior_low_contrast_choice_le_0.125 | cortical_sensorimotor | CSH_ZAD_019 | reject: target1 | +0.121 | +0.249 | 0.813 | 0.379 | 2/4 |
| neutral_prior_low_contrast_choice_le_0.125 | midbrain | NR_0019 | reject: target0 | +0.106 | +0.072 | 0.324 | 0.922 | 2/4 |
| neutral_prior_low_contrast_choice_le_0.0625 | cortical_sensorimotor | CSH_ZAD_019 | reject: target0 | +0.049 | +0.136 | 0.302 | 0.853 | 2/4 |
| neutral_prior_low_contrast_choice_le_0.25 | cortical_sensorimotor | CSH_ZAD_019 | reject: target1 | +0.045 | +0.261 | 0.806 | 0.362 | 2/4 |
| neutral_prior_low_contrast_choice_le_1 | fiber_tracts | NR_0019 | reject: total baseline | +0.034 | -0.164 | 0.411 | 0.678 | 2/4 |
| neutral_prior_low_contrast_choice_le_0.25 | midbrain | KS014 | reject: recording bidirectionality | +0.027 | +0.023 | 0.587 | 0.577 | 2/4 |
| neutral_prior_low_contrast_choice_le_1 | broad_named_anatomy | CSH_ZAD_019 | reject: shuffle | -0.002 | -0.006 | 0.583 | 0.655 | 2/4 |
| neutral_prior_low_contrast_choice_le_0.125 | broad_named_anatomy | CSH_ZAD_019 | reject: shuffle | -0.002 | +0.365 | 0.567 | 0.652 | 2/4 |
| neutral_prior_low_contrast_choice_le_0.125 | broad_named_anatomy | NR_0019 | reject: total baseline | +0.394 | -0.005 | 0.493 | 0.844 | 1/4 |
| neutral_prior_low_contrast_choice_le_0.25 | broad_named_anatomy | NR_0019 | reject: total baseline | +0.302 | -0.002 | 0.529 | 0.759 | 1/4 |
| neutral_prior_low_contrast_choice_le_1 | brainstem_interbrain | CSH_ZAD_019 | reject: target1 | +0.246 | +0.354 | 0.803 | 0.387 | 1/4 |
| neutral_prior_low_contrast_choice_le_0.125 | hippocampal_formation | SWC_038 | reject: target0 | +0.115 | +0.266 | 0.262 | 0.928 | 1/4 |
| neutral_prior_low_contrast_choice_le_0.0625 | basal_ganglia | CSH_ZAD_019 | reject: target1 | +0.100 | +0.199 | 0.779 | 0.265 | 1/4 |
| neutral_prior_low_contrast_choice_le_1 | hippocampal_formation | SWC_038 | reject: target1 | +0.092 | +0.295 | 0.850 | 0.112 | 1/4 |
| neutral_prior_low_contrast_choice_le_0.125 | cortical_sensorimotor | SWC_043 | reject: target0 | +0.091 | +0.082 | 0.291 | 0.785 | 1/4 |

## Decision

Do not train: neutral-prior low-contrast choice targets do not pass the strict local gate.
