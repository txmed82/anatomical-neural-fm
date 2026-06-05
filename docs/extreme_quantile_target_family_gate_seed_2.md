# Extreme-Quantile Target Family Gate

No-spend target/control redesign audit. Continuous behavioral targets are labeled by within-recording low/high quantiles with middle trials dropped, then evaluated under the unchanged shared-family promotion gate.

- quantiles: `0.25` / `0.75`
- rows: `7`
- candidates: `0`
- positive centered-delta rows: `2`
- max bidirectional recordings: `4`
- max bidirectional recording fraction: `1.000`
- decision: `no_extreme_quantile_target_family_candidate`

## Target Balance

| target | trials | eligible recordings | recordings |
|---|---:|---:|---:|
| response_latency_extreme | 8956 | 28 | 28 |

## Top Rows

| target | family | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs |
|---|---|---|---|---:|---:|---:|---:|---:|
| response_latency_extreme | broad_named_anatomy | NR_0019 | reject: shuffle | -0.001 | +0.000 | 0.629 | 0.665 | 4/4 |
| response_latency_extreme | broad_named_anatomy | KS014 | reject: shuffle | -0.002 | -0.004 | 0.752 | 0.789 | 3/4 |
| response_latency_extreme | broad_named_anatomy | SWC_043 | reject: recording bidirectionality | +0.015 | +0.017 | 0.587 | 0.675 | 2/4 |
| response_latency_extreme | broad_named_anatomy | CSH_ZAD_019 | reject: shuffle | -0.002 | -0.002 | 0.513 | 0.553 | 2/4 |
| response_latency_extreme | broad_named_anatomy | SWC_038 | reject: shuffle | -0.006 | -0.005 | 0.625 | 0.532 | 1/4 |
| response_latency_extreme | broad_named_anatomy | MFD_06 | reject: target0 | +0.051 | +0.042 | 0.429 | 0.536 | 0/4 |
| response_latency_extreme | broad_named_anatomy | NYU-12 | reject: shuffle | -0.000 | -0.011 | 0.458 | 0.415 | 0/4 |

## Decision

Extreme-quantile targets are only a training trigger if they pass the unchanged local gate: nonnegative true-vs-shuffle and true-vs-total deltas, both target classes >=0.55, and at least 3/4 same-recording bidirectional support.
