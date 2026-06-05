"""Exploratory two-region composites for the extreme response-latency target."""
from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "vendor" / "torch_brain"))

from audit_extreme_quantile_interpretable_region_filter import (  # noqa: E402
    NON_SPECIFIC_REGIONS,
    is_interpretable_region,
)
from audit_extreme_quantile_region_specificity import summarize_rows as summarize_single_region_rows  # noqa: E402
from audit_extreme_quantile_target_family_gate import build_extreme_trial_samples  # noqa: E402
from audit_model_free_positive_holdouts import recording_target_rows  # noqa: E402
from audit_model_free_recording_bidirectional_gate import recording_bidirectional_summary  # noqa: E402
from audit_model_free_region_signal import (  # noqa: E402
    build_region_vocab,
    evaluate_feature_set,
    make_feature_matrix,
    paired_improvement,
    recording_region_unit_fractions,
    total_spike_feature,
    transform_region_features,
)
from audit_shared_family_target_control_gate import family_gate_decision  # noqa: E402
from torch_brain.dataset import Dataset  # noqa: E402
from train import build_vocab, select_recording_ids  # noqa: E402


def pair_label(left: str, right: str) -> str:
    return f"{left}+{right}"


def select_regions_from_source(
    source: Path,
    *,
    top_n_regions: int,
    excluded_regions: set[str] | frozenset[str] = NON_SPECIFIC_REGIONS,
) -> list[str]:
    payload = json.loads(source.read_text())
    rows = [
        row for row in payload.get("rows", [])
        if is_interpretable_region(row.get("region", ""), excluded_regions)
    ]
    ranked = summarize_single_region_rows(rows)["top_rows"]
    selected = []
    for row in ranked:
        region = row["region"]
        if region not in selected:
            selected.append(region)
        if len(selected) >= top_n_regions:
            break
    return selected


def region_pairs(regions: list[str]) -> list[tuple[str, str]]:
    return list(itertools.combinations(regions, 2))


def evaluate_region_pair_row(
    *,
    target_mode: str,
    regions: tuple[str, str],
    holdout: str,
    region_indices: tuple[int, int],
    train_region_true: np.ndarray,
    eval_region_true: np.ndarray,
    train_region_shuffle: np.ndarray,
    eval_region_shuffle: np.ndarray,
    train_total: np.ndarray,
    eval_total: np.ndarray,
    train_y: np.ndarray,
    eval_y: np.ndarray,
    eval_recordings: list[str],
    l2: float,
    min_centered_delta: float,
    min_total_delta: float,
    min_target_improvement: float,
    min_bidirectional_recording_fraction: float,
) -> dict:
    left_idx, right_idx = region_indices
    train_true_pair = train_region_true[:, [left_idx]] + train_region_true[:, [right_idx]]
    eval_true_pair = eval_region_true[:, [left_idx]] + eval_region_true[:, [right_idx]]
    train_shuffle_pair = train_region_shuffle[:, [left_idx]] + train_region_shuffle[:, [right_idx]]
    eval_shuffle_pair = eval_region_shuffle[:, [left_idx]] + eval_region_shuffle[:, [right_idx]]
    label = pair_label(*regions)
    true = evaluate_feature_set(
        name=f"{label}_true",
        train_x=train_true_pair,
        train_y=train_y,
        eval_x=eval_true_pair,
        eval_y=eval_y,
        eval_recording_ids=eval_recordings,
        l2=l2,
    )
    shuffle = evaluate_feature_set(
        name=f"{label}_shuffle",
        train_x=train_shuffle_pair,
        train_y=train_y,
        eval_x=eval_shuffle_pair,
        eval_y=eval_y,
        eval_recording_ids=eval_recordings,
        l2=l2,
    )
    total = evaluate_feature_set(
        name="total_spikes",
        train_x=train_total,
        train_y=train_y,
        eval_x=eval_total,
        eval_y=eval_y,
        eval_recording_ids=eval_recordings,
        l2=l2,
    )
    paired_shuffle = paired_improvement(true["eval_scores"], shuffle["eval_scores"], eval_y)
    paired_total = paired_improvement(true["eval_scores"], total["eval_scores"], eval_y)
    rec_target_rows = recording_target_rows(true["eval_scores"], shuffle["eval_scores"], eval_y, eval_recordings)
    bidirectional = recording_bidirectional_summary(rec_target_rows, min_target_improvement=min_target_improvement)
    row = {
        "target_mode": target_mode,
        "region_pair": label,
        "regions": list(regions),
        "holdout": holdout,
        "train_nonzero_fraction": float(np.mean(train_true_pair[:, 0] > 0.0)),
        "eval_nonzero_fraction": float(np.mean(eval_true_pair[:, 0] > 0.0)),
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
        "n_recordings": bidirectional["n_evaluable_recordings"],
        "n_bidirectional_recordings": bidirectional["n_bidirectional_recordings"],
        "bidirectional_recording_fraction": bidirectional["bidirectional_recording_fraction"],
        "recording_target_rows": rec_target_rows,
    }
    row["decision"] = family_gate_decision(
        row,
        min_centered_delta=min_centered_delta,
        min_total_delta=min_total_delta,
        min_target_improvement=min_target_improvement,
        min_bidirectional_recording_fraction=min_bidirectional_recording_fraction,
    )
    return row


def summarize_rows(rows: list[dict]) -> dict:
    candidates = [row for row in rows if row["decision"] == "candidate"]
    top_rows = sorted(
        rows,
        key=lambda row: (
            row["decision"] == "candidate",
            row["n_bidirectional_recordings"],
            row["bidirectional_recording_fraction"],
            row["centered_delta_vs_shuffle"],
            min(row["target0_improved_vs_shuffle"], row["target1_improved_vs_shuffle"]),
            row["eval_nonzero_fraction"],
        ),
        reverse=True,
    )
    return {
        "n_rows": len(rows),
        "n_region_pairs": len({row["region_pair"] for row in rows}),
        "n_holdouts": len({row["holdout"] for row in rows}),
        "n_candidates": len(candidates),
        "n_positive_centered_delta": sum(1 for row in rows if row["centered_delta_vs_shuffle"] > 0.0),
        "max_bidirectional_recording_fraction": max(
            (row["bidirectional_recording_fraction"] for row in rows),
            default=0.0,
        ),
        "candidate_rows": [
            {"target_mode": row["target_mode"], "region_pair": row["region_pair"], "holdout": row["holdout"]}
            for row in candidates
        ],
        "top_rows": top_rows[:20],
        "decision": (
            "extreme_quantile_interpretable_region_pair_candidate"
            if candidates
            else "no_extreme_quantile_interpretable_region_pair_candidate"
        ),
        "gpu_training_ready": False,
        "next_action": (
            "Validate any exploratory pair across shuffle seeds and a prospective "
            "manifest before GPU training."
            if candidates
            else "Do not train: no interpretable two-region composite passes the strict local gate."
        ),
    }


def render_markdown(report: dict) -> str:
    summary = report["summary"]
    lines = [
        "# Extreme-Quantile Interpretable Region Pair Scan",
        "",
        (
            "Exploratory scan of conservative two-region summed composites for the "
            "response-latency extreme target. Candidate rows still require shuffle-seed "
            "and prospective-manifest validation before any GPU run."
        ),
        "",
        f"- target: `{report['target_mode']}`",
        f"- quantiles: `{report['quantiles']['low']:.2f}` / `{report['quantiles']['high']:.2f}`",
        f"- selected regions: `{', '.join(report['selected_regions'])}`",
        f"- region pairs: `{summary['n_region_pairs']}`",
        f"- holdouts: `{summary['n_holdouts']}`",
        f"- candidates: `{summary['n_candidates']}`",
        f"- positive centered-delta rows: `{summary['n_positive_centered_delta']}`",
        f"- decision: `{summary['decision']}`",
        f"- gpu training ready: `{summary['gpu_training_ready']}`",
        "",
        "## Top Rows",
        "",
        "| pair | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs | eval nonzero |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary["top_rows"][:16]:
        lines.append(
            f"| {row['region_pair']} | {row['holdout']} | {row['decision']} | "
            f"{row['centered_delta_vs_shuffle']:+.3f} | {row['centered_delta_vs_total']:+.3f} | "
            f"{row['target0_improved_vs_shuffle']:.3f} | {row['target1_improved_vs_shuffle']:.3f} | "
            f"{row['n_bidirectional_recordings']}/{row['n_recordings']} | "
            f"{row['eval_nonzero_fraction']:.3f} |"
        )
    lines += [
        "",
        "## Decision",
        "",
        summary["next_action"],
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
    parser.add_argument(
        "--source-json",
        type=Path,
        default=REPO_ROOT / "docs/extreme_quantile_region_specificity.json",
    )
    parser.add_argument("--target", default="response_latency_extreme")
    parser.add_argument("--low-quantile", type=float, default=0.20)
    parser.add_argument("--high-quantile", type=float, default=0.80)
    parser.add_argument("--feature-mode", default="recording_centered", choices=["counts", "fractions", "recording_centered", "unit_residuals"])
    parser.add_argument("--region-granularity", default="parent", choices=["fine", "parent", "grandparent"])
    parser.add_argument("--top-n-regions", type=int, default=12)
    parser.add_argument("--window-len", type=float, default=1.0)
    parser.add_argument("--pre-window-len", type=float, default=0.5)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--l2", type=float, default=10.0)
    parser.add_argument("--min-centered-delta", type=float, default=0.0)
    parser.add_argument("--min-total-delta", type=float, default=0.0)
    parser.add_argument("--min-target-improvement", type=float, default=0.55)
    parser.add_argument("--min-bidirectional-recording-fraction", type=float, default=0.75)
    parser.add_argument(
        "--out-json",
        type=Path,
        default=REPO_ROOT / "docs/extreme_quantile_interpretable_region_pair_scan.json",
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=REPO_ROOT / "docs/extreme_quantile_interpretable_region_pair_scan.md",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    selected_regions = select_regions_from_source(args.source_json, top_n_regions=args.top_n_regions)
    ds = Dataset(dataset_dir=args.data_dir, keep_files_open=True)
    selected_rids = select_recording_ids(ds, args.manifest, args.data_dir)
    vocab = build_vocab(ds, args.region_granularity, selected_rids)
    trials = build_extreme_trial_samples(
        vocab["recs"],
        selected_rids,
        target_name=args.target,
        low_quantile=args.low_quantile,
        high_quantile=args.high_quantile,
        window_len=args.window_len,
        pre_window_len=args.pre_window_len,
    )
    all_regions = build_region_vocab(vocab["recs"], selected_rids, args.region_granularity)
    region_to_index = {region: index for index, region in enumerate(all_regions)}
    missing_regions = [region for region in selected_regions if region not in region_to_index]
    if missing_regions:
        raise ValueError(f"selected regions not present in feature vocab: {missing_regions}")
    true_x, y, recording_ids = make_feature_matrix(
        ds,
        vocab["recs"],
        trials,
        regions=all_regions,
        region_granularity=args.region_granularity,
        region_control="none",
        seed=args.seed,
        window_len=args.window_len,
    )
    shuffle_x, _shuffle_y, _shuffle_recordings = make_feature_matrix(
        ds,
        vocab["recs"],
        trials,
        regions=all_regions,
        region_granularity=args.region_granularity,
        region_control="within_recording_shuffle",
        seed=args.seed,
        window_len=args.window_len,
    )
    true_unit_fractions = recording_region_unit_fractions(
        vocab["recs"],
        selected_rids,
        regions=all_regions,
        region_granularity=args.region_granularity,
        region_control="none",
        seed=args.seed,
    )
    shuffle_unit_fractions = recording_region_unit_fractions(
        vocab["recs"],
        selected_rids,
        regions=all_regions,
        region_granularity=args.region_granularity,
        region_control="within_recording_shuffle",
        seed=args.seed,
    )
    true_model_x = transform_region_features(
        true_x,
        args.feature_mode,
        recording_ids=recording_ids,
        unit_region_fractions=true_unit_fractions,
    )
    shuffle_model_x = transform_region_features(
        shuffle_x,
        args.feature_mode,
        recording_ids=recording_ids,
        unit_region_fractions=shuffle_unit_fractions,
    )
    subject_ids = np.asarray([vocab["subject_by_rid"][rid] for rid in recording_ids], dtype=object)
    holdouts = sorted(set(subject_ids))
    total = total_spike_feature(true_x)
    rows = []
    for holdout in holdouts:
        train_mask = subject_ids != holdout
        eval_mask = subject_ids == holdout
        if not np.any(train_mask) or not np.any(eval_mask):
            continue
        if len(set(y[train_mask])) < 2 or len(set(y[eval_mask])) < 2:
            continue
        eval_recordings = [rid for rid, use in zip(recording_ids, eval_mask) if bool(use)]
        for left, right in region_pairs(selected_regions):
            rows.append(evaluate_region_pair_row(
                target_mode=args.target,
                regions=(left, right),
                holdout=str(holdout),
                region_indices=(region_to_index[left], region_to_index[right]),
                train_region_true=true_model_x[train_mask],
                eval_region_true=true_model_x[eval_mask],
                train_region_shuffle=shuffle_model_x[train_mask],
                eval_region_shuffle=shuffle_model_x[eval_mask],
                train_total=total[train_mask],
                eval_total=total[eval_mask],
                train_y=y[train_mask],
                eval_y=y[eval_mask],
                eval_recordings=eval_recordings,
                l2=args.l2,
                min_centered_delta=args.min_centered_delta,
                min_total_delta=args.min_total_delta,
                min_target_improvement=args.min_target_improvement,
                min_bidirectional_recording_fraction=args.min_bidirectional_recording_fraction,
            ))
    report = {
        "manifest": str(args.manifest),
        "source_json": str(args.source_json),
        "target_mode": args.target,
        "feature_mode": args.feature_mode,
        "region_granularity": args.region_granularity,
        "selected_regions": selected_regions,
        "quantiles": {"low": args.low_quantile, "high": args.high_quantile},
        "thresholds": {
            "min_centered_delta": args.min_centered_delta,
            "min_total_delta": args.min_total_delta,
            "min_target_improvement": args.min_target_improvement,
            "min_bidirectional_recording_fraction": args.min_bidirectional_recording_fraction,
        },
        "summary": summarize_rows(rows),
        "rows": rows,
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
