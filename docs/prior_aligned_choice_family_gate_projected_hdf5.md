# Prior-Aligned Choice Family Gate

Prospective no-spend target redesign: restrict trials by absolute stimulus contrast and classify whether choice aligns with the biased block prior under the unchanged shared-family model-free promotion gate.

- rows: `128`
- candidates: `0`
- positive centered-delta rows: `56`
- max bidirectional recordings: `1`
- max bidirectional recording fraction: `0.250`
- decision: `no_prior_aligned_choice_family_candidate`
- gpu training ready: `False`

## Target Balance

| target | trials | eligible recordings | recordings |
|---|---:|---:|---:|
| prior_aligned_choice_le_0.0625 | 5984 | 27 | 31 |
| prior_aligned_choice_le_0.125 | 9834 | 31 | 31 |
| prior_aligned_choice_le_0.25 | 13842 | 31 | 31 |
| prior_aligned_choice_le_1 | 17870 | 31 | 31 |

## Top Rows

| target | family | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs |
|---|---|---|---|---:|---:|---:|---:|---:|
| prior_aligned_choice_le_0.0625 | hippocampal_formation | CSH_ZAD_019 | reject: total baseline | +0.066 | -0.072 | 0.445 | 0.708 | 1/4 |
| prior_aligned_choice_le_0.125 | hippocampal_formation | CSH_ZAD_019 | reject: total baseline | +0.044 | -0.052 | 0.607 | 0.445 | 1/4 |
| prior_aligned_choice_le_0.125 | thalamic | CSHL045 | reject: target1 | +0.032 | +0.042 | 0.775 | 0.253 | 1/4 |
| prior_aligned_choice_le_0.25 | thalamic | CSHL045 | reject: target1 | +0.029 | +0.024 | 0.777 | 0.254 | 1/4 |
| prior_aligned_choice_le_0.0625 | broad_named_anatomy | MFD_06 | reject: target1 | +0.009 | +0.010 | 0.571 | 0.478 | 1/4 |
| prior_aligned_choice_le_0.125 | broad_named_anatomy | CSHL045 | reject: target1 | +0.008 | +0.011 | 0.625 | 0.431 | 1/4 |
| prior_aligned_choice_le_0.0625 | broad_named_anatomy | NR_0019 | reject: recording bidirectionality | +0.004 | +0.002 | 0.551 | 0.564 | 1/4 |
| prior_aligned_choice_le_0.125 | broad_named_anatomy | NR_0019 | reject: target0 | +0.003 | +0.001 | 0.536 | 0.521 | 1/4 |
| prior_aligned_choice_le_0.25 | broad_named_anatomy | NR_0019 | reject: target0 | +0.003 | +0.001 | 0.534 | 0.504 | 1/4 |
| prior_aligned_choice_le_0.0625 | broad_named_anatomy | CSHL045 | reject: target1 | +0.002 | +0.004 | 0.621 | 0.476 | 1/4 |
| prior_aligned_choice_le_1 | broad_named_anatomy | NR_0019 | reject: target0 | +0.002 | +0.001 | 0.535 | 0.502 | 1/4 |
| prior_aligned_choice_le_1 | broad_named_anatomy | KS014 | reject: shuffle | -0.001 | -0.001 | 0.510 | 0.547 | 1/4 |
| prior_aligned_choice_le_0.125 | broad_named_anatomy | SWC_038 | reject: shuffle | -0.001 | +0.142 | 0.479 | 0.589 | 1/4 |
| prior_aligned_choice_le_1 | broad_named_anatomy | SWC_038 | reject: shuffle | -0.001 | -0.002 | 0.497 | 0.612 | 1/4 |
| prior_aligned_choice_le_0.0625 | broad_named_anatomy | SWC_038 | reject: shuffle | -0.002 | +0.127 | 0.474 | 0.604 | 1/4 |
| prior_aligned_choice_le_0.25 | broad_named_anatomy | SWC_038 | reject: shuffle | -0.002 | -0.003 | 0.503 | 0.619 | 1/4 |

## Decision

Do not train: prior-aligned choice targets do not pass the strict local gate.
