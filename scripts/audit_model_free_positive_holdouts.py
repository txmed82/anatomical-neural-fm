"""Inspect weak positive model-free holdouts for target/recording artifacts."""
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
    interpret,
    make_feature_matrix,
    summarize_results,
    total_spike_feature,
    zscore_train_eval,
)
from train import (  # noqa: E402
    build_trial_samples,
    build_vocab,
    select_recording_ids,
    split_recordings_by_subject,
)


def fit_region_weights(train_x: np.ndarray, train_y: np.ndarray, *, l2: float) -> np.ndarray:
    y = np.where(train_y > 0, 1.0, -1.0).astype(np.float64)
    train_z, _ = zscore_train_eval(train_x.astype(np.float64), train_x.astype(np.float64))
    train_design = np.concatenate([train_z, np.ones((train_z.shape[0], 1), dtype=np.float64)], axis=1)
    penalty = np.eye(train_design.shape[1], dtype=np.float64) * l2
    penalty[-1, -1] = 0.0
    weights = np.linalg.solve(train_design.T @ train_design + penalty, train_design.T @ y)
    return weights[:-1]


def target_delta_summary(true_scores: np.ndarray, shuffle_scores: np.ndarray, labels: np.ndarray) -> dict:
    true_class_delta = np.where(labels > 0, true_scores - shuffle_scores, shuffle_scores - true_scores)
    out = {}
    for label, mask in [("target0", labels <= 0), ("target1", labels > 0)]:
        values = true_class_delta[mask]
        out[label] = {
            "n_trials": int(values.size),
            "improved_fraction": float(np.mean(values > 0.0)) if values.size else float("nan"),
            "mean_true_class_delta": float(np.mean(values)) if values.size else float("nan"),
        }
    return out


def recording_target_rows(
    true_scores: np.ndarray,
    shuffle_scores: np.ndarray,
    labels: np.ndarray,
    recording_ids: list[str],
) -> list[dict]:
    rows = []
    true_class_delta = np.where(labels > 0, true_scores - shuffle_scores, shuffle_scores - true_scores)
    for rid in sorted(set(recording_ids)):
        mask = np.asarray([value == rid for value in recording_ids], dtype=bool)
        labels_i = labels[mask]
        delta_i = true_class_delta[mask]
        target1_frac = float(np.mean(labels_i > 0)) if labels_i.size else float("nan")
        rows.append({
            "recording": rid,
            "n_trials": int(labels_i.size),
            "target1_fraction": target1_frac,
            "improved_fraction": float(np.mean(delta_i > 0.0)) if delta_i.size else float("nan"),
            "mean_true_class_delta": float(np.mean(delta_i)) if delta_i.size else float("nan"),
            "target0_improved": (
                float(np.mean(delta_i[labels_i <= 0] > 0.0))
                if np.any(labels_i <= 0) else float("nan")
            ),
            "target1_improved": (
                float(np.mean(delta_i[labels_i > 0] > 0.0))
                if np.any(labels_i > 0) else float("nan")
            ),
        })
    return rows


def top_weight_rows(regions: list[str], weights: np.ndarray, *, n: int) -> dict:
    order_pos = np.argsort(weights)[::-1][:n]
    order_neg = np.argsort(weights)[:n]
    return {
        "positive": [{"region": regions[i], "weight": float(weights[i])} for i in order_pos],
        "negative": [{"region": regions[i], "weight": float(weights[i])} for i in order_neg],
    }


def audit_holdout(args: argparse.Namespace, holdout: str) -> dict:
    ds = Dataset(dataset_dir=args.data_dir, keep_files_open=True)
    selected_recording_ids = select_recording_ids(ds, args.manifest, args.data_dir)
    vocab = build_vocab(ds, args.region_granularity, selected_recording_ids)
    split = split_recordings_by_subject(vocab["subject_by_rid"], [holdout])
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
    eval_true_x, eval_y, eval_recordings = make_feature_matrix(
        ds,
        vocab["recs"],
        eval_trials,
        regions=regions,
        region_granularity=args.region_granularity,
        region_control="none",
        seed=args.seed,
        window_len=args.window_len,
    )
    train_shuffle_x, _, _ = make_feature_matrix(
        ds,
        vocab["recs"],
        train_trials,
        regions=regions,
        region_granularity=args.region_granularity,
        region_control="within_recording_shuffle",
        seed=args.seed,
        window_len=args.window_len,
    )
    eval_shuffle_x, _, _ = make_feature_matrix(
        ds,
        vocab["recs"],
        eval_trials,
        regions=regions,
        region_granularity=args.region_granularity,
        region_control="within_recording_shuffle",
        seed=args.seed,
        window_len=args.window_len,
    )
    results = {
        "total_spikes": evaluate_feature_set(
            name="total_spikes",
            train_x=total_spike_feature(train_true_x),
            train_y=train_y,
            eval_x=total_spike_feature(eval_true_x),
            eval_y=eval_y,
            eval_recording_ids=eval_recordings,
            l2=args.l2,
        ),
        "region_true": evaluate_feature_set(
            name="region_true",
            train_x=train_true_x,
            train_y=train_y,
            eval_x=eval_true_x,
            eval_y=eval_y,
            eval_recording_ids=eval_recordings,
            l2=args.l2,
        ),
        "region_shuffle": evaluate_feature_set(
            name="region_shuffle",
            train_x=train_shuffle_x,
            train_y=train_y,
            eval_x=eval_shuffle_x,
            eval_y=eval_y,
            eval_recording_ids=eval_recordings,
            l2=args.l2,
        ),
    }
    summary = summarize_results(results, eval_y, eval_recordings)
    summary["decision"] = interpret(summary)
    true_scores = results["region_true"]["eval_scores"]
    shuffle_scores = results["region_shuffle"]["eval_scores"]
    weights = fit_region_weights(train_true_x, train_y, l2=args.l2)
    return {
        "holdout": holdout,
        "train_subjects": split.train_subjects,
        "target_mode": args.target_mode,
        "region_granularity": args.region_granularity,
        "n_train_trials": len(train_trials),
        "n_eval_trials": len(eval_trials),
        "n_regions": len(regions),
        "summary": {
            "decision": summary["decision"],
            "delta_centered_auc": summary["deltas"]["true_minus_shuffle_centered_auc"],
            "paired_true_vs_shuffle": summary["paired_true_vs_shuffle"],
            "recordings_positive_true_minus_shuffle": summary["recordings_positive_true_minus_shuffle"],
            "n_recordings": summary["n_recordings"],
        },
        "target_delta_summary": target_delta_summary(true_scores, shuffle_scores, eval_y),
        "recording_target_rows": recording_target_rows(true_scores, shuffle_scores, eval_y, eval_recordings),
        "top_region_weights": top_weight_rows(regions, weights, n=args.top_regions),
    }


def render_markdown(report: dict) -> str:
    lines = [
        "# Model-Free Positive-Holdout Mechanism Audit",
        "",
        "Focused audit for holdouts with positive centered true-minus-shuffle AUC but failed gates.",
        "",
        "| holdout | centered_delta | target0_improved | target1_improved | positive_recordings | interpretation |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for row in report["holdouts"]:
        paired = row["summary"]["paired_true_vs_shuffle"]
        interpretation = (
            "not bidirectional"
            if min(paired["target0_improved_fraction"], paired["target1_improved_fraction"]) < 0.55
            else "low recording support"
        )
        lines.append(
            f"| {row['holdout']} | {row['summary']['delta_centered_auc']:+.3f} | "
            f"{paired['target0_improved_fraction']:.3f} | {paired['target1_improved_fraction']:.3f} | "
            f"{row['summary']['recordings_positive_true_minus_shuffle']}/{row['summary']['n_recordings']} | "
            f"{interpretation} |"
        )
    for row in report["holdouts"]:
        lines += [
            "",
            f"## {row['holdout']}",
            "",
            "| recording | n_trials | target1_frac | improved | mean_delta | target0_improved | target1_improved |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
        for rec in row["recording_target_rows"]:
            lines.append(
                f"| {rec['recording']} | {rec['n_trials']} | {rec['target1_fraction']:.3f} | "
                f"{rec['improved_fraction']:.3f} | {rec['mean_true_class_delta']:+.3f} | "
                f"{rec['target0_improved']:.3f} | {rec['target1_improved']:.3f} |"
            )
        lines += [
            "",
            "Top positive region weights:",
            ", ".join(
                f"{item['region']}={item['weight']:+.3f}"
                for item in row["top_region_weights"]["positive"][:8]
            ),
            "",
            "Top negative region weights:",
            ", ".join(
                f"{item['region']}={item['weight']:+.3f}"
                for item in row["top_region_weights"]["negative"][:8]
            ),
            "",
        ]
    lines += [
        "## Decision",
        "",
        (
            "These weak positive model-free deltas are not promotable. They are either "
            "below the bidirectional target-class gate or supported by too few recordings."
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
    parser.add_argument("--holdout", nargs="+", default=["KS014", "NR_0019"])
    parser.add_argument("--target-mode", default="stimulus_side", choices=["choice", "stimulus_side", "feedback", "prior_side"])
    parser.add_argument("--region-granularity", default="parent", choices=["fine", "parent", "grandparent"])
    parser.add_argument("--window-len", type=float, default=1.0)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--l2", type=float, default=10.0)
    parser.add_argument("--top-regions", type=int, default=12)
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument("--out-md", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = {
        "manifest": str(args.manifest),
        "holdouts": [audit_holdout(args, holdout) for holdout in args.holdout],
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
