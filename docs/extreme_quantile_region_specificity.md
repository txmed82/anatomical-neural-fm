# Extreme-Quantile Region Specificity Scan

Strict single-parent-region scan for the response-latency extreme target. Rows use the same true-vs-shuffle, total-baseline, target-class, and same-recording bidirectionality gate as the family candidate.

- target: `response_latency_extreme`
- quantiles: `0.20` / `0.80`
- regions: `79`
- holdouts: `7`
- candidates: `1`
- positive centered-delta rows: `234`
- max bidirectional recording fraction: `0.750`
- decision: `extreme_quantile_region_candidate`

## Top Rows

| region | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs | eval nonzero |
|---|---|---|---:|---:|---:|---:|---:|---:|
| root | CSH_ZAD_019 | candidate | +0.136 | +0.019 | 0.625 | 0.588 | 3/4 | 0.478 |
| cVIIIn | NYU-12 | reject: target1 | +0.192 | +0.262 | 0.866 | 0.322 | 2/4 | 0.224 |
| BS | KS014 | reject: total baseline | +0.104 | -0.106 | 0.422 | 0.681 | 2/4 | 0.387 |
| PRT | CSH_ZAD_019 | reject: target0 | +0.082 | +0.038 | 0.411 | 0.791 | 2/4 | 0.268 |
| root | NR_0019 | reject: total baseline | +0.041 | -0.186 | 0.696 | 0.357 | 2/4 | 0.249 |
| root | NYU-12 | reject: target0 | +0.027 | +0.125 | 0.345 | 0.777 | 2/4 | 0.250 |
| cc | SWC_038 | reject: total baseline | +0.010 | -0.004 | 0.782 | 0.342 | 2/4 | 0.285 |
| MOs | SWC_038 | reject: shuffle | -0.023 | -0.051 | 0.874 | 0.299 | 2/4 | 0.208 |
| LZ | NYU-12 | reject: target0 | +0.343 | +0.337 | 0.164 | 0.927 | 1/4 | 0.148 |
| IIn | KS014 | reject: total baseline | +0.332 | -0.169 | 0.269 | 0.986 | 1/4 | 0.148 |
| LGd | MFD_06 | reject: target0 | +0.316 | +0.292 | 0.122 | 0.956 | 1/4 | 0.080 |
| CA | NYU-12 | reject: target1 | +0.305 | +0.214 | 0.765 | 0.354 | 1/4 | 0.215 |
| IIn | NR_0019 | reject: target1 | +0.270 | +0.099 | 0.955 | 0.130 | 1/4 | 0.097 |
| VP | MFD_06 | reject: target0 | +0.263 | +0.308 | 0.135 | 0.967 | 1/4 | 0.071 |
| CA | SWC_038 | reject: target0 | +0.255 | +0.175 | 0.126 | 0.973 | 1/4 | 0.076 |
| VENT | CSH_ZAD_019 | reject: target1 | +0.223 | +0.151 | 0.933 | 0.141 | 1/4 | 0.104 |

## Decision

At least one parent region passes the strict local gate; validate across shuffle seeds before GPU training.
