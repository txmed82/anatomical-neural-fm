# Cloud Phase 3-5 Results

Date: 2026-06-05T15:48:09Z

RunPod target: NVIDIA A100 80GB PCIe,NVIDIA A100-SXM4-80GB.

Exit status: 0

Configuration:

- branch: runpod-pilot-phases-3-5
- build recordings: 0
- max steps: 300
- eval batches: 20
- target mode: post_error_response_extreme_25_75_le_1
- sweep script: scripts/run_response_extreme_trigger_a100.sh
- setup mode: project
- build mode: batch
- skip cell-type priors: True
- skip sweep: False
- startup smoke only: False
- dependency diagnostic: False
- max runtime seconds: 3600
- output root: `runs/response_extreme_trigger_a100`
- sweep env: `RESPONSE_EXTREME_TRIGGER=1`

## Build Report

# IBL BrainSet Batch Build

Manifest: `manifests/ibl_bwm_local_cached_external_support80_projected_hdf5.json`
Shard: 1/1
Selected recordings: 31
Available recordings: 31
Skipped existing: 31
Failures: 0
Elapsed seconds: 0
Include wheel: `True`
Trial-window-only spikes: `False`
Window length: `1.0`

## Available

| session | probe | path |
|---|---|---|
| 03063955-2523-47bd-ae57-f7489dd40f15 | probe01 | `data/brainsets/ibl_bwm/03063955-2523-47bd-ae57-f7489dd40f15_probe01.h5` |
| 032ffcdf-7692-40b3-b9ff-8def1fc18b2e | probe00 | `data/brainsets/ibl_bwm/032ffcdf-7692-40b3-b9ff-8def1fc18b2e_probe00.h5` |
| 034e726f-b35f-41e0-8d6c-a22cc32391fb | probe01 | `data/brainsets/ibl_bwm/034e726f-b35f-41e0-8d6c-a22cc32391fb_probe01.h5` |
| 09b2c4d1-058d-4c84-9fd4-97530f85baf6 | probe00 | `data/brainsets/ibl_bwm/09b2c4d1-058d-4c84-9fd4-97530f85baf6_probe00.h5` |
| 16693458-0801-4d35-a3f1-9115c7e5acfd | probe00 | `data/brainsets/ibl_bwm/16693458-0801-4d35-a3f1-9115c7e5acfd_probe00.h5` |
| 16693458-0801-4d35-a3f1-9115c7e5acfd | probe01 | `data/brainsets/ibl_bwm/16693458-0801-4d35-a3f1-9115c7e5acfd_probe01.h5` |
| 1e45d992-c356-40e1-9be1-a506d944896f | probe01 | `data/brainsets/ibl_bwm/1e45d992-c356-40e1-9be1-a506d944896f_probe01.h5` |
| 35eeb752-8f4f-4040-9714-ba0f5b7ccdfe | probe00 | `data/brainsets/ibl_bwm/35eeb752-8f4f-4040-9714-ba0f5b7ccdfe_probe00.h5` |
| 3f71aa98-08c6-4e79-b4c8-00eae4f03eff | probe00 | `data/brainsets/ibl_bwm/3f71aa98-08c6-4e79-b4c8-00eae4f03eff_probe00.h5` |
| 41872d7f-75cb-4445-bb1a-132b354c44f0 | probe01 | `data/brainsets/ibl_bwm/41872d7f-75cb-4445-bb1a-132b354c44f0_probe01.h5` |
| 49e0ab27-827a-4c91-bcaa-97eea27a1b8d | probe01 | `data/brainsets/ibl_bwm/49e0ab27-827a-4c91-bcaa-97eea27a1b8d_probe01.h5` |
| 4d8c7767-981c-4347-8e5e-5d5fffe38534 | probe01 | `data/brainsets/ibl_bwm/4d8c7767-981c-4347-8e5e-5d5fffe38534_probe01.h5` |
| 5adab0b7-dfd0-467d-b09d-43cb7ca5d59c | probe00 | `data/brainsets/ibl_bwm/5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe00.h5` |
| 5adab0b7-dfd0-467d-b09d-43cb7ca5d59c | probe01 | `data/brainsets/ibl_bwm/5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe01.h5` |
| 5d6aa933-4b00-4e99-ae2d-5003657592e9 | probe01 | `data/brainsets/ibl_bwm/5d6aa933-4b00-4e99-ae2d-5003657592e9_probe01.h5` |
| 63c70ae8-4dfb-418b-b21b-f0b1e5fba6c9 | probe00 | `data/brainsets/ibl_bwm/63c70ae8-4dfb-418b-b21b-f0b1e5fba6c9_probe00.h5` |
| 63c70ae8-4dfb-418b-b21b-f0b1e5fba6c9 | probe01 | `data/brainsets/ibl_bwm/63c70ae8-4dfb-418b-b21b-f0b1e5fba6c9_probe01.h5` |
| 63f3dbc1-1a5f-44e5-98dd-ce25cd2b7871 | probe00 | `data/brainsets/ibl_bwm/63f3dbc1-1a5f-44e5-98dd-ce25cd2b7871_probe00.h5` |
| 6899a67d-2e53-4215-a52a-c7021b5da5d4 | probe00 | `data/brainsets/ibl_bwm/6899a67d-2e53-4215-a52a-c7021b5da5d4_probe00.h5` |
| 7939711b-8b4d-4251-b698-b97c1eaa846e | probe01 | `data/brainsets/ibl_bwm/7939711b-8b4d-4251-b698-b97c1eaa846e_probe01.h5` |
| a1782f4f-86b0-480c-a7f2-3d8f1ab482ab | probe00 | `data/brainsets/ibl_bwm/a1782f4f-86b0-480c-a7f2-3d8f1ab482ab_probe00.h5` |
| a8a8af78-16de-4841-ab07-fde4b5281a03 | probe00 | `data/brainsets/ibl_bwm/a8a8af78-16de-4841-ab07-fde4b5281a03_probe00.h5` |
| a8a8af78-16de-4841-ab07-fde4b5281a03 | probe01 | `data/brainsets/ibl_bwm/a8a8af78-16de-4841-ab07-fde4b5281a03_probe01.h5` |
| b182b754-3c3e-4942-8144-6ee790926b58 | probe01 | `data/brainsets/ibl_bwm/b182b754-3c3e-4942-8144-6ee790926b58_probe01.h5` |
| b887df2c-bb9c-44c9-a9c0-538da87b2cab | probe00 | `data/brainsets/ibl_bwm/b887df2c-bb9c-44c9-a9c0-538da87b2cab_probe00.h5` |
| b887df2c-bb9c-44c9-a9c0-538da87b2cab | probe01 | `data/brainsets/ibl_bwm/b887df2c-bb9c-44c9-a9c0-538da87b2cab_probe01.h5` |
| b9c205c3-feac-485b-a89d-afc96d9cb280 | probe00 | `data/brainsets/ibl_bwm/b9c205c3-feac-485b-a89d-afc96d9cb280_probe00.h5` |
| dfd8e7df-dc51-4589-b6ca-7baccfeb94b4 | probe01 | `data/brainsets/ibl_bwm/dfd8e7df-dc51-4589-b6ca-7baccfeb94b4_probe01.h5` |
| e1931de1-cf7b-49af-af33-2ade15e8abe7 | probe00 | `data/brainsets/ibl_bwm/e1931de1-cf7b-49af-af33-2ade15e8abe7_probe00.h5` |
| edd22318-216c-44ff-bc24-49ce8be78374 | probe00 | `data/brainsets/ibl_bwm/edd22318-216c-44ff-bc24-49ce8be78374_probe00.h5` |
| fa704052-147e-46f6-b190-a65b837e605e | probe00 | `data/brainsets/ibl_bwm/fa704052-147e-46f6-b190-a65b837e605e_probe00.h5` |

## Cache Audit

# BrainSet S3 Cache Audit

Manifest: `manifests/ibl_bwm_local_cached_external_support80_projected_hdf5.json`
Cache: `s3://rppfvo6ifn/brainsets/ibl_bwm`
Present: 31/31 (100.0%)

## Missing

none

## Present

| filename |
|---|
| `03063955-2523-47bd-ae57-f7489dd40f15_probe01.h5` |
| `032ffcdf-7692-40b3-b9ff-8def1fc18b2e_probe00.h5` |
| `034e726f-b35f-41e0-8d6c-a22cc32391fb_probe01.h5` |
| `09b2c4d1-058d-4c84-9fd4-97530f85baf6_probe00.h5` |
| `16693458-0801-4d35-a3f1-9115c7e5acfd_probe00.h5` |
| `16693458-0801-4d35-a3f1-9115c7e5acfd_probe01.h5` |
| `1e45d992-c356-40e1-9be1-a506d944896f_probe01.h5` |
| `35eeb752-8f4f-4040-9714-ba0f5b7ccdfe_probe00.h5` |
| `3f71aa98-08c6-4e79-b4c8-00eae4f03eff_probe00.h5` |
| `41872d7f-75cb-4445-bb1a-132b354c44f0_probe01.h5` |
| `49e0ab27-827a-4c91-bcaa-97eea27a1b8d_probe01.h5` |
| `4d8c7767-981c-4347-8e5e-5d5fffe38534_probe01.h5` |
| `5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe00.h5` |
| `5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe01.h5` |
| `5d6aa933-4b00-4e99-ae2d-5003657592e9_probe01.h5` |
| `63c70ae8-4dfb-418b-b21b-f0b1e5fba6c9_probe00.h5` |
| `63c70ae8-4dfb-418b-b21b-f0b1e5fba6c9_probe01.h5` |
| `63f3dbc1-1a5f-44e5-98dd-ce25cd2b7871_probe00.h5` |
| `6899a67d-2e53-4215-a52a-c7021b5da5d4_probe00.h5` |
| `7939711b-8b4d-4251-b698-b97c1eaa846e_probe01.h5` |
| `a1782f4f-86b0-480c-a7f2-3d8f1ab482ab_probe00.h5` |
| `a8a8af78-16de-4841-ab07-fde4b5281a03_probe00.h5` |
| `a8a8af78-16de-4841-ab07-fde4b5281a03_probe01.h5` |
| `b182b754-3c3e-4942-8144-6ee790926b58_probe01.h5` |
| `b887df2c-bb9c-44c9-a9c0-538da87b2cab_probe00.h5` |
| `b887df2c-bb9c-44c9-a9c0-538da87b2cab_probe01.h5` |
| `b9c205c3-feac-485b-a89d-afc96d9cb280_probe00.h5` |
| `dfd8e7df-dc51-4589-b6ca-7baccfeb94b4_probe01.h5` |
| `e1931de1-cf7b-49af-af33-2ade15e8abe7_probe00.h5` |
| `edd22318-216c-44ff-bc24-49ce8be78374_probe00.h5` |
| `fa704052-147e-46f6-b190-a65b837e605e_probe00.h5` |

## Summary

# Response-Extreme Trigger A100 Pilot

Cases:

- CSHL045, target `post_error_response_extreme_25_75_le_1`
- NR_0019, target `post_error_response_extreme_33_67_le_1`

Common settings:

- seeds: `0`
- max steps: `300`
- eval batches: `20`
- region filter: `shared_regions`
- region granularity: `parent`
- shuffle control: `shuffle`

## CSHL045 25/75

# Leave-subject-out analysis

root: `runs/response_extreme_trigger_a100/cshl045_post_error_extreme_25_75`

## Per-Holdout AUC and Delta vs Shared Null

| holdout | arm | n_seeds | mean_AUC | mean_delta_vs_shared | seed_deltas |
|---|---|---|---|---|---|
| CSHL045 | region_only | 1 | 0.496 | -0.065 | -0.065 |
| CSHL045 | region_shuffle | 1 | 0.602 | +0.041 | +0.041 |

## Aggregate Delta vs Shared Null

| arm | n_pairs | mean_delta | positive_pairs |
|---|---|---|---|
| region_only | 1 | -0.065 | 0/1 |
| region_shuffle | 1 | +0.041 | 1/1 |

## NR_0019 33/67

# Leave-subject-out analysis

root: `runs/response_extreme_trigger_a100/nr0019_post_error_extreme_33_67`

## Per-Holdout AUC and Delta vs Shared Null

| holdout | arm | n_seeds | mean_AUC | mean_delta_vs_shared | seed_deltas |
|---|---|---|---|---|---|
| NR_0019 | region_only | 1 | 0.552 | -0.037 | -0.037 |
| NR_0019 | region_shuffle | 1 | 0.593 | +0.004 | +0.004 |

## Aggregate Delta vs Shared Null

| arm | n_pairs | mean_delta | positive_pairs |
|---|---|---|---|
| region_only | 1 | -0.037 | 0/1 |
| region_shuffle | 1 | +0.004 | 1/1 |
