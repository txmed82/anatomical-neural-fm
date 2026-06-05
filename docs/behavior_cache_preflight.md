# Behavior Cache Preflight

No-spend preflight for the next branch after cached trial targets failed.

- manifest recordings: `28`
- present files: `28`
- missing files: `0`
- required stream coverage: `wheel=3/28`
- recordings needing behavior rebuild: `25`
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
| 4ecb5d24-f5cc-402c-be28-9d0f7cb14b3a_probe00 | wheel |
| 4d8c7767-981c-4347-8e5e-5d5fffe38534_probe01 | wheel |
| 63c70ae8-4dfb-418b-b21b-f0b1e5fba6c9_probe00 | wheel |
| 5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe00 | wheel |
| a8a8af78-16de-4841-ab07-fde4b5281a03_probe00 | wheel |
| 6899a67d-2e53-4215-a52a-c7021b5da5d4_probe00 | wheel |
| e1931de1-cf7b-49af-af33-2ade15e8abe7_probe00 | wheel |
| 6fb1e12c-883b-46d1-a745-473cde3232c8_probe00 | wheel |
| 1e45d992-c356-40e1-9be1-a506d944896f_probe01 | wheel |
| b887df2c-bb9c-44c9-a9c0-538da87b2cab_probe00 | wheel |
| 5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe01 | wheel |
| a8a8af78-16de-4841-ab07-fde4b5281a03_probe01 | wheel |
