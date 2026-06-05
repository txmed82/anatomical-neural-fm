# Prior-Aligned Choice Family Gate

Prospective no-spend target redesign: restrict trials by absolute stimulus contrast and classify whether choice aligns with the biased block prior under the unchanged shared-family model-free promotion gate.

- rows: `112`
- candidates: `0`
- positive centered-delta rows: `52`
- max bidirectional recordings: `2`
- max bidirectional recording fraction: `0.500`
- decision: `no_prior_aligned_choice_family_candidate`
- gpu training ready: `False`

## Target Balance

| target | trials | eligible recordings | recordings |
|---|---:|---:|---:|
| prior_aligned_choice_le_0.0625 | 5098 | 24 | 28 |
| prior_aligned_choice_le_0.125 | 8386 | 28 | 28 |
| prior_aligned_choice_le_0.25 | 11832 | 28 | 28 |
| prior_aligned_choice_le_1 | 15266 | 28 | 28 |

## Top Rows

| target | family | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs |
|---|---|---|---|---:|---:|---:|---:|---:|
| prior_aligned_choice_le_0.25 | fiber_tracts | SWC_043 | reject: target0 | +0.011 | +0.004 | 0.505 | 0.484 | 2/4 |
| prior_aligned_choice_le_0.0625 | fiber_tracts | SWC_043 | reject: shuffle | -0.002 | -0.009 | 0.506 | 0.455 | 2/4 |
| prior_aligned_choice_le_0.25 | broad_named_anatomy | SWC_043 | reject: shuffle | -0.005 | -0.004 | 0.563 | 0.495 | 2/4 |
| prior_aligned_choice_le_0.0625 | hippocampal_formation | CSH_ZAD_019 | reject: total baseline | +0.105 | -0.065 | 0.425 | 0.682 | 1/4 |
| prior_aligned_choice_le_0.125 | hippocampal_formation | CSH_ZAD_019 | reject: total baseline | +0.067 | -0.049 | 0.603 | 0.433 | 1/4 |
| prior_aligned_choice_le_0.125 | fiber_tracts | SWC_043 | reject: total baseline | +0.004 | -0.015 | 0.504 | 0.478 | 1/4 |
| prior_aligned_choice_le_0.0625 | broad_named_anatomy | NR_0019 | reject: target1 | +0.004 | +0.002 | 0.558 | 0.513 | 1/4 |
| prior_aligned_choice_le_0.125 | broad_named_anatomy | NR_0019 | reject: target0 | +0.004 | +0.001 | 0.526 | 0.509 | 1/4 |
| prior_aligned_choice_le_0.25 | broad_named_anatomy | NR_0019 | reject: target0 | +0.003 | +0.001 | 0.532 | 0.511 | 1/4 |
| prior_aligned_choice_le_1 | broad_named_anatomy | NR_0019 | reject: target0 | +0.002 | +0.001 | 0.536 | 0.496 | 1/4 |
| prior_aligned_choice_le_1 | broad_named_anatomy | KS014 | reject: shuffle | -0.001 | -0.001 | 0.513 | 0.545 | 1/4 |
| prior_aligned_choice_le_1 | broad_named_anatomy | SWC_038 | reject: shuffle | -0.001 | -0.002 | 0.498 | 0.612 | 1/4 |
| prior_aligned_choice_le_0.25 | broad_named_anatomy | SWC_038 | reject: shuffle | -0.002 | -0.003 | 0.500 | 0.608 | 1/4 |
| prior_aligned_choice_le_0.0625 | broad_named_anatomy | NYU-12 | reject: shuffle | -0.004 | -0.004 | 0.480 | 0.541 | 1/4 |
| prior_aligned_choice_le_0.125 | broad_named_anatomy | SWC_043 | reject: shuffle | -0.005 | -0.003 | 0.557 | 0.512 | 1/4 |
| prior_aligned_choice_le_0.0625 | broad_named_anatomy | CSH_ZAD_019 | reject: shuffle | -0.005 | -0.000 | 0.490 | 0.542 | 1/4 |

## Decision

Do not train: prior-aligned choice targets do not pass the strict local gate.
