# Fixed Broad-Family Train Arm RunPod Panel

RunPod `train.py --arm fixed_broad_family_count` panel for the two response-extreme demo cases.

- decision: `fixed_broad_family_train_arm_runpod_candidate`
- positive centered-delta cases: `2/2`
- paid GPU trigger: `False`
- next action: Package this as bounded cloud fixed-feature train-path evidence, then decide whether the remaining goal requires a transformer/foundation-model mechanism.

| holdout | target | family | feature | n eval | true centered AUC | shuffle centered AUC | delta |
|---|---|---|---|---:|---:|---:|---:|
| CSHL045 | post_error_response_extreme_25_75_le_1 | broad_named_anatomy | recording_centered | 276 | 0.8521 | 0.8388 | +0.0132 |
| NR_0019 | post_error_response_extreme_33_67_le_1 | broad_named_anatomy | recording_centered | 228 | 0.7565 | 0.7528 | +0.0036 |

## Run Artifacts

- CSHL045 true: `runs/fixed_broad_family_train_arm_panel_runpod/holdout_CSHL045/fixed_broad_family_count_none_seed0/eval_predictions.jsonl`
- CSHL045 shuffle: `runs/fixed_broad_family_train_arm_panel_runpod/holdout_CSHL045/fixed_broad_family_count_within_recording_shuffle_seed0/eval_predictions.jsonl`
- NR_0019 true: `runs/fixed_broad_family_train_arm_panel_runpod/holdout_NR_0019/fixed_broad_family_count_none_seed0/eval_predictions.jsonl`
- NR_0019 shuffle: `runs/fixed_broad_family_train_arm_panel_runpod/holdout_NR_0019/fixed_broad_family_count_within_recording_shuffle_seed0/eval_predictions.jsonl`
