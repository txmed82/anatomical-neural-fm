# Direct Broad-Family Trainable Readout

No-spend logistic-readout audit over the same fixed broad_named_anatomy response-extreme features used by the model-free package.

- decision: `direct_broad_family_trainable_candidate`
- rows: `6`
- candidate rows: `6`
- robust cases: `2/2`
- paid GPU trigger: `False`
- next action: Implement this exact fixed-family-count arm in the training code before any new GPU run.

| holdout | target | family | candidate seeds | delta shuffle | delta total | targets | bidir range |
|---|---|---|---:|---:|---:|---:|---:|
| CSHL045 | post_error_response_extreme_25_75_le_1 | broad_named_anatomy | 3/3 | +0.0655 | +0.0366 | 0.775/0.884 | 3-3 |
| NR_0019 | post_error_response_extreme_33_67_le_1 | broad_named_anatomy | 3/3 | +0.0061 | +0.0042 | 0.675/0.702 | 3-3 |

## Per-Seed Rows

| holdout | target | train seed | decision | delta shuffle | delta total | targets | bidir |
|---|---|---:|---|---:|---:|---:|---:|
| CSHL045 | post_error_response_extreme_25_75_le_1 | 0 | candidate | +0.0655 | +0.0366 | 0.775/0.884 | 3/4 |
| CSHL045 | post_error_response_extreme_25_75_le_1 | 1 | candidate | +0.0655 | +0.0366 | 0.775/0.884 | 3/4 |
| CSHL045 | post_error_response_extreme_25_75_le_1 | 2 | candidate | +0.0655 | +0.0366 | 0.775/0.884 | 3/4 |
| NR_0019 | post_error_response_extreme_33_67_le_1 | 0 | candidate | +0.0061 | +0.0042 | 0.675/0.702 | 3/4 |
| NR_0019 | post_error_response_extreme_33_67_le_1 | 1 | candidate | +0.0061 | +0.0042 | 0.675/0.702 | 3/4 |
| NR_0019 | post_error_response_extreme_33_67_le_1 | 2 | candidate | +0.0061 | +0.0042 | 0.675/0.702 | 3/4 |
