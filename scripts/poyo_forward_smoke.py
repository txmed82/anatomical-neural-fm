"""Smoke test: instantiate a tiny POYO, init vocabs from our IBL HDF5, run one forward pass.

We bypass POYO.tokenize() since it requires a readout target we don't have yet;
instead we construct the model_inputs dict by hand from a 1-second sample.

This verifies:
  - torch_brain.dataset.Dataset loads our HDF5
  - InfiniteVocabEmbedding can be initialized from our units.id / session.id
  - POYO.forward runs on our spike data with the right tensor shapes
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "vendor" / "torch_brain"))

import numpy as np  # noqa: E402
import torch  # noqa: E402

from torch_brain.dataset import Dataset, DatasetIndex  # noqa: E402
from torch_brain.models.poyo import POYO  # noqa: E402
from torch_brain.registry import DataType, ModalitySpec  # noqa: E402
from torch_brain.utils import create_linspace_latent_tokens  # noqa: E402


def main() -> int:
    # --- Load our HDF5 ---
    ds_dir = REPO_ROOT / "data" / "brainsets" / "ibl_bwm"
    ds = Dataset(dataset_dir=ds_dir, keep_files_open=True)
    rid = ds.recording_ids[0]
    rec = ds.get_recording(rid)
    unit_ids = rec.units.id.astype(str).tolist()
    session_id = str(rec.session.id)
    print(f"Loaded {len(unit_ids)} units from {session_id}")

    # --- Build a tiny POYO ---
    # Dummy readout spec (we won't compute loss; only need it for __init__)
    spec = ModalitySpec(
        id=1,
        dim=2,
        type=DataType.CONTINUOUS,
        timestamp_key="dummy.timestamps",
        value_key="dummy.values",
        loss_fn=torch.nn.functional.mse_loss,
    )
    model = POYO(
        sequence_length=1.0,
        latent_step=0.125,
        dim=32,
        depth=1,
        dim_head=16,
        num_latents_per_step=8,
        cross_heads=2,
        self_heads=4,
        readout_spec=spec,
        ffn_dropout=0.0,
        lin_dropout=0.0,
        atn_dropout=0.0,
    )
    # --- Initialize embedding vocabs (must happen before counting params; emb is lazy) ---
    model.unit_emb.initialize_vocab(unit_ids)
    model.session_emb.initialize_vocab([session_id])
    n_params = sum(p.numel() for p in model.parameters())
    print(f"Built POYO with {n_params:,} parameters")

    # --- Slice a 1-second sample ---
    t0, t1 = 100.0, 101.0
    sample = ds[DatasetIndex(recording_id=rid, start=t0, end=t1)]
    sample_unit_ids = sample.units.id.astype(str).tolist()
    print(f"\nSliced sample: {len(sample.spikes.timestamps)} spikes")

    # --- Construct model_inputs by hand ---
    # Map local cluster index → global vocab index
    local_to_global = np.array(model.unit_emb.tokenizer(sample_unit_ids), dtype=np.int64)
    input_unit_index = local_to_global[sample.spikes.unit_index]

    # All spikes are token_type=0 (skip start/end markers for this smoke test)
    input_timestamps = sample.spikes.timestamps.astype(np.float32) - t0  # 0..1s
    input_token_type = np.zeros(len(input_timestamps), dtype=np.int64)

    # Latents on a fixed grid
    latent_index, latent_timestamps = create_linspace_latent_tokens(
        start=0.0, end=1.0, step=0.125, num_latents_per_step=8,
    )

    # A few output queries at evenly spaced times in the window
    n_query = 4
    output_session_index = np.full(
        n_query, model.session_emb.tokenizer([session_id])[0], dtype=np.int64,
    )
    output_timestamps = np.linspace(0.1, 0.9, n_query, dtype=np.float32)

    # Batch dim
    def t(x, dtype):
        return torch.as_tensor(x, dtype=dtype).unsqueeze(0)

    inputs = {
        "input_unit_index": t(input_unit_index, torch.long),
        "input_timestamps": t(input_timestamps, torch.float32),
        "input_token_type": t(input_token_type, torch.long),
        "latent_index": t(latent_index, torch.long),
        "latent_timestamps": t(latent_timestamps, torch.float32),
        "output_session_index": t(output_session_index, torch.long),
        "output_timestamps": t(output_timestamps, torch.float32),
    }
    print(f"\nInput shapes:")
    for k, v in inputs.items():
        print(f"  {k}: {tuple(v.shape)} {v.dtype}")

    # --- Forward pass ---
    print("\nRunning forward pass...")
    model.eval()
    with torch.no_grad():
        out = model(**inputs)
    print(f"Output shape: {tuple(out.shape)} {out.dtype}")
    print(f"Output stats: mean={out.mean().item():.4f}  std={out.std().item():.4f}")

    # --- Backward smoke (one step of grad) ---
    print("\nRunning a single grad step to verify backprop...")
    model.train()
    out = model(**inputs)
    fake_target = torch.zeros_like(out)
    loss = torch.nn.functional.mse_loss(out, fake_target)
    loss.backward()
    grad_norms = sum(p.grad.norm().item() for p in model.parameters() if p.grad is not None)
    print(f"  loss = {loss.item():.4f}")
    print(f"  sum of grad norms = {grad_norms:.4f}")

    print("\nAll checks passed — end-to-end IBL HDF5 → POYO forward + backward works.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
