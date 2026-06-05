# Composite Behavior Response-Extreme Seed Sensitivity

Reruns the projected post-error response-extreme broad-anatomy candidates across within-recording shuffle seeds.

- cases: `4`
- robust response-extreme seed candidates: `2`
- max positive shuffle-delta fraction: `1.000`
- max candidate seed fraction: `1.000`
- decision: `response_extreme_seed_candidate`
- gpu training ready: `True`

| target | family | holdout | positive seeds | candidate seeds | mean delta shuffle | min/max delta shuffle | mean delta total | mean targets | bidir range |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| post_error_response_extreme_25_75_le_1 | broad_named_anatomy | CSHL045 | 5/5 | 5/5 | +0.0507 | +0.0245/+0.0698 | +0.0366 | 0.700/0.800 | 3-3 |
| post_error_response_extreme_33_67_le_1 | broad_named_anatomy | CSHL045 | 5/5 | 4/5 | +0.0450 | +0.0277/+0.0606 | +0.0253 | 0.677/0.786 | 2-3 |
| post_error_response_extreme_33_67_le_1 | broad_named_anatomy | NR_0019 | 5/5 | 5/5 | +0.0051 | +0.0028/+0.0078 | +0.0042 | 0.656/0.684 | 3-4 |
| post_error_response_extreme_25_75_le_1 | broad_named_anatomy | NR_0019 | 5/5 | 4/5 | +0.0042 | +0.0021/+0.0062 | +0.0043 | 0.714/0.725 | 2-4 |

## Robust Candidates

| target | family | holdout |
|---|---|---|
| post_error_response_extreme_25_75_le_1 | broad_named_anatomy | CSHL045 |
| post_error_response_extreme_33_67_le_1 | broad_named_anatomy | NR_0019 |

## Decision

Run a bounded A100 pilot for the robust response-extreme candidates under the existing cost cap.
