# Behavior Cache Preflight

No-spend preflight for the next branch after cached trial targets failed.

- manifest recordings: `28`
- present files: `28`
- missing files: `0`
- required stream coverage: `wheel=28/28`
- recordings needing behavior rebuild: `0`
- decision: `behavior_cache_ready`

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
