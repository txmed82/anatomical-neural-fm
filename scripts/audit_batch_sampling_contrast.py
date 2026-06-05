"""Audit whether training samplers produce recording-local target contrast.

This is a no-spend diagnostic for objective redesign. It uses the same trial
selection helpers as `scripts/train.py`, but does not instantiate a model or
touch GPU. The key question is whether a proposed sampler gives recording-local
ranking losses enough same-recording target-0/target-1 pairs before any model
training happens.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "vendor" / "torch_brain"))

from torch_brain.dataset import Dataset  # noqa: E402
from train import (  # noqa: E402
    apply_region_label_control,
    build_trial_samples,
    build_vocab,
    choose_recording_for_balanced_pair,
    choose_trial_index,
    select_recording_ids,
    split_recordings_by_subject,
    trial_indices_by_recording_target,
)


def _draw_trial_indices(
    trial_list: list[tuple[str, float, float]],
    *,
    rng: np.random.Generator,
    batch_sampling: str,
    batch_size: int,
) -> list[int]:
    indices = []
    target_offset = int(rng.integers(2)) if batch_sampling in {"target_balanced", "recording_target_balanced"} else 0
    pair_recording_id = None
    while len(indices) < batch_size:
        if batch_sampling == "recording_target_balanced" and len(indices) % 2 == 0:
            pair_recording_id = choose_recording_for_balanced_pair(trial_list, rng)
        indices.append(choose_trial_index(
            trial_list,
            rng,
            batch_sampling,
            accepted_count=len(indices),
            target_offset=target_offset,
            recording_id=pair_recording_id,
        ))
    return indices


def batch_contrast_summary(
    trial_list: list[tuple[str, float, float]],
    *,
    batch_sampling: str,
    batch_size: int,
    n_batches: int,
    seed: int,
) -> dict:
    rng = np.random.default_rng(seed)
    target_counts = Counter()
    recording_counts = Counter()
    rankable_batches = 0
    same_recording_adjacent_pairs = 0
    adjacent_pairs = 0
    rankable_recordings_per_batch = []
    rankable_pair_counts = []

    for _ in range(n_batches):
        indices = _draw_trial_indices(
            trial_list,
            rng=rng,
            batch_sampling=batch_sampling,
            batch_size=batch_size,
        )
        rows = [trial_list[idx] for idx in indices]
        by_recording: dict[str, Counter] = defaultdict(Counter)
        for rid, _t0, target in rows:
            target_counts[int(target)] += 1
            recording_counts[str(rid)] += 1
            by_recording[str(rid)][int(target)] += 1

        rankable_recordings = 0
        rankable_pairs = 0
        for counts in by_recording.values():
            if counts[0] and counts[1]:
                rankable_recordings += 1
                rankable_pairs += int(counts[0] * counts[1])
        if rankable_recordings:
            rankable_batches += 1
        rankable_recordings_per_batch.append(rankable_recordings)
        rankable_pair_counts.append(rankable_pairs)

        for left, right in zip(rows[::2], rows[1::2]):
            adjacent_pairs += 1
            if left[0] == right[0] and int(left[2]) != int(right[2]):
                same_recording_adjacent_pairs += 1

    total_samples = sum(target_counts.values())
    by_recording_target = trial_indices_by_recording_target(trial_list)
    eligible_recordings = {
        rid: {str(target): len(indices) for target, indices in targets.items()}
        for rid, targets in by_recording_target.items()
        if targets.get(0) and targets.get(1)
    }
    return {
        "batch_sampling": batch_sampling,
        "batch_size": batch_size,
        "n_batches": n_batches,
        "seed": seed,
        "n_trials": len(trial_list),
        "n_recordings": len(by_recording_target),
        "n_eligible_recordings": len(eligible_recordings),
        "eligible_recording_fraction": len(eligible_recordings) / max(1, len(by_recording_target)),
        "target_counts": {"0": int(target_counts[0]), "1": int(target_counts[1])},
        "target1_fraction": target_counts[1] / max(1, total_samples),
        "rankable_batch_fraction": rankable_batches / max(1, n_batches),
        "mean_rankable_recordings_per_batch": float(np.mean(rankable_recordings_per_batch)),
        "mean_rankable_pairs_per_batch": float(np.mean(rankable_pair_counts)),
        "same_recording_adjacent_pair_fraction": same_recording_adjacent_pairs / max(1, adjacent_pairs),
        "n_recordings_sampled": len(recording_counts),
        "top_sampled_recordings": [
            {"recording_id": rid, "samples": int(count)}
            for rid, count in recording_counts.most_common(10)
        ],
        "eligible_recordings": eligible_recordings,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=REPO_ROOT / "data/brainsets/ibl_bwm")
    parser.add_argument("--manifest", type=Path, default=REPO_ROOT / "manifests/ibl_bwm_region_matched_support80_best6.json")
    parser.add_argument("--holdout", nargs="*", default=["CSH_ZAD_019"])
    parser.add_argument("--target-mode", default="stimulus_side", choices=["choice", "stimulus_side", "feedback", "prior_side"])
    parser.add_argument("--region-granularity", default="parent", choices=["fine", "parent", "grandparent"])
    parser.add_argument("--region-label-control", default="none", choices=["none", "shuffle", "within_recording_shuffle"])
    parser.add_argument("--window-len", type=float, default=1.0)
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--n-batches", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--samplings", nargs="+", default=["uniform", "target_balanced", "recording_target_balanced"])
    parser.add_argument("--out-json", type=Path, default=REPO_ROOT / "docs/csh_batch_sampling_contrast_audit.json")
    parser.add_argument("--out-md", type=Path, default=REPO_ROOT / "docs/csh_batch_sampling_contrast_audit.md")
    return parser.parse_args()


def render_markdown(report: dict) -> str:
    lines = [
        "# CSH Batch Sampling Contrast Audit",
        "",
        (
            "No-spend sampler audit for recording-local objectives. A recording-local "
            "ranking loss needs batches that contain at least one same-recording "
            "target-0/target-1 pair."
        ),
        "",
        f"Holdout: `{', '.join(report['holdout'])}`",
        f"Train trials: `{report['n_train_trials']}` across `{report['n_train_recordings']}` recordings",
        f"Eligible recordings with both targets: `{report['n_eligible_recordings']}/{report['n_train_recordings']}`",
        "",
        "| sampler | batch_size | target1_fraction | rankable_batch_fraction | mean_rankable_pairs | same_recording_adjacent_pairs | sampled_recordings |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["samplers"]:
        lines.append(
            "| "
            f"{row['batch_sampling']} | {row['batch_size']} | "
            f"{row['target1_fraction']:.3f} | "
            f"{row['rankable_batch_fraction']:.3f} | "
            f"{row['mean_rankable_pairs_per_batch']:.3f} | "
            f"{row['same_recording_adjacent_pair_fraction']:.3f} | "
            f"{row['n_recordings_sampled']} |"
        )
    lines += [
        "",
        "Decision rule:",
        "",
        (
            "Promote only samplers that make the recording-local loss active in almost "
            "every batch, then require the local probe matrix to pass centered AUC, "
            "bidirectional target-class improvement, and recording support before any "
            "RunPod launch."
        ),
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    ds = Dataset(dataset_dir=args.data_dir, keep_files_open=True)
    selected_recording_ids = select_recording_ids(ds, args.manifest, args.data_dir)
    vocab = build_vocab(ds, args.region_granularity, selected_recording_ids)
    vocab = apply_region_label_control(vocab, args.region_label_control, args.seed)
    split = split_recordings_by_subject(vocab["subject_by_rid"], args.holdout)
    train_trials = build_trial_samples(vocab["recs"], split.train_rids, args.window_len, args.target_mode)
    by_recording_target = trial_indices_by_recording_target(train_trials)
    eligible = {
        rid: targets
        for rid, targets in by_recording_target.items()
        if targets.get(0) and targets.get(1)
    }
    samplers = [
        batch_contrast_summary(
            train_trials,
            batch_sampling=sampling,
            batch_size=args.batch_size,
            n_batches=args.n_batches,
            seed=args.seed,
        )
        for sampling in args.samplings
    ]
    report = {
        "holdout": split.holdout_subjects,
        "train_subjects": split.train_subjects,
        "target_mode": args.target_mode,
        "region_granularity": args.region_granularity,
        "region_label_control": args.region_label_control,
        "window_len": args.window_len,
        "n_train_trials": len(train_trials),
        "n_train_recordings": len(by_recording_target),
        "n_eligible_recordings": len(eligible),
        "samplers": samplers,
    }
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text(render_markdown(report))
    print(f"wrote {args.out_json}")
    print(f"wrote {args.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
