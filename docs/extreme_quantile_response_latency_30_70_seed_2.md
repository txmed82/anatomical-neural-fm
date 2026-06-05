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
| response_latency_extreme | broad_named_anatomy | KS014 | reject: shuffle | -0.002 | -0.004 | 0.761 | 0.783 | 3/4 |
| response_latency_extreme | broad_named_anatomy | SWC_043 | reject: recording bidirectionality | +0.014 | +0.014 | 0.565 | 0.654 | 2/4 |
| response_latency_extreme | broad_named_anatomy | NR_0019 | reject: shuffle | -0.000 | -0.000 | 0.598 | 0.626 | 2/4 |
| response_latency_extreme | broad_named_anatomy | CSH_ZAD_019 | reject: shuffle | -0.002 | -0.001 | 0.504 | 0.543 | 2/4 |
| response_latency_extreme | broad_named_anatomy | SWC_038 | reject: shuffle | -0.006 | -0.004 | 0.635 | 0.533 | 1/4 |
| response_latency_extreme | broad_named_anatomy | MFD_06 | reject: target0 | +0.036 | +0.021 | 0.432 | 0.534 | 0/4 |
| response_latency_extreme | broad_named_anatomy | NYU-12 | reject: total baseline | +0.001 | -0.008 | 0.464 | 0.415 | 0/4 |

## Decision

Extreme-quantile targets are only a training trigger if they pass the unchanged local gate: nonnegative true-vs-shuffle and true-vs-total deltas, both target classes >=0.55, and at least 3/4 same-recording bidirectional support.
