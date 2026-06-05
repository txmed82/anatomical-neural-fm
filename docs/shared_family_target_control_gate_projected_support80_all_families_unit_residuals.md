# Shared-Family Target/Control Gate

No-spend model-free screen for the next benchmark redesign. Each row is a single shared anatomical family, target mode, and held-out subject. The true family feature must beat within-recording shuffled labels, beat the total-spike baseline, and satisfy global plus same-recording bidirectional target support.

- rows: `320`
- candidates: `0`
- positive centered-delta rows: `135`
- max bidirectional recordings: `1`
- max bidirectional recording fraction: `0.250`
- decision: `no_shared_family_target_candidate`

## Target Summary

| target | rows | candidates | positive centered delta | max bidir frac |
|---|---:|---:|---:|---:|
| choice | 80 | 0 | 27 | 0.250 |
| feedback | 80 | 0 | 42 | 0.250 |
| prior_side | 80 | 0 | 32 | 0.250 |
| stimulus_side | 80 | 0 | 34 | 0.250 |

## Family Summary

| family | rows | candidates | positive centered delta | max bidir frac |
|---|---:|---:|---:|---:|
| basal_ganglia | 32 | 0 | 14 | 0.250 |
| brainstem_interbrain | 32 | 0 | 9 | 0.250 |
| broad_named_anatomy | 32 | 0 | 10 | 0.250 |
| cortical_retrosplenial | 32 | 0 | 18 | 0.000 |
| cortical_sensorimotor | 32 | 0 | 14 | 0.000 |
| cortical_visual | 32 | 0 | 17 | 0.250 |
| fiber_tracts | 32 | 0 | 11 | 0.250 |
| hippocampal_formation | 32 | 0 | 13 | 0.000 |
| midbrain | 32 | 0 | 16 | 0.000 |
| thalamic | 32 | 0 | 13 | 0.000 |

## Top Rows

| target | family | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs |
|---|---|---|---|---:|---:|---:|---:|---:|
| feedback | fiber_tracts | NYU-12 | reject: target1 | +0.197 | +0.105 | 0.552 | 0.516 | 1/4 |
| feedback | basal_ganglia | CSHL045 | reject: total baseline | +0.151 | -0.004 | 0.887 | 0.138 | 1/4 |
| prior_side | brainstem_interbrain | NR_0019 | reject: target0 | +0.111 | +0.146 | 0.113 | 0.951 | 1/4 |
| feedback | cortical_visual | KS014 | reject: total baseline | +0.070 | -0.165 | 0.284 | 0.717 | 1/4 |
| prior_side | broad_named_anatomy | CSHL045 | reject: total baseline | +0.049 | -0.017 | 0.403 | 0.590 | 1/4 |
| feedback | broad_named_anatomy | NR_0019 | reject: total baseline | +0.020 | -0.196 | 0.711 | 0.333 | 1/4 |
| stimulus_side | brainstem_interbrain | NR_0019 | reject: shuffle | -0.003 | +0.048 | 0.137 | 0.959 | 1/4 |
| stimulus_side | broad_named_anatomy | KS014 | reject: shuffle | -0.039 | -0.066 | 0.278 | 0.778 | 1/4 |
| choice | broad_named_anatomy | KS014 | reject: shuffle | -0.045 | -0.016 | 0.721 | 0.355 | 1/4 |
| stimulus_side | cortical_sensorimotor | KS014 | reject: target0 | +0.588 | +0.460 | 0.000 | 1.000 | 0/4 |
| choice | basal_ganglia | NYU-12 | reject: target1 | +0.481 | +0.482 | 1.000 | 0.000 | 0/4 |
| stimulus_side | cortical_sensorimotor | ZFM-01577 | reject: target0 | +0.481 | +0.459 | 0.000 | 1.000 | 0/3 |
| stimulus_side | cortical_retrosplenial | ZFM-01577 | reject: target0 | +0.481 | +0.459 | 0.000 | 1.000 | 0/3 |
| prior_side | cortical_retrosplenial | SWC_038 | reject: target1 | +0.334 | +0.278 | 1.000 | 0.000 | 0/4 |

## Decision

A GPU run is justified only if this screen yields a candidate or a very near miss with clear same-recording bidirectional support. Otherwise the next move is another local target/control redesign.
