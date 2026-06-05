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

## Missing Sweep Summary

No `runs/fixed_broad_family_train_arm_panel_runpod/summary.md`, `within_summary.md`, or
`cross_summary.md` file was present when cleanup pushed artifacts. Treat this
cloud result as incomplete/non-evidence even if the pod exit status is 0.

