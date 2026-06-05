# Compact Matched Cache Next Run

Goal: build the smallest practical BrainSet cache for the current cross-animal
anatomical-transfer target before spending on another training sweep.

Use this manifest, not the original 48-recording candidate set:

```bash
manifests/ibl_bwm_region_matched_support80_best6.json
```

It covers 28 recordings across 7 subjects/labs. Metadata-only region scoring
shows 6/7 subjects pass the 80% held-out unit-support gate after subset
optimization, which makes it a better first cache target than the full
candidate set.

## Compact Build Mode

First audit the S3 cache and write a shard plan:

```bash
python scripts/sync_brainset_s3.py audit \
  --manifest manifests/ibl_bwm_region_matched_support80_best6.json \
  --datacenter US-IL-1 \
  --report docs/compact_support80_best6_s3_audit.md \
  --num-shards 4 \
  --compact-build-args "--no-wheel --trial-window-only --window-len 1.0"
```

For the choice/stimulus training scripts, the HDF5 cache does not need wheel
samples, and it does not need spikes outside trial-aligned windows. Build with:

```bash
python scripts/build_ibl_brainset_batch.py \
  --manifest manifests/ibl_bwm_region_matched_support80_best6.json \
  --no-wheel \
  --trial-window-only \
  --window-len 1.0 \
  --report runs/matched_support80_best6_compact_build_report.md
```

For sharded builds:

```bash
python scripts/build_ibl_brainset_batch.py \
  --manifest manifests/ibl_bwm_region_matched_support80_best6.json \
  --num-shards 4 \
  --shard-index 0 \
  --no-wheel \
  --trial-window-only \
  --window-len 1.0 \
  --report runs/matched_support80_best6_compact_build_shard0.md
```

Run `--shard-index 0..3` for the four shards.

For the current shard-0 retry, use the missing-only manifest instead of the
full 7-recording shard:

```bash
manifests/ibl_bwm_region_matched_support80_best6_shard0_missing.json
```

It contains only the four shard-0 HDF5s that are absent from S3.

## RunPod Guardrails

Stay under the active $100 cap. Prefer a cheap CPU or low-end GPU data-build
pod first, because this step is IO/download-heavy rather than model-training
heavy. Do not start A100 training until the compact cache is verified.

The RunPod clone launcher can pass the same compact flags through:

```bash
python scripts/runpod_clone_a100.py \
  --compute-type CPU \
  --datacenter ANY \
  --setup-mode minimal-data \
  --container-disk-gb 20 \
  --manifest-path manifests/ibl_bwm_region_matched_support80_best6_shard0_missing.json \
  --s3-bucket rppfvo6ifn \
  --s3-datacenter US-IL-1 \
  --skip-sweep \
  --skip-verification \
  --skip-cell-type-priors \
  --build-extra-args "--no-wheel --trial-window-only --window-len 1.0" \
  --result-doc docs/compact_support80_best6_shard0_results.md \
  --max-provision-seconds 600 \
  --poll
```

Before and after every cloud attempt, verify `/pods` is zero or only contains
the intended active pod. If provisioning stalls before the command starts, stop
the pod and do not retry the same shape repeatedly.

For CPU pods, RunPod may report `machineReady=false` while the container is
actually running. Check S3 logs before killing a pod for that reason.

## Verification Gate

After the compact HDF5s exist, run:

```bash
python scripts/plan_matched_region_manifest.py \
  --input-manifest manifests/ibl_bwm_region_matched_support80_best6.json \
  --data-dir data/brainsets/ibl_bwm \
  --out-manifest manifests/ibl_bwm_region_matched_support80_best6_local_scored.json \
  --out-report docs/matched_region_support80_best6_local_cache.md
```

Then run the first training sweep only if the local-HDF5 scoring still shows
most subjects near or above the 80% support gate and the cache audit reports all
28 expected HDF5 files.
