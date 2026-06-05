# Derived Target Family Gate

No-spend audit for new benchmark/control target definitions derived from cached trial fields, using the same shared-family model-free promotion gate.

- rows: `84`
- candidates: `1`
- positive centered-delta rows: `41`
- max bidirectional recordings: `1`
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
| prior_engaged | broad_named_anatomy | NR_0019 | candidate | +0.033 | +0.004 | 0.844 | 0.603 | 1/1 |
| prior_engaged | broad_named_anatomy | SWC_043 | reject: shuffle | -0.004 | -0.006 | 0.744 | 0.349 | 1/3 |
| prior_engaged | thalamic | CSH_ZAD_019 | reject: shuffle | -0.005 | -0.035 | 0.304 | 0.944 | 1/3 |
| prior_engaged | fiber_tracts | SWC_038 | reject: shuffle | -0.078 | +0.122 | 1.000 | 0.308 | 1/3 |
| prior_engaged | fiber_tracts | KS014 | reject: target1 | +0.263 | +0.220 | 0.800 | 0.398 | 1/4 |
| contrast_strength | hippocampal_formation | KS014 | reject: target1 | +0.000 | +0.002 | 0.955 | 0.261 | 1/4 |
| response_latency | broad_named_anatomy | KS014 | reject: shuffle | -0.004 | -0.005 | 0.304 | 0.801 | 1/4 |
| contrast_strength | fiber_tracts | KS014 | reject: shuffle | -0.015 | -0.105 | 0.571 | 0.330 | 1/4 |
| contrast_strength | fiber_tracts | CSH_ZAD_019 | reject: total baseline | +0.239 | -0.044 | 0.584 | 0.500 | 0/3 |
| response_latency | thalamic | NYU-12 | reject: target1 | +0.207 | +0.308 | 0.673 | 0.327 | 0/3 |
| response_latency | thalamic | KS014 | reject: total baseline | +0.181 | -0.040 | 0.992 | 0.004 | 0/4 |
| prior_engaged | fiber_tracts | NR_0019 | reject: target0 | +0.113 | +0.324 | 0.300 | 0.874 | 0/1 |
| prior_engaged | thalamic | SWC_038 | reject: target1 | +0.095 | +0.018 | 0.944 | 0.022 | 0/3 |
| prior_engaged | thalamic | SWC_043 | reject: target1 | +0.090 | +0.051 | 0.807 | 0.316 | 0/3 |

## Decision

A derived target is only a training trigger if it passes the same local gate as prior audits: nonnegative true-vs-shuffle and true-vs-total deltas, both global target classes >=0.55, and at least 3/4 same-recording bidirectional support.
