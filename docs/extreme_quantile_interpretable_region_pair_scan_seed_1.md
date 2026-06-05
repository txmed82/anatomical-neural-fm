# Extreme-Quantile Interpretable Region Pair Scan

Exploratory scan of conservative two-region summed composites for the response-latency extreme target. Candidate rows still require shuffle-seed and prospective-manifest validation before any GPU run.

- target: `response_latency_extreme`
- quantiles: `0.20` / `0.80`
- selected regions: `cVIIIn, BS, PRT, cc, MOs, LZ, IIn, LGd, CA, VP, VENT, IB`
- region pairs: `66`
- holdouts: `7`
- candidates: `0`
- positive centered-delta rows: `209`
- decision: `no_extreme_quantile_interpretable_region_pair_candidate`
- gpu training ready: `False`

## Top Rows

| pair | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs | eval nonzero |
|---|---|---|---:|---:|---:|---:|---:|---:|
| PRT+cc | CSH_ZAD_019 | reject: target1 | +0.069 | +0.038 | 0.746 | 0.489 | 3/4 | 0.394 |
| PRT+cc | SWC_038 | reject: target1 | +0.059 | +0.032 | 0.721 | 0.475 | 3/4 | 0.385 |
| PRT+MOs | SWC_038 | reject: shuffle | -0.011 | -0.015 | 0.804 | 0.448 | 3/4 | 0.308 |
| cVIIIn+LGd | MFD_06 | reject: target0 | +0.394 | +0.012 | 0.488 | 0.695 | 2/4 | 0.335 |
| LGd+CA | NYU-12 | reject: target0 | +0.234 | +0.116 | 0.291 | 0.845 | 2/4 | 0.215 |
| PRT+IIn | NR_0019 | reject: target1 | +0.222 | +0.027 | 0.906 | 0.264 | 2/4 | 0.185 |
| BS+IIn | NR_0019 | reject: target0 | +0.197 | +0.041 | 0.226 | 0.891 | 2/4 | 0.191 |
| cc+LZ | SWC_038 | reject: total baseline | +0.126 | -0.004 | 0.311 | 0.788 | 2/4 | 0.285 |
| cVIIIn+LZ | NYU-12 | reject: target0 | +0.115 | +0.195 | 0.446 | 0.690 | 2/4 | 0.372 |
| BS+LZ | NYU-12 | reject: target0 | +0.100 | +0.167 | 0.439 | 0.681 | 2/4 | 0.383 |
| cVIIIn+LGd | NYU-12 | reject: target1 | +0.069 | +0.132 | 0.634 | 0.401 | 2/4 | 0.351 |
| PRT+VP | CSH_ZAD_019 | reject: target1 | +0.067 | +0.083 | 0.784 | 0.486 | 2/4 | 0.368 |
| cc+LZ | CSH_ZAD_019 | reject: recording bidirectionality | +0.060 | +0.041 | 0.607 | 0.559 | 2/4 | 0.492 |
| cc+VP | CSH_ZAD_019 | reject: recording bidirectionality | +0.059 | +0.044 | 0.615 | 0.581 | 2/4 | 0.489 |
| PRT+LZ | CSH_ZAD_019 | reject: recording bidirectionality | +0.056 | +0.064 | 0.556 | 0.679 | 2/4 | 0.371 |
| MOs+IIn | SWC_038 | reject: target1 | +0.051 | +0.042 | 0.871 | 0.302 | 2/4 | 0.208 |

## Decision

Do not train: no interpretable two-region composite passes the strict local gate.
