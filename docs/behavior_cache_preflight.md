# Behavior Cache Preflight

No-spend preflight for the next branch after cached trial targets failed.

- manifest recordings: `28`
- present files: `28`
- missing files: `0`
- required stream coverage: `wheel=21/28`
- recordings needing behavior rebuild: `7`
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
| 032ffcdf-7692-40b3-b9ff-8def1fc18b2e_probe00 | wheel |
| 35eeb752-8f4f-4040-9714-ba0f5b7ccdfe_probe00 | wheel |
| 16693458-0801-4d35-a3f1-9115c7e5acfd_probe01 | wheel |
| 6f09ba7e-e3ce-44b0-932b-c003fb44fb89_probe01 | wheel |
| 41872d7f-75cb-4445-bb1a-132b354c44f0_probe01 | wheel |
| b887df2c-bb9c-44c9-a9c0-538da87b2cab_probe01 | wheel |
| edd22318-216c-44ff-bc24-49ce8be78374_probe00 | wheel |
