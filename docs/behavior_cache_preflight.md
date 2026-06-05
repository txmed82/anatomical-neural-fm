# Behavior Cache Preflight

No-spend preflight for the next branch after cached trial targets failed.

- manifest recordings: `28`
- present files: `28`
- missing files: `0`
- required stream coverage: `wheel=14/28`
- recordings needing behavior rebuild: `14`
- decision: `behavior_cache_rebuild_required`

## Build Plan

The current compact cache was built for trial-window decoding. Rebuild without `--no-wheel` so `scripts/build_ibl_brainset.py` stores the `wheel` stream from Open Alyx.

```bash
uv run python scripts/build_ibl_brainset_batch.py --manifest manifests/ibl_bwm_region_matched_candidates_s3_present_support80_hdf5_scored.json --num-shards 4 --shard-index 0 --report docs/behavior_cache_build_shard00.md --trial-window-only --window-len 1.0 --rebuild-missing-stream wheel # writes data/brainsets/ibl_bwm
uv run python scripts/build_ibl_brainset_batch.py --manifest manifests/ibl_bwm_region_matched_candidates_s3_present_support80_hdf5_scored.json --num-shards 4 --shard-index 1 --report docs/behavior_cache_build_shard01.md --trial-window-only --window-len 1.0 --rebuild-missing-stream wheel # writes data/brainsets/ibl_bwm
uv run python scripts/build_ibl_brainset_batch.py --manifest manifests/ibl_bwm_region_matched_candidates_s3_present_support80_hdf5_scored.json --num-shards 4 --shard-index 2 --report docs/behavior_cache_build_shard02.md --trial-window-only --window-len 1.0 --rebuild-missing-stream wheel # writes data/brainsets/ibl_bwm
uv run python scripts/build_ibl_brainset_batch.py --manifest manifests/ibl_bwm_region_matched_candidates_s3_present_support80_hdf5_scored.json --num-shards 4 --shard-index 3 --report docs/behavior_cache_build_shard03.md --trial-window-only --window-len 1.0 --rebuild-missing-stream wheel # writes data/brainsets/ibl_bwm
```

## Target Gate After Rebuild

After building a behavior-inclusive cache, define the behavior target and rerun the local true-vs-shuffle, total-baseline, global target, and same-recording bidirectional gate before any GPU training.

Candidate behavior targets to test first:

- wheel movement onset versus quiescence in trial-aligned windows
- high versus low absolute wheel velocity after stimulus onset
- signed wheel velocity consistent with left/right action

## First Rows Needing Rebuild

| recording | missing streams |
|---|---|
| a8a8af78-16de-4841-ab07-fde4b5281a03_probe01 | wheel |
| a1782f4f-86b0-480c-a7f2-3d8f1ab482ab_probe00 | wheel |
| b9c205c3-feac-485b-a89d-afc96d9cb280_probe00 | wheel |
| 88d24c31-52e4-49cc-9f32-6adbeb9eba87_probe00 | wheel |
| 03063955-2523-47bd-ae57-f7489dd40f15_probe01 | wheel |
| 63c70ae8-4dfb-418b-b21b-f0b1e5fba6c9_probe01 | wheel |
| 49e0ab27-827a-4c91-bcaa-97eea27a1b8d_probe01 | wheel |
| 032ffcdf-7692-40b3-b9ff-8def1fc18b2e_probe00 | wheel |
| 35eeb752-8f4f-4040-9714-ba0f5b7ccdfe_probe00 | wheel |
| 16693458-0801-4d35-a3f1-9115c7e5acfd_probe01 | wheel |
| 6f09ba7e-e3ce-44b0-932b-c003fb44fb89_probe01 | wheel |
| 41872d7f-75cb-4445-bb1a-132b354c44f0_probe01 | wheel |
