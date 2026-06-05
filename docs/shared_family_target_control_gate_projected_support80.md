# Shared-Family Target/Control Gate

No-spend model-free screen for the next benchmark redesign. Each row is a single shared anatomical family, target mode, and held-out subject. The true family feature must beat within-recording shuffled labels, beat the total-spike baseline, and satisfy global plus same-recording bidirectional target support.

- rows: `128`
- candidates: `0`
- positive centered-delta rows: `69`
- max bidirectional recordings: `2`
- max bidirectional recording fraction: `0.500`
- decision: `no_shared_family_target_candidate`

## Target Summary

| target | rows | candidates | positive centered delta | max bidir frac |
|---|---:|---:|---:|---:|
| choice | 32 | 0 | 21 | 0.250 |
| feedback | 32 | 0 | 15 | 0.500 |
| prior_side | 32 | 0 | 17 | 0.250 |
| stimulus_side | 32 | 0 | 16 | 0.250 |

## Family Summary

| family | rows | candidates | positive centered delta | max bidir frac |
|---|---:|---:|---:|---:|
| broad_named_anatomy | 32 | 0 | 13 | 0.500 |
| fiber_tracts | 32 | 0 | 17 | 0.250 |
| hippocampal_formation | 32 | 0 | 18 | 0.250 |
| thalamic | 32 | 0 | 21 | 0.250 |

## Top Rows

| target | family | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs |
|---|---|---|---|---:|---:|---:|---:|---:|
| feedback | broad_named_anatomy | CSHL045 | reject: target0 | +0.038 | +0.031 | 0.516 | 0.645 | 2/4 |
| feedback | broad_named_anatomy | NYU-12 | reject: shuffle | -0.002 | -0.008 | 0.529 | 0.559 | 2/4 |
| stimulus_side | hippocampal_formation | MFD_06 | reject: target0 | +0.028 | +0.038 | 0.419 | 0.676 | 1/4 |
| feedback | thalamic | CSHL045 | reject: total baseline | +0.027 | -0.050 | 0.633 | 0.457 | 1/4 |
| prior_side | fiber_tracts | KS014 | reject: target1 | +0.021 | +0.073 | 0.649 | 0.367 | 1/4 |
| feedback | hippocampal_formation | NR_0019 | reject: shuffle | +0.007 | -0.017 | 0.260 | 0.829 | 1/4 |
| feedback | broad_named_anatomy | NR_0019 | reject: shuffle | +0.003 | +0.001 | 0.465 | 0.534 | 1/4 |
| prior_side | fiber_tracts | SWC_038 | reject: shuffle | +0.001 | +0.079 | 0.678 | 0.404 | 1/4 |
| choice | broad_named_anatomy | SWC_038 | reject: shuffle | -0.001 | -0.003 | 0.512 | 0.538 | 1/4 |
| prior_side | broad_named_anatomy | MFD_06 | reject: shuffle | -0.005 | +0.008 | 0.601 | 0.443 | 1/4 |
| stimulus_side | broad_named_anatomy | MFD_06 | reject: shuffle | -0.005 | -0.009 | 0.572 | 0.443 | 1/4 |
| feedback | broad_named_anatomy | CSH_ZAD_019 | reject: shuffle | -0.005 | -0.008 | 0.536 | 0.507 | 1/4 |
| stimulus_side | broad_named_anatomy | KS014 | reject: shuffle | -0.008 | -0.010 | 0.414 | 0.541 | 1/4 |
| prior_side | thalamic | MFD_06 | reject: shuffle | -0.023 | +0.357 | 0.087 | 0.946 | 1/4 |

## Decision

A GPU run is justified only if this screen yields a candidate or a very near miss with clear same-recording bidirectional support. Otherwise the next move is another local target/control redesign.
