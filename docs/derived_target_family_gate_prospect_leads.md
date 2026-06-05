# Derived Target Family Gate

No-spend audit for new benchmark/control target definitions derived from cached trial fields, using the same shared-family model-free promotion gate.

- rows: `84`
- candidates: `3`
- positive centered-delta rows: `39`
- max bidirectional recordings: `3`
- max bidirectional recording fraction: `1.000`
- decision: `derived_target_family_candidate`

## Target Balance

| target | trials | eligible recordings | recordings |
|---|---:|---:|---:|
| contrast_strength | 7108 | 18 | 18 |
| response_latency | 10952 | 18 | 18 |
| prior_engaged | 10964 | 18 | 18 |

## Top Rows

| target | family | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs |
|---|---|---|---|---:|---:|---:|---:|---:|
| response_latency | thalamic | MFD_06 | candidate | +0.050 | +0.012 | 0.687 | 0.716 | 1/1 |
| prior_engaged | broad_named_anatomy | NR_0019 | candidate | +0.033 | +0.004 | 0.844 | 0.603 | 1/1 |
| response_latency | broad_named_anatomy | NR_0019 | candidate | +0.021 | +0.009 | 0.615 | 0.686 | 1/1 |
| response_latency | broad_named_anatomy | KS014 | reject: shuffle | -0.004 | -0.005 | 0.698 | 0.704 | 3/4 |
| response_latency | broad_named_anatomy | SWC_043 | reject: target0 | +0.006 | +0.003 | 0.538 | 0.599 | 2/3 |
| prior_engaged | broad_named_anatomy | SWC_038 | reject: shuffle | -0.000 | -0.005 | 0.430 | 0.545 | 2/3 |
| prior_engaged | fiber_tracts | KS014 | reject: target1 | +0.263 | +0.220 | 0.839 | 0.478 | 2/4 |
| response_latency | hippocampal_formation | KS014 | reject: total baseline | +0.003 | -0.671 | 0.426 | 0.877 | 2/4 |
| contrast_strength | broad_named_anatomy | KS014 | reject: shuffle | -0.005 | -0.006 | 0.580 | 0.542 | 2/4 |
| prior_engaged | fiber_tracts | MFD_06 | reject: total baseline | +0.061 | -0.218 | 0.567 | 0.558 | 1/1 |
| contrast_strength | thalamic | MFD_06 | reject: total baseline | +0.020 | -0.003 | 0.563 | 0.686 | 1/1 |
| response_latency | broad_named_anatomy | MFD_06 | reject: total baseline | +0.005 | -0.001 | 0.642 | 0.567 | 1/1 |
| contrast_strength | thalamic | SWC_043 | reject: target1 | +0.133 | +0.123 | 0.794 | 0.133 | 1/3 |
| prior_engaged | fiber_tracts | CSH_ZAD_019 | reject: total baseline | +0.061 | -0.039 | 0.796 | 0.556 | 1/3 |

## Decision

A derived target is only a training trigger if it passes the same local gate as prior audits: nonnegative true-vs-shuffle and true-vs-total deltas, both global target classes >=0.55, and at least 3/4 same-recording bidirectional support.
