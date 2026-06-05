"""Real training script: AnatomicalPOYO for IBL decoding with held-out-animal eval.

Sampling is trial-aligned: each training window is [stimOn_time, stimOn_time + window_len]
from a real IBL trial. Targets can be animal choice or stimulus side.
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
from collections import Counter, defaultdict
from functools import lru_cache
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
from eval_design import (  # noqa: E402
    arm_flags,
    build_session_vocab,
    output_query_session_id,
    split_recordings_by_subject,
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
    p.add_argument("--manifest", type=Path, default=None,
                   help="Optional recording manifest. When set, train/eval only use matching "
                        "HDF5 recording ids from --data-dir.")
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
    p.add_argument("--output-query-mode", default="shared", choices=["shared", "session"],
                   help="'shared' uses one trainable task query for all recordings, which is "
                        "the primary cross-animal setting. 'session' preserves the original "
                        "per-recording query for diagnostics.")
    p.add_argument("--target-mode", default="choice", choices=["choice", "stimulus_side"],
                   help="'choice' decodes animal L/R choice. 'stimulus_side' decodes whether "
                        "the visual stimulus contrast was stronger on the right than left.")
    p.add_argument("--region-filter", default="none", choices=["none", "shared_regions", "include_regions"],
                   help="'shared_regions' keeps only units whose region acronym appears in both "
                        "the train and held-out recordings for the current split. "
                        "'include_regions' keeps only units whose mapped acronym is listed in "
                        "--region-include.")
    p.add_argument("--region-include", default="",
                   help="Comma-separated region acronyms to keep after --region-granularity mapping. "
                        "Used when --region-filter=include_regions.")
    p.add_argument("--region-granularity", default="fine", choices=["fine", "parent", "grandparent"],
                   help="Granularity for region embeddings and region filtering. Cell-type priors "
                        "still use original fine acronyms with their existing ancestor fallback.")
    p.add_argument("--region-label-control", default="none", choices=["none", "shuffle"],
                   help="'shuffle' permutes region labels across unit tokens after vocab build, "
                        "preserving the marginal region distribution but breaking anatomy-to-unit identity.")
    # Model
    p.add_argument("--dim", type=int, default=64)
    p.add_argument("--depth", type=int, default=2)
    p.add_argument("--dim-head", type=int, default=32)
    p.add_argument("--num-latents", type=int, default=16)
    p.add_argument("--window-len", type=float, default=1.0)
    p.add_argument("--latent-step", type=float, default=0.125)
    # Ablation: which conditioning channels are on
    p.add_argument("--arm", default="baseline",
                   choices=["baseline", "shared_baseline", "region", "cell_type", "region_ctype",
                            "region_only", "cell_type_only", "pure_anatomy",
                            "waveform", "waveform_only"])
    # Optim
    p.add_argument("--batch-size", type=int, default=4)
    p.add_argument("--batch-sampling", default="uniform", choices=["uniform", "target_balanced"],
                   help="'uniform' samples trial windows uniformly. 'target_balanced' alternates "
                        "left/right targets within accepted training batches to reduce target-prior "
                        "leakage; sampled eval remains uniform.")
    p.add_argument("--lr", type=float, default=3e-4)
    p.add_argument("--weight-decay", type=float, default=1e-4)
    p.add_argument("--max-steps", type=int, default=500)
    p.add_argument("--warmup-steps", type=int, default=50)
    p.add_argument("--eval-every", type=int, default=100)
    p.add_argument("--eval-batches", type=int, default=20)
    p.add_argument("--log-every", type=int, default=20)
    p.add_argument("--best-metric", default="eval_loss",
                   choices=["eval_loss", "eval_auc", "full_eval_auc", "full_eval_centered_auc"],
                   help="Metric used to select best.ckpt. full_eval_* metrics score every "
                        "held-out trial at each eval point and are best aligned with the "
                        "anatomy-transfer demo gate.")
    p.add_argument("--save-eval-predictions", action="store_true",
                   help="When a new best checkpoint is found, write deterministic held-out "
                        "trial predictions to eval_predictions.jsonl for model diagnostics.")
    p.add_argument("--full-eval-on-best", action="store_true",
                   help="When a new best checkpoint is found, score every held-out trial "
                        "and log full_eval metrics for official deterministic summaries.")
    p.add_argument("--eval-prediction-max-trials", type=int, default=0,
                   help="Maximum eval trials to export when --save-eval-predictions is set. "
                        "0 exports all valid eval trials.")
    p.add_argument("--save-region-embeddings", action="store_true",
                   help="When a new best checkpoint is found, write region embedding vectors "
                        "to region_embeddings.jsonl for anatomical-code diagnostics.")
    return p.parse_args()


def resolve_device(name: str) -> torch.device:
    if name == "auto":
        if torch.cuda.is_available():
            return torch.device("cuda")
        if torch.backends.mps.is_available():
            return torch.device("mps")
        return torch.device("cpu")
    return torch.device(name)


# -------------------------------------------------------- data & sampling

@lru_cache(maxsize=None)
def _ancestor_acronyms(acronym: str) -> tuple[str, ...]:
    from iblatlas.regions import BrainRegions
    br = BrainRegions()
    try:
        ids = np.atleast_1d(br.acronym2id(acronym))
    except Exception:
        return ()
    if len(ids) == 0:
        return ()
    try:
        anc = br.ancestors(np.array([int(ids[0])]))
    except Exception:
        return ()
    if hasattr(anc, "acronym"):
        return tuple(str(a) for a in anc.acronym)
    if isinstance(anc, dict) and "acronym" in anc:
        return tuple(str(a) for a in anc["acronym"])
    return ()


def region_acronym_at_granularity(acronym: str, granularity: str) -> str:
    if granularity == "fine":
        return str(acronym)
    ancestors = _ancestor_acronyms(str(acronym))
    if not ancestors:
        return str(acronym)
    offset = {"parent": 2, "grandparent": 3}[granularity]
    if len(ancestors) >= offset:
        candidate = ancestors[-offset]
        if candidate not in {"root", "grey"}:
            return candidate
    return str(acronym)


def map_region_acronyms(acronyms, granularity: str) -> list[str]:
    cache: dict[str, str] = {}
    out: list[str] = []
    for acronym in acronyms:
        key = str(acronym)
        if key not in cache:
            cache[key] = region_acronym_at_granularity(key, granularity)
        out.append(cache[key])
    return out


def manifest_recording_ids(path: Path) -> list[str]:
    payload = json.loads(path.read_text())
    rows = payload["recordings"] if isinstance(payload, dict) else payload
    out: list[str] = []
    for row in rows:
        eid = row.get("session_id") or row.get("eid") or row.get("session")
        probe = row.get("probe_name") or row.get("probe") or row.get("name")
        if eid and probe:
            out.append(f"{eid}_{probe}")
    return out


def select_recording_ids(ds: Dataset, manifest: Path | None, data_dir: Path | None = None) -> list[str]:
    if manifest is None:
        return list(ds.recording_ids)
    requested = manifest_recording_ids(manifest)
    available = set(ds.recording_ids)
    selected = [rid for rid in requested if rid in available]
    missing = sorted(set(requested) - available)
    if missing:
        preview = ", ".join(missing[:5])
        suffix = "" if len(missing) <= 5 else f", ... ({len(missing)} total)"
        location = str(data_dir) if data_dir is not None else "dataset"
        raise SystemExit(f"Manifest recordings missing from {location}: {preview}{suffix}")
    if not selected:
        location = str(data_dir) if data_dir is not None else "dataset"
        raise SystemExit(f"Manifest {manifest} did not match any recordings in {location}")
    return selected


def build_vocab(ds: Dataset, region_granularity: str = "fine", recording_ids: list[str] | None = None):
    """Collect global unit_ids / session_ids / region info / waveform features across all recordings."""
    recording_ids = list(ds.recording_ids) if recording_ids is None else recording_ids
    recs = {rid: ds.get_recording(rid) for rid in recording_ids}
    all_unit_ids: list[str] = []
    all_region_acronyms: list[str] = []
    all_region_labels: list[str] = []
    all_fine_region_acronyms: list[str] = []
    waveform_rows: list[np.ndarray] = []
    subject_by_rid: dict[str, str] = {}
    for rid, rec in recs.items():
        prefix = f"{rid}/"
        unit_ids = [prefix + u for u in rec.units.id.astype(str).tolist()]
        all_unit_ids.extend(unit_ids)
        fine_acronyms = rec.units.region_acronym.astype(str).tolist()
        region_labels = map_region_acronyms(fine_acronyms, region_granularity)
        all_region_acronyms.extend(region_labels)
        all_fine_region_acronyms.extend(fine_acronyms)
        all_region_labels.extend(region_labels)
        # Per-unit waveform features: (amps, depths, peak_to_trough)
        amps = np.asarray(rec.units.amps, dtype=np.float32)
        depths = np.asarray(rec.units.depths, dtype=np.float32)
        ptt = np.asarray(rec.units.peak_to_trough, dtype=np.float32)
        waveform_rows.append(np.stack([amps, depths, ptt], axis=-1))
        subject_by_rid[rid] = str(rec.subject.id)
    unique_region_labels = sorted(set(all_region_labels))
    region_id_to_idx = {label: i for i, label in enumerate(unique_region_labels)}
    region_idx_per_unit = np.array(
        [region_id_to_idx[r] for r in all_region_labels], dtype=np.int64,
    )
    waveform_features = np.concatenate(waveform_rows, axis=0).astype(np.float32)
    return {
        "recs": recs,
        "all_unit_ids": all_unit_ids,
        "session_ids": list(recs.keys()),
        "region_idx_per_unit": region_idx_per_unit,
        "region_acronyms": np.array(all_region_acronyms),
        "cell_type_region_acronyms": np.array(all_fine_region_acronyms),
        "n_regions": len(unique_region_labels),
        "region_granularity": region_granularity,
        "waveform_features": waveform_features,
        "subject_by_rid": subject_by_rid,
    }


def apply_region_label_control(vocab: dict, control: str, seed: int) -> dict:
    if control == "none":
        return vocab
    if control != "shuffle":
        raise ValueError(f"unknown region label control {control!r}")
    rng = np.random.default_rng(seed + 17_003)
    shuffled = dict(vocab)
    region_idx = np.asarray(vocab["region_idx_per_unit"], dtype=np.int64).copy()
    region_acronyms = np.asarray(vocab["region_acronyms"]).copy()
    cell_type_acronyms = np.asarray(vocab["cell_type_region_acronyms"]).copy()
    perm = rng.permutation(len(region_idx))
    shuffled["region_idx_per_unit"] = region_idx[perm]
    shuffled["region_acronyms"] = region_acronyms[perm]
    shuffled["cell_type_region_acronyms"] = cell_type_acronyms[perm]
    return shuffled


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


def _target_from_trial(rec, idx: int, target_mode: str) -> float | None:
    if target_mode == "choice":
        choice = int(np.asarray(rec.trials.choice, dtype=np.int64)[idx])
        if choice == 0:
            return None
        return 0.0 if choice == -1 else 1.0
    if target_mode == "stimulus_side":
        left = np.asarray(rec.trials.contrast_left, dtype=np.float64)[idx]
        right = np.asarray(rec.trials.contrast_right, dtype=np.float64)[idx]
        left = 0.0 if not np.isfinite(left) else float(left)
        right = 0.0 if not np.isfinite(right) else float(right)
        if left == right:
            return None
        return 1.0 if right > left else 0.0
    raise ValueError(f"unknown target_mode {target_mode!r}")


def build_trial_samples(
    recs,
    rids: list[str],
    window_len: float,
    target_mode: str,
) -> list[tuple[str, float, float]]:
    """Return a flat list of (recording_id, window_start_time, choice_binary) triples.

    Each entry is a trial-aligned window: t0 = trials.stim_on_times, t1 = t0 + window_len.
    Target is 0.0 for left and 1.0 for right. Invalid/no-go/equal-contrast trials
    and trials with NaN stim_on_time or windows past the recording domain are skipped.
    """
    out: list[tuple[str, float, float]] = []
    for rid in rids:
        rec = recs[rid]
        if not hasattr(rec, "trials"):
            continue
        stim_on = np.asarray(rec.trials.stim_on_times, dtype=np.float64)
        domain_hi = float(rec.domain.end[-1])
        for idx, t0 in enumerate(stim_on):
            if not np.isfinite(t0):
                continue
            if t0 + window_len > domain_hi:
                continue
            target = _target_from_trial(rec, idx, target_mode)
            if target is None:
                continue
            out.append((rid, float(t0), target))
    return out


def trial_indices_by_target(trial_list: list[tuple[str, float, float]]) -> dict[int, list[int]]:
    by_target: dict[int, list[int]] = defaultdict(list)
    for idx, (_rid, _t0, target) in enumerate(trial_list):
        by_target[int(target)].append(idx)
    return dict(by_target)


def choose_trial_index(
    trial_list: list[tuple[str, float, float]],
    rng,
    batch_sampling: str,
    accepted_count: int,
    target_offset: int = 0,
) -> int:
    if batch_sampling == "uniform":
        return int(rng.integers(len(trial_list)))
    if batch_sampling != "target_balanced":
        raise ValueError(f"unknown batch_sampling {batch_sampling!r}")
    by_target = trial_indices_by_target(trial_list)
    if not by_target.get(0) or not by_target.get(1):
        return int(rng.integers(len(trial_list)))
    desired_target = int((accepted_count + target_offset) % 2)
    choices = by_target[desired_target]
    return int(choices[int(rng.integers(len(choices)))])


def recording_region_acronyms(recs, rids: list[str], region_granularity: str = "fine") -> set[str]:
    regions: set[str] = set()
    for rid in rids:
        regions.update(map_region_acronyms(
            recs[rid].units.region_acronym.astype(str).tolist(),
            region_granularity,
        ))
    return regions


def shared_split_regions(
    recs,
    train_rids: list[str],
    eval_rids: list[str],
    region_granularity: str = "fine",
) -> set[str]:
    return (
        recording_region_acronyms(recs, train_rids, region_granularity)
        & recording_region_acronyms(recs, eval_rids, region_granularity)
    )


def parse_region_include(value: str) -> set[str]:
    return {part.strip() for part in value.split(",") if part.strip()}


def recording_diagnostics(recs, rids: list[str]) -> list[dict]:
    rows = []
    for rid in sorted(rids):
        rec = recs[rid]
        choice = np.asarray(rec.trials.choice, dtype=np.int64) if hasattr(rec, "trials") else np.array([])
        rows.append({
            "recording_id": rid,
            "subject": str(rec.subject.id),
            "n_units": int(len(rec.units.id)),
            "n_regions": int(len(set(rec.units.region_acronym.astype(str).tolist()))),
            "n_trials": int(len(choice)),
            "choice_counts": {
                "L": int((choice == -1).sum()),
                "R": int((choice == 1).sum()),
                "nogo": int((choice == 0).sum()),
            },
        })
    return rows


def subject_trial_counts(trials: list[tuple[str, float, float]], subject_by_rid: dict[str, str]) -> dict:
    counts: dict[str, Counter] = defaultdict(Counter)
    for rid, _t0, target in trials:
        subject = subject_by_rid[rid]
        counts[subject]["R" if target == 1.0 else "L"] += 1
    return {
        subject: {"L": int(counter["L"]), "R": int(counter["R"])}
        for subject, counter in sorted(counts.items())
    }


def build_inputs_for_window(model, sample, rid, t0, args, allowed_region_acronyms: set[str] | None = None):
    """Build per-window arrays. Returns a dict of np.ndarrays, or None if no spikes."""
    prefix = f"{rid}/"
    sample_unit_ids = [prefix + u for u in sample.units.id.astype(str).tolist()]
    local_to_global = np.array(model.unit_emb.tokenizer(sample_unit_ids), dtype=np.int64)

    spike_unit_index = np.asarray(sample.spikes.unit_index, dtype=np.int64)
    spike_timestamps = np.asarray(sample.spikes.timestamps, dtype=np.float32)
    if allowed_region_acronyms is not None:
        unit_regions = map_region_acronyms(sample.units.region_acronym.astype(str), args.region_granularity)
        unit_allowed = np.array([region in allowed_region_acronyms for region in unit_regions], dtype=bool)
        spike_mask = unit_allowed[spike_unit_index]
        spike_unit_index = spike_unit_index[spike_mask]
        spike_timestamps = spike_timestamps[spike_mask]

    n_spikes = len(spike_timestamps)
    if n_spikes == 0:
        return None
    input_unit_index = local_to_global[spike_unit_index]
    input_timestamps = spike_timestamps - t0
    input_token_type = np.zeros(n_spikes, dtype=np.int64)

    latent_index, latent_timestamps = create_linspace_latent_tokens(
        start=0.0, end=args.window_len, step=args.latent_step,
        num_latents_per_step=args.num_latents,
    )

    query_session_id = output_query_session_id(rid, args.output_query_mode)
    session_idx = model.session_emb.tokenizer([query_session_id])[0]
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
    def t(x, d):
        return torch.as_tensor(x, dtype=d, device=device)

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


def best_metric_initial_value(metric: str) -> float:
    if metric == "eval_loss":
        return float("inf")
    if metric in {"eval_auc", "full_eval_auc", "full_eval_centered_auc"}:
        return -float("inf")
    raise ValueError(f"unknown best metric {metric!r}")


def is_better_metric(metric: str, candidate: float, current: float) -> bool:
    if math.isnan(candidate):
        return False
    if metric == "eval_loss":
        return candidate < current
    if metric in {"eval_auc", "full_eval_auc", "full_eval_centered_auc"}:
        return candidate > current
    raise ValueError(f"unknown best metric {metric!r}")


def best_metric_requires_full_eval(metric: str) -> bool:
    return metric.startswith("full_eval_")


def draw_batch(
    ds,
    trial_list,
    args,
    model,
    rng,
    allowed_region_acronyms: set[str] | None = None,
    batch_sampling: str | None = None,
) -> tuple[dict, torch.Tensor]:
    """Draw a batch of `batch_size` trial-aligned windows from the precomputed list.

    `trial_list` is the output of `build_trial_samples` — every entry is already a valid
    trial; we just retry on the rare case where a window has zero spikes.
    """
    samples = []
    targets = []
    attempts = 0
    sampling_mode = getattr(args, "batch_sampling", "uniform") if batch_sampling is None else batch_sampling
    target_offset = int(rng.integers(2)) if sampling_mode == "target_balanced" else 0
    while len(samples) < args.batch_size and attempts < 50:
        attempts += 1
        idx = choose_trial_index(
            trial_list,
            rng,
            sampling_mode,
            accepted_count=len(samples),
            target_offset=target_offset,
        )
        rid, t0, target = trial_list[idx]
        sample = ds[DatasetIndex(recording_id=rid, start=t0, end=t0 + args.window_len)]
        inputs_np = build_inputs_for_window(model, sample, rid, t0, args, allowed_region_acronyms)
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


def evaluate(model, ds, eval_trial_list, args, allowed_region_acronyms: set[str] | None = None) -> dict:
    model.eval()
    all_logits = []
    all_tgts = []
    rng = np.random.default_rng(args.seed + 1000)  # deterministic eval order
    with torch.no_grad():
        for _ in range(args.eval_batches):
            batch, tgt = draw_batch(
                ds,
                eval_trial_list,
                args,
                model,
                rng,
                allowed_region_acronyms,
                batch_sampling="uniform",
            )
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


def region_index_lookup(vocab: dict) -> dict[int, str]:
    """Recover the mapped region acronym for each region embedding index."""
    lookup: dict[int, str] = {}
    for idx, acronym in zip(vocab["region_idx_per_unit"], vocab["region_acronyms"]):
        idx_int = int(idx)
        if idx_int not in lookup:
            lookup[idx_int] = str(acronym)
    return lookup


def write_region_embeddings(model, vocab: dict, path: Path) -> int:
    if getattr(model, "region_emb", None) is None:
        return 0
    lookup = region_index_lookup(vocab)
    weights = model.region_emb.weight.detach().float().cpu().numpy()
    rows_written = 0
    with path.open("w") as fh:
        for idx in sorted(lookup):
            vec = weights[idx]
            fh.write(json.dumps({
                "region_idx": idx,
                "region": lookup[idx],
                "norm": float(np.linalg.norm(vec)),
                "embedding": [float(x) for x in vec],
            }) + "\n")
            rows_written += 1
    return rows_written


def eval_prediction_rows(
    model,
    ds,
    eval_trial_list,
    args,
    allowed_region_acronyms: set[str] | None,
    subject_by_rid: dict[str, str],
    *,
    max_trials: int = 0,
) -> list[dict]:
    """Deterministically score held-out trials one by one for diagnostics."""
    model.eval()
    rows = []
    limit = None if max_trials <= 0 else max_trials
    with torch.no_grad():
        for rid, t0, target in eval_trial_list:
            sample = ds[DatasetIndex(recording_id=rid, start=t0, end=t0 + args.window_len)]
            inputs_np = build_inputs_for_window(model, sample, rid, t0, args, allowed_region_acronyms)
            if inputs_np is None:
                continue
            batch = collate_batch([inputs_np], device=next(model.parameters()).device)
            logit = float(model(**batch).squeeze(-1).detach().float().cpu().numpy().ravel()[0])
            prob = float(1 / (1 + math.exp(-logit)))
            rows.append({
                "recording_id": rid,
                "subject": subject_by_rid.get(rid),
                "t0": float(t0),
                "target": int(target),
                "logit": logit,
                "prob": prob,
            })
            if limit is not None and len(rows) >= limit:
                break
    model.train()
    return rows


def metrics_from_prediction_rows(rows: list[dict], prefix: str = "full_eval") -> dict:
    if not rows:
        return {
            f"{prefix}_loss": float("nan"),
            f"{prefix}_acc": float("nan"),
            f"{prefix}_auc": float("nan"),
            f"{prefix}_centered_auc": float("nan"),
            f"{prefix}_n": 0,
            f"{prefix}_n_pos": 0,
            f"{prefix}_n_neg": 0,
        }
    probs = np.asarray([float(row["prob"]) for row in rows], dtype=np.float64)
    tgts = np.asarray([int(row["target"]) for row in rows], dtype=np.int64)
    bce = -float(np.mean(tgts * np.log(np.clip(probs, 1e-7, 1.0)) +
                         (1 - tgts) * np.log(np.clip(1 - probs, 1e-7, 1.0))))
    acc = float(np.mean((probs > 0.5) == tgts.astype(bool)))
    return {
        f"{prefix}_loss": bce,
        f"{prefix}_acc": acc,
        f"{prefix}_auc": _auc(probs, tgts),
        f"{prefix}_centered_auc": recording_centered_auc_from_prediction_rows(rows),
        f"{prefix}_n": int(len(tgts)),
        f"{prefix}_n_pos": int((tgts == 1).sum()),
        f"{prefix}_n_neg": int((tgts == 0).sum()),
    }


def recording_centered_auc_from_prediction_rows(rows: list[dict]) -> float:
    rows_by_recording: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        rows_by_recording[str(row.get("recording_id", "__all__"))].append(row)
    scores = []
    labels = []
    for recording_rows in rows_by_recording.values():
        probs = np.asarray([float(row["prob"]) for row in recording_rows], dtype=np.float64)
        centered = probs - float(np.mean(probs))
        scores.extend(float(x) for x in centered)
        labels.extend(int(row["target"]) for row in recording_rows)
    if not scores:
        return float("nan")
    return _auc(np.asarray(scores, dtype=np.float64), np.asarray(labels, dtype=np.int64))


def write_eval_prediction_rows(rows: list[dict], path: Path) -> int:
    with path.open("w") as fh:
        for row in rows:
            fh.write(json.dumps(row) + "\n")
    return len(rows)


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
    selected_recording_ids = select_recording_ids(ds, args.manifest, args.data_dir)
    vocab = build_vocab(ds, args.region_granularity, selected_recording_ids)
    vocab = apply_region_label_control(vocab, args.region_label_control, args.seed)

    if args.split_mode == "animal":
        animal_split = split_recordings_by_subject(vocab["subject_by_rid"], args.holdout)
        train_rids = animal_split.train_rids
        eval_rids = animal_split.eval_rids
        train_trials = build_trial_samples(vocab["recs"], train_rids, args.window_len, args.target_mode)
        eval_trials = build_trial_samples(vocab["recs"], eval_rids, args.window_len, args.target_mode)
        split_info = {"split_mode": "animal",
                      "holdout_subjects": animal_split.holdout_subjects,
                      "train_subjects": animal_split.train_subjects,
                      "eval_subjects": animal_split.eval_subjects,
                      "n_train_rids": len(train_rids), "n_eval_rids": len(eval_rids)}
    else:
        # Within-animal: all recordings in both splits, trials shuffled 80/20
        all_rids = list(vocab["recs"].keys())
        train_rids = all_rids
        eval_rids = all_rids
        all_trials = build_trial_samples(vocab["recs"], all_rids, args.window_len, args.target_mode)
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
    allowed_region_acronyms = None
    include_regions = parse_region_include(args.region_include)
    region_filter_info = {"region_filter": args.region_filter, "region_include": sorted(include_regions)}
    if args.region_filter == "shared_regions":
        allowed_region_acronyms = shared_split_regions(
            vocab["recs"], train_rids, eval_rids, args.region_granularity,
        )
        region_filter_info.update({
            "n_allowed_regions": len(allowed_region_acronyms),
            "allowed_regions": sorted(allowed_region_acronyms),
        })
    elif args.region_filter == "include_regions":
        if not include_regions:
            log({"event": "fatal", "msg": "--region-filter=include_regions requires --region-include"})
            return 1
        allowed_region_acronyms = include_regions
        region_filter_info.update({
            "n_allowed_regions": len(allowed_region_acronyms),
            "allowed_regions": sorted(allowed_region_acronyms),
        })
    log({"event": "split", "n_recordings": len(selected_recording_ids),
         "data_recordings_available": len(ds.recording_ids),
         "manifest": str(args.manifest) if args.manifest else None,
         **split_info,
         **region_filter_info,
         "region_granularity": args.region_granularity,
         "region_label_control": args.region_label_control,
         "target_mode": args.target_mode,
         "n_train_trials": len(train_trials),
         "n_eval_trials": len(eval_trials),
         "train_class_balance": {"L": n_train_left, "R": n_train_right},
         "eval_class_balance": {"L": n_eval_left, "R": n_eval_right},
         "train_subject_trial_counts": subject_trial_counts(train_trials, vocab["subject_by_rid"]),
         "eval_subject_trial_counts": subject_trial_counts(eval_trials, vocab["subject_by_rid"]),
         "train_recordings": recording_diagnostics(vocab["recs"], train_rids),
         "eval_recordings": recording_diagnostics(vocab["recs"], eval_rids)})
    if not train_trials or not eval_trials:
        log({"event": "fatal", "msg": "no trials available in train or eval split"})
        return 1

    flags = arm_flags(args.arm)
    priors_df = None
    taxonomy: list[str] = []
    if flags["use_cell_type_emb"]:
        priors_df = pd.read_parquet(args.priors_path)
        taxonomy = pd.read_parquet(args.taxonomy_path)["subclass"].tolist()
    model, flags = build_model(vocab, args, len(taxonomy))
    model.unit_emb.initialize_vocab(vocab["all_unit_ids"])
    model.session_emb.initialize_vocab(
        build_session_vocab(vocab["session_ids"], args.output_query_mode)
    )
    model.register_unit_anatomy(vocab["all_unit_ids"], vocab["region_idx_per_unit"])
    if flags["use_cell_type_emb"]:
        assert priors_df is not None
        model.register_unit_cell_types(
            vocab["all_unit_ids"], vocab["cell_type_region_acronyms"], priors_df, taxonomy,
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

    best_eval = best_metric_initial_value(args.best_metric)
    losses = []
    t_start = time.time()
    model.train()
    for step in range(1, args.max_steps + 1):
        batch, target = draw_batch(ds, train_trials, args, model, rng, allowed_region_acronyms)
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
            eval_metrics = evaluate(model, ds, eval_trials, args, allowed_region_acronyms)
            log({"event": "eval", "step": step, **eval_metrics})
            prediction_rows = None
            full_eval_metrics = None
            full_eval_selection = best_metric_requires_full_eval(args.best_metric)
            if full_eval_selection:
                prediction_rows = eval_prediction_rows(
                    model,
                    ds,
                    eval_trials,
                    args,
                    allowed_region_acronyms,
                    vocab["subject_by_rid"],
                    max_trials=0,
                )
                full_eval_metrics = metrics_from_prediction_rows(prediction_rows)
                log({"event": "full_eval", "step": step, **full_eval_metrics})
            metric_values = {**eval_metrics, **(full_eval_metrics or {})}
            candidate_metric = float(metric_values[args.best_metric])
            if is_better_metric(args.best_metric, candidate_metric, best_eval):
                best_eval = candidate_metric
                ckpt = {"step": step, "args": vars(args), "state_dict": model.state_dict(),
                        "vocab_unit_ids": vocab["all_unit_ids"],
                        "vocab_session_ids": vocab["session_ids"],
                        "eval": eval_metrics}
                torch.save(ckpt, args.out_dir / "best.ckpt")
                log({"event": "ckpt_best", "step": step,
                     "best_metric": args.best_metric, "best_metric_value": best_eval,
                     "eval_loss": eval_metrics["eval_loss"],
                     "eval_acc": eval_metrics["eval_acc"], "eval_auc": eval_metrics["eval_auc"]})
                if args.save_eval_predictions or args.full_eval_on_best:
                    if prediction_rows is None:
                        prediction_rows = eval_prediction_rows(
                            model,
                            ds,
                            eval_trials,
                            args,
                            allowed_region_acronyms,
                            vocab["subject_by_rid"],
                            max_trials=0 if args.full_eval_on_best else args.eval_prediction_max_trials,
                        )
                if args.full_eval_on_best and not full_eval_selection:
                    assert prediction_rows is not None
                    log({"event": "full_eval", "step": step, **metrics_from_prediction_rows(prediction_rows)})
                if args.save_eval_predictions:
                    assert prediction_rows is not None
                    rows_to_write = prediction_rows
                    if args.eval_prediction_max_trials > 0:
                        rows_to_write = rows_to_write[:args.eval_prediction_max_trials]
                    n_pred_rows = write_eval_prediction_rows(rows_to_write, args.out_dir / "eval_predictions.jsonl")
                    log({"event": "eval_predictions_saved", "step": step, "rows": n_pred_rows,
                         "path": str(args.out_dir / "eval_predictions.jsonl")})
                if args.save_region_embeddings:
                    n_region_rows = write_region_embeddings(
                        model,
                        vocab,
                        args.out_dir / "region_embeddings.jsonl",
                    )
                    log({"event": "region_embeddings_saved", "step": step, "rows": n_region_rows,
                         "path": str(args.out_dir / "region_embeddings.jsonl")})

    # Save last
    torch.save({"step": step, "args": vars(args), "state_dict": model.state_dict()},
               args.out_dir / "last.ckpt")
    done_record = {
        "event": "done",
        "wall_clock_s": time.time() - t_start,
        "best_metric": args.best_metric,
        "best_metric_value": best_eval,
    }
    if args.best_metric == "eval_loss":
        done_record["best_eval_loss"] = best_eval
    log(done_record)
    log_fh.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
