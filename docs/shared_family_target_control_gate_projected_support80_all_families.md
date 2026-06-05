# Shared-Family Target/Control Gate

No-spend model-free screen for the next benchmark redesign. Each row is a single shared anatomical family, target mode, and held-out subject. The true family feature must beat within-recording shuffled labels, beat the total-spike baseline, and satisfy global plus same-recording bidirectional target support.

- rows: `320`
- candidates: `0`
- positive centered-delta rows: `162`
- max bidirectional recordings: `2`
- max bidirectional recording fraction: `0.500`
- decision: `no_shared_family_target_candidate`

## Target Summary

| target | rows | candidates | positive centered delta | max bidir frac |
|---|---:|---:|---:|---:|
| choice | 80 | 0 | 48 | 0.333 |
| feedback | 80 | 0 | 32 | 0.500 |
| prior_side | 80 | 0 | 41 | 0.333 |
| stimulus_side | 80 | 0 | 41 | 0.250 |

## Family Summary

| family | rows | candidates | positive centered delta | max bidir frac |
|---|---:|---:|---:|---:|
| basal_ganglia | 32 | 0 | 15 | 0.333 |
| brainstem_interbrain | 32 | 0 | 19 | 0.250 |
| broad_named_anatomy | 32 | 0 | 13 | 0.500 |
| cortical_retrosplenial | 32 | 0 | 13 | 0.000 |
| cortical_sensorimotor | 32 | 0 | 15 | 0.250 |
| cortical_visual | 32 | 0 | 13 | 0.250 |
| fiber_tracts | 32 | 0 | 17 | 0.250 |
| hippocampal_formation | 32 | 0 | 18 | 0.250 |
| midbrain | 32 | 0 | 18 | 0.333 |
| thalamic | 32 | 0 | 21 | 0.250 |

## Top Rows

| target | family | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs |
|---|---|---|---|---:|---:|---:|---:|---:|
| feedback | broad_named_anatomy | CSHL045 | reject: target0 | +0.038 | +0.031 | 0.516 | 0.645 | 2/4 |
| feedback | broad_named_anatomy | NYU-12 | reject: shuffle | -0.002 | -0.008 | 0.529 | 0.559 | 2/4 |
| choice | basal_ganglia | ZFM-01577 | reject: target0 | +0.153 | +0.171 | 0.142 | 0.912 | 1/3 |
| prior_side | midbrain | ZFM-01577 | reject: target1 | +0.054 | +0.046 | 0.922 | 0.156 | 1/3 |
| choice | basal_ganglia | CSHL045 | reject: target1 | +0.335 | +0.292 | 0.864 | 0.253 | 1/4 |
| choice | basal_ganglia | NR_0019 | reject: target1 | +0.136 | +0.182 | 0.705 | 0.411 | 1/4 |
| choice | brainstem_interbrain | NR_0019 | reject: target0 | +0.123 | +0.286 | 0.425 | 0.765 | 1/4 |
| stimulus_side | brainstem_interbrain | NR_0019 | reject: target0 | +0.117 | +0.062 | 0.415 | 0.753 | 1/4 |
| choice | basal_ganglia | SWC_038 | reject: target1 | +0.096 | +0.126 | 0.774 | 0.296 | 1/4 |
| prior_side | cortical_visual | MFD_06 | reject: target0 | +0.085 | +0.138 | 0.259 | 0.817 | 1/4 |
| feedback | brainstem_interbrain | NYU-12 | reject: target1 | +0.084 | +0.118 | 0.719 | 0.387 | 1/4 |
| prior_side | brainstem_interbrain | NR_0019 | reject: target1 | +0.082 | +0.135 | 0.700 | 0.408 | 1/4 |
| feedback | brainstem_interbrain | KS014 | reject: total baseline | +0.057 | -0.072 | 0.724 | 0.411 | 1/4 |
| stimulus_side | brainstem_interbrain | KS014 | reject: total baseline | +0.054 | -0.031 | 0.419 | 0.644 | 1/4 |

## Decision

A GPU run is justified only if this screen yields a candidate or a very near miss with clear same-recording bidirectional support. Otherwise the next move is another local target/control redesign.
