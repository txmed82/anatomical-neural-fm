# Extreme-Quantile Region Specificity Scan

Strict single-parent-region scan for the response-latency extreme target. Rows use the same true-vs-shuffle, total-baseline, target-class, and same-recording bidirectionality gate as the family candidate.

- target: `response_latency_extreme`
- quantiles: `0.20` / `0.80`
- regions: `79`
- holdouts: `7`
- candidates: `0`
- positive centered-delta rows: `222`
- max bidirectional recording fraction: `0.500`
- decision: `no_extreme_quantile_region_candidate`

## Top Rows

| region | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs | eval nonzero |
|---|---|---|---:|---:|---:|---:|---:|---:|
| CA | NYU-12 | reject: target0 | +0.277 | +0.214 | 0.298 | 0.843 | 2/4 | 0.215 |
| root | CSH_ZAD_019 | reject: target0 | +0.056 | +0.019 | 0.538 | 0.537 | 2/4 | 0.478 |
| cc | CSH_ZAD_019 | reject: total baseline | +0.052 | -0.021 | 0.677 | 0.423 | 2/4 | 0.388 |
| root | NYU-12 | reject: target0 | +0.040 | +0.125 | 0.366 | 0.805 | 2/4 | 0.250 |
| fiber tracts | KS014 | reject: total baseline | +0.012 | -0.056 | 0.433 | 0.832 | 2/4 | 0.286 |
| MOs | SWC_038 | reject: shuffle | -0.116 | -0.051 | 0.872 | 0.302 | 2/4 | 0.208 |
| LGd | MFD_06 | reject: target1 | +0.448 | +0.292 | 0.975 | 0.122 | 1/4 | 0.080 |
| IB | SWC_043 | reject: target1 | +0.235 | +0.315 | 0.930 | 0.189 | 1/4 | 0.112 |
| LAT | CSH_ZAD_019 | reject: target1 | +0.230 | +0.095 | 0.781 | 0.300 | 1/4 | 0.236 |
| fxs | MFD_06 | reject: target0 | +0.210 | +0.039 | 0.098 | 0.950 | 1/4 | 0.087 |
| IIn | KS014 | reject: total baseline | +0.195 | -0.169 | 0.267 | 0.988 | 1/4 | 0.148 |
| VP | MFD_06 | reject: target1 | +0.191 | +0.308 | 0.975 | 0.118 | 1/4 | 0.071 |
| IIn | NR_0019 | reject: target1 | +0.179 | +0.099 | 0.957 | 0.145 | 1/4 | 0.097 |
| PRT | KS014 | reject: total baseline | +0.168 | -0.014 | 0.938 | 0.251 | 1/4 | 0.144 |
| SSp-bfd | NR_0019 | reject: total baseline | +0.157 | -0.039 | 0.225 | 0.859 | 1/4 | 0.150 |
| VP | CSH_ZAD_019 | reject: target1 | +0.145 | +0.296 | 0.939 | 0.160 | 1/4 | 0.101 |

## Decision

No single parent region improves on the broad-anatomy candidate under the strict local gate.
