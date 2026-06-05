# Shared-Family Target/Control Gate

No-spend model-free screen for the next benchmark redesign. Each row is a single shared anatomical family, target mode, and held-out subject. The true family feature must beat within-recording shuffled labels, beat the total-spike baseline, and satisfy global plus same-recording bidirectional target support.

- rows: `320`
- candidates: `0`
- positive centered-delta rows: `154`
- max bidirectional recordings: `2`
- max bidirectional recording fraction: `0.500`
- decision: `no_shared_family_target_candidate`

## Target Summary

| target | rows | candidates | positive centered delta | max bidir frac |
|---|---:|---:|---:|---:|
| choice | 80 | 0 | 36 | 0.500 |
| feedback | 80 | 0 | 35 | 0.333 |
| prior_side | 80 | 0 | 47 | 0.333 |
| stimulus_side | 80 | 0 | 36 | 0.333 |

## Family Summary

| family | rows | candidates | positive centered delta | max bidir frac |
|---|---:|---:|---:|---:|
| basal_ganglia | 32 | 0 | 9 | 0.000 |
| brainstem_interbrain | 32 | 0 | 20 | 0.500 |
| broad_named_anatomy | 32 | 0 | 14 | 0.333 |
| cortical_retrosplenial | 32 | 0 | 14 | 0.000 |
| cortical_sensorimotor | 32 | 0 | 15 | 0.000 |
| cortical_visual | 32 | 0 | 14 | 0.250 |
| fiber_tracts | 32 | 0 | 15 | 0.250 |
| hippocampal_formation | 32 | 0 | 23 | 0.500 |
| midbrain | 32 | 0 | 12 | 0.250 |
| thalamic | 32 | 0 | 18 | 0.250 |

## Top Rows

| target | family | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs |
|---|---|---|---|---:|---:|---:|---:|---:|
| choice | brainstem_interbrain | NR_0019 | reject: target1 | +0.134 | +0.305 | 0.721 | 0.416 | 2/4 |
| choice | hippocampal_formation | CSH_ZAD_019 | reject: shuffle | -0.024 | +0.217 | 0.461 | 0.617 | 2/4 |
| prior_side | hippocampal_formation | ZFM-01577 | reject: target1 | +0.041 | +0.102 | 0.648 | 0.408 | 1/3 |
| choice | hippocampal_formation | ZFM-01577 | reject: target0 | +0.036 | +0.146 | 0.429 | 0.697 | 1/3 |
| stimulus_side | hippocampal_formation | ZFM-01577 | reject: target0 | +0.032 | +0.069 | 0.444 | 0.669 | 1/3 |
| prior_side | broad_named_anatomy | ZFM-01577 | reject: shuffle | +0.007 | +0.038 | 0.536 | 0.568 | 1/3 |
| feedback | broad_named_anatomy | ZFM-01577 | reject: shuffle | -0.001 | +0.036 | 0.563 | 0.521 | 1/3 |
| feedback | brainstem_interbrain | NYU-12 | reject: target0 | +0.070 | +0.082 | 0.460 | 0.644 | 1/4 |
| feedback | brainstem_interbrain | KS014 | reject: total baseline | +0.064 | -0.108 | 0.761 | 0.404 | 1/4 |
| stimulus_side | brainstem_interbrain | KS014 | reject: total baseline | +0.050 | -0.050 | 0.418 | 0.655 | 1/4 |
| prior_side | fiber_tracts | CSHL045 | reject: target1 | +0.048 | +0.078 | 0.814 | 0.162 | 1/4 |
| choice | hippocampal_formation | MFD_06 | reject: target0 | +0.044 | +0.070 | 0.330 | 0.698 | 1/4 |
| choice | broad_named_anatomy | SWC_038 | reject: target0 | +0.034 | +0.040 | 0.549 | 0.514 | 1/4 |
| choice | brainstem_interbrain | KS014 | reject: total baseline | +0.033 | -0.044 | 0.403 | 0.606 | 1/4 |

## Decision

A GPU run is justified only if this screen yields a candidate or a very near miss with clear same-recording bidirectional support. Otherwise the next move is another local target/control redesign.
