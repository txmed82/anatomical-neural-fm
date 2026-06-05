# Shared-Family Target/Control Gate

No-spend model-free screen for the next benchmark redesign. Each row is a single shared anatomical family, target mode, and held-out subject. The true family feature must beat within-recording shuffled labels, beat the total-spike baseline, and satisfy global plus same-recording bidirectional target support.

- rows: `320`
- candidates: `0`
- positive centered-delta rows: `144`
- max bidirectional recordings: `1`
- max bidirectional recording fraction: `0.250`
- decision: `no_shared_family_target_candidate`

## Target Summary

| target | rows | candidates | positive centered delta | max bidir frac |
|---|---:|---:|---:|---:|
| choice | 80 | 0 | 36 | 0.000 |
| feedback | 80 | 0 | 34 | 0.250 |
| prior_side | 80 | 0 | 38 | 0.000 |
| stimulus_side | 80 | 0 | 36 | 0.000 |

## Family Summary

| family | rows | candidates | positive centered delta | max bidir frac |
|---|---:|---:|---:|---:|
| basal_ganglia | 32 | 0 | 15 | 0.000 |
| brainstem_interbrain | 32 | 0 | 13 | 0.000 |
| broad_named_anatomy | 32 | 0 | 13 | 0.250 |
| cortical_retrosplenial | 32 | 0 | 13 | 0.000 |
| cortical_sensorimotor | 32 | 0 | 12 | 0.000 |
| cortical_visual | 32 | 0 | 15 | 0.250 |
| fiber_tracts | 32 | 0 | 16 | 0.000 |
| hippocampal_formation | 32 | 0 | 16 | 0.000 |
| midbrain | 32 | 0 | 20 | 0.000 |
| thalamic | 32 | 0 | 11 | 0.000 |

## Top Rows

| target | family | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs |
|---|---|---|---|---:|---:|---:|---:|---:|
| feedback | broad_named_anatomy | KS014 | reject: total baseline | +0.147 | -0.134 | 0.139 | 0.924 | 1/4 |
| feedback | cortical_visual | NR_0019 | reject: total baseline | +0.039 | -0.073 | 0.101 | 0.928 | 1/4 |
| choice | basal_ganglia | KS014 | reject: target0 | +0.621 | +0.507 | 0.000 | 1.000 | 0/4 |
| prior_side | cortical_sensorimotor | KS014 | reject: target1 | +0.390 | +0.508 | 1.000 | 0.000 | 0/4 |
| prior_side | basal_ganglia | MFD_06 | reject: target1 | +0.378 | +0.289 | 1.000 | 0.000 | 0/4 |
| prior_side | cortical_visual | SWC_038 | reject: target1 | +0.350 | +0.328 | 0.956 | 0.048 | 0/4 |
| prior_side | cortical_retrosplenial | SWC_038 | reject: target1 | +0.347 | +0.494 | 1.000 | 0.000 | 0/4 |
| choice | basal_ganglia | NYU-12 | reject: target0 | +0.295 | +0.482 | 0.000 | 1.000 | 0/4 |
| prior_side | cortical_sensorimotor | NR_0019 | reject: target1 | +0.267 | +0.270 | 0.661 | 0.337 | 0/4 |
| stimulus_side | hippocampal_formation | SWC_038 | reject: target0 | +0.250 | +0.321 | 0.014 | 0.992 | 0/4 |
| stimulus_side | midbrain | SWC_038 | reject: target0 | +0.215 | +0.288 | 0.000 | 1.000 | 0/4 |
| stimulus_side | midbrain | ZFM-01577 | reject: target0 | +0.199 | +0.216 | 0.205 | 0.747 | 0/3 |
| prior_side | cortical_visual | MFD_06 | reject: target1 | +0.197 | +0.131 | 0.927 | 0.128 | 0/4 |
| feedback | hippocampal_formation | KS014 | reject: total baseline | +0.188 | -0.024 | 1.000 | 0.000 | 0/4 |

## Decision

A GPU run is justified only if this screen yields a candidate or a very near miss with clear same-recording bidirectional support. Otherwise the next move is another local target/control redesign.
