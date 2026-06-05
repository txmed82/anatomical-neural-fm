# Derived Target Family Gate

No-spend audit for new benchmark/control target definitions derived from cached trial fields, using the same shared-family model-free promotion gate.

- rows: `84`
- candidates: `0`
- positive centered-delta rows: `51`
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
| prior_engaged | broad_named_anatomy | CSH_ZAD_019 | reject: total baseline | +0.174 | -0.421 | 0.506 | 0.783 | 2/4 |
| prior_engaged | broad_named_anatomy | SWC_038 | reject: target0 | +0.297 | +0.236 | 0.231 | 0.928 | 1/4 |
| prior_engaged | fiber_tracts | SWC_038 | reject: target0 | +0.295 | +0.271 | 0.339 | 0.921 | 1/4 |
| prior_engaged | broad_named_anatomy | NR_0019 | reject: target1 | +0.263 | +0.170 | 0.597 | 0.534 | 1/4 |
| prior_engaged | broad_named_anatomy | SWC_043 | reject: total baseline | +0.216 | -0.149 | 0.456 | 0.664 | 1/4 |
| response_latency | fiber_tracts | KS014 | reject: total baseline | +0.155 | -0.320 | 0.741 | 0.421 | 1/4 |
| prior_engaged | hippocampal_formation | CSH_ZAD_019 | reject: total baseline | +0.099 | -0.155 | 0.308 | 0.746 | 1/4 |
| response_latency | broad_named_anatomy | KS014 | reject: total baseline | +0.099 | -0.408 | 0.701 | 0.462 | 1/4 |
| prior_engaged | thalamic | CSH_ZAD_019 | reject: shuffle | -0.029 | -0.091 | 0.472 | 0.682 | 1/4 |
| response_latency | thalamic | MFD_06 | reject: target1 | +0.356 | +0.294 | 0.856 | 0.156 | 0/4 |
| response_latency | hippocampal_formation | KS014 | reject: total baseline | +0.289 | -0.224 | 0.184 | 0.917 | 0/4 |
| prior_engaged | fiber_tracts | NYU-12 | reject: total baseline | +0.241 | -0.183 | 0.353 | 0.717 | 0/4 |
| response_latency | fiber_tracts | NYU-12 | reject: target1 | +0.236 | +0.221 | 0.693 | 0.404 | 0/4 |
| prior_engaged | fiber_tracts | KS014 | reject: target0 | +0.226 | +0.316 | 0.503 | 0.635 | 0/4 |

## Decision

A derived target is only a training trigger if it passes the same local gate as prior audits: nonnegative true-vs-shuffle and true-vs-total deltas, both global target classes >=0.55, and at least 3/4 same-recording bidirectional support.
