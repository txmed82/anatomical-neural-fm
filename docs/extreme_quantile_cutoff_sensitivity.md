# Extreme-Quantile Cutoff Sensitivity

Tests whether changing the response-latency extreme cutoff rescues the single-seed candidate across multiple within-recording shuffle seeds.

- target: `response_latency_extreme`
- family: `broad_named_anatomy`
- holdout: `NR_0019`
- cutoffs: `3`
- robust cutoff candidates: `0`
- best cutoff: `20/80`
- decision: `no_extreme_quantile_cutoff_candidate`

| cutoff | positive seeds | candidate seeds | mean delta shuffle | min/max delta shuffle | mean delta total | mean targets | bidir range |
|---|---:|---:|---:|---:|---:|---:|---:|
| 20/80 | 2/5 | 2/5 | +0.0002 | -0.0006/+0.0017 | +0.0003 | 0.678/0.709 | 4-4 |
| 25/75 | 2/5 | 2/5 | -0.0001 | -0.0008/+0.0010 | +0.0004 | 0.638/0.676 | 4-4 |
| 30/70 | 1/5 | 0/5 | -0.0002 | -0.0018/+0.0017 | -0.0001 | 0.598/0.638 | 1-3 |

## Decision

Do not train: cutoff changes do not make the extreme response-latency candidate robust to within-recording shuffled anatomy.
