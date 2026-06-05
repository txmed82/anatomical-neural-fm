# Neutral-Prior Low-Contrast Choice Family Gate

Prospective no-spend target redesign: restrict trials by absolute stimulus contrast and neutral block prior, then classify left-vs-right choice under the unchanged shared-family model-free promotion gate.

- rows: `280`
- candidates: `1`
- positive centered-delta rows: `110`
- max bidirectional recordings: `3`
- max bidirectional recording fraction: `0.750`
- decision: `neutral_prior_low_contrast_choice_family_candidate`
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
| neutral_prior_low_contrast_choice_le_0.25 | fiber_tracts | CSH_ZAD_019 | candidate | +0.074 | +0.133 | 0.634 | 0.619 | 3/4 |
| neutral_prior_low_contrast_choice_le_0.25 | broad_named_anatomy | CSH_ZAD_019 | reject: recording bidirectionality | +0.428 | +0.424 | 0.606 | 0.676 | 2/4 |
| neutral_prior_low_contrast_choice_le_0.0625 | fiber_tracts | SWC_038 | reject: target1 | +0.259 | +0.332 | 0.703 | 0.410 | 2/4 |
| neutral_prior_low_contrast_choice_le_0.125 | cortical_sensorimotor | CSH_ZAD_019 | reject: target0 | +0.120 | +0.249 | 0.284 | 0.803 | 2/4 |
| neutral_prior_low_contrast_choice_le_1 | cortical_visual | KS014 | reject: target1 | +0.113 | +0.052 | 0.725 | 0.445 | 2/4 |
| neutral_prior_low_contrast_choice_le_0.125 | midbrain | NR_0019 | reject: target0 | +0.071 | +0.072 | 0.324 | 0.922 | 2/4 |
| neutral_prior_low_contrast_choice_le_0.25 | cortical_sensorimotor | CSH_ZAD_019 | reject: target1 | +0.070 | +0.261 | 0.811 | 0.333 | 2/4 |
| neutral_prior_low_contrast_choice_le_1 | fiber_tracts | CSH_ZAD_019 | reject: recording bidirectionality | +0.068 | +0.126 | 0.610 | 0.634 | 2/4 |
| neutral_prior_low_contrast_choice_le_0.125 | brainstem_interbrain | MFD_06 | reject: target0 | +0.060 | +0.168 | 0.325 | 0.807 | 2/4 |
| neutral_prior_low_contrast_choice_le_0.125 | midbrain | KS014 | reject: total baseline | +0.035 | -0.011 | 0.592 | 0.529 | 2/4 |
| neutral_prior_low_contrast_choice_le_0.125 | brainstem_interbrain | CSH_ZAD_019 | reject: target0 | +0.020 | +0.303 | 0.276 | 0.803 | 2/4 |
| neutral_prior_low_contrast_choice_le_0.0625 | broad_named_anatomy | NR_0019 | reject: total baseline | +0.010 | -0.407 | 0.533 | 0.750 | 2/4 |
| neutral_prior_low_contrast_choice_le_1 | broad_named_anatomy | NR_0019 | reject: total baseline | +0.009 | -0.227 | 0.561 | 0.719 | 2/4 |
| neutral_prior_low_contrast_choice_le_0.25 | broad_named_anatomy | MFD_06 | reject: total baseline | +0.006 | -0.036 | 0.519 | 0.541 | 2/4 |
| neutral_prior_low_contrast_choice_le_0.125 | broad_named_anatomy | CSH_ZAD_019 | reject: recording bidirectionality | +0.003 | +0.365 | 0.567 | 0.667 | 2/4 |
| neutral_prior_low_contrast_choice_le_1 | broad_named_anatomy | CSH_ZAD_019 | reject: shuffle | -0.006 | -0.006 | 0.564 | 0.620 | 2/4 |

## Decision

Validate neutral-prior low-contrast choice candidates across shuffle seeds before GPU training.
