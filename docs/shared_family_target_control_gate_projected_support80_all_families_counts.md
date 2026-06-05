# Shared-Family Target/Control Gate

No-spend model-free screen for the next benchmark redesign. Each row is a single shared anatomical family, target mode, and held-out subject. The true family feature must beat within-recording shuffled labels, beat the total-spike baseline, and satisfy global plus same-recording bidirectional target support.

- rows: `320`
- candidates: `0`
- positive centered-delta rows: `143`
- max bidirectional recordings: `1`
- max bidirectional recording fraction: `0.250`
- decision: `no_shared_family_target_candidate`

## Target Summary

| target | rows | candidates | positive centered delta | max bidir frac |
|---|---:|---:|---:|---:|
| choice | 80 | 0 | 34 | 0.250 |
| feedback | 80 | 0 | 32 | 0.250 |
| prior_side | 80 | 0 | 41 | 0.250 |
| stimulus_side | 80 | 0 | 36 | 0.250 |

## Family Summary

| family | rows | candidates | positive centered delta | max bidir frac |
|---|---:|---:|---:|---:|
| basal_ganglia | 32 | 0 | 12 | 0.000 |
| brainstem_interbrain | 32 | 0 | 16 | 0.250 |
| broad_named_anatomy | 32 | 0 | 13 | 0.250 |
| cortical_retrosplenial | 32 | 0 | 11 | 0.000 |
| cortical_sensorimotor | 32 | 0 | 11 | 0.000 |
| cortical_visual | 32 | 0 | 14 | 0.000 |
| fiber_tracts | 32 | 0 | 18 | 0.250 |
| hippocampal_formation | 32 | 0 | 18 | 0.250 |
| midbrain | 32 | 0 | 15 | 0.000 |
| thalamic | 32 | 0 | 15 | 0.000 |

## Top Rows

| target | family | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs |
|---|---|---|---|---:|---:|---:|---:|---:|
| feedback | broad_named_anatomy | CSHL045 | reject: target1 | +0.038 | +0.031 | 0.825 | 0.309 | 1/4 |
| prior_side | hippocampal_formation | MFD_06 | reject: target1 | +0.029 | +0.036 | 0.708 | 0.376 | 1/4 |
| choice | brainstem_interbrain | MFD_06 | reject: target1 | +0.026 | +0.107 | 0.723 | 0.270 | 1/4 |
| feedback | broad_named_anatomy | NR_0019 | reject: shuffle | +0.003 | +0.001 | 0.474 | 0.639 | 1/4 |
| feedback | broad_named_anatomy | KS014 | reject: shuffle | -0.004 | -0.003 | 0.483 | 0.619 | 1/4 |
| stimulus_side | fiber_tracts | KS014 | reject: shuffle | -0.027 | +0.027 | 0.330 | 0.766 | 1/4 |
| choice | basal_ganglia | NYU-12 | reject: target1 | +0.508 | +0.482 | 1.000 | 0.000 | 0/4 |
| stimulus_side | hippocampal_formation | CSHL045 | reject: target1 | +0.388 | +0.425 | 1.000 | 0.000 | 0/4 |
| stimulus_side | brainstem_interbrain | SWC_038 | reject: target0 | +0.316 | +0.459 | 0.000 | 1.000 | 0/4 |
| stimulus_side | midbrain | SWC_038 | reject: target0 | +0.299 | +0.233 | 0.000 | 1.000 | 0/4 |
| choice | cortical_visual | CSH_ZAD_019 | reject: target0 | +0.296 | +0.419 | 0.000 | 1.000 | 0/4 |
| stimulus_side | cortical_sensorimotor | NR_0019 | reject: target1 | +0.273 | +0.172 | 0.669 | 0.321 | 0/4 |
| prior_side | cortical_sensorimotor | NR_0019 | reject: target1 | +0.263 | +0.256 | 0.661 | 0.337 | 0/4 |
| choice | hippocampal_formation | SWC_038 | reject: target0 | +0.246 | +0.316 | 0.011 | 0.999 | 0/4 |

## Decision

A GPU run is justified only if this screen yields a candidate or a very near miss with clear same-recording bidirectional support. Otherwise the next move is another local target/control redesign.
