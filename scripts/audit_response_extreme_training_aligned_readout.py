"""Local training-aligned readout for the response-extreme A100 failure.

The failed A100 pilot trained learned region embeddings over the shared
parent-region feature space. This no-spend audit asks whether a closed-form
ridge readout over that same shared parent-region count space has a true-region
advantage over within-recording shuffled region labels.
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
    recording_region_unit_fractions,
    summarize_results,
    total_spike_feature,
    transform_region_features,
)
from train import (  # noqa: E402
    build_trial_samples,
    build_vocab,
    select_recording_ids,
    shared_split_regions,
    split_recordings_by_subject,
)


CASES = (
    {
        "holdout": "CSHL045",
        "target_mode": "post_error_response_extreme_25_75_le_1",
        "local_family": "broad_named_anatomy",
    },
    {
        "holdout": "NR_0019",
        "target_mode": "post_error_response_extreme_33_67_le_1",
        "local_family": "broad_named_anatomy",
    },
)
FEATURE_MODES = ("counts", "recording_centered")


def candidate_decision(summary: dict, *, min_centered_delta: float, min_target_improvement: float) -> str:
    deltas = summary["deltas"]
    paired = summary["paired_true_vs_shuffle"]
    if deltas["true_minus_shuffle_centered_auc"] < min_centered_delta:
        return "reject: shuffle"
    if deltas["true_minus_total_centered_auc"] < min_centered_delta:
        return "reject: total baseline"
    if paired["target0_improved_fraction"] < min_target_improvement:
        return "reject: target0"
    if paired["target1_improved_fraction"] < min_target_improvement:
        return "reject: target1"
    if summary["recording_support_fraction"] < 0.75:
        return "reject: recording support"
    return "candidate"


def strip_scores(summary: dict) -> dict:
    out = dict(summary)
    out["metrics"] = {
        name: {key: value for key, value in row.items() if key != "eval_scores"}
        for name, row in summary["metrics"].items()
    }
    return out


def evaluate_case(
    *,
    ds: Dataset,
    vocab: dict,
    holdout: str,
    target_mode: str,
    region_granularity: str,
    window_len: float,
    seed: int,
    l2: float,
    min_centered_delta: float,
    min_target_improvement: float,
) -> dict:
    split = split_recordings_by_subject(vocab["subject_by_rid"], [holdout])
    train_trials = build_trial_samples(vocab["recs"], split.train_rids, window_len, target_mode)
    eval_trials = build_trial_samples(vocab["recs"], split.eval_rids, window_len, target_mode)
    regions = sorted(shared_split_regions(vocab["recs"], split.train_rids, split.eval_rids, region_granularity))
    if not regions:
        regions = build_region_vocab(vocab["recs"], split.train_rids + split.eval_rids, region_granularity)

    train_true_x, train_y, train_recordings = make_feature_matrix(
        ds,
        vocab["recs"],
        train_trials,
        regions=regions,
        region_granularity=region_granularity,
        region_control="none",
        seed=seed,
        window_len=window_len,
    )
    eval_true_x, eval_y, eval_recordings = make_feature_matrix(
        ds,
        vocab["recs"],
        eval_trials,
        regions=regions,
        region_granularity=region_granularity,
        region_control="none",
        seed=seed,
        window_len=window_len,
    )
    train_shuffle_x, _train_y, _ = make_feature_matrix(
        ds,
        vocab["recs"],
        train_trials,
        regions=regions,
        region_granularity=region_granularity,
        region_control="within_recording_shuffle",
        seed=seed,
        window_len=window_len,
    )
    eval_shuffle_x, _eval_y, _ = make_feature_matrix(
        ds,
        vocab["recs"],
        eval_trials,
        regions=regions,
        region_granularity=region_granularity,
        region_control="within_recording_shuffle",
        seed=seed,
        window_len=window_len,
    )
    true_unit_fractions = recording_region_unit_fractions(
        vocab["recs"],
        split.train_rids + split.eval_rids,
        regions=regions,
        region_granularity=region_granularity,
        region_control="none",
        seed=seed,
    )
    shuffle_unit_fractions = recording_region_unit_fractions(
        vocab["recs"],
        split.train_rids + split.eval_rids,
        regions=regions,
        region_granularity=region_granularity,
        region_control="within_recording_shuffle",
        seed=seed,
    )

    feature_rows = []
    for feature_mode in FEATURE_MODES:
        train_model_x = transform_region_features(
            train_true_x,
            feature_mode,
            recording_ids=train_recordings,
            unit_region_fractions=true_unit_fractions,
        )
        eval_model_x = transform_region_features(
            eval_true_x,
            feature_mode,
            recording_ids=eval_recordings,
            unit_region_fractions=true_unit_fractions,
        )
        train_shuffle_model_x = transform_region_features(
            train_shuffle_x,
            feature_mode,
            recording_ids=train_recordings,
            unit_region_fractions=shuffle_unit_fractions,
        )
        eval_shuffle_model_x = transform_region_features(
            eval_shuffle_x,
            feature_mode,
            recording_ids=eval_recordings,
            unit_region_fractions=shuffle_unit_fractions,
        )
        results = {
            "total_spikes": evaluate_feature_set(
                name="total_spikes",
                train_x=total_spike_feature(train_true_x),
                train_y=train_y,
                eval_x=total_spike_feature(eval_true_x),
                eval_y=eval_y,
                eval_recording_ids=eval_recordings,
                l2=l2,
            ),
            "region_true": evaluate_feature_set(
                name="region_true",
                train_x=train_model_x,
                train_y=train_y,
                eval_x=eval_model_x,
                eval_y=eval_y,
                eval_recording_ids=eval_recordings,
                l2=l2,
            ),
            "region_shuffle": evaluate_feature_set(
                name="region_shuffle",
                train_x=train_shuffle_model_x,
                train_y=train_y,
                eval_x=eval_shuffle_model_x,
                eval_y=eval_y,
                eval_recording_ids=eval_recordings,
                l2=l2,
            ),
        }
        summary = summarize_results(results, eval_y, eval_recordings)
        summary["decision"] = candidate_decision(
            summary,
            min_centered_delta=min_centered_delta,
            min_target_improvement=min_target_improvement,
        )
        feature_rows.append({
            "feature_mode": feature_mode,
            "summary": strip_scores(summary),
        })

    return {
        "holdout": holdout,
        "target_mode": target_mode,
        "train_subjects": split.train_subjects,
        "n_train_trials": len(train_trials),
        "n_eval_trials": len(eval_trials),
        "n_train_recordings": len(split.train_rids),
        "n_eval_recordings": len(split.eval_rids),
        "n_shared_regions": len(regions),
        "shared_regions": regions,
        "feature_modes": feature_rows,
    }


def report_decision(cases: list[dict]) -> str:
    candidates = [
        (case, row)
        for case in cases
        for row in case["feature_modes"]
        if row["summary"]["decision"] == "candidate"
    ]
    if candidates:
        return "training_aligned_local_candidate"
    positive_true = [
        row
        for case in cases
        for row in case["feature_modes"]
        if row["summary"]["deltas"]["true_minus_shuffle_centered_auc"] > 0.0
    ]
    if positive_true:
        return "weak_training_aligned_true_region_advantage"
    return "no_training_aligned_true_region_advantage"


def render_markdown(report: dict) -> str:
    lines = [
        "# Response-Extreme Training-Aligned Readout",
        "",
        "Closed-form ridge readout over the same shared parent-region feature space used by the A100 pilot.",
        "",
        f"- manifest: `{report['manifest']}`",
        f"- region granularity: `{report['region_granularity']}`",
        f"- seed: `{report['seed']}`",
        f"- l2: `{report['l2']}`",
        f"- decision: `{report['summary']['decision']}`",
        f"- paid GPU trigger: `{report['summary']['paid_gpu_trigger']}`",
        "",
        "| holdout | target | feature mode | shared regions | centered AUC | delta shuffle | delta total | target0 | target1 | recordings | decision |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for case in report["cases"]:
        for row in case["feature_modes"]:
            summary = row["summary"]
            deltas = summary["deltas"]
            paired = summary["paired_true_vs_shuffle"]
            metrics = summary["metrics"]["region_true"]
            lines.append(
                "| "
                f"{case['holdout']} | {case['target_mode']} | {row['feature_mode']} | "
                f"{case['n_shared_regions']} | {metrics['eval_centered_auc']:.3f} | "
                f"{deltas['true_minus_shuffle_centered_auc']:+.3f} | "
                f"{deltas['true_minus_total_centered_auc']:+.3f} | "
                f"{paired['target0_improved_fraction']:.3f} | "
                f"{paired['target1_improved_fraction']:.3f} | "
                f"{summary['recordings_positive_true_minus_shuffle']}/{summary['n_recordings']} | "
                f"{summary['decision']} |"
            )
    lines += [
        "",
        "Decision:",
        "",
        report["summary"]["interpretation"],
        "",
    ]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=REPO_ROOT / "data/brainsets/ibl_bwm")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=REPO_ROOT / "manifests/ibl_bwm_local_cached_external_support80_projected_hdf5.json",
    )
    parser.add_argument("--region-granularity", default="parent", choices=["fine", "parent", "grandparent"])
    parser.add_argument("--window-len", type=float, default=1.0)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--l2", type=float, default=10.0)
    parser.add_argument("--min-centered-delta", type=float, default=0.01)
    parser.add_argument("--min-target-improvement", type=float, default=0.55)
    parser.add_argument(
        "--out-json",
        type=Path,
        default=REPO_ROOT / "docs/response_extreme_training_aligned_readout.json",
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=REPO_ROOT / "docs/response_extreme_training_aligned_readout.md",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ds = Dataset(dataset_dir=args.data_dir, keep_files_open=True)
    selected_recording_ids = select_recording_ids(ds, args.manifest, args.data_dir)
    vocab = build_vocab(ds, args.region_granularity, selected_recording_ids)
    cases = [
        evaluate_case(
            ds=ds,
            vocab=vocab,
            holdout=case["holdout"],
            target_mode=case["target_mode"],
            region_granularity=args.region_granularity,
            window_len=args.window_len,
            seed=args.seed,
            l2=args.l2,
            min_centered_delta=args.min_centered_delta,
            min_target_improvement=args.min_target_improvement,
        )
        | {"local_family": case["local_family"]}
        for case in CASES
    ]
    decision = report_decision(cases)
    interpretation = (
        "At least one cloud-aligned local readout passes the strict gate; the next step is a diagnostics-enabled GPU rerun."
        if decision == "training_aligned_local_candidate"
        else (
            "The shared parent-region feature space does not reproduce the local broad-family trigger. "
            "Do not launch another GPU run; either expose the successful broad-family feature directly "
            "or redesign the local target/control."
        )
    )
    report = {
        "manifest": str(args.manifest.relative_to(REPO_ROOT) if args.manifest.is_absolute() else args.manifest),
        "region_granularity": args.region_granularity,
        "window_len": args.window_len,
        "seed": args.seed,
        "l2": args.l2,
        "thresholds": {
            "min_centered_delta": args.min_centered_delta,
            "min_target_improvement": args.min_target_improvement,
            "min_recording_support_fraction": 0.75,
        },
        "summary": {
            "decision": decision,
            "paid_gpu_trigger": decision == "training_aligned_local_candidate",
            "interpretation": interpretation,
        },
        "cases": cases,
    }
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text(render_markdown(report) + "\n")
    print(f"wrote {args.out_json}")
    print(f"wrote {args.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
