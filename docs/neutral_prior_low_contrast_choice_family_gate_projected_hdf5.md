# Neutral-Prior Low-Contrast Choice Family Gate

Prospective no-spend target redesign: restrict trials by absolute stimulus contrast and neutral block prior, then classify left-vs-right choice under the unchanged shared-family model-free promotion gate.

- rows: `320`
- candidates: `0`
- positive centered-delta rows: `133`
- max bidirectional recordings: `3`
- max bidirectional recording fraction: `0.750`
- decision: `no_neutral_prior_low_contrast_choice_family_candidate`
- gpu training ready: `False`

## Target Balance

| target | trials | eligible recordings | recordings |
|---|---:|---:|---:|
| neutral_prior_low_contrast_choice_le_0.0625 | 930 | 0 | 31 |
| neutral_prior_low_contrast_choice_le_0.125 | 1550 | 0 | 31 |
| neutral_prior_low_contrast_choice_le_0.25 | 2170 | 0 | 31 |
| neutral_prior_low_contrast_choice_le_1 | 2790 | 11 | 31 |

## Top Rows

| target | family | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs |
|---|---|---|---|---:|---:|---:|---:|---:|
| neutral_prior_low_contrast_choice_le_1 | broad_named_anatomy | CSH_ZAD_019 | reject: shuffle | -0.003 | -0.006 | 0.596 | 0.683 | 3/4 |
| neutral_prior_low_contrast_choice_le_0.125 | fiber_tracts | ZFM-01577 | reject: target1 | +0.146 | +0.146 | 0.783 | 0.463 | 2/3 |
| neutral_prior_low_contrast_choice_le_0.25 | brainstem_interbrain | CSH_ZAD_019 | reject: target0 | +0.251 | +0.436 | 0.309 | 0.838 | 2/4 |
| neutral_prior_low_contrast_choice_le_0.0625 | basal_ganglia | SWC_038 | reject: target1 | +0.125 | +0.164 | 0.865 | 0.325 | 2/4 |
| neutral_prior_low_contrast_choice_le_0.125 | midbrain | NR_0019 | reject: target1 | +0.079 | +0.465 | 0.846 | 0.469 | 2/4 |
| neutral_prior_low_contrast_choice_le_1 | brainstem_interbrain | CSH_ZAD_019 | reject: target0 | +0.063 | +0.234 | 0.317 | 0.831 | 2/4 |
| neutral_prior_low_contrast_choice_le_0.0625 | basal_ganglia | CSHL045 | reject: target0 | +0.051 | +0.193 | 0.408 | 0.845 | 2/4 |
| neutral_prior_low_contrast_choice_le_0.125 | midbrain | KS014 | reject: total baseline | +0.026 | -0.011 | 0.592 | 0.549 | 2/4 |
| neutral_prior_low_contrast_choice_le_0.0625 | broad_named_anatomy | MFD_06 | reject: target0 | +0.012 | +0.040 | 0.500 | 0.521 | 2/4 |
| neutral_prior_low_contrast_choice_le_0.125 | broad_named_anatomy | CSH_ZAD_019 | reject: recording bidirectionality | +0.001 | +0.365 | 0.552 | 0.667 | 2/4 |
| neutral_prior_low_contrast_choice_le_0.25 | broad_named_anatomy | CSH_ZAD_019 | reject: shuffle | -0.001 | +0.424 | 0.571 | 0.705 | 2/4 |
| neutral_prior_low_contrast_choice_le_0.25 | broad_named_anatomy | NR_0019 | reject: shuffle | -0.003 | -0.002 | 0.529 | 0.713 | 2/4 |
| neutral_prior_low_contrast_choice_le_0.125 | broad_named_anatomy | NR_0019 | reject: shuffle | -0.004 | +0.395 | 0.522 | 0.844 | 2/4 |
| neutral_prior_low_contrast_choice_le_1 | midbrain | ZFM-01577 | reject: target0 | +0.057 | +0.250 | 0.231 | 0.870 | 1/3 |
| neutral_prior_low_contrast_choice_le_0.25 | midbrain | ZFM-01577 | reject: target0 | +0.056 | +0.270 | 0.200 | 0.874 | 1/3 |
| neutral_prior_low_contrast_choice_le_0.125 | hippocampal_formation | ZFM-01577 | reject: target1 | +0.016 | +0.116 | 0.723 | 0.403 | 1/3 |

## Decision

Do not train: neutral-prior low-contrast choice targets do not pass the strict local gate.
