# Extreme-Quantile Interpretable Region Pair Scan

Exploratory scan of conservative two-region summed composites for the response-latency extreme target. Candidate rows still require shuffle-seed and prospective-manifest validation before any GPU run.

- target: `response_latency_extreme`
- quantiles: `0.20` / `0.80`
- selected regions: `cVIIIn, BS, PRT, cc, MOs, LZ, IIn, LGd, CA, VP, VENT, IB`
- region pairs: `66`
- holdouts: `7`
- candidates: `3`
- positive centered-delta rows: `221`
- decision: `extreme_quantile_interpretable_region_pair_candidate`
- gpu training ready: `False`

## Top Rows

| pair | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs | eval nonzero |
|---|---|---|---:|---:|---:|---:|---:|---:|
| cc+LZ | CSH_ZAD_019 | candidate | +0.219 | +0.041 | 0.628 | 0.681 | 4/4 | 0.492 |
| cc+VENT | CSH_ZAD_019 | candidate | +0.087 | +0.018 | 0.610 | 0.620 | 4/4 | 0.492 |
| cc+VP | CSH_ZAD_019 | candidate | +0.083 | +0.044 | 0.591 | 0.637 | 4/4 | 0.489 |
| cVIIIn+LZ | NYU-12 | reject: target1 | +0.206 | +0.195 | 0.793 | 0.523 | 3/4 | 0.372 |
| PRT+cc | CSH_ZAD_019 | reject: target0 | +0.141 | +0.038 | 0.508 | 0.703 | 3/4 | 0.394 |
| PRT+LZ | CSH_ZAD_019 | reject: target0 | +0.125 | +0.064 | 0.543 | 0.744 | 3/4 | 0.371 |
| cc+LGd | CSH_ZAD_019 | reject: total baseline | +0.105 | -0.021 | 0.679 | 0.500 | 3/4 | 0.388 |
| cc+IIn | CSH_ZAD_019 | reject: total baseline | +0.105 | -0.021 | 0.679 | 0.497 | 3/4 | 0.388 |
| PRT+VP | CSH_ZAD_019 | reject: target1 | +0.028 | +0.083 | 0.717 | 0.503 | 3/4 | 0.368 |
| PRT+MOs | SWC_038 | reject: total baseline | +0.018 | -0.015 | 0.782 | 0.446 | 3/4 | 0.308 |
| cc+MOs | SWC_038 | reject: total baseline | +0.009 | -0.015 | 0.770 | 0.498 | 3/4 | 0.362 |
| LZ+IIn | NR_0019 | reject: total baseline | +0.385 | -0.127 | 0.366 | 0.893 | 2/4 | 0.245 |
| cc+IIn | SWC_038 | reject: target1 | +0.189 | +0.043 | 0.795 | 0.333 | 2/4 | 0.285 |
| cVIIIn+PRT | NYU-12 | reject: target1 | +0.181 | +0.262 | 0.883 | 0.343 | 2/4 | 0.224 |
| cVIIIn+IIn | NYU-12 | reject: target1 | +0.181 | +0.262 | 0.866 | 0.336 | 2/4 | 0.224 |
| cVIIIn+MOs | NYU-12 | reject: target1 | +0.181 | +0.262 | 0.857 | 0.331 | 2/4 | 0.224 |

## Decision

Validate any exploratory pair across shuffle seeds and a prospective manifest before GPU training.
