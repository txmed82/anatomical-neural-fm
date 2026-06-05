# Extreme-Quantile Interpretable Region Pair Scan

Exploratory scan of conservative two-region summed composites for the response-latency extreme target. Candidate rows still require shuffle-seed and prospective-manifest validation before any GPU run.

- target: `response_latency_extreme`
- quantiles: `0.20` / `0.80`
- selected regions: `cVIIIn, BS, PRT, cc, MOs, LZ, IIn, LGd, CA, VP, VENT, IB`
- region pairs: `66`
- holdouts: `7`
- candidates: `1`
- positive centered-delta rows: `231`
- decision: `extreme_quantile_interpretable_region_pair_candidate`
- gpu training ready: `False`

## Top Rows

| pair | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs | eval nonzero |
|---|---|---|---:|---:|---:|---:|---:|---:|
| PRT+VENT | CSH_ZAD_019 | candidate | +0.122 | +0.066 | 0.561 | 0.706 | 3/4 | 0.371 |
| PRT+LZ | CSH_ZAD_019 | reject: target1 | +0.110 | +0.064 | 0.780 | 0.503 | 3/4 | 0.371 |
| PRT+cc | SWC_038 | reject: target1 | +0.074 | +0.032 | 0.743 | 0.498 | 3/4 | 0.385 |
| PRT+VP | CSH_ZAD_019 | reject: target1 | +0.058 | +0.083 | 0.740 | 0.465 | 3/4 | 0.368 |
| cc+MOs | SWC_038 | reject: shuffle | -0.018 | -0.015 | 0.683 | 0.493 | 3/4 | 0.362 |
| PRT+MOs | SWC_038 | reject: shuffle | -0.018 | -0.015 | 0.457 | 0.757 | 3/4 | 0.308 |
| cVIIIn+LGd | MFD_06 | reject: target0 | +0.280 | +0.012 | 0.481 | 0.676 | 2/4 | 0.335 |
| cVIIIn+LZ | NYU-12 | reject: target1 | +0.256 | +0.195 | 0.765 | 0.526 | 2/4 | 0.372 |
| cVIIIn+cc | SWC_038 | reject: target1 | +0.178 | +0.043 | 0.795 | 0.351 | 2/4 | 0.285 |
| cVIIIn+LGd | NYU-12 | reject: target1 | +0.169 | +0.132 | 0.772 | 0.462 | 2/4 | 0.351 |
| cVIIIn+IB | MFD_06 | reject: total baseline | +0.167 | -0.036 | 0.792 | 0.342 | 2/4 | 0.255 |
| BS+LZ | NYU-12 | reject: target1 | +0.127 | +0.167 | 0.711 | 0.472 | 2/4 | 0.383 |
| cVIIIn+BS | NYU-12 | reject: target0 | +0.122 | +0.278 | 0.354 | 0.831 | 2/4 | 0.243 |
| cc+VP | SWC_038 | reject: target1 | +0.097 | +0.043 | 0.786 | 0.336 | 2/4 | 0.285 |
| PRT+CA | CSH_ZAD_019 | reject: target0 | +0.094 | +0.015 | 0.497 | 0.688 | 2/4 | 0.376 |
| cVIIIn+VENT | NYU-12 | reject: target1 | +0.074 | +0.098 | 0.688 | 0.451 | 2/4 | 0.363 |

## Decision

Validate any exploratory pair across shuffle seeds and a prospective manifest before GPU training.
