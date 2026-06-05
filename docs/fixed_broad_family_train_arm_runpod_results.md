# Cloud Phase 3-5 Results

Date: 2026-06-05T16:25:40Z

RunPod target: NVIDIA L4.

Exit status: 0

Configuration:

- branch: runpod-pilot-phases-3-5
- build recordings: 0
- max steps: 1000
- eval batches: 1
- target mode: post_error_response_extreme_25_75_le_1
- sweep script: scripts/run_fixed_broad_family_train_arm_panel.sh
- setup mode: project
- build mode: batch
- skip cell-type priors: True
- skip sweep: False
- startup smoke only: False
- dependency diagnostic: False
- max runtime seconds: 1800
- output root: `runs/fixed_broad_family_train_arm_panel_runpod`
- sweep env: `MANIFEST_PATH=manifests/ibl_bwm_local_cached_external_support80_projected_hdf5.json, SEEDS=0, DEVICE=cpu, MAX_STEPS=1000, BEST_METRIC=full_eval_centered_auc`

## Summary

The wrapper completed and wrote held-out prediction files for all four arms.
The generic artifact collector did not commit the wrapper `summary.md`, so the
panel was re-summarized from committed `eval_predictions.jsonl` files in
`docs/fixed_broad_family_train_arm_runpod_panel.md`.

| holdout | target | true centered AUC | shuffle centered AUC | delta |
|---|---|---:|---:|---:|
| CSHL045 | post_error_response_extreme_25_75_le_1 | 0.8521 | 0.8388 | +0.0132 |
| NR_0019 | post_error_response_extreme_33_67_le_1 | 0.7565 | 0.7528 | +0.0036 |

Decision: bounded cloud replication of the fixed broad-family count arm is
positive on both response-extreme cases. This is fixed-feature train-path
evidence, not a transformer/foundation-model result.
