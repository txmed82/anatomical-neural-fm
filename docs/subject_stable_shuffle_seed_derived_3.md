# Derived Target Family Gate

No-spend audit for new benchmark/control target definitions derived from cached trial fields, using the same shared-family model-free promotion gate.

- rows: `7`
- candidates: `0`
- positive centered-delta rows: `4`
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
| response_latency | broad_named_anatomy | KS014 | reject: shuffle | -0.002 | -0.005 | 0.742 | 0.781 | 3/4 |
| response_latency | broad_named_anatomy | SWC_043 | reject: target0 | +0.010 | +0.009 | 0.516 | 0.619 | 2/4 |
| response_latency | broad_named_anatomy | CSH_ZAD_019 | reject: total baseline | +0.004 | -0.000 | 0.536 | 0.561 | 2/4 |
| response_latency | broad_named_anatomy | NR_0019 | reject: shuffle | -0.003 | -0.001 | 0.536 | 0.611 | 2/4 |
| response_latency | broad_named_anatomy | SWC_038 | reject: shuffle | -0.004 | -0.005 | 0.603 | 0.543 | 2/4 |
| response_latency | broad_named_anatomy | MFD_06 | reject: target0 | +0.030 | +0.005 | 0.513 | 0.582 | 1/4 |
| response_latency | broad_named_anatomy | NYU-12 | reject: total baseline | +0.004 | -0.003 | 0.508 | 0.488 | 0/4 |

## Decision

A derived target is only a training trigger if it passes the same local gate as prior audits: nonnegative true-vs-shuffle and true-vs-total deltas, both global target classes >=0.55, and at least 3/4 same-recording bidirectional support.
