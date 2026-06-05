# Low-Contrast Choice Family Gate

Prospective no-spend target redesign: restrict trials by absolute stimulus contrast and classify left-vs-right choice under the unchanged shared-family model-free promotion gate.

- rows: `96`
- candidates: `1`
- positive centered-delta rows: `48`
- max bidirectional recordings: `3`
- max bidirectional recording fraction: `0.750`
- decision: `low_contrast_choice_family_candidate`
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
| low_contrast_choice_le_0.125 | fiber_tracts | CSH_ZAD_019 | candidate | +0.021 | +0.215 | 0.552 | 0.593 | 3/4 |
| low_contrast_choice_le_0.0625 | fiber_tracts | CSH_ZAD_019 | reject: target0 | +0.014 | +0.237 | 0.538 | 0.645 | 2/4 |
| low_contrast_choice_le_0.125 | fiber_tracts | ZFM-01577 | reject: target1 | +0.013 | +0.077 | 0.656 | 0.414 | 1/3 |
| low_contrast_choice_le_0.125 | thalamic | MFD_06 | reject: target0 | +0.082 | +0.263 | 0.061 | 0.919 | 1/4 |
| low_contrast_choice_le_0.0625 | fiber_tracts | NYU-12 | reject: target1 | +0.054 | +0.033 | 0.640 | 0.325 | 1/4 |
| low_contrast_choice_le_0.125 | broad_named_anatomy | SWC_038 | reject: shuffle | -0.002 | -0.003 | 0.501 | 0.538 | 1/4 |
| low_contrast_choice_le_0.25 | broad_named_anatomy | SWC_038 | reject: shuffle | -0.002 | -0.003 | 0.506 | 0.527 | 1/4 |
| low_contrast_choice_le_0.0625 | fiber_tracts | SWC_038 | reject: shuffle | -0.019 | -0.097 | 0.607 | 0.334 | 1/4 |
| low_contrast_choice_le_0.0625 | hippocampal_formation | SWC_038 | reject: shuffle | -0.022 | +0.059 | 0.189 | 0.954 | 1/4 |
| low_contrast_choice_le_0.0625 | fiber_tracts | MFD_06 | reject: shuffle | -0.066 | +0.070 | 0.814 | 0.266 | 1/4 |
| low_contrast_choice_le_0.0625 | fiber_tracts | CSHL045 | reject: target1 | +0.260 | +0.316 | 0.851 | 0.163 | 0/4 |
| low_contrast_choice_le_0.25 | thalamic | MFD_06 | reject: target0 | +0.225 | +0.285 | 0.065 | 0.919 | 0/4 |
| low_contrast_choice_le_0.25 | fiber_tracts | MFD_06 | reject: target1 | +0.222 | +0.227 | 0.811 | 0.233 | 0/4 |
| low_contrast_choice_le_0.25 | hippocampal_formation | SWC_038 | reject: target0 | +0.199 | +0.288 | 0.164 | 0.938 | 0/4 |
| low_contrast_choice_le_0.0625 | thalamic | NYU-12 | reject: target0 | +0.182 | +0.210 | 0.123 | 0.861 | 0/4 |
| low_contrast_choice_le_0.125 | fiber_tracts | MFD_06 | reject: target1 | +0.122 | +0.231 | 0.814 | 0.255 | 0/4 |

## Decision

Validate low-contrast choice candidates across shuffle seeds before GPU training.
