"""Hand-rolled training smoke: AnatomicalPOYO regresses wheel velocity from 1-second
spike windows, across multiple IBL recordings.

Goal: prove the loss decreases over ~200 steps on MPS (M4) — confirming the full
pipeline (data → conditioning → model → optimizer) trains end-to-end. NOT a real
training run; tiny model, single-window batches.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "vendor" / "torch_brain"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import torch  # noqa: E402
import torch.nn.functional as F  # noqa: E402

from anatomical_poyo_smoke import (  # noqa: E402
    AnatomicalPOYO, PRIORS_PATH, TAXONOMY_PATH,
)
from torch_brain.dataset import Dataset, DatasetIndex  # noqa: E402
from torch_brain.registry import DataType, ModalitySpec  # noqa: E402
from torch_brain.utils import create_linspace_latent_tokens  # noqa: E402


WINDOW_LEN = 1.0       # seconds — short for fast iteration
LATENT_STEP = 0.125    # 8 latent steps per window
N_LATENTS = 16
VELOCITY_SCALE = 5.0   # rad/s — typical scale for wheel velocity, normalizes target
DEVICE = torch.device("mps") if torch.backends.mps.is_available() else torch.device("cpu")


def _build_vocabs_and_anatomy(ds: Dataset):
    """Collect global unit_ids / session_ids / region info across all recordings.

    Unit IDs are prefixed with recording_id for global uniqueness.
    """
    recs = {rid: ds.get_recording(rid) for rid in ds.recording_ids}
    all_unit_ids: list[str] = []
    all_region_acronyms: list[str] = []
    all_region_ids: list[int] = []
    for rid, rec in recs.items():
        prefix = f"{rid}/"
        unit_ids = [prefix + u for u in rec.units.id.astype(str).tolist()]
        all_unit_ids.extend(unit_ids)
        all_region_acronyms.extend(rec.units.region_acronym.astype(str).tolist())
        all_region_ids.extend(rec.units.region_id.astype(np.int64).tolist())

    unique_region_ids = np.unique(all_region_ids)
    region_id_to_idx = {int(r): i for i, r in enumerate(unique_region_ids)}
    region_idx_per_unit = np.array(
        [region_id_to_idx[r] for r in all_region_ids], dtype=np.int64
    )
    session_ids = list(recs.keys())
    return {
        "recs": recs,
        "all_unit_ids": all_unit_ids,
        "session_ids": session_ids,
        "region_idx_per_unit": region_idx_per_unit,
        "region_acronyms": np.array(all_region_acronyms),
        "n_regions": len(unique_region_ids),
    }


def _build_model(vocab, n_cell_types: int):
    spec = ModalitySpec(
        id=1, dim=1, type=DataType.CONTINUOUS,
        timestamp_key="wheel.timestamps", value_key="wheel.velocity",
        loss_fn=F.mse_loss,
    )
    model = AnatomicalPOYO(
        use_unit_emb=True,
        use_region_emb=True,
        use_cell_type_emb=True,
        n_regions=vocab["n_regions"],
        n_cell_types=n_cell_types,
        sequence_length=WINDOW_LEN,
        latent_step=LATENT_STEP,
        dim=64,
        depth=2,
        dim_head=32,
        num_latents_per_step=N_LATENTS,
        cross_heads=2,
        self_heads=4,
        ffn_dropout=0.1,
        lin_dropout=0.1,
        atn_dropout=0.0,
        readout_spec=spec,
    )
    return model


def _model_inputs(model, sample, rid, t0, sample_unit_ids, session_id_str):
    local_to_global = np.array(model.unit_emb.tokenizer(sample_unit_ids), dtype=np.int64)
    input_unit_index = local_to_global[sample.spikes.unit_index]
    input_timestamps = sample.spikes.timestamps.astype(np.float32) - t0
    input_token_type = np.zeros(len(input_timestamps), dtype=np.int64)
    latent_index, latent_timestamps = create_linspace_latent_tokens(
        start=0.0, end=WINDOW_LEN, step=LATENT_STEP, num_latents_per_step=N_LATENTS,
    )
    output_session_index = np.array(
        [model.session_emb.tokenizer([session_id_str])[0]], dtype=np.int64,
    )
    output_timestamps = np.array([WINDOW_LEN / 2], dtype=np.float32)

    def t(x, dtype):
        return torch.as_tensor(x, dtype=dtype).unsqueeze(0).to(DEVICE)

    return {
        "input_unit_index": t(input_unit_index, torch.long),
        "input_timestamps": t(input_timestamps, torch.float32),
        "input_token_type": t(input_token_type, torch.long),
        "latent_index": t(latent_index, torch.long),
        "latent_timestamps": t(latent_timestamps, torch.float32),
        "output_session_index": t(output_session_index, torch.long),
        "output_timestamps": t(output_timestamps, torch.float32),
    }


def main() -> int:
    print(f"Device: {DEVICE}")
    ds = Dataset(dataset_dir=REPO_ROOT / "data/brainsets/ibl_bwm", keep_files_open=True)
    print(f"Loaded {len(ds.recording_ids)} recordings")

    vocab = _build_vocabs_and_anatomy(ds)
    print(f"  units (global): {len(vocab['all_unit_ids'])}")
    print(f"  sessions:       {len(vocab['session_ids'])}")
    print(f"  unique regions: {vocab['n_regions']}")

    priors_df = pd.read_parquet(PRIORS_PATH)
    taxonomy = pd.read_parquet(TAXONOMY_PATH)["subclass"].tolist()
    n_cell_types = len(taxonomy)

    model = _build_model(vocab, n_cell_types)
    model.unit_emb.initialize_vocab(vocab["all_unit_ids"])
    model.session_emb.initialize_vocab(vocab["session_ids"])
    model.register_unit_anatomy(vocab["all_unit_ids"], vocab["region_idx_per_unit"])
    model.register_unit_cell_types(
        vocab["all_unit_ids"], vocab["region_acronyms"], priors_df, taxonomy,
    )
    n_params = sum(p.numel() for p in model.parameters())
    print(f"\nModel: {n_params:,} params  → moving to {DEVICE}")
    model = model.to(DEVICE)

    optimizer = torch.optim.AdamW(model.parameters(), lr=3e-4, weight_decay=1e-4)

    # ---- Training loop ----
    n_steps = 200
    rng = np.random.default_rng(0)
    losses: list[float] = []
    abs_targets: list[float] = []
    t_start = time.time()
    model.train()

    for step in range(n_steps):
        rid = vocab["session_ids"][rng.integers(len(vocab["session_ids"]))]
        rec = vocab["recs"][rid]
        domain_lo = float(rec.domain.start[0])
        domain_hi = float(rec.domain.end[-1])
        t0 = float(rng.uniform(domain_lo, domain_hi - WINDOW_LEN))
        t1 = t0 + WINDOW_LEN

        sample = ds[DatasetIndex(recording_id=rid, start=t0, end=t1)]
        wt = sample.wheel.timestamps
        wp = sample.wheel.position
        if len(wt) < 2 or (wt[-1] - wt[0]) < 0.05:
            continue
        velocity = float((wp[-1] - wp[0]) / (wt[-1] - wt[0])) / VELOCITY_SCALE
        target = torch.tensor([[velocity]], dtype=torch.float32, device=DEVICE)

        if len(sample.spikes.timestamps) == 0:
            continue
        prefix = f"{rid}/"
        sample_unit_ids = [prefix + u for u in sample.units.id.astype(str).tolist()]
        inputs = _model_inputs(model, sample, rid, t0, sample_unit_ids, rid)

        out = model(**inputs)  # (1, 1, 1)
        pred = out.squeeze(-1).squeeze(-1)
        loss = F.mse_loss(pred, target.squeeze(-1))

        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()

        losses.append(loss.item())
        abs_targets.append(abs(velocity))

        if (step + 1) % 20 == 0:
            recent = float(np.mean(losses[-20:]))
            recent_t = float(np.mean(abs_targets[-20:]))
            recent_pred = float(pred.detach().cpu().item())
            print(
                f"  step {step + 1:>4d}  loss={loss.item():.4f}  "
                f"recent_mean_loss={recent:.4f}  |target|≈{recent_t:.3f}  pred={recent_pred:+.3f}"
            )

    dt = time.time() - t_start
    if len(losses) >= 40:
        first = float(np.mean(losses[:20]))
        last = float(np.mean(losses[-20:])
)
        improvement = (first - last) / first * 100
        # Trivial baseline: predict zero (loss = mean(target^2))
        zero_baseline = float(np.mean(np.array(abs_targets) ** 2))
        print(f"\n=== Training smoke complete ({len(losses)} valid steps in {dt:.1f}s) ===")
        print(f"  loss[first 20] = {first:.4f}")
        print(f"  loss[last  20] = {last:.4f}    ({improvement:+.1f}%)")
        print(f"  predict-zero   = {zero_baseline:.4f}  (trivial baseline)")
        if last < first:
            print("\n✓ Loss decreased — training pipeline is wired correctly.")
            return 0
        else:
            print("\n✗ Loss did not decrease — investigate.")
            return 1
    return 1


if __name__ == "__main__":
    sys.exit(main())
