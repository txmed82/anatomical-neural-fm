# Neutral-Prior Low-Contrast Choice Family Gate

Prospective no-spend target redesign: restrict trials by absolute stimulus contrast and neutral block prior, then classify left-vs-right choice under the unchanged shared-family model-free promotion gate.

- rows: `280`
- candidates: `0`
- positive centered-delta rows: `92`
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
| neutral_prior_low_contrast_choice_le_0.25 | broad_named_anatomy | CSH_ZAD_019 | reject: recording bidirectionality | +0.429 | +0.424 | 0.594 | 0.657 | 2/4 |
| neutral_prior_low_contrast_choice_le_0.125 | midbrain | NR_0019 | reject: target1 | +0.092 | +0.072 | 0.824 | 0.438 | 2/4 |
| neutral_prior_low_contrast_choice_le_0.0625 | fiber_tracts | NR_0019 | reject: total baseline | +0.085 | -0.285 | 0.663 | 0.429 | 2/4 |
| neutral_prior_low_contrast_choice_le_1 | fiber_tracts | CSH_ZAD_019 | reject: target0 | +0.066 | +0.126 | 0.532 | 0.648 | 2/4 |
| neutral_prior_low_contrast_choice_le_0.0625 | hippocampal_formation | KS014 | reject: total baseline | +0.052 | -0.023 | 0.339 | 0.885 | 2/4 |
| neutral_prior_low_contrast_choice_le_0.0625 | cortical_sensorimotor | CSH_ZAD_019 | reject: target0 | +0.045 | +0.136 | 0.291 | 0.794 | 2/4 |
| neutral_prior_low_contrast_choice_le_0.125 | hippocampal_formation | KS014 | reject: target1 | +0.029 | +0.051 | 0.796 | 0.275 | 2/4 |
| neutral_prior_low_contrast_choice_le_0.0625 | broad_named_anatomy | NR_0019 | reject: total baseline | +0.006 | -0.407 | 0.565 | 0.786 | 2/4 |
| neutral_prior_low_contrast_choice_le_0.125 | broad_named_anatomy | CSH_ZAD_019 | reject: recording bidirectionality | +0.001 | +0.365 | 0.560 | 0.697 | 2/4 |
| neutral_prior_low_contrast_choice_le_1 | broad_named_anatomy | CSH_ZAD_019 | reject: shuffle | -0.006 | -0.006 | 0.573 | 0.606 | 2/4 |
| neutral_prior_low_contrast_choice_le_0.0625 | hippocampal_formation | MFD_06 | reject: shuffle | -0.052 | +0.061 | 0.347 | 0.646 | 2/4 |
| neutral_prior_low_contrast_choice_le_0.125 | broad_named_anatomy | NR_0019 | reject: total baseline | +0.393 | -0.005 | 0.493 | 0.844 | 1/4 |
| neutral_prior_low_contrast_choice_le_0.25 | broad_named_anatomy | NR_0019 | reject: total baseline | +0.302 | -0.002 | 0.517 | 0.759 | 1/4 |
| neutral_prior_low_contrast_choice_le_1 | brainstem_interbrain | CSH_ZAD_019 | reject: target1 | +0.214 | +0.354 | 0.803 | 0.324 | 1/4 |
| neutral_prior_low_contrast_choice_le_0.125 | basal_ganglia | NR_0019 | reject: total baseline | +0.115 | -0.121 | 0.743 | 0.219 | 1/4 |
| neutral_prior_low_contrast_choice_le_0.125 | fiber_tracts | NR_0019 | reject: total baseline | +0.086 | -0.275 | 0.669 | 0.453 | 1/4 |

## Decision

Do not train: neutral-prior low-contrast choice targets do not pass the strict local gate.
