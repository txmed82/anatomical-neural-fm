# Low-Contrast Choice Family Gate

Prospective no-spend target redesign: restrict trials by absolute stimulus contrast and classify left-vs-right choice under the unchanged shared-family model-free promotion gate.

- rows: `96`
- candidates: `0`
- positive centered-delta rows: `57`
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
| low_contrast_choice_le_0.0625 | fiber_tracts | CSH_ZAD_019 | reject: recording bidirectionality | +0.038 | +0.237 | 0.567 | 0.640 | 2/4 |
| low_contrast_choice_le_0.125 | thalamic | MFD_06 | reject: target1 | +0.234 | +0.263 | 0.953 | 0.115 | 1/4 |
| low_contrast_choice_le_0.125 | hippocampal_formation | SWC_038 | reject: target1 | +0.171 | +0.230 | 0.884 | 0.069 | 1/4 |
| low_contrast_choice_le_0.0625 | fiber_tracts | NYU-12 | reject: target1 | +0.079 | +0.033 | 0.658 | 0.399 | 1/4 |
| low_contrast_choice_le_0.0625 | hippocampal_formation | SWC_038 | reject: target0 | +0.048 | +0.059 | 0.204 | 0.951 | 1/4 |
| low_contrast_choice_le_0.125 | fiber_tracts | NYU-12 | reject: target1 | +0.033 | +0.054 | 0.646 | 0.375 | 1/4 |
| low_contrast_choice_le_0.25 | fiber_tracts | NYU-12 | reject: target1 | +0.027 | +0.058 | 0.647 | 0.379 | 1/4 |
| low_contrast_choice_le_0.125 | fiber_tracts | CSH_ZAD_019 | reject: target0 | +0.025 | +0.215 | 0.532 | 0.570 | 1/4 |
| low_contrast_choice_le_0.25 | fiber_tracts | CSH_ZAD_019 | reject: target0 | +0.021 | +0.201 | 0.531 | 0.524 | 1/4 |
| low_contrast_choice_le_0.0625 | hippocampal_formation | CSH_ZAD_019 | reject: target0 | +0.007 | +0.207 | 0.447 | 0.642 | 1/4 |
| low_contrast_choice_le_0.0625 | thalamic | NYU-12 | reject: target0 | +0.005 | +0.210 | 0.126 | 0.872 | 1/4 |
| low_contrast_choice_le_0.25 | fiber_tracts | SWC_038 | reject: target1 | +0.001 | +0.090 | 0.666 | 0.371 | 1/4 |
| low_contrast_choice_le_0.125 | broad_named_anatomy | SWC_038 | reject: shuffle | -0.002 | -0.003 | 0.491 | 0.522 | 1/4 |
| low_contrast_choice_le_0.0625 | thalamic | MFD_06 | reject: shuffle | -0.002 | +0.039 | 0.065 | 0.917 | 1/4 |
| low_contrast_choice_le_0.25 | broad_named_anatomy | SWC_038 | reject: shuffle | -0.003 | -0.003 | 0.495 | 0.513 | 1/4 |
| low_contrast_choice_le_0.0625 | fiber_tracts | SWC_038 | reject: shuffle | -0.004 | -0.097 | 0.616 | 0.344 | 1/4 |

## Decision

Do not train: low-contrast choice targets do not pass the strict local gate.
