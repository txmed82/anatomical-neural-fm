# RunPod Data-Build Image

The matched-region cache build does not need model training dependencies. The
cheap RunPod data-only attempts stalled before the first cache log because each
fresh pod had to install the Python stack before doing any IBL work.

Use `docker/runpod-data-build.Dockerfile` to preinstall only the packages needed
for public IBL HDF5 construction and S3 cache sync:

```bash
docker build -f docker/runpod-data-build.Dockerfile \
  -t <registry>/anatomical-neural-fm-data-build:py311 .

docker push <registry>/anatomical-neural-fm-data-build:py311
```

Then launch the shard with the prebuilt image and minimal setup:

```bash
uv run python scripts/runpod_clone_a100.py --poll \
  --datacenter ANY \
  --gpu-type 'NVIDIA L4,NVIDIA RTX 4000 Ada Generation,NVIDIA RTX A4000,NVIDIA RTX A4500,NVIDIA RTX A5000,NVIDIA RTX A6000,NVIDIA GeForce RTX 4090' \
  --image-name <registry>/anatomical-neural-fm-data-build:py311 \
  --container-disk-gb 80 \
  --max-runtime-seconds 1800 \
  --skip-verification \
  --skip-cell-type-priors \
  --skip-sweep \
  --setup-mode minimal-data \
  --build-recordings 48 \
  --manifest-path manifests/ibl_bwm_region_matched_candidates.json \
  --max-steps 1 \
  --eval-batches 1 \
  --seeds '0' \
  --target-mode stimulus_side \
  --sweep-script scripts/run_matched_region_audit_a100.sh \
  --output-root runs/matched_region_shard02_probe_a100 \
  --result-doc docs/matched_region_shard02_probe.md \
  --name-prefix anfm-data-matched-region-shard02 \
  --build-extra-args '--num-shards 24 --shard-index 2 --max-builds 2 --allow-partial' \
  --s3-bucket "$BRAINSET_S3_BUCKET" \
  --s3-prefix brainsets/ibl_bwm \
  --s3-datacenter US-IL-1
```

Do not launch training until the cache audit reaches `Present: 48/48` and
`scripts/plan_matched_region_manifest.py` passes the held-out region support
gate.
