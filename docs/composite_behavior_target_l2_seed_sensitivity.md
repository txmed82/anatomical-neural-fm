# Composite Behavior Target L2/Seed Sensitivity

Reruns the projected post-error fast-response broad-anatomy near miss across ridge regularization values and within-recording shuffle seeds.

- cases: `2`
- l2 values: `3`
- robust l2/seed candidates: `0`
- max positive shuffle-delta fraction: `1.000`
- max candidate seed fraction: `0.800`
- decision: `no_composite_behavior_l2_seed_candidate`
- gpu training ready: `False`

| l2 | target | family | holdout | positive seeds | candidate seeds | mean delta shuffle | mean delta total | mean targets | bidir range |
|---:|---|---|---|---:|---:|---:|---:|---:|---:|
| 1 | post_error_fast_response_le_1 | broad_named_anatomy | CSHL045 | 5/5 | 3/5 | +0.0626 | +0.0386 | 0.632/0.756 | 2-3 |
| 1 | post_error_fast_response_le_1 | broad_named_anatomy | NR_0019 | 5/5 | 4/5 | +0.0023 | +0.0024 | 0.576/0.640 | 2-4 |
| 10 | post_error_fast_response_le_1 | broad_named_anatomy | CSHL045 | 5/5 | 3/5 | +0.0626 | +0.0386 | 0.632/0.756 | 2-3 |
| 10 | post_error_fast_response_le_1 | broad_named_anatomy | NR_0019 | 5/5 | 4/5 | +0.0023 | +0.0024 | 0.576/0.640 | 2-4 |
| 100 | post_error_fast_response_le_1 | broad_named_anatomy | CSHL045 | 5/5 | 3/5 | +0.0626 | +0.0386 | 0.632/0.756 | 2-3 |
| 100 | post_error_fast_response_le_1 | broad_named_anatomy | NR_0019 | 5/5 | 4/5 | +0.0023 | +0.0024 | 0.576/0.640 | 2-4 |

## Decision

Do not train: changing ridge regularization does not make the composite behavior candidates strict across all shuffle seeds.
