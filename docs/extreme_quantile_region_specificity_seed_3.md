# Extreme-Quantile Region Specificity Scan

Strict single-parent-region scan for the response-latency extreme target. Rows use the same true-vs-shuffle, total-baseline, target-class, and same-recording bidirectionality gate as the family candidate.

- target: `response_latency_extreme`
- quantiles: `0.20` / `0.80`
- regions: `79`
- holdouts: `7`
- candidates: `0`
- positive centered-delta rows: `228`
- max bidirectional recording fraction: `0.750`
- decision: `no_extreme_quantile_region_candidate`

## Top Rows

| region | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs | eval nonzero |
|---|---|---|---:|---:|---:|---:|---:|---:|
| BS | KS014 | reject: total baseline | +0.223 | -0.106 | 0.602 | 0.828 | 3/4 | 0.387 |
| BS | NR_0019 | reject: target0 | +0.144 | +0.021 | 0.226 | 0.926 | 2/4 | 0.194 |
| PRT | CSH_ZAD_019 | reject: target0 | +0.034 | +0.038 | 0.404 | 0.789 | 2/4 | 0.268 |
| MOs | SWC_038 | reject: shuffle | -0.108 | -0.051 | 0.869 | 0.300 | 2/4 | 0.208 |
| VISpm | KS014 | reject: total baseline | +0.260 | -0.181 | 0.983 | 0.190 | 1/4 | 0.107 |
| LGd | MFD_06 | reject: target0 | +0.204 | +0.292 | 0.118 | 0.965 | 1/4 | 0.080 |
| IB | SWC_043 | reject: target1 | +0.198 | +0.315 | 0.921 | 0.191 | 1/4 | 0.112 |
| LAT | CSH_ZAD_019 | reject: target1 | +0.197 | +0.095 | 0.791 | 0.217 | 1/4 | 0.236 |
| LZ | NYU-12 | reject: target1 | +0.189 | +0.337 | 0.904 | 0.169 | 1/4 | 0.148 |
| PRT | SWC_038 | reject: target1 | +0.184 | +0.018 | 0.950 | 0.156 | 1/4 | 0.100 |
| CA | NYU-12 | reject: target0 | +0.183 | +0.214 | 0.268 | 0.815 | 1/4 | 0.215 |
| VP | CSH_ZAD_019 | reject: target0 | +0.170 | +0.296 | 0.157 | 0.946 | 1/4 | 0.101 |
| LZ | SWC_043 | reject: target1 | +0.141 | +0.028 | 0.900 | 0.156 | 1/4 | 0.125 |
| SSp-bfd | NR_0019 | reject: total baseline | +0.128 | -0.039 | 0.216 | 0.868 | 1/4 | 0.150 |
| cVIIIn | NYU-12 | reject: target0 | +0.124 | +0.262 | 0.251 | 0.770 | 1/4 | 0.224 |
| BS | NYU-12 | reject: target0 | +0.113 | +0.232 | 0.319 | 0.798 | 1/4 | 0.235 |

## Decision

No single parent region improves on the broad-anatomy candidate under the strict local gate.
