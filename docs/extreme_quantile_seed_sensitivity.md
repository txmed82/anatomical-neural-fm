# Extreme-Quantile Shuffle Seed Sensitivity

Reruns strict extreme-quantile candidates across multiple within-recording shuffle seeds.

- cases: `1`
- robust shuffle-seed candidates: `0`
- max positive shuffle-delta fraction: `0.400`
- decision: `no_extreme_quantile_shuffle_seed_candidate`

| target | family | holdout | positive seeds | candidate seeds | mean delta shuffle | min/max delta shuffle | mean delta total | mean targets | bidir range |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| response_latency_extreme | broad_named_anatomy | NR_0019 | 2/5 | 2/5 | -0.0001 | -0.0008/+0.0010 | +0.0004 | 0.638/0.676 | 4-4 |

## Decision

Do not train: the extreme-quantile candidate does not robustly beat within-recording shuffled anatomy across seeds.
