"""Decompose the strongest shared-family model-free near miss by recording."""
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
from audit_model_free_positive_holdouts import recording_target_rows  # noqa: E402
from audit_model_free_region_signal import evaluate_feature_set, paired_improvement, per_recording_auc  # noqa: E402
from audit_shared_family_target_control_gate import precompute_target_mode  # noqa: E402
from train import build_vocab, select_recording_ids  # noqa: E402


def target_feature_contrast(features: np.ndarray, labels: np.ndarray) -> dict:
    target0 = labels <= 0
    target1 = labels > 0
    target0_mean = float(np.mean(features[target0])) if np.any(target0) else float("nan")
    target1_mean = float(np.mean(features[target1])) if np.any(target1) else float("nan")
    return {
        "target0_mean": target0_mean,
        "target1_mean": target1_mean,
        "target1_minus_target0": target1_mean - target0_mean,
    }


def recording_interpretation(row: dict, *, min_target_improvement: float) -> str:
    target0 = row["target0_improved"]
    target1 = row["target1_improved"]
    if target0 >= min_target_improvement and target1 >= min_target_improvement:
        return "bidirectional"
    if target0 >= min_target_improvement:
        return "target0_only"
    if target1 >= min_target_improvement:
        return "target1_only"
    return "neither_target"


def recording_rows(
    *,
    true_scores: np.ndarray,
    shuffle_scores: np.ndarray,
    total_scores: np.ndarray,
    labels: np.ndarray,
    recording_ids: list[str],
    true_features: np.ndarray,
    shuffle_features: np.ndarray,
    min_target_improvement: float,
) -> list[dict]:
    true_auc = per_recording_auc(true_scores, labels, recording_ids)
    shuffle_auc = per_recording_auc(shuffle_scores, labels, recording_ids)
    total_auc = per_recording_auc(total_scores, labels, recording_ids)
    target_rows = {
        row["recording"]: row
        for row in recording_target_rows(true_scores, shuffle_scores, labels, recording_ids)
    }
    rows = []
    for rid in sorted(target_rows):
        mask = np.asarray([value == rid for value in recording_ids], dtype=bool)
        row = dict(target_rows[rid])
        true_contrast = target_feature_contrast(true_features[mask], labels[mask])
        shuffle_contrast = target_feature_contrast(shuffle_features[mask], labels[mask])
        row.update({
            "true_auc": true_auc[rid],
            "shuffle_auc": shuffle_auc[rid],
            "total_auc": total_auc[rid],
            "true_minus_shuffle_auc": true_auc[rid] - shuffle_auc[rid],
            "true_minus_total_auc": true_auc[rid] - total_auc[rid],
            "true_feature_target1_minus_target0": true_contrast["target1_minus_target0"],
            "shuffle_feature_target1_minus_target0": shuffle_contrast["target1_minus_target0"],
            "feature_contrast_delta": (
                true_contrast["target1_minus_target0"]
                - shuffle_contrast["target1_minus_target0"]
            ),
        })
        row["interpretation"] = recording_interpretation(row, min_target_improvement=min_target_improvement)
        rows.append(row)
    return sorted(
        rows,
        key=lambda row: (
            row["interpretation"] == "bidirectional",
            row["target0_improved"],
            row["target1_improved"],
            row["true_minus_shuffle_auc"],
        ),
        reverse=True,
    )


def summarize(recordings: list[dict], *, min_target_improvement: float) -> dict:
    counts: dict[str, int] = {}
    for row in recordings:
        counts[row["interpretation"]] = counts.get(row["interpretation"], 0) + 1
    bidirectional = [row for row in recordings if row["interpretation"] == "bidirectional"]
    target1_positive = [row for row in recordings if row["target1_improved"] >= min_target_improvement]
    target0_positive = [row for row in recordings if row["target0_improved"] >= min_target_improvement]
    return {
        "n_recordings": len(recordings),
        "n_bidirectional_recordings": len(bidirectional),
        "n_target0_positive_recordings": len(target0_positive),
        "n_target1_positive_recordings": len(target1_positive),
        "interpretation_counts": dict(sorted(counts.items())),
        "decision": (
            "recording_local_bidirectional_near_miss"
            if len(bidirectional) >= 2 else "one_sided_target1_recording_effect"
        ),
    }


def render_markdown(report: dict) -> str:
    summary = report["summary"]
    lines = [
        "# Shared-Family Near-Miss Audit",
        "",
        (
            "Decomposes the strongest shared-family target/control row by recording "
            "to decide whether it is a plausible training trigger or a one-sided "
            "recording-local artifact."
        ),
        "",
        f"- target: `{report['target_mode']}`",
        f"- family: `{report['family']}`",
        f"- holdout: `{report['holdout']}`",
        f"- bidirectional recordings: `{summary['n_bidirectional_recordings']}/{summary['n_recordings']}`",
        f"- target0-positive recordings: `{summary['n_target0_positive_recordings']}/{summary['n_recordings']}`",
        f"- target1-positive recordings: `{summary['n_target1_positive_recordings']}/{summary['n_recordings']}`",
        f"- decision: `{summary['decision']}`",
        "",
        "| recording | interpretation | target0 | target1 | true-shuffle AUC | true-total AUC | feature contrast delta | trials |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["recordings"]:
        lines.append(
            f"| {row['recording']} | {row['interpretation']} | "
            f"{row['target0_improved']:.3f} | {row['target1_improved']:.3f} | "
            f"{row['true_minus_shuffle_auc']:+.3f} | {row['true_minus_total_auc']:+.3f} | "
            f"{row['feature_contrast_delta']:+.3f} | {row['n_trials']} |"
        )
    lines += [
        "",
        "## Decision",
        "",
        (
            "Do not promote this near miss to GPU training unless the failure is "
            "recording-local and bidirectional. Here the effect is mostly target1-only: "
            "the anatomical family helps the target1 true-class score in every held-out "
            "recording, but target0 clears the gate in only one recording."
        ),
        "",
    ]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=REPO_ROOT / "data/brainsets/ibl_bwm")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=REPO_ROOT / "manifests/ibl_bwm_region_matched_candidates_s3_present_support80_hdf5_scored.json",
    )
    parser.add_argument("--target-mode", default="choice")
    parser.add_argument("--family", default="fiber_tracts")
    parser.add_argument("--holdout", default="CSH_ZAD_019")
    parser.add_argument("--feature-mode", default="recording_centered")
    parser.add_argument("--region-granularity", default="parent")
    parser.add_argument("--window-len", type=float, default=1.0)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--l2", type=float, default=10.0)
    parser.add_argument("--min-target-improvement", type=float, default=0.55)
    parser.add_argument("--out-json", type=Path, default=REPO_ROOT / "docs/shared_family_choice_fiber_csh_near_miss.json")
    parser.add_argument("--out-md", type=Path, default=REPO_ROOT / "docs/shared_family_choice_fiber_csh_near_miss.md")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ds = Dataset(dataset_dir=args.data_dir, keep_files_open=True)
    selected_rids = select_recording_ids(ds, args.manifest, args.data_dir)
    vocab = build_vocab(ds, args.region_granularity, selected_rids)
    payload = precompute_target_mode(
        ds=ds,
        vocab=vocab,
        selected_rids=selected_rids,
        target_mode=args.target_mode,
        families=(args.family,),
        feature_mode=args.feature_mode,
        region_granularity=args.region_granularity,
        window_len=args.window_len,
        seed=args.seed,
    )
    subject_ids = np.asarray(payload["subject_ids"], dtype=object)
    train_mask = subject_ids != args.holdout
    eval_mask = subject_ids == args.holdout
    if args.family not in payload["family_names"]:
        raise SystemExit(f"family {args.family!r} not available in payload")
    family_idx = payload["family_names"].index(args.family)
    true = evaluate_feature_set(
        name=f"{args.family}_true",
        train_x=payload["family_true"][train_mask][:, [family_idx]],
        train_y=payload["y"][train_mask],
        eval_x=payload["family_true"][eval_mask][:, [family_idx]],
        eval_y=payload["y"][eval_mask],
        eval_recording_ids=[rid for rid, use in zip(payload["recording_ids"], eval_mask) if bool(use)],
        l2=args.l2,
    )
    shuffle = evaluate_feature_set(
        name=f"{args.family}_shuffle",
        train_x=payload["family_shuffle"][train_mask][:, [family_idx]],
        train_y=payload["y"][train_mask],
        eval_x=payload["family_shuffle"][eval_mask][:, [family_idx]],
        eval_y=payload["y"][eval_mask],
        eval_recording_ids=[rid for rid, use in zip(payload["recording_ids"], eval_mask) if bool(use)],
        l2=args.l2,
    )
    total = evaluate_feature_set(
        name="total_spikes",
        train_x=payload["total"][train_mask],
        train_y=payload["y"][train_mask],
        eval_x=payload["total"][eval_mask],
        eval_y=payload["y"][eval_mask],
        eval_recording_ids=[rid for rid, use in zip(payload["recording_ids"], eval_mask) if bool(use)],
        l2=args.l2,
    )
    eval_y = payload["y"][eval_mask]
    eval_recordings = [rid for rid, use in zip(payload["recording_ids"], eval_mask) if bool(use)]
    rec_rows = recording_rows(
        true_scores=true["eval_scores"],
        shuffle_scores=shuffle["eval_scores"],
        total_scores=total["eval_scores"],
        labels=eval_y,
        recording_ids=eval_recordings,
        true_features=payload["family_true"][eval_mask][:, family_idx],
        shuffle_features=payload["family_shuffle"][eval_mask][:, family_idx],
        min_target_improvement=args.min_target_improvement,
    )
    paired = paired_improvement(true["eval_scores"], shuffle["eval_scores"], eval_y)
    report = {
        "target_mode": args.target_mode,
        "family": args.family,
        "holdout": args.holdout,
        "feature_mode": args.feature_mode,
        "thresholds": {"min_target_improvement": args.min_target_improvement},
        "global": {
            "target0_improved_vs_shuffle": paired["target0_improved_fraction"],
            "target1_improved_vs_shuffle": paired["target1_improved_fraction"],
            "paired_improved_vs_shuffle": paired["improved_fraction"],
            "eval_centered_auc": true["eval_centered_auc"],
            "shuffle_centered_auc": shuffle["eval_centered_auc"],
            "total_centered_auc": total["eval_centered_auc"],
            "centered_delta_vs_shuffle": true["eval_centered_auc"] - shuffle["eval_centered_auc"],
            "centered_delta_vs_total": true["eval_centered_auc"] - total["eval_centered_auc"],
        },
        "summary": summarize(rec_rows, min_target_improvement=args.min_target_improvement),
        "recordings": rec_rows,
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
