# Subject-Stable Broad-Anatomy Mechanism Audit

Contribution audit for the five subject-stable broad-anatomy near misses. Each row rebuilds the matching target/features and decomposes held-out true-vs-shuffle true-class movement across predefined anatomical families.

- subject-stable rows: `5`
- rows with bidirectional family candidates: `5`
- bidirectional family candidates: `9`
- exact family-gate candidates: `0`
- decision: `contribution_only_subject_stable_broad_family_mechanism`

## Stable Rows

| source | target | holdout | gate failures | gate delta shuffle | gate delta total | broad class | broad target0 | broad target1 | contribution candidates | exact gate candidates |
|---|---|---|---|---:|---:|---|---:|---:|---|---|
| reaction_recording_centered | wheel_reaction_latency | KS014 | shuffle | -0.0005 | +0.0027 | bidirectional_family_candidate | 0.664 | 0.713 | broad_named_anatomy | none |
| wheel_targets | wheel_active | KS014 | shuffle, total_baseline | -0.0018 | -0.0016 | bidirectional_family_candidate | 0.624 | 0.681 | midbrain, broad_named_anatomy | none |
| reaction_recording_centered | post_stim_speedup | KS014 | shuffle, total_baseline | -0.0035 | -0.0024 | bidirectional_family_candidate | 0.599 | 0.655 | midbrain, broad_named_anatomy | none |
| derived_recording_centered | response_latency | KS014 | shuffle, total_baseline | -0.0043 | -0.0053 | bidirectional_family_candidate | 0.810 | 0.912 | broad_named_anatomy, fiber_tracts | none |
| wheel_targets | wheel_displacement | KS014 | shuffle, total_baseline | -0.0084 | -0.0085 | bidirectional_family_candidate | 0.620 | 0.757 | broad_named_anatomy, midbrain | none |

## Top Contributions

### reaction_recording_centered / wheel_reaction_latency / KS014

| family | class | mean delta | target0 | target1 | recs |
|---|---|---:|---:|---:|---:|
| broad_named_anatomy | bidirectional_family_candidate | +0.0322 | 0.664 | 0.713 | 4/4 |
| midbrain | weak_or_mixed | -0.0078 | 0.448 | 0.448 | 1/4 |
| cortical_visual | weak_or_mixed | -0.0117 | 0.297 | 0.520 | 2/4 |
| cortical_retrosplenial | target1_only | -0.0005 | 0.080 | 0.910 | 0/4 |
| fiber_tracts | weak_or_mixed | -0.0028 | 0.514 | 0.341 | 2/4 |
| thalamic | target1_only | -0.0032 | 0.131 | 0.780 | 3/4 |
| hippocampal_formation | target0_only | +0.0003 | 0.719 | 0.309 | 3/4 |
| brainstem_interbrain | target0_only | -0.0033 | 0.552 | 0.346 | 1/4 |

Exact candidate-family gate checks:

| family | decision | delta shuffle | delta total | target0 | target1 | bidir recs |
|---|---|---:|---:|---:|---:|---:|
| broad_named_anatomy | reject: shuffle | -0.0005 | +0.0027 | 0.667 | 0.715 | 3/4 |

### wheel_targets / wheel_active / KS014

| family | class | mean delta | target0 | target1 | recs |
|---|---|---:|---:|---:|---:|
| midbrain | bidirectional_family_candidate | +0.0373 | 0.585 | 0.689 | 4/4 |
| cortical_retrosplenial | target0_only | -0.0116 | 0.865 | 0.099 | 1/4 |
| cortical_visual | weak_or_mixed | -0.0120 | 0.489 | 0.198 | 1/4 |
| brainstem_interbrain | target1_only | -0.0078 | 0.320 | 0.564 | 3/4 |
| fiber_tracts | target0_only | +0.0021 | 0.688 | 0.433 | 3/4 |
| thalamic | target1_only | +0.0017 | 0.168 | 0.896 | 4/4 |
| hippocampal_formation | target0_only | +0.0031 | 0.801 | 0.411 | 4/4 |
| broad_named_anatomy | bidirectional_family_candidate | +0.0008 | 0.624 | 0.681 | 4/4 |

Exact candidate-family gate checks:

| family | decision | delta shuffle | delta total | target0 | target1 | bidir recs |
|---|---|---:|---:|---:|---:|---:|
| midbrain | reject: shuffle | -0.0074 | -0.0130 | 0.477 | 0.442 | 1/4 |
| broad_named_anatomy | reject: shuffle | -0.0018 | -0.0016 | 0.587 | 0.598 | 3/4 |

### reaction_recording_centered / post_stim_speedup / KS014

| family | class | mean delta | target0 | target1 | recs |
|---|---|---:|---:|---:|---:|
| cortical_retrosplenial | target0_only | -0.0206 | 0.861 | 0.092 | 0/4 |
| midbrain | bidirectional_family_candidate | +0.0278 | 0.612 | 0.711 | 3/4 |
| cortical_visual | weak_or_mixed | -0.0144 | 0.451 | 0.203 | 0/4 |
| fiber_tracts | target1_only | +0.0040 | 0.509 | 0.688 | 3/4 |
| broad_named_anatomy | bidirectional_family_candidate | +0.0042 | 0.599 | 0.655 | 3/4 |
| brainstem_interbrain | weak_or_mixed | -0.0066 | 0.305 | 0.544 | 2/4 |
| hippocampal_formation | target1_only | +0.0034 | 0.400 | 0.867 | 2/4 |
| thalamic | target1_only | +0.0013 | 0.180 | 0.909 | 3/4 |

Exact candidate-family gate checks:

| family | decision | delta shuffle | delta total | target0 | target1 | bidir recs |
|---|---|---:|---:|---:|---:|---:|
| midbrain | reject: shuffle | -0.0129 | -0.0179 | 0.412 | 0.369 | 1/4 |
| broad_named_anatomy | reject: shuffle | -0.0035 | -0.0024 | 0.608 | 0.584 | 3/4 |

### derived_recording_centered / response_latency / KS014

| family | class | mean delta | target0 | target1 | recs |
|---|---|---:|---:|---:|---:|
| broad_named_anatomy | bidirectional_family_candidate | +0.0866 | 0.810 | 0.912 | 4/4 |
| cortical_retrosplenial | target1_only | -0.0611 | 0.053 | 0.850 | 1/4 |
| cortical_visual | weak_or_mixed | -0.0554 | 0.372 | 0.148 | 0/4 |
| midbrain | weak_or_mixed | -0.0322 | 0.329 | 0.281 | 1/4 |
| fiber_tracts | bidirectional_family_candidate | +0.0099 | 0.608 | 0.771 | 3/4 |
| brainstem_interbrain | weak_or_mixed | -0.0078 | 0.509 | 0.330 | 2/4 |
| hippocampal_formation | target0_only | +0.0080 | 0.924 | 0.480 | 2/4 |
| thalamic | target0_only | -0.0037 | 0.817 | 0.089 | 0/4 |

Exact candidate-family gate checks:

| family | decision | delta shuffle | delta total | target0 | target1 | bidir recs |
|---|---|---:|---:|---:|---:|---:|
| broad_named_anatomy | reject: shuffle | -0.0043 | -0.0053 | 0.714 | 0.745 | 3/4 |
| fiber_tracts | reject: shuffle | -0.0661 | -0.2024 | 0.445 | 0.279 | 0/4 |

### wheel_targets / wheel_displacement / KS014

| family | class | mean delta | target0 | target1 | recs |
|---|---|---:|---:|---:|---:|
| broad_named_anatomy | bidirectional_family_candidate | +0.0600 | 0.620 | 0.757 | 4/4 |
| cortical_retrosplenial | target1_only | -0.0233 | 0.069 | 0.870 | 1/4 |
| midbrain | bidirectional_family_candidate | +0.0253 | 0.573 | 0.687 | 3/4 |
| brainstem_interbrain | target1_only | -0.0061 | 0.364 | 0.614 | 3/4 |
| cortical_visual | weak_or_mixed | -0.0100 | 0.504 | 0.268 | 1/4 |
| fiber_tracts | target1_only | +0.0011 | 0.453 | 0.626 | 1/4 |
| hippocampal_formation | target0_only | -0.0016 | 0.661 | 0.209 | 0/4 |
| thalamic | target1_only | -0.0013 | 0.122 | 0.802 | 0/4 |

Exact candidate-family gate checks:

| family | decision | delta shuffle | delta total | target0 | target1 | bidir recs |
|---|---|---:|---:|---:|---:|---:|
| broad_named_anatomy | reject: shuffle | -0.0084 | -0.0085 | 0.556 | 0.593 | 3/4 |
| midbrain | reject: shuffle | -0.0209 | -0.0322 | 0.439 | 0.416 | 1/4 |

## Decision

Family contribution checks found bidirectional movement, but exact single-family gates still do not pass the strict local promotion criteria.
