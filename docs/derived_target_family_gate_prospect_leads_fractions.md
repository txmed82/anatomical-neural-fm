# Derived Target Family Gate

No-spend audit for new benchmark/control target definitions derived from cached trial fields, using the same shared-family model-free promotion gate.

- rows: `84`
- candidates: `0`
- positive centered-delta rows: `40`
- max bidirectional recordings: `1`
- max bidirectional recording fraction: `0.333`
- decision: `no_derived_target_family_candidate`

## Target Balance

| target | trials | eligible recordings | recordings |
|---|---:|---:|---:|
| contrast_strength | 7108 | 18 | 18 |
| response_latency | 10952 | 18 | 18 |
| prior_engaged | 10964 | 18 | 18 |

## Top Rows

| target | family | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs |
|---|---|---|---|---:|---:|---:|---:|---:|
| prior_engaged | broad_named_anatomy | SWC_038 | reject: shuffle | -0.106 | +0.066 | 0.993 | 0.259 | 1/3 |
| contrast_strength | fiber_tracts | KS014 | reject: shuffle | -0.066 | -0.345 | 0.618 | 0.470 | 1/4 |
| response_latency | broad_named_anatomy | MFD_06 | reject: total baseline | +0.320 | -0.002 | 1.000 | 0.000 | 0/1 |
| prior_engaged | fiber_tracts | KS014 | reject: target1 | +0.297 | +0.317 | 0.783 | 0.346 | 0/4 |
| prior_engaged | broad_named_anatomy | KS014 | reject: target1 | +0.273 | +0.247 | 0.753 | 0.292 | 0/4 |
| contrast_strength | thalamic | KS014 | reject: total baseline | +0.265 | -0.107 | 0.001 | 0.997 | 0/4 |
| response_latency | thalamic | MFD_06 | reject: total baseline | +0.246 | -0.094 | 0.000 | 1.000 | 0/1 |
| contrast_strength | fiber_tracts | NR_0019 | reject: total baseline | +0.230 | -0.195 | 0.343 | 0.873 | 0/1 |
| prior_engaged | thalamic | CSH_ZAD_019 | reject: total baseline | +0.217 | -0.663 | 0.656 | 0.324 | 0/3 |
| response_latency | thalamic | SWC_043 | reject: target1 | +0.193 | +0.241 | 0.661 | 0.339 | 0/3 |
| prior_engaged | fiber_tracts | CSH_ZAD_019 | reject: total baseline | +0.191 | -0.274 | 0.359 | 0.604 | 0/3 |
| prior_engaged | broad_named_anatomy | MFD_06 | reject: total baseline | +0.161 | -0.152 | 1.000 | 0.000 | 0/1 |
| response_latency | thalamic | SWC_038 | reject: target1 | +0.160 | +0.229 | 0.762 | 0.238 | 0/3 |
| prior_engaged | hippocampal_formation | MFD_06 | reject: target0 | +0.128 | +0.137 | 0.000 | 0.990 | 0/1 |

## Decision

A derived target is only a training trigger if it passes the same local gate as prior audits: nonnegative true-vs-shuffle and true-vs-total deltas, both global target classes >=0.55, and at least 3/4 same-recording bidirectional support.
