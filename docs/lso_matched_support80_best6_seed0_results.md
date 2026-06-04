# Cloud Phase 3-5 Results

Date: 2026-06-04T21:18:42Z

RunPod target: A100 pilot.

Exit status: 0

Configuration:

- branch: runpod-pilot-phases-3-5
- build recordings: 28
- max steps: 300
- eval batches: 20
- target mode: stimulus_side
- sweep script: scripts/run_lso_matched_support80_best6_a100.sh
- setup mode: project
- skip cell-type priors: False
- skip sweep: False
- startup smoke only: False
- max runtime seconds: 10800
- output root: `runs/lso_matched_support80_best6_seed0`

## Build Report

# IBL BrainSet Batch Build

Manifest: `manifests/ibl_bwm_region_matched_support80_best6.json`
Shard: 1/1
Selected recordings: 28
Available recordings: 28
Skipped existing: 28
Failures: 0
Elapsed seconds: 0
Include wheel: `False`
Trial-window-only spikes: `True`
Window length: `1.0`

## Available

| session | probe | path |
|---|---|---|
| b182b754-3c3e-4942-8144-6ee790926b58 | probe01 | `data/brainsets/ibl_bwm/b182b754-3c3e-4942-8144-6ee790926b58_probe01.h5` |
| 3f71aa98-08c6-4e79-b4c8-00eae4f03eff | probe00 | `data/brainsets/ibl_bwm/3f71aa98-08c6-4e79-b4c8-00eae4f03eff_probe00.h5` |
| 16693458-0801-4d35-a3f1-9115c7e5acfd | probe00 | `data/brainsets/ibl_bwm/16693458-0801-4d35-a3f1-9115c7e5acfd_probe00.h5` |
| 4ecb5d24-f5cc-402c-be28-9d0f7cb14b3a | probe00 | `data/brainsets/ibl_bwm/4ecb5d24-f5cc-402c-be28-9d0f7cb14b3a_probe00.h5` |
| 4d8c7767-981c-4347-8e5e-5d5fffe38534 | probe01 | `data/brainsets/ibl_bwm/4d8c7767-981c-4347-8e5e-5d5fffe38534_probe01.h5` |
| 63c70ae8-4dfb-418b-b21b-f0b1e5fba6c9 | probe00 | `data/brainsets/ibl_bwm/63c70ae8-4dfb-418b-b21b-f0b1e5fba6c9_probe00.h5` |
| 5adab0b7-dfd0-467d-b09d-43cb7ca5d59c | probe00 | `data/brainsets/ibl_bwm/5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe00.h5` |
| a8a8af78-16de-4841-ab07-fde4b5281a03 | probe00 | `data/brainsets/ibl_bwm/a8a8af78-16de-4841-ab07-fde4b5281a03_probe00.h5` |
| 6899a67d-2e53-4215-a52a-c7021b5da5d4 | probe00 | `data/brainsets/ibl_bwm/6899a67d-2e53-4215-a52a-c7021b5da5d4_probe00.h5` |
| e1931de1-cf7b-49af-af33-2ade15e8abe7 | probe00 | `data/brainsets/ibl_bwm/e1931de1-cf7b-49af-af33-2ade15e8abe7_probe00.h5` |
| 6fb1e12c-883b-46d1-a745-473cde3232c8 | probe00 | `data/brainsets/ibl_bwm/6fb1e12c-883b-46d1-a745-473cde3232c8_probe00.h5` |
| 1e45d992-c356-40e1-9be1-a506d944896f | probe01 | `data/brainsets/ibl_bwm/1e45d992-c356-40e1-9be1-a506d944896f_probe01.h5` |
| b887df2c-bb9c-44c9-a9c0-538da87b2cab | probe00 | `data/brainsets/ibl_bwm/b887df2c-bb9c-44c9-a9c0-538da87b2cab_probe00.h5` |
| 5adab0b7-dfd0-467d-b09d-43cb7ca5d59c | probe01 | `data/brainsets/ibl_bwm/5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe01.h5` |
| a8a8af78-16de-4841-ab07-fde4b5281a03 | probe01 | `data/brainsets/ibl_bwm/a8a8af78-16de-4841-ab07-fde4b5281a03_probe01.h5` |
| a1782f4f-86b0-480c-a7f2-3d8f1ab482ab | probe00 | `data/brainsets/ibl_bwm/a1782f4f-86b0-480c-a7f2-3d8f1ab482ab_probe00.h5` |
| b9c205c3-feac-485b-a89d-afc96d9cb280 | probe00 | `data/brainsets/ibl_bwm/b9c205c3-feac-485b-a89d-afc96d9cb280_probe00.h5` |
| 88d24c31-52e4-49cc-9f32-6adbeb9eba87 | probe00 | `data/brainsets/ibl_bwm/88d24c31-52e4-49cc-9f32-6adbeb9eba87_probe00.h5` |
| 03063955-2523-47bd-ae57-f7489dd40f15 | probe01 | `data/brainsets/ibl_bwm/03063955-2523-47bd-ae57-f7489dd40f15_probe01.h5` |
| 63c70ae8-4dfb-418b-b21b-f0b1e5fba6c9 | probe01 | `data/brainsets/ibl_bwm/63c70ae8-4dfb-418b-b21b-f0b1e5fba6c9_probe01.h5` |
| 49e0ab27-827a-4c91-bcaa-97eea27a1b8d | probe01 | `data/brainsets/ibl_bwm/49e0ab27-827a-4c91-bcaa-97eea27a1b8d_probe01.h5` |
| 032ffcdf-7692-40b3-b9ff-8def1fc18b2e | probe00 | `data/brainsets/ibl_bwm/032ffcdf-7692-40b3-b9ff-8def1fc18b2e_probe00.h5` |
| 35eeb752-8f4f-4040-9714-ba0f5b7ccdfe | probe00 | `data/brainsets/ibl_bwm/35eeb752-8f4f-4040-9714-ba0f5b7ccdfe_probe00.h5` |
| 16693458-0801-4d35-a3f1-9115c7e5acfd | probe01 | `data/brainsets/ibl_bwm/16693458-0801-4d35-a3f1-9115c7e5acfd_probe01.h5` |
| 6f09ba7e-e3ce-44b0-932b-c003fb44fb89 | probe01 | `data/brainsets/ibl_bwm/6f09ba7e-e3ce-44b0-932b-c003fb44fb89_probe01.h5` |
| 41872d7f-75cb-4445-bb1a-132b354c44f0 | probe01 | `data/brainsets/ibl_bwm/41872d7f-75cb-4445-bb1a-132b354c44f0_probe01.h5` |
| b887df2c-bb9c-44c9-a9c0-538da87b2cab | probe01 | `data/brainsets/ibl_bwm/b887df2c-bb9c-44c9-a9c0-538da87b2cab_probe01.h5` |
| edd22318-216c-44ff-bc24-49ce8be78374 | probe00 | `data/brainsets/ibl_bwm/edd22318-216c-44ff-bc24-49ce8be78374_probe00.h5` |

## Cache Audit

# BrainSet S3 Cache Audit

Manifest: `manifests/ibl_bwm_region_matched_support80_best6.json`
Cache: `s3://rppfvo6ifn/brainsets/ibl_bwm`
Present: 28/28 (100.0%)

## Missing

none

## Present

| filename |
|---|
| `03063955-2523-47bd-ae57-f7489dd40f15_probe01.h5` |
| `032ffcdf-7692-40b3-b9ff-8def1fc18b2e_probe00.h5` |
| `16693458-0801-4d35-a3f1-9115c7e5acfd_probe00.h5` |
| `16693458-0801-4d35-a3f1-9115c7e5acfd_probe01.h5` |
| `1e45d992-c356-40e1-9be1-a506d944896f_probe01.h5` |
| `35eeb752-8f4f-4040-9714-ba0f5b7ccdfe_probe00.h5` |
| `3f71aa98-08c6-4e79-b4c8-00eae4f03eff_probe00.h5` |
| `41872d7f-75cb-4445-bb1a-132b354c44f0_probe01.h5` |
| `49e0ab27-827a-4c91-bcaa-97eea27a1b8d_probe01.h5` |
| `4d8c7767-981c-4347-8e5e-5d5fffe38534_probe01.h5` |
| `4ecb5d24-f5cc-402c-be28-9d0f7cb14b3a_probe00.h5` |
| `5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe00.h5` |
| `5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe01.h5` |
| `63c70ae8-4dfb-418b-b21b-f0b1e5fba6c9_probe00.h5` |
| `63c70ae8-4dfb-418b-b21b-f0b1e5fba6c9_probe01.h5` |
| `6899a67d-2e53-4215-a52a-c7021b5da5d4_probe00.h5` |
| `6f09ba7e-e3ce-44b0-932b-c003fb44fb89_probe01.h5` |
| `6fb1e12c-883b-46d1-a745-473cde3232c8_probe00.h5` |
| `88d24c31-52e4-49cc-9f32-6adbeb9eba87_probe00.h5` |
| `a1782f4f-86b0-480c-a7f2-3d8f1ab482ab_probe00.h5` |
| `a8a8af78-16de-4841-ab07-fde4b5281a03_probe00.h5` |
| `a8a8af78-16de-4841-ab07-fde4b5281a03_probe01.h5` |
| `b182b754-3c3e-4942-8144-6ee790926b58_probe01.h5` |
| `b887df2c-bb9c-44c9-a9c0-538da87b2cab_probe00.h5` |
| `b887df2c-bb9c-44c9-a9c0-538da87b2cab_probe01.h5` |
| `b9c205c3-feac-485b-a89d-afc96d9cb280_probe00.h5` |
| `e1931de1-cf7b-49af-af33-2ade15e8abe7_probe00.h5` |
| `edd22318-216c-44ff-bc24-49ce8be78374_probe00.h5` |

## Partial LSO Summary

The cloud log contains a partial leave-subject-out sweep. It completed all
three planned arms for `CSH_ZAD_019`, `KS014`, and `MFD_06`, plus
`shared_baseline` and `pure_anatomy` for `NR_0019`. The run exited before
writing `runs/lso_matched_support80_best6_seed0/summary.md`, so this table was
recovered from `docs/cloud_phase3_5_runpod.log` with
`scripts/analyze_lso_log.py`.

### Per-Run Best AUC

| holdout | arm | seed | complete | best_AUC | step |
|---|---|---:|:---:|---:|---:|
| CSH_ZAD_019 | pure_anatomy | 0 | yes | 0.542 | 300 |
| CSH_ZAD_019 | region_only | 0 | yes | 0.569 | 150 |
| CSH_ZAD_019 | shared_baseline | 0 | yes | 0.541 | 300 |
| KS014 | pure_anatomy | 0 | yes | 0.555 | 300 |
| KS014 | region_only | 0 | yes | 0.576 | 300 |
| KS014 | shared_baseline | 0 | yes | 0.538 | 300 |
| MFD_06 | pure_anatomy | 0 | yes | 0.573 | 300 |
| MFD_06 | region_only | 0 | yes | 0.573 | 300 |
| MFD_06 | shared_baseline | 0 | yes | 0.506 | 300 |
| NR_0019 | pure_anatomy | 0 | yes | 0.524 | 150 |
| NR_0019 | shared_baseline | 0 | yes | 0.529 | 150 |

### Delta vs Shared Baseline

| holdout | arm | n_pairs | mean_delta | seed_deltas |
|---|---|---:|---:|---|
| CSH_ZAD_019 | pure_anatomy | 1 | +0.002 | +0.002 |
| CSH_ZAD_019 | region_only | 1 | +0.029 | +0.029 |
| KS014 | pure_anatomy | 1 | +0.017 | +0.017 |
| KS014 | region_only | 1 | +0.038 | +0.038 |
| MFD_06 | pure_anatomy | 1 | +0.067 | +0.067 |
| MFD_06 | region_only | 1 | +0.067 | +0.067 |
| NR_0019 | pure_anatomy | 1 | -0.005 | -0.005 |

### Aggregate Delta vs Shared Baseline

| arm | n_pairs | mean_delta | positive_pairs |
|---|---:|---:|---:|
| pure_anatomy | 4 | +0.020 | 3/4 |
| region_only | 3 | +0.045 | 3/3 |

Interpretation: this is not a demo-grade result yet because it is one seed and
partial. It is enough to prioritize the next spend: confirm `MFD_06` and
`KS014` with seeds 1-2 before broadening the sweep. `MFD_06` is the strongest
candidate because both `pure_anatomy` and `region_only` were +0.067 AUC over
the shared null on seed 0.
