# Derived Target Family Gate

No-spend audit for new benchmark/control target definitions derived from cached trial fields, using the same shared-family model-free promotion gate.

- rows: `84`
- candidates: `0`
- positive centered-delta rows: `43`
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
| prior_engaged | broad_named_anatomy | SWC_038 | reject: target0 | +0.307 | +0.053 | 0.307 | 0.949 | 1/3 |
| prior_engaged | fiber_tracts | SWC_038 | reject: target0 | +0.303 | +0.112 | 0.326 | 0.935 | 1/3 |
| prior_engaged | fiber_tracts | CSH_ZAD_019 | reject: total baseline | +0.159 | -0.477 | 0.652 | 0.538 | 1/3 |
| prior_engaged | broad_named_anatomy | CSH_ZAD_019 | reject: total baseline | +0.095 | -0.464 | 0.633 | 0.578 | 1/3 |
| response_latency | hippocampal_formation | CSH_ZAD_019 | reject: total baseline | +0.047 | -0.011 | 0.880 | 0.178 | 1/3 |
| prior_engaged | fiber_tracts | KS014 | reject: target0 | +0.226 | +0.316 | 0.408 | 0.764 | 1/4 |
| response_latency | fiber_tracts | KS014 | reject: total baseline | +0.155 | -0.320 | 0.753 | 0.399 | 1/4 |
| contrast_strength | broad_named_anatomy | KS014 | reject: total baseline | +0.067 | -0.281 | 0.680 | 0.319 | 1/4 |
| response_latency | fiber_tracts | NR_0019 | reject: total baseline | +0.445 | -0.099 | 0.305 | 0.929 | 0/1 |
| response_latency | thalamic | MFD_06 | reject: target0 | +0.420 | +0.012 | 0.030 | 1.000 | 0/1 |
| prior_engaged | fiber_tracts | NR_0019 | reject: target0 | +0.403 | +0.492 | 0.033 | 0.997 | 0/1 |
| prior_engaged | broad_named_anatomy | NR_0019 | reject: target0 | +0.341 | +0.221 | 0.389 | 0.851 | 0/1 |
| response_latency | broad_named_anatomy | NR_0019 | reject: total baseline | +0.319 | -0.128 | 0.314 | 0.854 | 0/1 |
| prior_engaged | broad_named_anatomy | KS014 | reject: target1 | +0.269 | +0.254 | 0.750 | 0.367 | 0/4 |

## Decision

A derived target is only a training trigger if it passes the same local gate as prior audits: nonnegative true-vs-shuffle and true-vs-total deltas, both global target classes >=0.55, and at least 3/4 same-recording bidirectional support.
