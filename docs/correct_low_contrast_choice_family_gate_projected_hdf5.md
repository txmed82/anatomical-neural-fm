# Correct Low-Contrast Choice Family Gate

Prospective no-spend target redesign: restrict trials by absolute stimulus contrast, keep correct trials, and classify left-vs-right choice under the unchanged shared-family model-free promotion gate.

- rows: `96`
- candidates: `0`
- positive centered-delta rows: `52`
- max bidirectional recordings: `1`
- max bidirectional recording fraction: `0.333`
- decision: `no_correct_low_contrast_choice_family_candidate`
- gpu training ready: `False`

## Target Balance

| target | trials | eligible recordings | recordings |
|---|---:|---:|---:|
| correct_low_contrast_choice_le_0.0625 | 4565 | 24 | 31 |
| correct_low_contrast_choice_le_0.125 | 8287 | 31 | 31 |
| correct_low_contrast_choice_le_0.25 | 12449 | 31 | 31 |

## Top Rows

| target | family | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs |
|---|---|---|---|---:|---:|---:|---:|---:|
| correct_low_contrast_choice_le_0.25 | fiber_tracts | ZFM-01577 | reject: target1 | +0.022 | +0.085 | 0.675 | 0.411 | 1/3 |
| correct_low_contrast_choice_le_0.125 | fiber_tracts | ZFM-01577 | reject: target1 | +0.018 | +0.095 | 0.657 | 0.426 | 1/3 |
| correct_low_contrast_choice_le_0.0625 | hippocampal_formation | SWC_038 | reject: target0 | +0.069 | +0.029 | 0.194 | 0.963 | 1/4 |
| correct_low_contrast_choice_le_0.0625 | hippocampal_formation | MFD_06 | reject: target0 | +0.065 | +0.061 | 0.338 | 0.716 | 1/4 |
| correct_low_contrast_choice_le_0.0625 | thalamic | NYU-12 | reject: target1 | +0.039 | +0.063 | 0.900 | 0.163 | 1/4 |
| correct_low_contrast_choice_le_0.0625 | fiber_tracts | NYU-12 | reject: target0 | +0.032 | +0.037 | 0.426 | 0.622 | 1/4 |
| correct_low_contrast_choice_le_0.0625 | hippocampal_formation | NYU-12 | reject: target0 | +0.017 | +0.013 | 0.383 | 0.626 | 1/4 |
| correct_low_contrast_choice_le_0.0625 | broad_named_anatomy | MFD_06 | reject: target0 | +0.009 | +0.061 | 0.437 | 0.562 | 1/4 |
| correct_low_contrast_choice_le_0.125 | broad_named_anatomy | MFD_06 | reject: target0 | +0.006 | +0.056 | 0.442 | 0.565 | 1/4 |
| correct_low_contrast_choice_le_0.0625 | hippocampal_formation | CSH_ZAD_019 | reject: target0 | +0.003 | +0.191 | 0.462 | 0.557 | 1/4 |
| correct_low_contrast_choice_le_0.125 | fiber_tracts | KS014 | reject: target1 | +0.000 | +0.074 | 0.563 | 0.428 | 1/4 |
| correct_low_contrast_choice_le_0.125 | broad_named_anatomy | SWC_038 | reject: shuffle | -0.000 | -0.002 | 0.495 | 0.524 | 1/4 |
| correct_low_contrast_choice_le_0.25 | broad_named_anatomy | SWC_038 | reject: shuffle | -0.002 | -0.003 | 0.494 | 0.529 | 1/4 |
| correct_low_contrast_choice_le_0.0625 | fiber_tracts | CSH_ZAD_019 | reject: shuffle | -0.004 | +0.175 | 0.522 | 0.598 | 1/4 |
| correct_low_contrast_choice_le_0.0625 | fiber_tracts | SWC_038 | reject: shuffle | -0.021 | -0.035 | 0.423 | 0.672 | 1/4 |
| correct_low_contrast_choice_le_0.25 | hippocampal_formation | CSHL045 | reject: target0 | +0.540 | +0.557 | 0.000 | 1.000 | 0/4 |

## Decision

Do not train: correct low-contrast choice targets do not pass the strict local gate.
