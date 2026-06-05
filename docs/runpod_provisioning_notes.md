# RunPod Provisioning Notes

Date: 2026-06-04

Goal: complete the matched-region BrainSet cache cheaply enough to continue
the cross-animal anatomical transfer benchmark.

## Current State

- Matched-region S3 cache remains at `4/48` recordings.
- Compact support80-best6 S3 cache is `3/28` recordings. Shard 0 contains
  7 recordings; 3 were already remote and 4 still need upload.
- Missing-only retry manifest:
  `manifests/ibl_bwm_region_matched_support80_best6_shard0_missing.json`.
- Local workstation is not viable for cache construction right now: only about
  `1.7 GiB` is free on `/System/Volumes/Data`, and shard02 failed locally with
  `No space left on device`.
- RunPod resources after cleanup:
  - pods: `0`
  - persistent cache volume: `rppfvo6ifn`, `US-IL-1`, `80 GB`

## What Was Tested

The launcher now:

- supports CPU pods via `--compute-type CPU`;
- forces `dockerEntrypoint: ["bash", "-lc"]` and passes the script as a single
  `dockerStartCmd`;
- supports `--startup-smoke-only`, which stops after dependency setup and first
  S3 log upload;
- supports `--max-provision-seconds`, which terminates a rented pod if it never
  becomes provisioned enough to expose a machine/public IP state.

Focused validation:

```bash
uv run pytest -q tests/test_runpod_clone_a100.py tests/test_sync_brainset_s3.py
```

Result after the compact-cache updates: `25 passed`.

Cheap CPU smoke test:

```bash
uv run python scripts/runpod_clone_a100.py --poll \
  --max-provision-seconds 120 \
  --compute-type CPU \
  --cpu-flavor 'cpu3c,cpu3g,cpu3m' \
  --datacenter ANY \
  --image-name python:3.11 \
  --container-disk-gb 20 \
  --volume-gb 20 \
  --max-runtime-seconds 300 \
  --skip-verification \
  --skip-cell-type-priors \
  --skip-sweep \
  --setup-mode minimal-data \
  --startup-smoke-only \
  --build-recordings 48 \
  --manifest-path manifests/ibl_bwm_region_matched_candidates.json \
  --max-steps 1 \
  --eval-batches 1 \
  --seeds '0' \
  --target-mode stimulus_side \
  --sweep-script scripts/run_matched_region_audit_a100.sh \
  --output-root runs/runpod_startup_smoke_cpu \
  --result-doc docs/runpod_startup_smoke.md \
  --name-prefix anfm-startup-smoke-cpu \
  --build-extra-args '--num-shards 24 --shard-index 2 --max-builds 1 --allow-partial' \
  --s3-bucket rppfvo6ifn \
  --s3-prefix brainsets/ibl_bwm \
  --s3-datacenter US-IL-1
```

Observed state:

- pod created at `$0.06/hr`;
- status stayed `desiredStatus: RUNNING`;
- `publicIp` stayed empty;
- `machineReady` became false while rented;
- no `logs/docs_runpod_startup_smoke.log` appeared in S3;
- local watchdog terminated the pod after `120s`;
- final RunPod state had `0` pods.

Interpretation: the container command is not starting. This is not a BrainSet
builder failure yet; it is a RunPod provisioning/startup failure before repo
clone or S3 logging.

## Compact Shard 0 Attempt

The compact target is now:

```bash
manifests/ibl_bwm_region_matched_support80_best6.json
```

It uses compact HDF5s (`--no-wheel --trial-window-only --window-len 1.0`) and
four contiguous shards. Shard 0 was launched on a cheap CPU pod with:

```bash
uv run python scripts/runpod_clone_a100.py \
  --compute-type CPU \
  --datacenter ANY \
  --setup-mode minimal-data \
  --container-disk-gb 20 \
  --manifest-path manifests/ibl_bwm_region_matched_support80_best6.json \
  --s3-bucket rppfvo6ifn \
  --s3-datacenter US-IL-1 \
  --skip-sweep \
  --skip-verification \
  --skip-cell-type-priors \
  --build-extra-args "--num-shards 4 --shard-index 0 --no-wheel --trial-window-only --window-len 1.0" \
  --output-root runs/compact_support80_best6_shard0 \
  --result-doc docs/compact_support80_best6_shard0_results.md \
  --name-prefix anfm-compact-shard0-final \
  --max-runtime-seconds 7200 \
  --max-provision-seconds 600 \
  --poll
```

Observed:

- first `US-IL-1` CPU create failed before renting because CPU container disk
  must be `<=20 GB`;
- `ANY` CPU created pods at `$0.06/hr`;
- RunPod's pod status API reported `machineReady=false` even while the
  container was actively building, so that flag is not reliable for CPU pods;
- the compact shard 0 builder reached the container and built `7/7` selected
  shard recordings in `459s` with `0` build failures;
- the pod was manually deleted during the upload phase, before the four new
  compact HDF5s reached S3;
- S3 logs confirm the build succeeded locally on the pod, but the post-run S3
  audit still reports `3/28`;
- a follow-up commit added `sync_brainset_s3.py upload --skip-existing`, so the
  next shard 0 retry will upload only newly built files instead of re-uploading
  the existing three remote cache files first;
- the final retry create request failed before renting due no available CPU
  instances.

Estimated compute spend from these CPU attempts was well under `$1`.

Do not kill a CPU build solely because `machineReady=false` if S3 logs are
updating; use logs/cache audit as the source of truth.

## Next Viable Paths

Latest CSH rerun attempts requested one `NVIDIA L4` with
`BEST_METRIC=full_eval_centered_auc`, `FULL_EVAL_ON_BEST=1`, and
`SAVE_DIAGNOSTICS=1`. RunPod repeatedly rented pods at `$0.39/hr` while the
status API exposed no public IP or usable machine details. The first centered
attempt was terminated by the old provisioning guard despite partial S3/Git
artifacts. After `scripts/runpod_clone_a100.py` was hardened to preserve pods
with active S3 logs, the second centered attempt
(`anfm-csh-centered-l4-20260604-205209`, pod `jt36y9tajx4p5u`) reached the body
completion marker and self-cleanup path. Final preflight reported
`active_pods: 0`.

The matched compact cache is complete for
`manifests/ibl_bwm_region_matched_support80_best6.json`; the later cloud audit
reported `Present: 28/28`. The completed CSH centered-selection rerun is
suggestive but below the demo gate: `n_passing_seeds=1/3`, with paired
true-vs-shuffle improvements `0.513`, `0.486`, and `0.552` against the `0.550`
threshold.

1. Retry the CSH centered-selection L4 command only after a clean
   `active_pods: 0` preflight. Keep `--max-provision-seconds 300`, one pod at a
   time, and `BEST_METRIC=full_eval_centered_auc`. Because the status API was
   misleading on this attempt, use S3 log progress as the source of truth before
   terminating a rented pod that has started uploading logs; the launcher now
   preserves such pods until a completion marker or the runtime guard fires.
2. If RunPod continues renting without usable runtime details, move the same
   pushed-branch command to another provider with a hard runtime cap and enough
   disk for the cached HDF5 download.
3. Make GHCR private-image pull work, or publish a reliable public image, then
   repeat a startup smoke before another paid training attempt. The temporary
   `ttl.sh` image did not produce logs on earlier GPU attempts.

Resume model training only with the complete compact cache, the matched-region
manifest, and the executable CSH gate ready to run on the resulting artifacts.
