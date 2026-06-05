"""Apply the recording-bidirectional gate to predefined region-family features."""
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
from audit_model_free_recording_bidirectional_gate import (  # noqa: E402
    gate_decision,
    manifest_subjects,
    recording_bidirectional_summary,
    summarize_panel,
)
from audit_model_free_region_signal import (  # noqa: E402
    build_region_vocab,
    evaluate_feature_set,
    interpret,
    make_feature_matrix,
    recording_region_unit_fractions,
    summarize_results,
    total_spike_feature,
    transform_region_features,
)
from scan_model_free_region_family_candidates import (  # noqa: E402
    aggregate_features,
    present_family_definitions,
)
from train import (  # noqa: E402
    build_trial_samples,
    build_vocab,
    select_recording_ids,
    split_recordings_by_subject,
)


def aggregate_unit_fraction_map(
    unit_fractions: dict[str, np.ndarray],
    *,
    regions: list[str],
    families: dict[str, tuple[str, ...]],
) -> dict[str, np.ndarray]:
    rids = list(unit_fractions)
    matrix = np.vstack([unit_fractions[rid] for rid in rids]).astype(np.float32)
    family_matrix = aggregate_features(matrix, regions, families)
    return {rid: family_matrix[idx] for idx, rid in enumerate(rids)}


def audit_family_holdout(args: argparse.Namespace, holdout: str) -> dict:
    ds = Dataset(dataset_dir=args.data_dir, keep_files_open=True)
    selected_recording_ids = select_recording_ids(ds, args.manifest, args.data_dir)
    vocab = build_vocab(ds, args.region_granularity, selected_recording_ids)
    split = split_recordings_by_subject(vocab["subject_by_rid"], [holdout])
    train_trials = build_trial_samples(vocab["recs"], split.train_rids, args.window_len, args.target_mode)
    eval_trials = build_trial_samples(vocab["recs"], split.eval_rids, args.window_len, args.target_mode)
    regions = build_region_vocab(vocab["recs"], split.train_rids + split.eval_rids, args.region_granularity)
    family_definitions = present_family_definitions(regions)
    family_names = list(family_definitions)

    train_true_x, train_y, train_recordings = make_feature_matrix(
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

    train_family_x = aggregate_features(train_true_x, regions, family_definitions)
    eval_family_x = aggregate_features(eval_true_x, regions, family_definitions)
    train_shuffle_family_x = aggregate_features(train_shuffle_x, regions, family_definitions)
    eval_shuffle_family_x = aggregate_features(eval_shuffle_x, regions, family_definitions)
    true_parent_unit_fractions = recording_region_unit_fractions(
        vocab["recs"],
        split.train_rids + split.eval_rids,
        regions=regions,
        region_granularity=args.region_granularity,
        region_control="none",
        seed=args.seed,
    )
    shuffle_parent_unit_fractions = recording_region_unit_fractions(
        vocab["recs"],
        split.train_rids + split.eval_rids,
        regions=regions,
        region_granularity=args.region_granularity,
        region_control="within_recording_shuffle",
        seed=args.seed,
    )
    true_family_unit_fractions = aggregate_unit_fraction_map(
        true_parent_unit_fractions,
        regions=regions,
        families=family_definitions,
    )
    shuffle_family_unit_fractions = aggregate_unit_fraction_map(
        shuffle_parent_unit_fractions,
        regions=regions,
        families=family_definitions,
    )
    train_model_x = transform_region_features(
        train_family_x,
        args.feature_mode,
        recording_ids=train_recordings,
        unit_region_fractions=true_family_unit_fractions,
    )
    eval_model_x = transform_region_features(
        eval_family_x,
        args.feature_mode,
        recording_ids=eval_recordings,
        unit_region_fractions=true_family_unit_fractions,
    )
    train_shuffle_model_x = transform_region_features(
        train_shuffle_family_x,
        args.feature_mode,
        recording_ids=train_recordings,
        unit_region_fractions=shuffle_family_unit_fractions,
    )
    eval_shuffle_model_x = transform_region_features(
        eval_shuffle_family_x,
        args.feature_mode,
        recording_ids=eval_recordings,
        unit_region_fractions=shuffle_family_unit_fractions,
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
            name="family_true",
            train_x=train_model_x,
            train_y=train_y,
            eval_x=eval_model_x,
            eval_y=eval_y,
            eval_recording_ids=eval_recordings,
            l2=args.l2,
        ),
        "region_shuffle": evaluate_feature_set(
            name="family_shuffle",
            train_x=train_shuffle_model_x,
            train_y=train_y,
            eval_x=eval_shuffle_model_x,
            eval_y=eval_y,
            eval_recording_ids=eval_recordings,
            l2=args.l2,
        ),
    }
    summary = summarize_results(results, eval_y, eval_recordings)
    summary["decision"] = interpret(summary)
    return {
        "holdout": holdout,
        "train_subjects": split.train_subjects,
        "target_mode": args.target_mode,
        "feature_mode": args.feature_mode,
        "region_granularity": args.region_granularity,
        "n_train_trials": len(train_trials),
        "n_eval_trials": len(eval_trials),
        "n_parent_regions": len(regions),
        "n_families": len(family_names),
        "family_names": family_names,
        "family_definitions": {name: list(members) for name, members in family_definitions.items()},
        "summary": {
            "decision": summary["decision"],
            "delta_centered_auc": summary["deltas"]["true_minus_shuffle_centered_auc"],
            "paired_true_vs_shuffle": summary["paired_true_vs_shuffle"],
            "recordings_positive_true_minus_shuffle": summary["recordings_positive_true_minus_shuffle"],
            "n_recordings": summary["n_recordings"],
        },
        "recording_target_rows": recording_target_rows(
            results["region_true"]["eval_scores"],
            results["region_shuffle"]["eval_scores"],
            eval_y,
            eval_recordings,
        ),
    }


def render_markdown(report: dict) -> str:
    lines = [
        "# Model-Free Family Recording-Bidirectional Gate",
        "",
        (
            "Closed-form ridge audit on predefined parent-region family aggregates, "
            "using the same recording-local bidirectional promotion rule."
        ),
        "",
        f"- target mode: `{report['target_mode']}`",
        f"- feature mode: `{report['feature_mode']}`",
        f"- holdouts: `{report['summary']['n_holdouts']}`",
        f"- candidates: `{report['summary']['n_candidates']}`",
        f"- positive centered-delta holdouts: `{report['summary']['n_positive_delta_holdouts']}`",
        f"- mean bidirectional recording fraction: `{report['summary']['mean_bidirectional_recording_fraction']:.3f}`",
        f"- decision: `{report['summary']['decision']}`",
        "",
        "| holdout | centered delta | target0 | target1 | positive recs | bidirectional recs | decision |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in report["holdouts"]:
        summary = row["summary"]
        paired = summary["paired_true_vs_shuffle"]
        bidir = row["recording_bidirectional"]
        lines.append(
            f"| {row['holdout']} | {summary['delta_centered_auc']:+.3f} | "
            f"{paired['target0_improved_fraction']:.3f} | "
            f"{paired['target1_improved_fraction']:.3f} | "
            f"{summary['recordings_positive_true_minus_shuffle']}/{summary['n_recordings']} | "
            f"{bidir['n_bidirectional_recordings']}/{bidir['n_evaluable_recordings']} | "
            f"{row['recording_bidirectional_decision']} |"
        )
    lines += [
        "",
        "## Decision",
        "",
        (
            "Do not promote to GPU training unless this family aggregate gate produces "
            "at least one candidate holdout. The family aggregate path is meant to reduce "
            "parent-region sparsity, not relax the same-recording target0+target1 rule."
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
    parser.add_argument("--holdout", nargs="*", default=None)
    parser.add_argument("--target-mode", default="stimulus_side", choices=["choice", "stimulus_side", "feedback", "prior_side"])
    parser.add_argument(
        "--feature-mode",
        default="recording_centered",
        choices=["counts", "fractions", "recording_centered", "unit_residuals"],
    )
    parser.add_argument("--region-granularity", default="parent", choices=["fine", "parent", "grandparent"])
    parser.add_argument("--window-len", type=float, default=1.0)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--l2", type=float, default=10.0)
    parser.add_argument("--min-centered-delta", type=float, default=0.01)
    parser.add_argument("--min-target-improvement", type=float, default=0.55)
    parser.add_argument("--min-bidirectional-recording-fraction", type=float, default=0.75)
    parser.add_argument(
        "--out-json",
        type=Path,
        default=REPO_ROOT / "docs/model_free_family_bidirectional_gate_recording_centered.json",
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=REPO_ROOT / "docs/model_free_family_bidirectional_gate_recording_centered.md",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    holdouts = args.holdout or manifest_subjects(args.manifest)
    rows = []
    for holdout in holdouts:
        row = audit_family_holdout(args, holdout)
        bidirectional = recording_bidirectional_summary(
            row["recording_target_rows"],
            min_target_improvement=args.min_target_improvement,
        )
        row["recording_bidirectional"] = bidirectional
        row["recording_bidirectional_decision"] = gate_decision(
            row,
            bidirectional,
            min_centered_delta=args.min_centered_delta,
            min_target_improvement=args.min_target_improvement,
            min_bidirectional_recording_fraction=args.min_bidirectional_recording_fraction,
        )
        rows.append(row)
    report = {
        "manifest": str(args.manifest),
        "target_mode": args.target_mode,
        "feature_mode": args.feature_mode,
        "region_granularity": args.region_granularity,
        "thresholds": {
            "min_centered_delta": args.min_centered_delta,
            "min_target_improvement": args.min_target_improvement,
            "min_bidirectional_recording_fraction": args.min_bidirectional_recording_fraction,
        },
        "summary": summarize_panel(rows),
        "holdouts": rows,
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
