# Low-Contrast Choice Family Gate

Prospective no-spend target redesign: restrict trials by absolute stimulus contrast and classify left-vs-right choice under the unchanged shared-family model-free promotion gate.

- rows: `96`
- candidates: `0`
- positive centered-delta rows: `52`
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
| low_contrast_choice_le_0.25 | fiber_tracts | SWC_038 | reject: target1 | +0.065 | +0.090 | 0.681 | 0.394 | 2/4 |
| low_contrast_choice_le_0.125 | fiber_tracts | SWC_038 | reject: target1 | +0.044 | +0.066 | 0.658 | 0.383 | 2/4 |
| low_contrast_choice_le_0.0625 | fiber_tracts | CSH_ZAD_019 | reject: target0 | +0.020 | +0.237 | 0.543 | 0.611 | 2/4 |
| low_contrast_choice_le_0.0625 | fiber_tracts | CSHL045 | reject: target1 | +0.275 | +0.316 | 0.853 | 0.194 | 1/4 |
| low_contrast_choice_le_0.0625 | thalamic | KS014 | reject: target0 | +0.170 | +0.115 | 0.130 | 0.851 | 1/4 |
| low_contrast_choice_le_0.125 | thalamic | CSHL045 | reject: target1 | +0.069 | +0.184 | 0.705 | 0.322 | 1/4 |
| low_contrast_choice_le_0.0625 | thalamic | CSHL045 | reject: target0 | +0.068 | +0.227 | 0.403 | 0.700 | 1/4 |
| low_contrast_choice_le_0.0625 | fiber_tracts | SWC_038 | reject: total baseline | +0.056 | -0.097 | 0.648 | 0.375 | 1/4 |
| low_contrast_choice_le_0.0625 | fiber_tracts | NYU-12 | reject: target1 | +0.052 | +0.033 | 0.662 | 0.352 | 1/4 |
| low_contrast_choice_le_0.125 | fiber_tracts | NYU-12 | reject: target1 | +0.049 | +0.054 | 0.669 | 0.357 | 1/4 |
| low_contrast_choice_le_0.0625 | hippocampal_formation | SWC_038 | reject: target0 | +0.046 | +0.059 | 0.192 | 0.949 | 1/4 |
| low_contrast_choice_le_0.125 | fiber_tracts | CSH_ZAD_019 | reject: target1 | +0.024 | +0.215 | 0.554 | 0.515 | 1/4 |
| low_contrast_choice_le_0.125 | broad_named_anatomy | SWC_038 | reject: shuffle | -0.004 | -0.003 | 0.493 | 0.526 | 1/4 |
| low_contrast_choice_le_0.25 | broad_named_anatomy | SWC_038 | reject: shuffle | -0.004 | -0.003 | 0.490 | 0.510 | 1/4 |
| low_contrast_choice_le_0.125 | fiber_tracts | CSHL045 | reject: shuffle | -0.236 | +0.055 | 0.855 | 0.196 | 1/4 |
| low_contrast_choice_le_0.0625 | hippocampal_formation | CSHL045 | reject: target0 | +0.539 | +0.421 | 0.000 | 1.000 | 0/4 |

## Decision

Do not train: low-contrast choice targets do not pass the strict local gate.
