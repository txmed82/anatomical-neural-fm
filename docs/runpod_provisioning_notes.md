# RunPod Provisioning Notes

Date: 2026-06-04

Goal: complete the matched-region BrainSet cache cheaply enough to continue
the cross-animal anatomical transfer benchmark.

## Current State

- Matched-region S3 cache remains at `4/48` recordings.
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

Result: `22 passed`.

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

## Next Viable Paths

1. Use a different RunPod mode or region/GPU class only after confirming it
   transitions to a provisioned machine with a smoke log. Keep
   `--startup-smoke-only` and `--max-provision-seconds` enabled first.
2. Make GHCR private-image pull work, or publish a reliable public image, then
   repeat the startup smoke. The temporary `ttl.sh` image was pushed but did not
   produce logs on earlier GPU attempts.
3. Free at least `20-30 GiB` locally, then build data shards locally and upload
   to `rppfvo6ifn`. The current local disk pressure makes this unsafe.
4. If RunPod continues renting without provisioning, use another provider with
   enough ephemeral disk for CPU data builds. GPU is not required for cache
   construction.

Do not resume model training until the cache is substantially complete and
`scripts/plan_matched_region_manifest.py` passes the held-out support gate.
