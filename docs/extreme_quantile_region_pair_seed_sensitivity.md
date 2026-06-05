# Extreme-Quantile Region Pair Seed Sensitivity

Reruns exploratory interpretable two-region pair candidates across shuffle seeds.

- cases: `2`
- robust region-pair seed candidates: `0`
- max positive shuffle-delta fraction: `1.000`
- decision: `no_extreme_quantile_region_pair_seed_candidate`
- gpu training ready: `False`

| target | pair | holdout | positive seeds | candidate seeds | mean delta shuffle | min/max delta shuffle | mean delta total | mean targets | bidir range |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| response_latency_extreme | PRT+VP | CSH_ZAD_019 | 5/5 | 2/5 | +0.0689 | +0.0284/+0.0992 | +0.0835 | 0.673/0.585 | 2-3 |
| response_latency_extreme | cc+VP | CSH_ZAD_019 | 4/5 | 2/5 | +0.0401 | -0.0065/+0.0835 | +0.0443 | 0.570/0.586 | 2-4 |

## Decision

Do not train: exploratory interpretable region-pair candidates do not remain strict candidates across shuffle seeds.
