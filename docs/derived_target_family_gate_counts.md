# Derived Target Family Gate

No-spend audit for new benchmark/control target definitions derived from cached trial fields, using the same shared-family model-free promotion gate.

- rows: `84`
- candidates: `0`
- positive centered-delta rows: `40`
- max bidirectional recordings: `1`
- max bidirectional recording fraction: `0.250`
- decision: `no_derived_target_family_candidate`

## Target Balance

| target | trials | eligible recordings | recordings |
|---|---:|---:|---:|
| contrast_strength | 11556 | 28 | 28 |
| response_latency | 17868 | 28 | 28 |
| prior_engaged | 17882 | 28 | 28 |

## Top Rows

| target | family | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs |
|---|---|---|---|---:|---:|---:|---:|---:|
| response_latency | hippocampal_formation | KS014 | reject: total baseline | +0.669 | -0.004 | 0.942 | 0.272 | 1/4 |
| prior_engaged | fiber_tracts | KS014 | reject: target1 | +0.263 | +0.220 | 0.894 | 0.331 | 1/4 |
| prior_engaged | fiber_tracts | SWC_038 | reject: target1 | +0.098 | +0.217 | 0.964 | 0.364 | 1/4 |
| prior_engaged | hippocampal_formation | MFD_06 | reject: target0 | +0.064 | +0.055 | 0.461 | 0.782 | 1/4 |
| contrast_strength | broad_named_anatomy | NR_0019 | reject: target0 | +0.003 | +0.000 | 0.525 | 0.638 | 1/4 |
| prior_engaged | broad_named_anatomy | SWC_043 | reject: shuffle | -0.001 | -0.010 | 0.750 | 0.406 | 1/4 |
| response_latency | broad_named_anatomy | KS014 | reject: shuffle | -0.004 | -0.005 | 0.472 | 0.771 | 1/4 |
| contrast_strength | broad_named_anatomy | KS014 | reject: shuffle | -0.005 | -0.006 | 0.657 | 0.557 | 1/4 |
| contrast_strength | fiber_tracts | KS014 | reject: shuffle | -0.015 | -0.105 | 0.698 | 0.308 | 1/4 |
| response_latency | thalamic | SWC_038 | reject: target1 | +0.339 | +0.198 | 0.999 | 0.005 | 0/4 |
| response_latency | hippocampal_formation | SWC_038 | reject: target1 | +0.255 | +0.056 | 1.000 | 0.000 | 0/4 |
| response_latency | thalamic | SWC_043 | reject: target1 | +0.131 | +0.325 | 0.755 | 0.240 | 0/4 |
| prior_engaged | hippocampal_formation | NR_0019 | reject: target0 | +0.127 | +0.065 | 0.244 | 0.844 | 0/4 |
| prior_engaged | hippocampal_formation | CSH_ZAD_019 | reject: total baseline | +0.125 | -0.667 | 0.500 | 0.500 | 0/4 |

## Decision

A derived target is only a training trigger if it passes the same local gate as prior audits: nonnegative true-vs-shuffle and true-vs-total deltas, both global target classes >=0.55, and at least 3/4 same-recording bidirectional support.
