# Derived Target Family Gate

No-spend audit for new benchmark/control target definitions derived from cached trial fields, using the same shared-family model-free promotion gate.

- rows: `84`
- candidates: `0`
- positive centered-delta rows: `38`
- max bidirectional recordings: `3`
- max bidirectional recording fraction: `0.750`
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
| response_latency | broad_named_anatomy | KS014 | reject: shuffle | -0.004 | -0.005 | 0.714 | 0.745 | 3/4 |
| response_latency | hippocampal_formation | KS014 | reject: total baseline | +0.669 | -0.004 | 0.915 | 0.527 | 2/4 |
| prior_engaged | fiber_tracts | KS014 | reject: target1 | +0.263 | +0.220 | 0.850 | 0.473 | 2/4 |
| prior_engaged | fiber_tracts | CSH_ZAD_019 | reject: total baseline | +0.042 | -0.061 | 0.739 | 0.546 | 2/4 |
| response_latency | broad_named_anatomy | SWC_038 | reject: shuffle | -0.004 | -0.005 | 0.609 | 0.543 | 2/4 |
| contrast_strength | broad_named_anatomy | KS014 | reject: shuffle | -0.005 | -0.006 | 0.564 | 0.507 | 2/4 |
| response_latency | hippocampal_formation | NR_0019 | reject: target1 | +0.109 | +0.085 | 0.853 | 0.228 | 1/4 |
| response_latency | thalamic | NR_0019 | reject: target0 | +0.098 | +0.062 | 0.275 | 0.832 | 1/4 |
| prior_engaged | fiber_tracts | SWC_038 | reject: target1 | +0.098 | +0.217 | 0.775 | 0.383 | 1/4 |
| response_latency | thalamic | SWC_038 | reject: total baseline | +0.093 | -0.047 | 0.939 | 0.150 | 1/4 |
| prior_engaged | thalamic | NYU-12 | reject: total baseline | +0.085 | -0.086 | 0.972 | 0.151 | 1/4 |
| response_latency | thalamic | CSH_ZAD_019 | reject: target1 | +0.033 | +0.030 | 0.557 | 0.496 | 1/4 |
| contrast_strength | thalamic | SWC_043 | reject: target1 | +0.023 | +0.152 | 0.833 | 0.097 | 1/4 |
| prior_engaged | broad_named_anatomy | MFD_06 | reject: recording bidirectionality | +0.022 | +0.041 | 0.550 | 0.583 | 1/4 |

## Decision

A derived target is only a training trigger if it passes the same local gate as prior audits: nonnegative true-vs-shuffle and true-vs-total deltas, both global target classes >=0.55, and at least 3/4 same-recording bidirectional support.
