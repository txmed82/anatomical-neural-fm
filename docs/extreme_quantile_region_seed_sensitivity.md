# Extreme-Quantile Region Seed Sensitivity

Reruns the strict parent-region candidate across multiple within-recording shuffle seeds.

- cases: `1`
- robust region-seed candidates: `0`
- max positive shuffle-delta fraction: `1.000`
- decision: `no_extreme_quantile_region_seed_candidate`

| target | region | holdout | positive seeds | candidate seeds | mean delta shuffle | min/max delta shuffle | mean delta total | mean targets | bidir range |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| response_latency_extreme | root | CSH_ZAD_019 | 5/5 | 1/5 | +0.0792 | +0.0483/+0.1359 | +0.0186 | 0.538/0.555 | 1-3 |

## Decision

Do not train: the coarse root-region row beats shuffle across seeds, but target and recording bidirectionality do not remain stable.
