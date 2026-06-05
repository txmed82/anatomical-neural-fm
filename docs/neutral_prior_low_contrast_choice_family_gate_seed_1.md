# Neutral-Prior Low-Contrast Choice Family Gate

Prospective no-spend target redesign: restrict trials by absolute stimulus contrast and neutral block prior, then classify left-vs-right choice under the unchanged shared-family model-free promotion gate.

- rows: `280`
- candidates: `1`
- positive centered-delta rows: `108`
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
| neutral_prior_low_contrast_choice_le_1 | fiber_tracts | CSH_ZAD_019 | candidate | +0.076 | +0.126 | 0.573 | 0.662 | 3/4 |
| neutral_prior_low_contrast_choice_le_0.0625 | broad_named_anatomy | NR_0019 | reject: total baseline | +0.020 | -0.407 | 0.565 | 0.821 | 3/4 |
| neutral_prior_low_contrast_choice_le_0.125 | broad_named_anatomy | NR_0019 | reject: total baseline | +0.399 | -0.005 | 0.515 | 0.844 | 2/4 |
| neutral_prior_low_contrast_choice_le_0.25 | broad_named_anatomy | NR_0019 | reject: total baseline | +0.305 | -0.002 | 0.535 | 0.769 | 2/4 |
| neutral_prior_low_contrast_choice_le_0.25 | fiber_tracts | NR_0019 | reject: total baseline | +0.095 | -0.207 | 0.436 | 0.741 | 2/4 |
| neutral_prior_low_contrast_choice_le_0.125 | cortical_sensorimotor | CSH_ZAD_019 | reject: target1 | +0.093 | +0.249 | 0.821 | 0.364 | 2/4 |
| neutral_prior_low_contrast_choice_le_0.0625 | fiber_tracts | CSH_ZAD_019 | reject: recording bidirectionality | +0.082 | +0.063 | 0.605 | 0.676 | 2/4 |
| neutral_prior_low_contrast_choice_le_0.125 | fiber_tracts | NR_0019 | reject: total baseline | +0.080 | -0.275 | 0.647 | 0.469 | 2/4 |
| neutral_prior_low_contrast_choice_le_0.25 | fiber_tracts | CSH_ZAD_019 | reject: recording bidirectionality | +0.073 | +0.133 | 0.560 | 0.629 | 2/4 |
| neutral_prior_low_contrast_choice_le_1 | fiber_tracts | NR_0019 | reject: total baseline | +0.067 | -0.164 | 0.411 | 0.747 | 2/4 |
| neutral_prior_low_contrast_choice_le_0.125 | fiber_tracts | CSH_ZAD_019 | reject: recording bidirectionality | +0.060 | +0.101 | 0.560 | 0.652 | 2/4 |
| neutral_prior_low_contrast_choice_le_0.25 | cortical_sensorimotor | CSH_ZAD_019 | reject: target0 | +0.056 | +0.261 | 0.309 | 0.800 | 2/4 |
| neutral_prior_low_contrast_choice_le_0.125 | midbrain | NR_0019 | reject: target0 | +0.043 | +0.072 | 0.324 | 0.906 | 2/4 |
| neutral_prior_low_contrast_choice_le_0.125 | midbrain | KS014 | reject: total baseline | +0.038 | -0.011 | 0.622 | 0.539 | 2/4 |
| neutral_prior_low_contrast_choice_le_0.0625 | midbrain | NR_0019 | reject: total baseline | +0.035 | -0.410 | 0.261 | 0.857 | 2/4 |
| neutral_prior_low_contrast_choice_le_0.125 | broad_named_anatomy | CSH_ZAD_019 | reject: recording bidirectionality | +0.006 | +0.365 | 0.582 | 0.712 | 2/4 |

## Decision

Validate neutral-prior low-contrast choice candidates across shuffle seeds before GPU training.
