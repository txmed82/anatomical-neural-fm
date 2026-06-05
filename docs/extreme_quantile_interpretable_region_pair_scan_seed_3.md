# Extreme-Quantile Interpretable Region Pair Scan

Exploratory scan of conservative two-region summed composites for the response-latency extreme target. Candidate rows still require shuffle-seed and prospective-manifest validation before any GPU run.

- target: `response_latency_extreme`
- quantiles: `0.20` / `0.80`
- selected regions: `cVIIIn, BS, PRT, cc, MOs, LZ, IIn, LGd, CA, VP, VENT, IB`
- region pairs: `66`
- holdouts: `7`
- candidates: `1`
- positive centered-delta rows: `217`
- decision: `extreme_quantile_interpretable_region_pair_candidate`
- gpu training ready: `False`

## Top Rows

| pair | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs | eval nonzero |
|---|---|---|---:|---:|---:|---:|---:|---:|
| PRT+VP | CSH_ZAD_019 | candidate | +0.092 | +0.083 | 0.559 | 0.720 | 3/4 | 0.368 |
| BS+cc | KS014 | reject: total baseline | +0.228 | -0.022 | 0.824 | 0.638 | 3/4 | 0.402 |
| BS+VP | KS014 | reject: total baseline | +0.223 | -0.106 | 0.619 | 0.843 | 3/4 | 0.387 |
| cVIIIn+BS | KS014 | reject: total baseline | +0.223 | -0.106 | 0.615 | 0.843 | 3/4 | 0.387 |
| BS+LGd | KS014 | reject: total baseline | +0.223 | -0.106 | 0.613 | 0.843 | 3/4 | 0.387 |
| BS+LZ | KS014 | reject: total baseline | +0.223 | -0.106 | 0.602 | 0.824 | 3/4 | 0.387 |
| BS+VENT | KS014 | reject: total baseline | +0.223 | -0.106 | 0.592 | 0.814 | 3/4 | 0.387 |
| BS+IB | KS014 | reject: total baseline | +0.223 | -0.106 | 0.573 | 0.785 | 3/4 | 0.387 |
| BS+IIn | KS014 | reject: total baseline | +0.139 | -0.007 | 0.621 | 0.841 | 3/4 | 0.401 |
| BS+PRT | KS014 | reject: total baseline | +0.083 | -0.025 | 0.878 | 0.704 | 3/4 | 0.404 |
| PRT+LZ | CSH_ZAD_019 | reject: target1 | +0.082 | +0.064 | 0.772 | 0.508 | 3/4 | 0.371 |
| BS+VP | NR_0019 | reject: total baseline | +0.011 | -0.027 | 0.486 | 0.909 | 3/4 | 0.378 |
| PRT+MOs | SWC_038 | reject: total baseline | +0.008 | -0.015 | 0.799 | 0.455 | 3/4 | 0.308 |
| BS+MOs | KS014 | reject: total baseline | +0.223 | -0.106 | 0.656 | 0.422 | 2/4 | 0.387 |
| BS+CA | KS014 | reject: total baseline | +0.223 | -0.106 | 0.636 | 0.420 | 2/4 | 0.387 |
| LZ+VENT | SWC_043 | reject: target0 | +0.186 | +0.118 | 0.336 | 0.816 | 2/4 | 0.256 |

## Decision

Validate any exploratory pair across shuffle seeds and a prospective manifest before GPU training.
