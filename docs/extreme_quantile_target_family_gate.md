# Extreme-Quantile Target Family Gate

No-spend target/control redesign audit. Continuous behavioral targets are labeled by within-recording low/high quantiles with middle trials dropped, then evaluated under the unchanged shared-family promotion gate.

- quantiles: `0.25` / `0.75`
- rows: `175`
- candidates: `1`
- positive centered-delta rows: `78`
- max bidirectional recordings: `4`
- max bidirectional recording fraction: `1.000`
- decision: `extreme_quantile_target_family_candidate`

## Target Balance

| target | trials | eligible recordings | recordings |
|---|---:|---:|---:|
| response_latency_extreme | 8956 | 28 | 28 |
| wheel_reaction_latency_extreme | 6038 | 27 | 28 |
| post_stim_speedup_extreme | 8410 | 28 | 28 |
| wheel_active_extreme | 8848 | 28 | 28 |
| wheel_displacement_extreme | 8536 | 28 | 28 |

## Top Rows

| target | family | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs |
|---|---|---|---|---:|---:|---:|---:|---:|
| response_latency_extreme | broad_named_anatomy | NR_0019 | candidate | +0.001 | +0.000 | 0.639 | 0.648 | 4/4 |
| wheel_displacement_extreme | broad_named_anatomy | NR_0019 | reject: total baseline | +0.000 | -0.001 | 0.566 | 0.618 | 3/4 |
| wheel_reaction_latency_extreme | broad_named_anatomy | KS014 | reject: shuffle | -0.003 | +0.003 | 0.738 | 0.753 | 3/4 |
| response_latency_extreme | broad_named_anatomy | KS014 | reject: shuffle | -0.004 | -0.004 | 0.702 | 0.767 | 3/4 |
| wheel_active_extreme | broad_named_anatomy | KS014 | reject: shuffle | -0.006 | -0.005 | 0.697 | 0.683 | 3/4 |
| post_stim_speedup_extreme | broad_named_anatomy | KS014 | reject: shuffle | -0.007 | -0.005 | 0.649 | 0.631 | 3/4 |
| wheel_displacement_extreme | broad_named_anatomy | KS014 | reject: shuffle | -0.009 | -0.007 | 0.668 | 0.700 | 3/4 |
| response_latency_extreme | hippocampal_formation | KS014 | reject: target1 | +0.754 | +0.001 | 0.978 | 0.549 | 2/4 |
| wheel_reaction_latency_extreme | fiber_tracts | NYU-12 | reject: target0 | +0.262 | +0.416 | 0.430 | 0.679 | 2/4 |
| wheel_active_extreme | thalamic | NR_0019 | reject: target0 | +0.091 | +0.062 | 0.319 | 0.867 | 2/4 |
| response_latency_extreme | thalamic | CSH_ZAD_019 | reject: target1 | +0.050 | +0.044 | 0.554 | 0.518 | 2/4 |
| wheel_active_extreme | fiber_tracts | CSH_ZAD_019 | reject: total baseline | +0.018 | -0.044 | 0.528 | 0.525 | 2/4 |
| wheel_active_extreme | broad_named_anatomy | SWC_043 | reject: recording bidirectionality | +0.014 | +0.018 | 0.568 | 0.655 | 2/4 |
| wheel_displacement_extreme | broad_named_anatomy | SWC_043 | reject: recording bidirectionality | +0.014 | +0.018 | 0.594 | 0.690 | 2/4 |
| response_latency_extreme | thalamic | NR_0019 | reject: target1 | +0.012 | +0.033 | 0.833 | 0.384 | 2/4 |
| post_stim_speedup_extreme | broad_named_anatomy | SWC_043 | reject: target0 | +0.012 | +0.017 | 0.538 | 0.638 | 2/4 |

## Decision

Extreme-quantile targets are only a training trigger if they pass the unchanged local gate: nonnegative true-vs-shuffle and true-vs-total deltas, both target classes >=0.55, and at least 3/4 same-recording bidirectional support.
