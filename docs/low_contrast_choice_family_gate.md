# Low-Contrast Choice Family Gate

Prospective no-spend target redesign: restrict trials by absolute stimulus contrast and classify left-vs-right choice under the unchanged shared-family model-free promotion gate.

- rows: `84`
- candidates: `0`
- positive centered-delta rows: `41`
- max bidirectional recordings: `2`
- max bidirectional recording fraction: `0.500`
- decision: `no_low_contrast_choice_family_candidate`
- gpu training ready: `False`

## Target Balance

| target | trials | eligible recordings | recordings |
|---|---:|---:|---:|
| low_contrast_choice_le_0.0625 | 5938 | 28 | 28 |
| low_contrast_choice_le_0.125 | 9786 | 28 | 28 |
| low_contrast_choice_le_0.25 | 13792 | 28 | 28 |

## Top Rows

| target | family | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs |
|---|---|---|---|---:|---:|---:|---:|---:|
| low_contrast_choice_le_0.125 | fiber_tracts | CSH_ZAD_019 | reject: target0 | +0.209 | +0.215 | 0.545 | 0.629 | 2/4 |
| low_contrast_choice_le_0.25 | broad_named_anatomy | SWC_043 | reject: total baseline | +0.008 | -0.132 | 0.526 | 0.591 | 2/4 |
| low_contrast_choice_le_0.125 | broad_named_anatomy | SWC_043 | reject: total baseline | +0.007 | -0.082 | 0.511 | 0.574 | 2/4 |
| low_contrast_choice_le_0.0625 | fiber_tracts | CSH_ZAD_019 | reject: recording bidirectionality | +0.242 | +0.237 | 0.560 | 0.642 | 1/4 |
| low_contrast_choice_le_0.25 | fiber_tracts | CSH_ZAD_019 | reject: target0 | +0.192 | +0.201 | 0.549 | 0.626 | 1/4 |
| low_contrast_choice_le_0.125 | thalamic | MFD_06 | reject: target0 | +0.177 | +0.183 | 0.062 | 0.919 | 1/4 |
| low_contrast_choice_le_0.0625 | hippocampal_formation | SWC_038 | reject: target0 | +0.163 | +0.317 | 0.189 | 0.954 | 1/4 |
| low_contrast_choice_le_0.0625 | thalamic | MFD_06 | reject: target0 | +0.155 | +0.216 | 0.065 | 0.917 | 1/4 |
| low_contrast_choice_le_0.0625 | fiber_tracts | MFD_06 | reject: target1 | +0.087 | +0.129 | 0.814 | 0.269 | 1/4 |
| low_contrast_choice_le_0.0625 | fiber_tracts | NYU-12 | reject: target1 | +0.044 | +0.014 | 0.640 | 0.325 | 1/4 |
| low_contrast_choice_le_0.0625 | fiber_tracts | SWC_038 | reject: target1 | +0.031 | +0.096 | 0.607 | 0.333 | 1/4 |
| low_contrast_choice_le_0.25 | fiber_tracts | SWC_038 | reject: target1 | +0.021 | +0.124 | 0.675 | 0.367 | 1/4 |
| low_contrast_choice_le_0.125 | broad_named_anatomy | SWC_038 | reject: shuffle | -0.002 | -0.003 | 0.511 | 0.534 | 1/4 |
| low_contrast_choice_le_0.25 | broad_named_anatomy | SWC_038 | reject: shuffle | -0.002 | -0.003 | 0.501 | 0.537 | 1/4 |
| low_contrast_choice_le_0.0625 | hippocampal_formation | KS014 | reject: shuffle | -0.004 | +0.008 | 0.224 | 0.671 | 1/4 |
| low_contrast_choice_le_0.0625 | thalamic | NYU-12 | reject: shuffle | -0.102 | +0.107 | 0.129 | 0.869 | 1/4 |

## Decision

Do not train: low-contrast choice targets do not pass the strict local gate.
