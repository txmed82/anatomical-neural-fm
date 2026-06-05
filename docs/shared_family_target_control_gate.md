# Shared-Family Target/Control Gate

No-spend model-free screen for the next benchmark redesign. Each row is a single shared anatomical family, target mode, and held-out subject. The true family feature must beat within-recording shuffled labels, beat the total-spike baseline, and satisfy global plus same-recording bidirectional target support.

- rows: `112`
- candidates: `0`
- positive centered-delta rows: `55`
- max bidirectional recordings: `2`
- max bidirectional recording fraction: `0.500`
- decision: `no_shared_family_target_candidate`

## Target Summary

| target | rows | candidates | positive centered delta | max bidir frac |
|---|---:|---:|---:|---:|
| choice | 28 | 0 | 14 | 0.500 |
| feedback | 28 | 0 | 10 | 0.500 |
| prior_side | 28 | 0 | 19 | 0.250 |
| stimulus_side | 28 | 0 | 12 | 0.250 |

## Family Summary

| family | rows | candidates | positive centered delta | max bidir frac |
|---|---:|---:|---:|---:|
| broad_named_anatomy | 28 | 0 | 13 | 0.500 |
| fiber_tracts | 28 | 0 | 15 | 0.250 |
| hippocampal_formation | 28 | 0 | 13 | 0.250 |
| thalamic | 28 | 0 | 14 | 0.250 |

## Top Rows

| target | family | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs |
|---|---|---|---|---:|---:|---:|---:|---:|
| choice | broad_named_anatomy | SWC_043 | reject: shuffle | +0.008 | -0.160 | 0.534 | 0.610 | 2/4 |
| feedback | broad_named_anatomy | NYU-12 | reject: shuffle | -0.002 | -0.008 | 0.540 | 0.554 | 2/4 |
| choice | fiber_tracts | CSH_ZAD_019 | reject: recording bidirectionality | +0.199 | +0.221 | 0.558 | 0.614 | 1/4 |
| stimulus_side | thalamic | MFD_06 | reject: target0 | +0.179 | +0.269 | 0.089 | 0.930 | 1/4 |
| prior_side | hippocampal_formation | MFD_06 | reject: target1 | +0.065 | +0.031 | 0.689 | 0.359 | 1/4 |
| stimulus_side | hippocampal_formation | MFD_06 | reject: target0 | +0.053 | +0.042 | 0.432 | 0.666 | 1/4 |
| prior_side | fiber_tracts | KS014 | reject: target1 | +0.036 | +0.081 | 0.647 | 0.373 | 1/4 |
| choice | fiber_tracts | SWC_038 | reject: target1 | +0.016 | +0.128 | 0.638 | 0.387 | 1/4 |
| feedback | hippocampal_formation | NR_0019 | reject: total baseline | +0.013 | -0.011 | 0.919 | 0.176 | 1/4 |
| prior_side | broad_named_anatomy | MFD_06 | reject: shuffle | +0.005 | -0.008 | 0.517 | 0.464 | 1/4 |
| feedback | broad_named_anatomy | SWC_043 | reject: shuffle | +0.003 | +0.007 | 0.554 | 0.559 | 1/4 |
| feedback | broad_named_anatomy | NR_0019 | reject: shuffle | +0.003 | +0.001 | 0.465 | 0.532 | 1/4 |
| choice | broad_named_anatomy | SWC_038 | reject: shuffle | -0.001 | -0.003 | 0.504 | 0.542 | 1/4 |
| stimulus_side | broad_named_anatomy | MFD_06 | reject: shuffle | -0.005 | -0.009 | 0.573 | 0.443 | 1/4 |

## Decision

A GPU run is justified only if this screen yields a candidate or a very near miss with clear same-recording bidirectional support. Otherwise the next move is another local target/control redesign.
