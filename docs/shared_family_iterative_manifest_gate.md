# Shared-Family Target/Control Gate

No-spend model-free screen for the next benchmark redesign. Each row is a single shared anatomical family, target mode, and held-out subject. The true family feature must beat within-recording shuffled labels, beat the total-spike baseline, and satisfy global plus same-recording bidirectional target support.

- rows: `56`
- candidates: `0`
- positive centered-delta rows: `20`
- max bidirectional recordings: `1`
- max bidirectional recording fraction: `0.250`
- decision: `no_shared_family_target_candidate`

## Target Summary

| target | rows | candidates | positive centered delta | max bidir frac |
|---|---:|---:|---:|---:|
| choice | 14 | 0 | 5 | 0.000 |
| feedback | 14 | 0 | 5 | 0.250 |
| prior_side | 14 | 0 | 5 | 0.250 |
| stimulus_side | 14 | 0 | 5 | 0.250 |

## Family Summary

| family | rows | candidates | positive centered delta | max bidir frac |
|---|---:|---:|---:|---:|
| brainstem_interbrain | 8 | 0 | 1 | 0.250 |
| broad_named_anatomy | 8 | 0 | 1 | 0.250 |
| cortical_visual | 8 | 0 | 3 | 0.250 |
| fiber_tracts | 8 | 0 | 5 | 0.250 |
| hippocampal_formation | 8 | 0 | 5 | 0.000 |
| midbrain | 8 | 0 | 3 | 0.250 |
| thalamic | 8 | 0 | 2 | 0.250 |

## Top Rows

| target | family | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs |
|---|---|---|---|---:|---:|---:|---:|---:|
| prior_side | thalamic | MFD_06 | reject: target1 | +0.299 | +0.362 | 0.954 | 0.095 | 1/4 |
| feedback | fiber_tracts | NYU-12 | reject: target0 | +0.168 | +0.049 | 0.415 | 0.703 | 1/4 |
| feedback | midbrain | NYU-12 | reject: target1 | +0.151 | +0.092 | 0.813 | 0.263 | 1/4 |
| stimulus_side | thalamic | MFD_06 | reject: target1 | +0.101 | +0.349 | 0.934 | 0.108 | 1/4 |
| prior_side | brainstem_interbrain | MFD_06 | reject: shuffle | +0.001 | -0.001 | 0.755 | 0.335 | 1/4 |
| feedback | broad_named_anatomy | NYU-12 | reject: shuffle | -0.002 | -0.008 | 0.571 | 0.476 | 1/4 |
| feedback | cortical_visual | MFD_06 | reject: shuffle | -0.002 | -0.036 | 0.231 | 0.804 | 1/4 |
| prior_side | broad_named_anatomy | MFD_06 | reject: shuffle | -0.005 | +0.008 | 0.597 | 0.445 | 1/4 |
| stimulus_side | broad_named_anatomy | MFD_06 | reject: shuffle | -0.005 | -0.010 | 0.610 | 0.422 | 1/4 |
| feedback | fiber_tracts | MFD_06 | reject: shuffle | -0.023 | +0.058 | 0.728 | 0.227 | 1/4 |
| prior_side | cortical_visual | MFD_06 | reject: target1 | +0.075 | +0.174 | 0.765 | 0.155 | 0/4 |
| prior_side | hippocampal_formation | MFD_06 | reject: target1 | +0.065 | +0.045 | 0.681 | 0.360 | 0/4 |
| choice | fiber_tracts | MFD_06 | reject: target1 | +0.060 | +0.166 | 0.786 | 0.211 | 0/4 |
| prior_side | fiber_tracts | MFD_06 | reject: target0 | +0.056 | +0.097 | 0.171 | 0.754 | 0/4 |

## Decision

A GPU run is justified only if this screen yields a candidate or a very near miss with clear same-recording bidirectional support. Otherwise the next move is another local target/control redesign.
