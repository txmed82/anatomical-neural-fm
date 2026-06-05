# Extreme-Quantile Region Specificity Scan

Strict single-parent-region scan for the response-latency extreme target. Rows use the same true-vs-shuffle, total-baseline, target-class, and same-recording bidirectionality gate as the family candidate.

- target: `response_latency_extreme`
- quantiles: `0.20` / `0.80`
- regions: `79`
- holdouts: `7`
- candidates: `0`
- positive centered-delta rows: `234`
- max bidirectional recording fraction: `0.750`
- decision: `no_extreme_quantile_region_candidate`

## Top Rows

| region | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs | eval nonzero |
|---|---|---|---:|---:|---:|---:|---:|---:|
| cc | CSH_ZAD_019 | reject: total baseline | +0.105 | -0.021 | 0.679 | 0.503 | 3/4 | 0.388 |
| CA | NYU-12 | reject: target0 | +0.224 | +0.214 | 0.296 | 0.852 | 2/4 | 0.215 |
| cc | SWC_038 | reject: total baseline | +0.142 | -0.004 | 0.797 | 0.344 | 2/4 | 0.285 |
| DG | NYU-12 | reject: total baseline | +0.070 | -0.008 | 0.796 | 0.364 | 2/4 | 0.212 |
| mfbc | CSH_ZAD_019 | reject: shuffle | -0.009 | -0.081 | 0.487 | 0.506 | 2/4 | 0.515 |
| PRT | CSH_ZAD_019 | reject: shuffle | -0.025 | +0.038 | 0.388 | 0.786 | 2/4 | 0.268 |
| MOs | SWC_038 | reject: shuffle | -0.036 | -0.051 | 0.867 | 0.297 | 2/4 | 0.208 |
| CA | SWC_038 | reject: target1 | +0.384 | +0.175 | 0.935 | 0.153 | 1/4 | 0.076 |
| LZ | NR_0019 | reject: total baseline | +0.342 | -0.069 | 0.226 | 0.947 | 1/4 | 0.149 |
| VP | CSH_ZAD_019 | reject: target1 | +0.225 | +0.296 | 0.920 | 0.152 | 1/4 | 0.101 |
| IB | SWC_043 | reject: target0 | +0.205 | +0.315 | 0.156 | 0.918 | 1/4 | 0.112 |
| LZ | NYU-12 | reject: target1 | +0.196 | +0.337 | 0.913 | 0.181 | 1/4 | 0.148 |
| cVIIIn | NYU-12 | reject: target0 | +0.181 | +0.262 | 0.310 | 0.824 | 1/4 | 0.224 |
| PRT | KS014 | reject: total baseline | +0.155 | -0.014 | 0.888 | 0.201 | 1/4 | 0.144 |
| CA | CSH_ZAD_019 | reject: target1 | +0.148 | +0.025 | 0.732 | 0.256 | 1/4 | 0.245 |
| PRT | SWC_038 | reject: target1 | +0.136 | +0.018 | 0.960 | 0.160 | 1/4 | 0.100 |

## Decision

No single parent region improves on the broad-anatomy candidate under the strict local gate.
