# Composite Behavior Target Seed Sensitivity

Reruns the projected-panel composite behavior candidates across within-recording shuffle seeds.

- cases: `2`
- robust composite behavior seed candidates: `0`
- max positive shuffle-delta fraction: `1.000`
- max candidate seed fraction: `0.800`
- decision: `no_composite_behavior_seed_candidate`
- gpu training ready: `False`

| target | family | holdout | positive seeds | candidate seeds | mean delta shuffle | min/max delta shuffle | mean delta total | mean targets | bidir range |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| post_error_fast_response_le_1 | broad_named_anatomy | CSHL045 | 5/5 | 3/5 | +0.0626 | +0.0430/+0.0740 | +0.0386 | 0.632/0.756 | 2-3 |
| post_error_fast_response_le_1 | broad_named_anatomy | NR_0019 | 5/5 | 4/5 | +0.0023 | +0.0007/+0.0044 | +0.0024 | 0.576/0.640 | 2-4 |

## Decision

Do not train: the composite behavior candidates do not remain strict candidates across shuffle seeds.
