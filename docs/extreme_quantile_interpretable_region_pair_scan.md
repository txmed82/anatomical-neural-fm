# Extreme-Quantile Interpretable Region Pair Scan

Exploratory scan of conservative two-region summed composites for the response-latency extreme target. Candidate rows still require shuffle-seed and prospective-manifest validation before any GPU run.

- target: `response_latency_extreme`
- quantiles: `0.20` / `0.80`
- selected regions: `cVIIIn, BS, PRT, cc, MOs, LZ, IIn, LGd, CA, VP, VENT, IB`
- region pairs: `66`
- holdouts: `7`
- candidates: `2`
- positive centered-delta rows: `221`
- decision: `extreme_quantile_interpretable_region_pair_candidate`
- gpu training ready: `False`

## Top Rows

| pair | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs | eval nonzero |
|---|---|---|---:|---:|---:|---:|---:|---:|
| PRT+VP | CSH_ZAD_019 | candidate | +0.099 | +0.083 | 0.562 | 0.749 | 3/4 | 0.368 |
| cc+VP | CSH_ZAD_019 | candidate | +0.041 | +0.044 | 0.556 | 0.617 | 3/4 | 0.489 |
| cVIIIn+LZ | NYU-12 | reject: target0 | +0.249 | +0.195 | 0.526 | 0.768 | 3/4 | 0.372 |
| cVIIIn+BS | KS014 | reject: total baseline | +0.104 | -0.106 | 0.520 | 0.723 | 3/4 | 0.387 |
| PRT+LZ | CSH_ZAD_019 | reject: target0 | +0.082 | +0.064 | 0.546 | 0.701 | 3/4 | 0.371 |
| PRT+VENT | CSH_ZAD_019 | reject: target1 | +0.081 | +0.066 | 0.757 | 0.486 | 3/4 | 0.371 |
| PRT+cc | SWC_038 | reject: target1 | +0.044 | +0.032 | 0.721 | 0.478 | 3/4 | 0.385 |
| BS+PRT | KS014 | reject: total baseline | +0.031 | -0.025 | 0.822 | 0.600 | 3/4 | 0.404 |
| cc+VENT | CSH_ZAD_019 | reject: target0 | +0.027 | +0.018 | 0.526 | 0.572 | 3/4 | 0.492 |
| PRT+MOs | SWC_038 | reject: total baseline | +0.005 | -0.015 | 0.804 | 0.451 | 3/4 | 0.308 |
| cc+MOs | SWC_038 | reject: shuffle | -0.019 | -0.015 | 0.745 | 0.495 | 3/4 | 0.362 |
| cVIIIn+IB | MFD_06 | reject: total baseline | +0.223 | -0.036 | 0.774 | 0.363 | 2/4 | 0.255 |
| cVIIIn+PRT | NYU-12 | reject: target1 | +0.192 | +0.262 | 0.883 | 0.324 | 2/4 | 0.224 |
| cVIIIn+IIn | NYU-12 | reject: target1 | +0.192 | +0.262 | 0.885 | 0.324 | 2/4 | 0.224 |
| cVIIIn+MOs | NYU-12 | reject: target1 | +0.192 | +0.262 | 0.854 | 0.317 | 2/4 | 0.224 |
| cVIIIn+cc | NYU-12 | reject: target1 | +0.161 | +0.120 | 0.751 | 0.392 | 2/4 | 0.329 |

## Decision

Validate any exploratory pair across shuffle seeds and a prospective manifest before GPU training.
