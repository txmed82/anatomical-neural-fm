# BrainSet S3 Cache Audit

Manifest: `manifests/ibl_bwm_region_matched_candidates.json`
Cache: `s3://rppfvo6ifn/brainsets/ibl_bwm`
Present: 29/48 (60.4%)

## Missing

| filename |
|---|
| `034e726f-b35f-41e0-8d6c-a22cc32391fb_probe01.h5` |
| `09156021-9a1d-4e1d-ae59-48cbde3c5d42_probe00.h5` |
| `09b2c4d1-058d-4c84-9fd4-97530f85baf6_probe00.h5` |
| `30e5937e-e86a-47e6-93ae-d2ae3877ff8e_probe00.h5` |
| `4ddb8a95-788b-48d0-8a0a-66c7c796da96_probe00.h5` |
| `4ddb8a95-788b-48d0-8a0a-66c7c796da96_probe01.h5` |
| `5d6aa933-4b00-4e99-ae2d-5003657592e9_probe01.h5` |
| `63f3dbc1-1a5f-44e5-98dd-ce25cd2b7871_probe00.h5` |
| `64977c74-9c04-437a-9ea1-50386c4996db_probe00.h5` |
| `65f5c9b4-4440-48b9-b914-c593a5184a18_probe00.h5` |
| `6668c4a0-70a4-4012-a7da-709660971d7a_probe00.h5` |
| `90e524a2-aa63-47ce-b5b8-1b1941a1223a_probe00.h5` |
| `9a6e127b-bb07-4be2-92e2-53dd858c2762_probe00.h5` |
| `a19c7a3a-7261-42ce-95d5-1f4ca46007ed_probe00.h5` |
| `de588204-8fd6-4ce3-92da-7a6d1dcae238_probe00.h5` |
| `dfd8e7df-dc51-4589-b6ca-7baccfeb94b4_probe01.h5` |
| `e5c772cd-9c92-47ab-9525-d618b66a9b5d_probe00.h5` |
| `f8041c1e-5ef4-4ae6-afec-ed82d7a74dc1_probe01.h5` |
| `fa704052-147e-46f6-b190-a65b837e605e_probe00.h5` |

## Shard Build Plan

Shards: 24

| shard | recordings | present | missing | build command |
|---:|---:|---:|---:|---|
| 0 | 2 | 2 | 0 | `python scripts/build_ibl_brainset_batch.py --manifest manifests/ibl_bwm_region_matched_candidates.json --num-shards 24 --shard-index 0 --max-builds 2 --allow-partial` |
| 1 | 2 | 2 | 0 | `python scripts/build_ibl_brainset_batch.py --manifest manifests/ibl_bwm_region_matched_candidates.json --num-shards 24 --shard-index 1 --max-builds 2 --allow-partial` |
| 2 | 2 | 0 | 2 | `python scripts/build_ibl_brainset_batch.py --manifest manifests/ibl_bwm_region_matched_candidates.json --num-shards 24 --shard-index 2 --max-builds 2 --allow-partial` |
| 3 | 2 | 1 | 1 | `python scripts/build_ibl_brainset_batch.py --manifest manifests/ibl_bwm_region_matched_candidates.json --num-shards 24 --shard-index 3 --max-builds 2 --allow-partial` |
| 4 | 2 | 2 | 0 | `python scripts/build_ibl_brainset_batch.py --manifest manifests/ibl_bwm_region_matched_candidates.json --num-shards 24 --shard-index 4 --max-builds 2 --allow-partial` |
| 5 | 2 | 1 | 1 | `python scripts/build_ibl_brainset_batch.py --manifest manifests/ibl_bwm_region_matched_candidates.json --num-shards 24 --shard-index 5 --max-builds 2 --allow-partial` |
| 6 | 2 | 1 | 1 | `python scripts/build_ibl_brainset_batch.py --manifest manifests/ibl_bwm_region_matched_candidates.json --num-shards 24 --shard-index 6 --max-builds 2 --allow-partial` |
| 7 | 2 | 2 | 0 | `python scripts/build_ibl_brainset_batch.py --manifest manifests/ibl_bwm_region_matched_candidates.json --num-shards 24 --shard-index 7 --max-builds 2 --allow-partial` |
| 8 | 2 | 0 | 2 | `python scripts/build_ibl_brainset_batch.py --manifest manifests/ibl_bwm_region_matched_candidates.json --num-shards 24 --shard-index 8 --max-builds 2 --allow-partial` |
| 9 | 2 | 1 | 1 | `python scripts/build_ibl_brainset_batch.py --manifest manifests/ibl_bwm_region_matched_candidates.json --num-shards 24 --shard-index 9 --max-builds 2 --allow-partial` |
| 10 | 2 | 2 | 0 | `python scripts/build_ibl_brainset_batch.py --manifest manifests/ibl_bwm_region_matched_candidates.json --num-shards 24 --shard-index 10 --max-builds 2 --allow-partial` |
| 11 | 2 | 1 | 1 | `python scripts/build_ibl_brainset_batch.py --manifest manifests/ibl_bwm_region_matched_candidates.json --num-shards 24 --shard-index 11 --max-builds 2 --allow-partial` |
| 12 | 2 | 1 | 1 | `python scripts/build_ibl_brainset_batch.py --manifest manifests/ibl_bwm_region_matched_candidates.json --num-shards 24 --shard-index 12 --max-builds 2 --allow-partial` |
| 13 | 2 | 2 | 0 | `python scripts/build_ibl_brainset_batch.py --manifest manifests/ibl_bwm_region_matched_candidates.json --num-shards 24 --shard-index 13 --max-builds 2 --allow-partial` |
| 14 | 2 | 0 | 2 | `python scripts/build_ibl_brainset_batch.py --manifest manifests/ibl_bwm_region_matched_candidates.json --num-shards 24 --shard-index 14 --max-builds 2 --allow-partial` |
| 15 | 2 | 1 | 1 | `python scripts/build_ibl_brainset_batch.py --manifest manifests/ibl_bwm_region_matched_candidates.json --num-shards 24 --shard-index 15 --max-builds 2 --allow-partial` |
| 16 | 2 | 2 | 0 | `python scripts/build_ibl_brainset_batch.py --manifest manifests/ibl_bwm_region_matched_candidates.json --num-shards 24 --shard-index 16 --max-builds 2 --allow-partial` |
| 17 | 2 | 1 | 1 | `python scripts/build_ibl_brainset_batch.py --manifest manifests/ibl_bwm_region_matched_candidates.json --num-shards 24 --shard-index 17 --max-builds 2 --allow-partial` |
| 18 | 2 | 1 | 1 | `python scripts/build_ibl_brainset_batch.py --manifest manifests/ibl_bwm_region_matched_candidates.json --num-shards 24 --shard-index 18 --max-builds 2 --allow-partial` |
| 19 | 2 | 2 | 0 | `python scripts/build_ibl_brainset_batch.py --manifest manifests/ibl_bwm_region_matched_candidates.json --num-shards 24 --shard-index 19 --max-builds 2 --allow-partial` |
| 20 | 2 | 0 | 2 | `python scripts/build_ibl_brainset_batch.py --manifest manifests/ibl_bwm_region_matched_candidates.json --num-shards 24 --shard-index 20 --max-builds 2 --allow-partial` |
| 21 | 2 | 1 | 1 | `python scripts/build_ibl_brainset_batch.py --manifest manifests/ibl_bwm_region_matched_candidates.json --num-shards 24 --shard-index 21 --max-builds 2 --allow-partial` |
| 22 | 2 | 2 | 0 | `python scripts/build_ibl_brainset_batch.py --manifest manifests/ibl_bwm_region_matched_candidates.json --num-shards 24 --shard-index 22 --max-builds 2 --allow-partial` |
| 23 | 2 | 1 | 1 | `python scripts/build_ibl_brainset_batch.py --manifest manifests/ibl_bwm_region_matched_candidates.json --num-shards 24 --shard-index 23 --max-builds 2 --allow-partial` |

### Missing By Shard

#### Shard 0

none

#### Shard 1

none

#### Shard 2

| filename |
|---|
| `e5c772cd-9c92-47ab-9525-d618b66a9b5d_probe00.h5` |
| `9a6e127b-bb07-4be2-92e2-53dd858c2762_probe00.h5` |

#### Shard 3

| filename |
|---|
| `de588204-8fd6-4ce3-92da-7a6d1dcae238_probe00.h5` |

#### Shard 4

none

#### Shard 5

| filename |
|---|
| `65f5c9b4-4440-48b9-b914-c593a5184a18_probe00.h5` |

#### Shard 6

| filename |
|---|
| `dfd8e7df-dc51-4589-b6ca-7baccfeb94b4_probe01.h5` |

#### Shard 7

none

#### Shard 8

| filename |
|---|
| `a19c7a3a-7261-42ce-95d5-1f4ca46007ed_probe00.h5` |
| `09156021-9a1d-4e1d-ae59-48cbde3c5d42_probe00.h5` |

#### Shard 9

| filename |
|---|
| `5d6aa933-4b00-4e99-ae2d-5003657592e9_probe01.h5` |

#### Shard 10

none

#### Shard 11

| filename |
|---|
| `4ddb8a95-788b-48d0-8a0a-66c7c796da96_probe01.h5` |

#### Shard 12

| filename |
|---|
| `fa704052-147e-46f6-b190-a65b837e605e_probe00.h5` |

#### Shard 13

none

#### Shard 14

| filename |
|---|
| `6668c4a0-70a4-4012-a7da-709660971d7a_probe00.h5` |
| `64977c74-9c04-437a-9ea1-50386c4996db_probe00.h5` |

#### Shard 15

| filename |
|---|
| `63f3dbc1-1a5f-44e5-98dd-ce25cd2b7871_probe00.h5` |

#### Shard 16

none

#### Shard 17

| filename |
|---|
| `4ddb8a95-788b-48d0-8a0a-66c7c796da96_probe00.h5` |

#### Shard 18

| filename |
|---|
| `034e726f-b35f-41e0-8d6c-a22cc32391fb_probe01.h5` |

#### Shard 19

none

#### Shard 20

| filename |
|---|
| `30e5937e-e86a-47e6-93ae-d2ae3877ff8e_probe00.h5` |
| `90e524a2-aa63-47ce-b5b8-1b1941a1223a_probe00.h5` |

#### Shard 21

| filename |
|---|
| `09b2c4d1-058d-4c84-9fd4-97530f85baf6_probe00.h5` |

#### Shard 22

none

#### Shard 23

| filename |
|---|
| `f8041c1e-5ef4-4ae6-afec-ed82d7a74dc1_probe01.h5` |


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
| `7939711b-8b4d-4251-b698-b97c1eaa846e_probe01.h5` |
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
