# Correct Low-Contrast Choice Family Gate

Prospective no-spend target redesign: restrict trials by absolute stimulus contrast, keep correct trials, and classify left-vs-right choice under the unchanged shared-family model-free promotion gate.

- rows: `84`
- candidates: `0`
- positive centered-delta rows: `45`
- max bidirectional recordings: `2`
- max bidirectional recording fraction: `0.500`
- decision: `no_correct_low_contrast_choice_family_candidate`
- gpu training ready: `False`

## Target Balance

| target | trials | eligible recordings | recordings |
|---|---:|---:|---:|
| correct_low_contrast_choice_le_0.0625 | 3948 | 22 | 28 |
| correct_low_contrast_choice_le_0.125 | 7137 | 28 | 28 |
| correct_low_contrast_choice_le_0.25 | 10718 | 28 | 28 |

## Top Rows

| target | family | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs |
|---|---|---|---|---:|---:|---:|---:|---:|
| correct_low_contrast_choice_le_0.25 | fiber_tracts | SWC_038 | reject: target1 | +0.016 | +0.130 | 0.665 | 0.381 | 2/4 |
| correct_low_contrast_choice_le_0.25 | broad_named_anatomy | SWC_043 | reject: total baseline | +0.009 | -0.147 | 0.539 | 0.598 | 2/4 |
| correct_low_contrast_choice_le_0.25 | fiber_tracts | CSH_ZAD_019 | reject: target0 | +0.007 | +0.150 | 0.520 | 0.582 | 2/4 |
| correct_low_contrast_choice_le_0.125 | fiber_tracts | CSH_ZAD_019 | reject: target0 | +0.006 | +0.161 | 0.526 | 0.601 | 2/4 |
| correct_low_contrast_choice_le_0.0625 | thalamic | NYU-12 | reject: target0 | +0.253 | +0.238 | 0.139 | 0.878 | 1/4 |
| correct_low_contrast_choice_le_0.0625 | hippocampal_formation | SWC_038 | reject: target0 | +0.252 | +0.308 | 0.194 | 0.963 | 1/4 |
| correct_low_contrast_choice_le_0.0625 | fiber_tracts | CSH_ZAD_019 | reject: recording bidirectionality | +0.191 | +0.175 | 0.559 | 0.612 | 1/4 |
| correct_low_contrast_choice_le_0.0625 | hippocampal_formation | MFD_06 | reject: target0 | +0.059 | +0.108 | 0.332 | 0.731 | 1/4 |
| correct_low_contrast_choice_le_0.0625 | fiber_tracts | NYU-12 | reject: target0 | +0.021 | +0.036 | 0.413 | 0.634 | 1/4 |
| correct_low_contrast_choice_le_0.0625 | hippocampal_formation | CSH_ZAD_019 | reject: target0 | +0.020 | +0.206 | 0.465 | 0.560 | 1/4 |
| correct_low_contrast_choice_le_0.0625 | broad_named_anatomy | SWC_043 | reject: target0 | +0.011 | +0.004 | 0.542 | 0.547 | 1/4 |
| correct_low_contrast_choice_le_0.125 | broad_named_anatomy | SWC_043 | reject: total baseline | +0.010 | -0.086 | 0.520 | 0.582 | 1/4 |
| correct_low_contrast_choice_le_0.25 | fiber_tracts | KS014 | reject: target1 | +0.009 | +0.100 | 0.568 | 0.426 | 1/4 |
| correct_low_contrast_choice_le_0.125 | fiber_tracts | KS014 | reject: target1 | +0.008 | +0.079 | 0.559 | 0.438 | 1/4 |
| correct_low_contrast_choice_le_0.125 | broad_named_anatomy | SWC_038 | reject: shuffle | -0.000 | -0.002 | 0.489 | 0.529 | 1/4 |
| correct_low_contrast_choice_le_0.25 | broad_named_anatomy | SWC_038 | reject: shuffle | -0.002 | -0.003 | 0.493 | 0.527 | 1/4 |

## Decision

Do not train: correct low-contrast choice targets do not pass the strict local gate.
