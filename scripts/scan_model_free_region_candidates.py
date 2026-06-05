"""Scan single-region model-free candidates for anatomical transfer.

The full parent-region vector failed the model-free audit. This script asks a
narrower question: does any individual parent-region spike-count feature beat a
within-recording shuffled counterpart and a total-spike baseline on held-out
CSH recordings with bidirectional target-class support?
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "vendor" / "torch_brain"))

from torch_brain.dataset import Dataset  # noqa: E402
from audit_model_free_region_signal import (  # noqa: E402
    build_region_vocab,
    evaluate_feature_set,
    make_feature_matrix,
    paired_improvement,
    per_recording_auc,
    total_spike_feature,
)
from train import (  # noqa: E402
    build_trial_samples,
    build_vocab,
    select_recording_ids,
    split_recordings_by_subject,
)


def candidate_outcome(row: dict, *, min_centered_delta: float, min_target_improvement: float) -> str:
    if row["eval_nonzero_fraction"] <= 0.0:
        return "reject: absent in eval"
    if row["centered_delta_vs_shuffle"] < min_centered_delta:
        return "reject: shuffle"
    if row["centered_delta_vs_total"] < min_centered_delta:
        return "reject: total baseline"
    if row["target0_improved_vs_shuffle"] < min_target_improvement:
        return "reject: target0"
    if row["target1_improved_vs_shuffle"] < min_target_improvement:
        return "reject: target1"
    if row["positive_recordings_vs_shuffle"] < 3:
        return "reject: recording support"
    return "candidate"


def scan_candidates(
    *,
    regions: list[str],
    train_true_x: np.ndarray,
    train_shuffle_x: np.ndarray,
    train_y: np.ndarray,
    eval_true_x: np.ndarray,
    eval_shuffle_x: np.ndarray,
    eval_y: np.ndarray,
    eval_recording_ids: list[str],
    l2: float,
    min_centered_delta: float,
    min_target_improvement: float,
) -> list[dict]:
    total = evaluate_feature_set(
        name="total_spikes",
        train_x=total_spike_feature(train_true_x),
        train_y=train_y,
        eval_x=total_spike_feature(eval_true_x),
        eval_y=eval_y,
        eval_recording_ids=eval_recording_ids,
        l2=l2,
    )
    rows = []
    for idx, region in enumerate(regions):
        true = evaluate_feature_set(
            name=f"{region}_true",
            train_x=train_true_x[:, [idx]],
            train_y=train_y,
            eval_x=eval_true_x[:, [idx]],
            eval_y=eval_y,
            eval_recording_ids=eval_recording_ids,
            l2=l2,
        )
        shuffle = evaluate_feature_set(
            name=f"{region}_shuffle",
            train_x=train_shuffle_x[:, [idx]],
            train_y=train_y,
            eval_x=eval_shuffle_x[:, [idx]],
            eval_y=eval_y,
            eval_recording_ids=eval_recording_ids,
            l2=l2,
        )
        paired_shuffle = paired_improvement(true["eval_scores"], shuffle["eval_scores"], eval_y)
        paired_total = paired_improvement(true["eval_scores"], total["eval_scores"], eval_y)
        true_recording_auc = per_recording_auc(true["eval_scores"], eval_y, eval_recording_ids)
        shuffle_recording_auc = per_recording_auc(shuffle["eval_scores"], eval_y, eval_recording_ids)
        recording_deltas = {
            rid: true_recording_auc[rid] - shuffle_recording_auc[rid]
            for rid in sorted(true_recording_auc)
        }
        row = {
            "region": region,
            "train_nonzero_fraction": float(np.mean(train_true_x[:, idx] > 0.0)),
            "eval_nonzero_fraction": float(np.mean(eval_true_x[:, idx] > 0.0)),
            "train_auc": true["train_auc"],
            "eval_auc": true["eval_auc"],
            "eval_centered_auc": true["eval_centered_auc"],
            "shuffle_centered_auc": shuffle["eval_centered_auc"],
            "total_centered_auc": total["eval_centered_auc"],
            "centered_delta_vs_shuffle": true["eval_centered_auc"] - shuffle["eval_centered_auc"],
            "centered_delta_vs_total": true["eval_centered_auc"] - total["eval_centered_auc"],
            "paired_improved_vs_shuffle": paired_shuffle["improved_fraction"],
            "target0_improved_vs_shuffle": paired_shuffle["target0_improved_fraction"],
            "target1_improved_vs_shuffle": paired_shuffle["target1_improved_fraction"],
            "paired_improved_vs_total": paired_total["improved_fraction"],
            "target0_improved_vs_total": paired_total["target0_improved_fraction"],
            "target1_improved_vs_total": paired_total["target1_improved_fraction"],
            "positive_recordings_vs_shuffle": int(sum(delta > 0.0 for delta in recording_deltas.values())),
            "n_recordings": len(recording_deltas),
            "recording_deltas_vs_shuffle": recording_deltas,
        }
        row["outcome"] = candidate_outcome(
            row,
            min_centered_delta=min_centered_delta,
            min_target_improvement=min_target_improvement,
        )
        rows.append(row)
    return sorted(rows, key=region_sort_key, reverse=True)


def region_sort_key(row: dict) -> tuple:
    """Rank usable region features before absent-in-eval artifacts."""
    return (
        row["outcome"] == "candidate",
        row["eval_nonzero_fraction"] > 0.0,
        row["centered_delta_vs_shuffle"],
        row["centered_delta_vs_total"],
        row["positive_recordings_vs_shuffle"],
    )


def render_markdown(report: dict) -> str:
    lines = [
        "# CSH Model-Free Region Candidate Scan",
        "",
        (
            "Single-parent-region ridge scans against within-recording shuffled labels "
            "and total-spike baseline. This is a no-spend feature/control redesign gate."
        ),
        "",
        f"Holdout: `{', '.join(report['holdout'])}`",
        f"Regions scanned: `{report['n_regions']}`",
        f"Candidates: `{report['n_candidates']}`",
        "",
        "| region | outcome | eval_centered_AUC | delta_vs_shuffle | delta_vs_total | target0 | target1 | recordings | eval_nonzero |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["top_regions"]:
        lines.append(
            "| "
            f"{row['region']} | {row['outcome']} | {row['eval_centered_auc']:.3f} | "
            f"{row['centered_delta_vs_shuffle']:+.3f} | {row['centered_delta_vs_total']:+.3f} | "
            f"{row['target0_improved_vs_shuffle']:.3f} | {row['target1_improved_vs_shuffle']:.3f} | "
            f"{row['positive_recordings_vs_shuffle']}/{row['n_recordings']} | "
            f"{row['eval_nonzero_fraction']:.3f} |"
        )
    lines += [
        "",
        "Decision:",
        "",
        report["decision"],
        "",
    ]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=REPO_ROOT / "data/brainsets/ibl_bwm")
    parser.add_argument("--manifest", type=Path, default=REPO_ROOT / "manifests/ibl_bwm_region_matched_support80_best6.json")
    parser.add_argument("--holdout", nargs="*", default=["CSH_ZAD_019"])
    parser.add_argument("--target-mode", default="stimulus_side", choices=["choice", "stimulus_side", "feedback", "prior_side"])
    parser.add_argument("--region-granularity", default="parent", choices=["fine", "parent", "grandparent"])
    parser.add_argument("--window-len", type=float, default=1.0)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--l2", type=float, default=10.0)
    parser.add_argument("--min-centered-delta", type=float, default=0.01)
    parser.add_argument("--min-target-improvement", type=float, default=0.55)
    parser.add_argument("--top-k", type=int, default=20)
    parser.add_argument("--out-json", type=Path, default=REPO_ROOT / "docs/csh_model_free_region_candidate_scan.json")
    parser.add_argument("--out-md", type=Path, default=REPO_ROOT / "docs/csh_model_free_region_candidate_scan.md")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ds = Dataset(dataset_dir=args.data_dir, keep_files_open=True)
    selected_recording_ids = select_recording_ids(ds, args.manifest, args.data_dir)
    vocab = build_vocab(ds, args.region_granularity, selected_recording_ids)
    split = split_recordings_by_subject(vocab["subject_by_rid"], args.holdout)
    train_trials = build_trial_samples(vocab["recs"], split.train_rids, args.window_len, args.target_mode)
    eval_trials = build_trial_samples(vocab["recs"], split.eval_rids, args.window_len, args.target_mode)
    regions = build_region_vocab(vocab["recs"], split.train_rids + split.eval_rids, args.region_granularity)
    train_true_x, train_y, _ = make_feature_matrix(
        ds,
        vocab["recs"],
        train_trials,
        regions=regions,
        region_granularity=args.region_granularity,
        region_control="none",
        seed=args.seed,
        window_len=args.window_len,
    )
    eval_true_x, eval_y, eval_recording_ids = make_feature_matrix(
        ds,
        vocab["recs"],
        eval_trials,
        regions=regions,
        region_granularity=args.region_granularity,
        region_control="none",
        seed=args.seed,
        window_len=args.window_len,
    )
    train_shuffle_x, _train_y, _ = make_feature_matrix(
        ds,
        vocab["recs"],
        train_trials,
        regions=regions,
        region_granularity=args.region_granularity,
        region_control="within_recording_shuffle",
        seed=args.seed,
        window_len=args.window_len,
    )
    eval_shuffle_x, _eval_y, _ = make_feature_matrix(
        ds,
        vocab["recs"],
        eval_trials,
        regions=regions,
        region_granularity=args.region_granularity,
        region_control="within_recording_shuffle",
        seed=args.seed,
        window_len=args.window_len,
    )
    rows = scan_candidates(
        regions=regions,
        train_true_x=train_true_x,
        train_shuffle_x=train_shuffle_x,
        train_y=train_y,
        eval_true_x=eval_true_x,
        eval_shuffle_x=eval_shuffle_x,
        eval_y=eval_y,
        eval_recording_ids=eval_recording_ids,
        l2=args.l2,
        min_centered_delta=args.min_centered_delta,
        min_target_improvement=args.min_target_improvement,
    )
    candidates = [row for row in rows if row["outcome"] == "candidate"]
    decision = (
        "At least one single-region model-free candidate passed the strict local gate; "
        "next step is a bounded multi-holdout model-free confirmation before GPU spend."
        if candidates
        else (
            "No single parent region passed the model-free promotion gate. The next no-spend "
            "step should test predefined region-family aggregates or alternative targets, not "
            "a GPU model run."
        )
    )
    report = {
        "holdout": split.holdout_subjects,
        "train_subjects": split.train_subjects,
        "target_mode": args.target_mode,
        "region_granularity": args.region_granularity,
        "window_len": args.window_len,
        "seed": args.seed,
        "l2": args.l2,
        "thresholds": {
            "min_centered_delta": args.min_centered_delta,
            "min_target_improvement": args.min_target_improvement,
            "min_positive_recordings": 3,
        },
        "n_train_trials": len(train_trials),
        "n_eval_trials": len(eval_trials),
        "n_regions": len(regions),
        "n_candidates": len(candidates),
        "decision": decision,
        "top_regions": rows[: args.top_k],
        "all_regions": rows,
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
