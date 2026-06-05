# Extreme-Quantile Region Specificity Scan

Strict single-parent-region scan for the response-latency extreme target. Rows use the same true-vs-shuffle, total-baseline, target-class, and same-recording bidirectionality gate as the family candidate.

- target: `response_latency_extreme`
- quantiles: `0.20` / `0.80`
- regions: `79`
- holdouts: `7`
- candidates: `0`
- positive centered-delta rows: `242`
- max bidirectional recording fraction: `0.500`
- decision: `no_extreme_quantile_region_candidate`

## Top Rows

| region | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs | eval nonzero |
|---|---|---|---:|---:|---:|---:|---:|---:|
| root | KS014 | reject: total baseline | +0.131 | -0.016 | 0.870 | 0.433 | 2/4 | 0.272 |
| root | NYU-12 | reject: target1 | +0.119 | +0.125 | 0.829 | 0.347 | 2/4 | 0.250 |
| cc | SWC_038 | reject: total baseline | +0.050 | -0.004 | 0.782 | 0.331 | 2/4 | 0.285 |
| PRT | CSH_ZAD_019 | reject: target0 | +0.046 | +0.038 | 0.399 | 0.773 | 2/4 | 0.268 |
| root | NR_0019 | reject: shuffle | -0.042 | -0.186 | 0.598 | 0.303 | 2/4 | 0.249 |
| MOs | SWC_038 | reject: shuffle | -0.124 | -0.051 | 0.813 | 0.293 | 2/4 | 0.208 |
| VP | MFD_06 | reject: target1 | +0.390 | +0.308 | 0.981 | 0.125 | 1/4 | 0.071 |
| LGd | MFD_06 | reject: target0 | +0.311 | +0.292 | 0.124 | 0.967 | 1/4 | 0.080 |
| LZ | NYU-12 | reject: target1 | +0.217 | +0.337 | 0.890 | 0.188 | 1/4 | 0.148 |
| cVIIIn | NYU-12 | reject: target1 | +0.213 | +0.262 | 0.871 | 0.312 | 1/4 | 0.224 |
| cVIIIn | MFD_06 | reject: target1 | +0.209 | +0.006 | 0.778 | 0.290 | 1/4 | 0.255 |
| LAT | CSH_ZAD_019 | reject: target1 | +0.190 | +0.095 | 0.797 | 0.276 | 1/4 | 0.236 |
| CA | NYU-12 | reject: target0 | +0.188 | +0.214 | 0.277 | 0.831 | 1/4 | 0.215 |
| IIn | NR_0019 | reject: target1 | +0.175 | +0.099 | 0.944 | 0.114 | 1/4 | 0.097 |
| IB | SWC_043 | reject: target1 | +0.173 | +0.315 | 0.944 | 0.193 | 1/4 | 0.112 |
| DG | MFD_06 | reject: target0 | +0.167 | +0.120 | 0.104 | 0.961 | 1/4 | 0.088 |

## Decision

No single parent region improves on the broad-anatomy candidate under the strict local gate.
