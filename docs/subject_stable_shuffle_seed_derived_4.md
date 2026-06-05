# Derived Target Family Gate

No-spend audit for new benchmark/control target definitions derived from cached trial fields, using the same shared-family model-free promotion gate.

- rows: `7`
- candidates: `0`
- positive centered-delta rows: `3`
- max bidirectional recordings: `3`
- max bidirectional recording fraction: `0.750`
- decision: `no_derived_target_family_candidate`

## Target Balance

| target | trials | eligible recordings | recordings |
|---|---:|---:|---:|
| response_latency | 17868 | 28 | 28 |

## Top Rows

| target | family | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs |
|---|---|---|---|---:|---:|---:|---:|---:|
| response_latency | broad_named_anatomy | KS014 | reject: shuffle | -0.002 | -0.005 | 0.748 | 0.774 | 3/4 |
| response_latency | broad_named_anatomy | NR_0019 | reject: shuffle | -0.001 | -0.001 | 0.545 | 0.605 | 2/4 |
| response_latency | broad_named_anatomy | SWC_038 | reject: shuffle | -0.004 | -0.005 | 0.620 | 0.556 | 2/4 |
| response_latency | broad_named_anatomy | CSH_ZAD_019 | reject: shuffle | -0.002 | -0.000 | 0.497 | 0.498 | 1/4 |
| response_latency | broad_named_anatomy | MFD_06 | reject: target0 | +0.033 | +0.005 | 0.429 | 0.538 | 0/4 |
| response_latency | broad_named_anatomy | SWC_043 | reject: target0 | +0.012 | +0.009 | 0.508 | 0.606 | 0/4 |
| response_latency | broad_named_anatomy | NYU-12 | reject: total baseline | +0.007 | -0.003 | 0.491 | 0.461 | 0/4 |

## Decision

A derived target is only a training trigger if it passes the same local gate as prior audits: nonnegative true-vs-shuffle and true-vs-total deltas, both global target classes >=0.55, and at least 3/4 same-recording bidirectional support.
