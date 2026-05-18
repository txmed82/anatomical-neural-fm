"""Real training script: AnatomicalPOYO for IBL choice decoding (L/R) with held-out-animal eval.

Sampling is trial-aligned: each training window is [stimOn_time, stimOn_time + window_len]
from a real IBL trial; target is sign(trials.choice). Nogo trials (choice=0) skipped.
Loss is BCE-with-logits; eval reports accuracy + AUC + loss.

Run on M4:
    uv run python scripts/train.py --device mps --batch-size 4 --dim 64 --depth 2 --max-steps 500

Run on A100:
    python scripts/train.py --device cuda --batch-size 16 --dim 128 --depth 4 --max-steps 10000

Outputs to --out-dir: best.ckpt, last.ckpt, log.jsonl (one JSON per training/eval line).
"""
from __future__ import annotations

import argparse
import json
import math
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


# --------------------------------------------------------------------- config

# Choice decoding: one binary target per trial-aligned window.
N_OUTPUT_QUERIES = 1     # single binary logit at trial-end


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--data-dir", type=Path, default=REPO_ROOT / "data/brainsets/ibl_bwm")
    p.add_argument("--priors-path", type=Path, default=PRIORS_PATH)
    p.add_argument("--taxonomy-path", type=Path, default=TAXONOMY_PATH)
    p.add_argument("--out-dir", type=Path, default=REPO_ROOT / "runs/baseline")
    p.add_argument("--device", default="auto", choices=["auto", "mps", "cuda", "cpu"])
    p.add_argument("--seed", type=int, default=0)
    # Split strategy
    p.add_argument("--split-mode", default="animal", choices=["animal", "trial"],
                   help="'animal' = hold out whole subjects (cross-animal eval). "
                        "'trial' = split trials within each subject (within-animal sanity check).")
    p.add_argument("--split-seed", type=int, default=42,
                   help="Seed for the trial-level split (kept constant across training seeds).")
    p.add_argument("--holdout", nargs="*", default=None,
                   help="Subjects to hold out (animal mode only). If omitted, last 2 by name.")
    # Model
    p.add_argument("--dim", type=int, default=64)
    p.add_argument("--depth", type=int, default=2)
    p.add_argument("--dim-head", type=int, default=32)
    p.add_argument("--num-latents", type=int, default=16)
    p.add_argument("--window-len", type=float, default=1.0)
    p.add_argument("--latent-step", type=float, default=0.125)
    # Ablation: which conditioning channels are on
    p.add_argument("--arm", default="baseline",
                   choices=["baseline", "region", "cell_type", "region_ctype",
                            "pure_anatomy", "waveform", "waveform_only"])
    # Optim
    p.add_argument("--batch-size", type=int, default=4)
    p.add_argument("--lr", type=float, default=3e-4)
    p.add_argument("--weight-decay", type=float, default=1e-4)
    p.add_argument("--max-steps", type=int, default=500)
    p.add_argument("--warmup-steps", type=int, default=50)
    p.add_argument("--eval-every", type=int, default=100)
    p.add_argument("--eval-batches", type=int, default=20)
    p.add_argument("--log-every", type=int, default=20)
    return p.parse_args()


def resolve_device(name: str) -> torch.device:
    if name == "auto":
        if torch.cuda.is_available():
            return torch.device("cuda")
        if torch.backends.mps.is_available():
            return torch.device("mps")
        return torch.device("cpu")
    return torch.device(name)


def arm_flags(arm: str) -> dict:
    # All flags default False; only the ones needed are enabled per arm.
    base = {"use_unit_emb": False, "use_region_emb": False,
            "use_cell_type_emb": False, "use_waveform_emb": False}
    flags_by_arm = {
        "baseline":      {"use_unit_emb": True},
        "region":        {"use_unit_emb": True, "use_region_emb": True},
        "cell_type":     {"use_unit_emb": True, "use_cell_type_emb": True},
        "region_ctype":  {"use_unit_emb": True, "use_region_emb": True, "use_cell_type_emb": True},
        "pure_anatomy":  {"use_region_emb": True, "use_cell_type_emb": True},
        "waveform":      {"use_unit_emb": True, "use_waveform_emb": True},
        "waveform_only": {"use_waveform_emb": True},
    }[arm]
    base.update(flags_by_arm)
    return base


# -------------------------------------------------------- data & sampling

def build_vocab(ds: Dataset):
    """Collect global unit_ids / session_ids / region info / waveform features across all recordings."""
    recs = {rid: ds.get_recording(rid) for rid in ds.recording_ids}
    all_unit_ids: list[str] = []
    all_region_acronyms: list[str] = []
    all_region_ids: list[int] = []
    waveform_rows: list[np.ndarray] = []
    subject_by_rid: dict[str, str] = {}
    for rid, rec in recs.items():
        prefix = f"{rid}/"
        unit_ids = [prefix + u for u in rec.units.id.astype(str).tolist()]
        all_unit_ids.extend(unit_ids)
        all_region_acronyms.extend(rec.units.region_acronym.astype(str).tolist())
        all_region_ids.extend(rec.units.region_id.astype(np.int64).tolist())
        # Per-unit waveform features: (amps, depths, peak_to_trough)
        amps = np.asarray(rec.units.amps, dtype=np.float32)
        depths = np.asarray(rec.units.depths, dtype=np.float32)
        ptt = np.asarray(rec.units.peak_to_trough, dtype=np.float32)
        waveform_rows.append(np.stack([amps, depths, ptt], axis=-1))
        subject_by_rid[rid] = str(rec.subject.id)
    unique_region_ids = np.unique(all_region_ids)
    region_id_to_idx = {int(r): i for i, r in enumerate(unique_region_ids)}
    region_idx_per_unit = np.array(
        [region_id_to_idx[r] for r in all_region_ids], dtype=np.int64,
    )
    waveform_features = np.concatenate(waveform_rows, axis=0).astype(np.float32)
    return {
        "recs": recs,
        "all_unit_ids": all_unit_ids,
        "session_ids": list(recs.keys()),
        "region_idx_per_unit": region_idx_per_unit,
        "region_acronyms": np.array(all_region_acronyms),
        "n_regions": len(unique_region_ids),
        "waveform_features": waveform_features,
        "subject_by_rid": subject_by_rid,
    }


def split_recordings(subject_by_rid: dict, holdout: list[str] | None):
    subjects = sorted(set(subject_by_rid.values()))
    if holdout is None:
        # default: last 2 subjects (by sorted name)
        holdout = subjects[-2:] if len(subjects) >= 2 else subjects[-1:]
    train_rids = [rid for rid, s in subject_by_rid.items() if s not in holdout]
    eval_rids = [rid for rid, s in subject_by_rid.items() if s in holdout]
    return train_rids, eval_rids, holdout


def build_model(vocab, args, n_cell_types: int):
    flags = arm_flags(args.arm)
    spec = ModalitySpec(
        id=2, dim=1, type=DataType.BINARY,
        timestamp_key="trials.stim_on_times", value_key="trials.choice",
        loss_fn=F.binary_cross_entropy_with_logits,
    )
    model = AnatomicalPOYO(
        n_regions=vocab["n_regions"],
        n_cell_types=n_cell_types,
        sequence_length=args.window_len,
        latent_step=args.latent_step,
        dim=args.dim,
        depth=args.depth,
        dim_head=args.dim_head,
        num_latents_per_step=args.num_latents,
        cross_heads=2,
        self_heads=4,
        ffn_dropout=0.1,
        lin_dropout=0.1,
        atn_dropout=0.0,
        readout_spec=spec,
        **flags,
    )
    return model, flags


def build_trial_samples(recs, rids: list[str], window_len: float) -> list[tuple[str, float, float]]:
    """Return a flat list of (recording_id, window_start_time, choice_binary) triples.

    Each entry is a trial-aligned window: t0 = trials.stim_on_times, t1 = t0 + window_len.
    Target is 0.0 for left (choice=-1) or 1.0 for right (choice=+1). Nogo (choice=0)
    and trials with NaN stim_on_time or windows past the recording domain are skipped.
    """
    out: list[tuple[str, float, float]] = []
    for rid in rids:
        rec = recs[rid]
        if not hasattr(rec, "trials"):
            continue
        choice = np.asarray(rec.trials.choice, dtype=np.int64)
        stim_on = np.asarray(rec.trials.stim_on_times, dtype=np.float64)
        domain_hi = float(rec.domain.end[-1])
        for c, t0 in zip(choice, stim_on):
            if c == 0 or not np.isfinite(t0):
                continue
            if t0 + window_len > domain_hi:
                continue
            target = 0.0 if c == -1 else 1.0
            out.append((rid, float(t0), target))
    return out


def build_inputs_for_window(model, sample, rid, t0, args):
    """Build per-window arrays. Returns a dict of np.ndarrays, or None if no spikes."""
    n_spikes = len(sample.spikes.timestamps)
    if n_spikes == 0:
        return None
    prefix = f"{rid}/"
    sample_unit_ids = [prefix + u for u in sample.units.id.astype(str).tolist()]
    local_to_global = np.array(model.unit_emb.tokenizer(sample_unit_ids), dtype=np.int64)
    input_unit_index = local_to_global[sample.spikes.unit_index]
    input_timestamps = sample.spikes.timestamps.astype(np.float32) - t0
    input_token_type = np.zeros(n_spikes, dtype=np.int64)

    latent_index, latent_timestamps = create_linspace_latent_tokens(
        start=0.0, end=args.window_len, step=args.latent_step,
        num_latents_per_step=args.num_latents,
    )

    session_idx = model.session_emb.tokenizer([rid])[0]
    # One output query at end-of-window (just before the response).
    output_session_index = np.array([session_idx], dtype=np.int64)
    output_timestamps = np.array([args.window_len * 0.95], dtype=np.float32)

    return {
        "input_unit_index": input_unit_index,
        "input_timestamps": input_timestamps,
        "input_token_type": input_token_type,
        "latent_index": latent_index,
        "latent_timestamps": latent_timestamps,
        "output_session_index": output_session_index,
        "output_timestamps": output_timestamps,
    }


def collate_batch(samples: list[dict], device: torch.device):
    """Pad variable-length spike sequences; everything else is fixed-shape."""
    max_in = max(s["input_unit_index"].shape[0] for s in samples)
    B = len(samples)
    n_latent = samples[0]["latent_index"].shape[0]
    n_out = samples[0]["output_timestamps"].shape[0]

    input_unit_index = np.zeros((B, max_in), dtype=np.int64)
    input_timestamps = np.zeros((B, max_in), dtype=np.float32)
    input_token_type = np.zeros((B, max_in), dtype=np.int64)
    input_mask = np.zeros((B, max_in), dtype=bool)
    latent_index = np.zeros((B, n_latent), dtype=np.int64)
    latent_timestamps = np.zeros((B, n_latent), dtype=np.float32)
    output_session_index = np.zeros((B, n_out), dtype=np.int64)
    output_timestamps = np.zeros((B, n_out), dtype=np.float32)
    for b, s in enumerate(samples):
        n = s["input_unit_index"].shape[0]
        input_unit_index[b, :n] = s["input_unit_index"]
        input_timestamps[b, :n] = s["input_timestamps"]
        input_token_type[b, :n] = s["input_token_type"]
        input_mask[b, :n] = True
        latent_index[b] = s["latent_index"]
        latent_timestamps[b] = s["latent_timestamps"]
        output_session_index[b] = s["output_session_index"]
        output_timestamps[b] = s["output_timestamps"]
    t = lambda x, d: torch.as_tensor(x, dtype=d, device=device)
    return {
        "input_unit_index": t(input_unit_index, torch.long),
        "input_timestamps": t(input_timestamps, torch.float32),
        "input_token_type": t(input_token_type, torch.long),
        "input_mask": t(input_mask, torch.bool),
        "latent_index": t(latent_index, torch.long),
        "latent_timestamps": t(latent_timestamps, torch.float32),
        "output_session_index": t(output_session_index, torch.long),
        "output_timestamps": t(output_timestamps, torch.float32),
    }


def lr_lambda(step: int, warmup: int, total: int) -> float:
    if step < warmup:
        return step / max(1, warmup)
    # cosine decay
    progress = (step - warmup) / max(1, total - warmup)
    return 0.5 * (1.0 + math.cos(math.pi * min(1.0, progress)))


def draw_batch(ds, trial_list, args, model, rng) -> tuple[dict, torch.Tensor]:
    """Draw a batch of `batch_size` trial-aligned windows from the precomputed list.

    `trial_list` is the output of `build_trial_samples` — every entry is already a valid
    trial; we just retry on the rare case where a window has zero spikes.
    """
    samples = []
    targets = []
    attempts = 0
    while len(samples) < args.batch_size and attempts < 50:
        attempts += 1
        rid, t0, target = trial_list[rng.integers(len(trial_list))]
        sample = ds[DatasetIndex(recording_id=rid, start=t0, end=t0 + args.window_len)]
        inputs_np = build_inputs_for_window(model, sample, rid, t0, args)
        if inputs_np is None:
            continue
        samples.append(inputs_np)
        targets.append(target)
    if len(samples) < args.batch_size:
        return None, None
    batch = collate_batch(samples, device=next(model.parameters()).device)
    # (B, 1) targets to match model output shape (B, n_out=1)
    tgt = torch.as_tensor(np.array(targets, dtype=np.float32)[:, None],
                          device=batch["input_unit_index"].device)
    return batch, tgt


def _auc(scores: np.ndarray, labels: np.ndarray) -> float:
    """ROC AUC via Mann-Whitney rank statistic. Returns NaN if only one class present."""
    pos = scores[labels == 1]
    neg = scores[labels == 0]
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    n_pos, n_neg = len(pos), len(neg)
    all_scores = np.concatenate([pos, neg])
    ranks = np.argsort(np.argsort(all_scores)) + 1
    sum_pos_ranks = ranks[:n_pos].sum()
    return float((sum_pos_ranks - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg))


def evaluate(model, ds, eval_trial_list, args) -> dict:
    model.eval()
    all_logits = []
    all_tgts = []
    rng = np.random.default_rng(args.seed + 1000)  # deterministic eval order
    with torch.no_grad():
        for _ in range(args.eval_batches):
            batch, tgt = draw_batch(ds, eval_trial_list, args, model, rng)
            if batch is None:
                continue
            out = model(**batch).squeeze(-1)  # (B, 1)
            all_logits.append(out.detach().float().cpu().numpy())
            all_tgts.append(tgt.detach().float().cpu().numpy())
    if not all_logits:
        return {"eval_loss": float("nan"), "eval_acc": float("nan"),
                "eval_auc": float("nan"), "eval_n": 0}
    logits = np.concatenate(all_logits, axis=0).ravel()
    tgts = np.concatenate(all_tgts, axis=0).ravel().astype(np.int64)
    probs = 1 / (1 + np.exp(-logits))
    bce = -float(np.mean(tgts * np.log(np.clip(probs, 1e-7, 1.0)) +
                         (1 - tgts) * np.log(np.clip(1 - probs, 1e-7, 1.0))))
    acc = float(np.mean((probs > 0.5) == tgts.astype(bool)))
    auc = _auc(probs, tgts)
    model.train()
    return {"eval_loss": bce, "eval_acc": acc, "eval_auc": auc, "eval_n": len(tgts),
            "eval_n_pos": int((tgts == 1).sum()), "eval_n_neg": int((tgts == 0).sum())}


def main():
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    device = resolve_device(args.device)
    rng = np.random.default_rng(args.seed)
    torch.manual_seed(args.seed)

    log_path = args.out_dir / "log.jsonl"
    log_fh = open(log_path, "a")
    def log(record: dict):
        record = {"t": time.time(), **record}
        print(json.dumps(record))
        log_fh.write(json.dumps(record) + "\n")
        log_fh.flush()

    log({"event": "config", **{k: (str(v) if isinstance(v, Path) else v) for k, v in vars(args).items()},
         "device": str(device)})

    ds = Dataset(dataset_dir=args.data_dir, keep_files_open=True)
    vocab = build_vocab(ds)

    if args.split_mode == "animal":
        train_rids, eval_rids, holdout = split_recordings(vocab["subject_by_rid"], args.holdout)
        train_trials = build_trial_samples(vocab["recs"], train_rids, args.window_len)
        eval_trials = build_trial_samples(vocab["recs"], eval_rids, args.window_len)
        split_info = {"split_mode": "animal", "holdout_subjects": holdout,
                      "n_train_rids": len(train_rids), "n_eval_rids": len(eval_rids)}
    else:
        # Within-animal: all recordings in both splits, trials shuffled 80/20
        all_rids = list(vocab["recs"].keys())
        all_trials = build_trial_samples(vocab["recs"], all_rids, args.window_len)
        split_rng = np.random.default_rng(args.split_seed)
        perm = split_rng.permutation(len(all_trials))
        n_train = int(len(all_trials) * 0.8)
        train_trials = [all_trials[i] for i in perm[:n_train]]
        eval_trials = [all_trials[i] for i in perm[n_train:]]
        split_info = {"split_mode": "trial", "split_seed": args.split_seed,
                      "n_recordings_used": len(all_rids), "frac_train": 0.8}

    n_train_left = sum(1 for *_, t in train_trials if t == 0.0)
    n_train_right = sum(1 for *_, t in train_trials if t == 1.0)
    n_eval_left = sum(1 for *_, t in eval_trials if t == 0.0)
    n_eval_right = sum(1 for *_, t in eval_trials if t == 1.0)
    log({"event": "split", "n_recordings": len(ds.recording_ids),
         **split_info,
         "n_train_trials": len(train_trials),
         "n_eval_trials": len(eval_trials),
         "train_class_balance": {"L": n_train_left, "R": n_train_right},
         "eval_class_balance": {"L": n_eval_left, "R": n_eval_right}})
    if not train_trials or not eval_trials:
        log({"event": "fatal", "msg": "no trials available in train or eval split"})
        return 1

    priors_df = pd.read_parquet(args.priors_path)
    taxonomy = pd.read_parquet(args.taxonomy_path)["subclass"].tolist()
    n_cell_types = len(taxonomy)
    model, flags = build_model(vocab, args, n_cell_types)
    model.unit_emb.initialize_vocab(vocab["all_unit_ids"])
    model.session_emb.initialize_vocab(vocab["session_ids"])
    model.register_unit_anatomy(vocab["all_unit_ids"], vocab["region_idx_per_unit"])
    if flags["use_cell_type_emb"]:
        model.register_unit_cell_types(
            vocab["all_unit_ids"], vocab["region_acronyms"], priors_df, taxonomy,
        )
    if flags["use_waveform_emb"]:
        model.register_unit_waveform_features(
            vocab["all_unit_ids"], vocab["waveform_features"],
        )
    n_params = sum(p.numel() for p in model.parameters())
    log({"event": "model", "arm": args.arm, "n_params": n_params, **flags})
    model = model.to(device)

    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    scheduler = torch.optim.lr_scheduler.LambdaLR(
        optimizer, lambda s: lr_lambda(s, args.warmup_steps, args.max_steps),
    )

    best_eval = float("inf")
    losses = []
    t_start = time.time()
    model.train()
    for step in range(1, args.max_steps + 1):
        batch, target = draw_batch(ds, train_trials, args, model, rng)
        if batch is None:
            log({"event": "skip_step", "step": step, "reason": "no_valid_samples"})
            continue
        out = model(**batch).squeeze(-1)  # (B, 1)
        loss = F.binary_cross_entropy_with_logits(out, target)
        optimizer.zero_grad()
        loss.backward()
        gnorm = torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()
        scheduler.step()
        losses.append(loss.item())

        if step % args.log_every == 0:
            with torch.no_grad():
                preds_correct = ((out > 0).float() == target).float().mean().item()
            log({"event": "train", "step": step, "loss": loss.item(),
                 "mean20": float(np.mean(losses[-20:])),
                 "batch_acc": preds_correct,
                 "grad_norm": float(gnorm),
                 "lr": optimizer.param_groups[0]["lr"]})

        if step % args.eval_every == 0 or step == args.max_steps:
            eval_metrics = evaluate(model, ds, eval_trials, args)
            log({"event": "eval", "step": step, **eval_metrics})
            if eval_metrics["eval_loss"] < best_eval:
                best_eval = eval_metrics["eval_loss"]
                ckpt = {"step": step, "args": vars(args), "state_dict": model.state_dict(),
                        "vocab_unit_ids": vocab["all_unit_ids"],
                        "vocab_session_ids": vocab["session_ids"],
                        "eval": eval_metrics}
                torch.save(ckpt, args.out_dir / "best.ckpt")
                log({"event": "ckpt_best", "step": step, "eval_loss": best_eval,
                     "eval_acc": eval_metrics["eval_acc"], "eval_auc": eval_metrics["eval_auc"]})

    # Save last
    torch.save({"step": step, "args": vars(args), "state_dict": model.state_dict()},
               args.out_dir / "last.ckpt")
    log({"event": "done", "wall_clock_s": time.time() - t_start, "best_eval_loss": best_eval})
    log_fh.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
