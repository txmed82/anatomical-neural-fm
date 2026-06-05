# Derived Target Family Gate

No-spend audit for new benchmark/control target definitions derived from cached trial fields, using the same shared-family model-free promotion gate.

- rows: `84`
- candidates: `0`
- positive centered-delta rows: `40`
- max bidirectional recordings: `2`
- max bidirectional recording fraction: `0.500`
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
| prior_engaged | fiber_tracts | SWC_038 | reject: target1 | +0.063 | +0.258 | 0.939 | 0.376 | 2/4 |
| contrast_strength | fiber_tracts | KS014 | reject: total baseline | +0.103 | -0.230 | 0.748 | 0.256 | 1/4 |
| prior_engaged | broad_named_anatomy | NYU-12 | reject: total baseline | +0.094 | -0.284 | 0.686 | 0.411 | 1/4 |
| prior_engaged | hippocampal_formation | CSH_ZAD_019 | reject: shuffle | -0.030 | -0.322 | 0.500 | 0.669 | 1/4 |
| response_latency | hippocampal_formation | KS014 | reject: total baseline | +0.345 | -0.139 | 1.000 | 0.000 | 0/4 |
| prior_engaged | fiber_tracts | KS014 | reject: target1 | +0.297 | +0.317 | 0.778 | 0.274 | 0/4 |
| prior_engaged | broad_named_anatomy | KS014 | reject: target1 | +0.273 | +0.247 | 0.783 | 0.255 | 0/4 |
| prior_engaged | fiber_tracts | CSH_ZAD_019 | reject: total baseline | +0.221 | -0.227 | 0.494 | 0.501 | 0/4 |
| response_latency | fiber_tracts | NYU-12 | reject: target0 | +0.218 | +0.221 | 0.121 | 0.934 | 0/4 |
| response_latency | thalamic | SWC_043 | reject: target1 | +0.171 | +0.178 | 0.742 | 0.258 | 0/4 |
| prior_engaged | broad_named_anatomy | CSH_ZAD_019 | reject: total baseline | +0.164 | -0.311 | 0.742 | 0.312 | 0/4 |
| contrast_strength | hippocampal_formation | SWC_043 | reject: target0 | +0.155 | +0.044 | 0.403 | 0.842 | 0/4 |
| prior_engaged | broad_named_anatomy | NR_0019 | reject: target1 | +0.125 | +0.156 | 0.925 | 0.155 | 0/4 |
| response_latency | thalamic | NR_0019 | reject: target0 | +0.116 | +0.026 | 0.500 | 0.500 | 0/4 |

## Decision

A derived target is only a training trigger if it passes the same local gate as prior audits: nonnegative true-vs-shuffle and true-vs-total deltas, both global target classes >=0.55, and at least 3/4 same-recording bidirectional support.
