# Extreme-Quantile Target Family Gate

No-spend target/control redesign audit. Continuous behavioral targets are labeled by within-recording low/high quantiles with middle trials dropped, then evaluated under the unchanged shared-family promotion gate.

- quantiles: `0.25` / `0.75`
- rows: `7`
- candidates: `1`
- positive centered-delta rows: `4`
- max bidirectional recordings: `4`
- max bidirectional recording fraction: `1.000`
- decision: `extreme_quantile_target_family_candidate`

## Target Balance

| target | trials | eligible recordings | recordings |
|---|---:|---:|---:|
| response_latency_extreme | 8956 | 28 | 28 |

## Top Rows

| target | family | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs |
|---|---|---|---|---:|---:|---:|---:|---:|
| response_latency_extreme | broad_named_anatomy | SWC_043 | candidate | +0.014 | +0.017 | 0.555 | 0.656 | 3/4 |
| response_latency_extreme | broad_named_anatomy | NR_0019 | reject: shuffle | -0.000 | +0.000 | 0.641 | 0.704 | 4/4 |
| response_latency_extreme | broad_named_anatomy | CSH_ZAD_019 | reject: total baseline | +0.007 | -0.002 | 0.569 | 0.608 | 3/4 |
| response_latency_extreme | broad_named_anatomy | KS014 | reject: shuffle | -0.002 | -0.004 | 0.759 | 0.780 | 3/4 |
| response_latency_extreme | broad_named_anatomy | SWC_038 | reject: shuffle | -0.005 | -0.005 | 0.641 | 0.574 | 2/4 |
| response_latency_extreme | broad_named_anatomy | MFD_06 | reject: target0 | +0.053 | +0.042 | 0.523 | 0.618 | 1/4 |
| response_latency_extreme | broad_named_anatomy | NYU-12 | reject: total baseline | +0.005 | -0.011 | 0.516 | 0.456 | 0/4 |

## Decision

Extreme-quantile targets are only a training trigger if they pass the unchanged local gate: nonnegative true-vs-shuffle and true-vs-total deltas, both target classes >=0.55, and at least 3/4 same-recording bidirectional support.
