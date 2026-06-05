# Low-Contrast Choice Family Gate

Prospective no-spend target redesign: restrict trials by absolute stimulus contrast and classify left-vs-right choice under the unchanged shared-family model-free promotion gate.

- rows: `96`
- candidates: `0`
- positive centered-delta rows: `49`
- max bidirectional recordings: `1`
- max bidirectional recording fraction: `0.250`
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
| low_contrast_choice_le_0.25 | thalamic | MFD_06 | reject: target1 | +0.122 | +0.285 | 0.948 | 0.097 | 1/4 |
| low_contrast_choice_le_0.25 | fiber_tracts | KS014 | reject: target0 | +0.030 | +0.059 | 0.384 | 0.634 | 1/4 |
| low_contrast_choice_le_0.125 | fiber_tracts | KS014 | reject: target1 | +0.009 | +0.037 | 0.619 | 0.445 | 1/4 |
| low_contrast_choice_le_0.0625 | fiber_tracts | SWC_038 | reject: shuffle | -0.000 | -0.097 | 0.384 | 0.666 | 1/4 |
| low_contrast_choice_le_0.125 | broad_named_anatomy | SWC_038 | reject: shuffle | -0.001 | -0.003 | 0.527 | 0.525 | 1/4 |
| low_contrast_choice_le_0.25 | broad_named_anatomy | SWC_038 | reject: shuffle | -0.001 | -0.003 | 0.537 | 0.519 | 1/4 |
| low_contrast_choice_le_0.0625 | thalamic | MFD_06 | reject: shuffle | -0.195 | +0.039 | 0.952 | 0.110 | 1/4 |
| low_contrast_choice_le_0.125 | fiber_tracts | CSHL045 | reject: shuffle | -0.228 | +0.055 | 0.846 | 0.203 | 1/4 |
| low_contrast_choice_le_0.125 | hippocampal_formation | CSHL045 | reject: target1 | +0.302 | +0.193 | 1.000 | 0.000 | 0/4 |
| low_contrast_choice_le_0.0625 | hippocampal_formation | CSHL045 | reject: target1 | +0.246 | +0.421 | 1.000 | 0.000 | 0/4 |
| low_contrast_choice_le_0.0625 | thalamic | NYU-12 | reject: target1 | +0.236 | +0.210 | 0.905 | 0.145 | 0/4 |
| low_contrast_choice_le_0.25 | hippocampal_formation | SWC_038 | reject: target0 | +0.212 | +0.288 | 0.159 | 0.938 | 0/4 |
| low_contrast_choice_le_0.0625 | thalamic | KS014 | reject: target1 | +0.161 | +0.115 | 0.885 | 0.177 | 0/4 |
| low_contrast_choice_le_0.125 | thalamic | KS014 | reject: target0 | +0.139 | +0.141 | 0.085 | 0.820 | 0/4 |
| low_contrast_choice_le_0.25 | thalamic | SWC_038 | reject: target1 | +0.109 | +0.172 | 0.855 | 0.065 | 0/4 |
| low_contrast_choice_le_0.125 | fiber_tracts | MFD_06 | reject: target1 | +0.086 | +0.231 | 0.774 | 0.265 | 0/4 |

## Decision

Do not train: low-contrast choice targets do not pass the strict local gate.
