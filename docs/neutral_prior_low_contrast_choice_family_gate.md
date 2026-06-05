# Neutral-Prior Low-Contrast Choice Family Gate

Prospective no-spend target redesign: restrict trials by absolute stimulus contrast and neutral block prior, then classify left-vs-right choice under the unchanged shared-family model-free promotion gate.

- rows: `280`
- candidates: `1`
- positive centered-delta rows: `112`
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
| neutral_prior_low_contrast_choice_le_1 | fiber_tracts | CSH_ZAD_019 | candidate | +0.042 | +0.126 | 0.550 | 0.613 | 3/4 |
| neutral_prior_low_contrast_choice_le_0.25 | broad_named_anatomy | CSH_ZAD_019 | reject: recording bidirectionality | +0.430 | +0.424 | 0.600 | 0.695 | 2/4 |
| neutral_prior_low_contrast_choice_le_0.0625 | fiber_tracts | SWC_038 | reject: target1 | +0.255 | +0.332 | 0.703 | 0.410 | 2/4 |
| neutral_prior_low_contrast_choice_le_1 | brainstem_interbrain | CSH_ZAD_019 | reject: target0 | +0.239 | +0.354 | 0.312 | 0.852 | 2/4 |
| neutral_prior_low_contrast_choice_le_0.125 | midbrain | NR_0019 | reject: target1 | +0.082 | +0.072 | 0.824 | 0.422 | 2/4 |
| neutral_prior_low_contrast_choice_le_0.25 | cortical_sensorimotor | CSH_ZAD_019 | reject: target1 | +0.046 | +0.261 | 0.806 | 0.343 | 2/4 |
| neutral_prior_low_contrast_choice_le_0.125 | broad_named_anatomy | CSH_ZAD_019 | reject: recording bidirectionality | +0.001 | +0.365 | 0.575 | 0.667 | 2/4 |
| neutral_prior_low_contrast_choice_le_1 | fiber_tracts | SWC_038 | reject: target0 | +0.000 | +0.055 | 0.535 | 0.682 | 2/4 |
| neutral_prior_low_contrast_choice_le_1 | broad_named_anatomy | CSH_ZAD_019 | reject: shuffle | -0.003 | -0.006 | 0.569 | 0.613 | 2/4 |
| neutral_prior_low_contrast_choice_le_0.125 | broad_named_anatomy | NR_0019 | reject: total baseline | +0.394 | -0.005 | 0.485 | 0.844 | 1/4 |
| neutral_prior_low_contrast_choice_le_0.25 | broad_named_anatomy | NR_0019 | reject: total baseline | +0.303 | -0.002 | 0.523 | 0.769 | 1/4 |
| neutral_prior_low_contrast_choice_le_0.25 | basal_ganglia | NR_0019 | reject: total baseline | +0.126 | -0.067 | 0.773 | 0.296 | 1/4 |
| neutral_prior_low_contrast_choice_le_1 | basal_ganglia | NR_0019 | reject: total baseline | +0.119 | -0.031 | 0.790 | 0.308 | 1/4 |
| neutral_prior_low_contrast_choice_le_0.0625 | fiber_tracts | NR_0019 | reject: total baseline | +0.107 | -0.285 | 0.620 | 0.500 | 1/4 |
| neutral_prior_low_contrast_choice_le_0.125 | fiber_tracts | SWC_043 | reject: total baseline | +0.105 | -0.001 | 0.557 | 0.537 | 1/4 |
| neutral_prior_low_contrast_choice_le_0.125 | basal_ganglia | NR_0019 | reject: total baseline | +0.095 | -0.121 | 0.287 | 0.812 | 1/4 |

## Decision

Validate neutral-prior low-contrast choice candidates across shuffle seeds before GPU training.
