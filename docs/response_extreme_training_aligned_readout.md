# Response-Extreme Training-Aligned Readout

Closed-form ridge readout over the same shared parent-region feature space used by the A100 pilot.

- manifest: `manifests/ibl_bwm_local_cached_external_support80_projected_hdf5.json`
- region granularity: `parent`
- seed: `0`
- l2: `10.0`
- decision: `no_training_aligned_true_region_advantage`
- paid GPU trigger: `False`

| holdout | target | feature mode | shared regions | centered AUC | delta shuffle | delta total | target0 | target1 | recordings | decision |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| CSHL045 | post_error_response_extreme_25_75_le_1 | counts | 21 | 0.294 | -0.283 | -0.541 | 0.565 | 0.536 | 1/4 | reject: shuffle |
| CSHL045 | post_error_response_extreme_25_75_le_1 | recording_centered | 21 | 0.712 | -0.058 | -0.123 | 0.391 | 0.478 | 1/4 | reject: shuffle |
| NR_0019 | post_error_response_extreme_33_67_le_1 | counts | 25 | 0.355 | -0.225 | -0.400 | 0.640 | 0.333 | 1/4 | reject: shuffle |
| NR_0019 | post_error_response_extreme_33_67_le_1 | recording_centered | 25 | 0.546 | -0.135 | -0.209 | 0.360 | 0.351 | 1/4 | reject: shuffle |

Decision:

The shared parent-region feature space does not reproduce the local broad-family trigger. Do not launch another GPU run; either expose the successful broad-family feature directly or redesign the local target/control.

