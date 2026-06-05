# Extreme-Quantile Target Family Gate

No-spend target/control redesign audit. Continuous behavioral targets are labeled by within-recording low/high quantiles with middle trials dropped, then evaluated under the unchanged shared-family promotion gate.

- quantiles: `0.30` / `0.70`
- rows: `7`
- candidates: `0`
- positive centered-delta rows: `3`
- max bidirectional recordings: `3`
- max bidirectional recording fraction: `0.750`
- decision: `no_extreme_quantile_target_family_candidate`

## Target Balance

| target | trials | eligible recordings | recordings |
|---|---:|---:|---:|
| response_latency_extreme | 10748 | 28 | 28 |

## Top Rows

| target | family | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs |
|---|---|---|---|---:|---:|---:|---:|---:|
| response_latency_extreme | broad_named_anatomy | NR_0019 | reject: shuffle | -0.001 | -0.000 | 0.607 | 0.675 | 3/4 |
| response_latency_extreme | broad_named_anatomy | KS014 | reject: shuffle | -0.001 | -0.004 | 0.769 | 0.775 | 3/4 |
| response_latency_extreme | broad_named_anatomy | SWC_038 | reject: shuffle | -0.005 | -0.004 | 0.657 | 0.574 | 2/4 |
| response_latency_extreme | broad_named_anatomy | SWC_043 | reject: target0 | +0.020 | +0.014 | 0.540 | 0.674 | 1/4 |
| response_latency_extreme | broad_named_anatomy | NYU-12 | reject: total baseline | +0.012 | -0.008 | 0.495 | 0.458 | 1/4 |
| response_latency_extreme | broad_named_anatomy | CSH_ZAD_019 | reject: shuffle | -0.002 | -0.001 | 0.521 | 0.519 | 1/4 |
| response_latency_extreme | broad_named_anatomy | MFD_06 | reject: target0 | +0.047 | +0.021 | 0.415 | 0.548 | 0/4 |

## Decision

Extreme-quantile targets are only a training trigger if they pass the unchanged local gate: nonnegative true-vs-shuffle and true-vs-total deltas, both target classes >=0.55, and at least 3/4 same-recording bidirectional support.
