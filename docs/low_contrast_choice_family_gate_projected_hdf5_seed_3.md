# Low-Contrast Choice Family Gate

Prospective no-spend target redesign: restrict trials by absolute stimulus contrast and classify left-vs-right choice under the unchanged shared-family model-free promotion gate.

- rows: `96`
- candidates: `0`
- positive centered-delta rows: `53`
- max bidirectional recordings: `2`
- max bidirectional recording fraction: `0.500`
- decision: `no_low_contrast_choice_family_candidate`
- gpu training ready: `False`

## Target Balance

| target | trials | eligible recordings | recordings |
|---|---:|---:|---:|
| low_contrast_choice_le_0.0625 | 6914 | 31 | 31 |
| low_contrast_choice_le_0.125 | 11384 | 31 | 31 |
| low_contrast_choice_le_0.25 | 16012 | 31 | 31 |

## Top Rows

| target | family | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs |
|---|---|---|---|---:|---:|---:|---:|---:|
| low_contrast_choice_le_0.125 | fiber_tracts | CSH_ZAD_019 | reject: target0 | +0.035 | +0.215 | 0.530 | 0.614 | 2/4 |
| low_contrast_choice_le_0.25 | fiber_tracts | CSH_ZAD_019 | reject: target0 | +0.032 | +0.201 | 0.529 | 0.592 | 2/4 |
| low_contrast_choice_le_0.125 | fiber_tracts | ZFM-01577 | reject: target1 | +0.000 | +0.077 | 0.652 | 0.410 | 1/3 |
| low_contrast_choice_le_0.0625 | thalamic | ZFM-01577 | reject: shuffle | -0.120 | +0.132 | 0.172 | 0.865 | 1/3 |
| low_contrast_choice_le_0.0625 | fiber_tracts | CSH_ZAD_019 | reject: target0 | +0.202 | +0.237 | 0.531 | 0.649 | 1/4 |
| low_contrast_choice_le_0.25 | fiber_tracts | MFD_06 | reject: target1 | +0.185 | +0.227 | 0.805 | 0.250 | 1/4 |
| low_contrast_choice_le_0.125 | fiber_tracts | MFD_06 | reject: target1 | +0.126 | +0.231 | 0.798 | 0.271 | 1/4 |
| low_contrast_choice_le_0.125 | hippocampal_formation | SWC_038 | reject: target1 | +0.067 | +0.230 | 0.880 | 0.071 | 1/4 |
| low_contrast_choice_le_0.0625 | fiber_tracts | KS014 | reject: target1 | +0.058 | +0.015 | 0.663 | 0.450 | 1/4 |
| low_contrast_choice_le_0.0625 | hippocampal_formation | SWC_038 | reject: target0 | +0.053 | +0.059 | 0.201 | 0.949 | 1/4 |
| low_contrast_choice_le_0.0625 | fiber_tracts | NYU-12 | reject: target1 | +0.052 | +0.033 | 0.658 | 0.320 | 1/4 |
| low_contrast_choice_le_0.25 | fiber_tracts | KS014 | reject: target1 | +0.048 | +0.059 | 0.641 | 0.463 | 1/4 |
| low_contrast_choice_le_0.25 | fiber_tracts | SWC_038 | reject: target1 | +0.023 | +0.090 | 0.652 | 0.377 | 1/4 |
| low_contrast_choice_le_0.0625 | fiber_tracts | SWC_038 | reject: total baseline | +0.006 | -0.097 | 0.626 | 0.354 | 1/4 |
| low_contrast_choice_le_0.125 | fiber_tracts | SWC_038 | reject: target1 | +0.002 | +0.066 | 0.640 | 0.366 | 1/4 |
| low_contrast_choice_le_0.125 | broad_named_anatomy | SWC_038 | reject: shuffle | -0.002 | -0.003 | 0.519 | 0.550 | 1/4 |

## Decision

Do not train: low-contrast choice targets do not pass the strict local gate.
