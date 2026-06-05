# Anatomical Neural Foundation Model

This project tests whether anatomical priors improve neural foundation-model
generalization across IBL Brain-Wide Map recordings.

The current local goal is phase 1-2:

1. Make the existing IBL + Allen Brain Cell Atlas pipeline reproducible on Apple
   Silicon.
2. Fix the core evaluation design before moving GPU sweeps to RunPod.

## Scientific Hypothesis

The primary cross-animal hypothesis is:

> Unit tokens based on anatomy, cell-type priors, or waveform features transfer
> better to held-out animals than arbitrary per-recording unit IDs.

For cross-animal claims, the primary arms are:

- `pure_anatomy`: region embedding + Allen cell-type prior projection, no unit-id embedding
- `waveform_only`: waveform-feature projection, no unit-id embedding

Arms that include `use_unit_emb=True` are still useful diagnostics, but they are
not the cleanest held-out-animal test because held-out units have untrained
identity embeddings.

## Setup

```bash
uv sync --dev
```

This repo uses the PyPI `torch-brain` package. The scripts also add
`vendor/torch_brain` to `sys.path` if present, so a local source checkout can
override the package during development, but it is not required for phase 1-2.

Verify imports with:

```bash
uv run python - <<'PY'
import torch_brain
print("torch_brain import ok")
PY
```

## Build Local Data

Smoke-test public IBL access:

```bash
uv run python scripts/00_ibl_smoke_test.py
```

Build Allen Brain Cell Atlas region-level cell-type priors:

```bash
uv run python scripts/build_cell_type_priors.py
```

Build a small IBL Brain-Wide Map dataset:

```bash
uv run python scripts/build_ibl_brainset_batch.py 3
```

Write a committed-safe manifest for the ignored local HDF5s:

```bash
uv run python scripts/write_dataset_manifest.py
```

The raw/processed data and the local manifest output are ignored. Commit only
curated example manifests or fixed split specs.

## Local Verification

Run tests that do not require downloaded data:

```bash
uv run pytest -q
```

Run syntax checks:

```bash
uv run python -m py_compile scripts/*.py
```

After data and `torch_brain` are present:

```bash
uv run python scripts/poyo_forward_smoke.py
uv run python scripts/anatomical_poyo_smoke.py
uv run python scripts/train_smoke.py
```

## Phase 2 Local Sweeps

The local Apple Silicon launcher is:

```bash
bash scripts/run_phase2_local.sh
```

It runs short MPS sweeps with:

- shared output query mode
- within-animal sanity checks
- cross-animal primary arms
- small step counts suitable for local iteration

The production RunPod pilot should use the same arm/query design with larger
data, more seeds, and longer training.

The latest local tiny-pilot result is tracked in
`docs/local_phase2_results.md`.

## Evaluation Design

`scripts/train.py` defaults to:

```bash
--output-query-mode shared
```

This uses one trainable task query, `choice_readout`, for every recording. That
is the primary cross-animal setting because held-out recordings no longer rely
on an untrained held-out session query embedding.

Use:

```bash
--output-query-mode session
```

only for diagnostics that intentionally preserve the original per-recording
query behavior.

## Next RunPod Step

Once local phase 1-2 passes, the cloud version needs:

```env
RUNPOD_API_KEY=
RUNPOD_S3_ACCESS_KEY=
RUNPOD_S3_SECRET_KEY=
```

The first GPU milestone should reproduce the local phase-2 sweep on a fixed IBL
manifest, then scale seeds and sessions.
