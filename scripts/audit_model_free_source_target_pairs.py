"""Screen source-subject to target-subject model-free anatomy transfer."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "vendor" / "torch_brain"))

from torch_brain.dataset import Dataset  # noqa: E402
from audit_model_free_positive_holdouts import recording_target_rows  # noqa: E402
from audit_model_free_recording_bidirectional_gate import (  # noqa: E402
    gate_decision,
    manifest_subjects,
    recording_bidirectional_summary,
)
from audit_model_free_region_signal import (  # noqa: E402
    build_region_vocab,
    evaluate_feature_set,
    make_feature_matrix,
    recording_region_unit_fractions,
    summarize_results,
    total_spike_feature,
    transform_region_features,
)
from train import build_trial_samples, build_vocab, select_recording_ids  # noqa: E402


def rids_for_subject(subject_by_rid: dict[str, str], subject: str) -> list[str]:
    return sorted(rid for rid, row_subject in subject_by_rid.items() if row_subject == subject)


def pair_decision_counts(rows: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        decision = row["recording_bidirectional_decision"]
        counts[decision] = counts.get(decision, 0) + 1
    return dict(sorted(counts.items()))


def summarize_pairs(rows: list[dict]) -> dict:
    candidates = [row for row in rows if row["recording_bidirectional_decision"] == "candidate"]
    positive = [row for row in rows if row["summary"]["delta_centered_auc"] > 0.0]
    mean_bidir = (
        sum(row["recording_bidirectional"]["bidirectional_recording_fraction"] for row in rows) / len(rows)
        if rows else 0.0
    )
    return {
        "n_pairs": len(rows),
        "n_candidates": len(candidates),
        "candidate_pairs": [
            {"source": row["source_subject"], "target": row["target_subject"]}
            for row in candidates
        ],
        "n_positive_delta_pairs": len(positive),
        "positive_delta_pairs": [
            {"source": row["source_subject"], "target": row["target_subject"]}
            for row in positive
        ],
        "mean_bidirectional_recording_fraction": mean_bidir,
        "decision_counts": pair_decision_counts(rows),
        "decision": "source_target_pair_candidate" if candidates else "no_source_target_model_free_signal",
    }


def audit_pair(args: argparse.Namespace, ds: Dataset, vocab: dict, source: str, target: str) -> dict | None:
    source_rids = rids_for_subject(vocab["subject_by_rid"], source)
    target_rids = rids_for_subject(vocab["subject_by_rid"], target)
    if not source_rids or not target_rids:
        return None

    train_trials = build_trial_samples(vocab["recs"], source_rids, args.window_len, args.target_mode)
    eval_trials = build_trial_samples(vocab["recs"], target_rids, args.window_len, args.target_mode)
    if not train_trials or not eval_trials:
        return None

    regions = build_region_vocab(vocab["recs"], source_rids + target_rids, args.region_granularity)
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
    true_unit_fractions = recording_region_unit_fractions(
        vocab["recs"],
        source_rids + target_rids,
        regions=regions,
        region_granularity=args.region_granularity,
        region_control="none",
        seed=args.seed,
    )
    shuffle_unit_fractions = recording_region_unit_fractions(
        vocab["recs"],
        source_rids + target_rids,
        regions=regions,
        region_granularity=args.region_granularity,
        region_control="within_recording_shuffle",
        seed=args.seed,
    )
    train_model_x = transform_region_features(
        train_true_x,
        args.feature_mode,
        recording_ids=train_recordings,
        unit_region_fractions=true_unit_fractions,
    )
    eval_model_x = transform_region_features(
        eval_true_x,
        args.feature_mode,
        recording_ids=eval_recordings,
        unit_region_fractions=true_unit_fractions,
    )
    train_shuffle_model_x = transform_region_features(
        train_shuffle_x,
        args.feature_mode,
        recording_ids=train_recordings,
        unit_region_fractions=shuffle_unit_fractions,
    )
    eval_shuffle_model_x = transform_region_features(
        eval_shuffle_x,
        args.feature_mode,
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
            l2=args.l2,
        ),
        "region_true": evaluate_feature_set(
            name="region_true",
            train_x=train_model_x,
            train_y=train_y,
            eval_x=eval_model_x,
            eval_y=eval_y,
            eval_recording_ids=eval_recordings,
            l2=args.l2,
        ),
        "region_shuffle": evaluate_feature_set(
            name="region_shuffle",
            train_x=train_shuffle_model_x,
            train_y=train_y,
            eval_x=eval_shuffle_model_x,
            eval_y=eval_y,
            eval_recording_ids=eval_recordings,
            l2=args.l2,
        ),
    }
    summary = summarize_results(results, eval_y, eval_recordings)
    pair = {
        "source_subject": source,
        "target_subject": target,
        "target_mode": args.target_mode,
        "feature_mode": args.feature_mode,
        "region_granularity": args.region_granularity,
        "n_source_recordings": len(source_rids),
        "n_target_recordings": len(target_rids),
        "n_train_trials": len(train_trials),
        "n_eval_trials": len(eval_trials),
        "n_regions": len(regions),
        "summary": {
            "delta_centered_auc": summary["deltas"]["true_minus_shuffle_centered_auc"],
            "delta_auc": summary["deltas"]["true_minus_shuffle_auc"],
            "paired_true_vs_shuffle": summary["paired_true_vs_shuffle"],
            "recordings_positive_true_minus_shuffle": summary["recordings_positive_true_minus_shuffle"],
            "n_recordings": summary["n_recordings"],
            "recording_support_fraction": summary["recording_support_fraction"],
        },
        "recording_target_rows": recording_target_rows(
            results["region_true"]["eval_scores"],
            results["region_shuffle"]["eval_scores"],
            eval_y,
            eval_recordings,
        ),
    }
    bidirectional = recording_bidirectional_summary(
        pair["recording_target_rows"],
        min_target_improvement=args.min_target_improvement,
    )
    pair["recording_bidirectional"] = bidirectional
    pair["recording_bidirectional_decision"] = gate_decision(
        pair,
        bidirectional,
        min_centered_delta=args.min_centered_delta,
        min_target_improvement=args.min_target_improvement,
        min_bidirectional_recording_fraction=args.min_bidirectional_recording_fraction,
    )
    return pair


def render_markdown(report: dict) -> str:
    summary = report["summary"]
    lines = [
        "# Model-Free Source-Target Pair Gate",
        "",
        (
            "Closed-form ridge audit that trains on one source subject and evaluates on "
            "one target subject. This tests whether the leave-subject-out panel is hiding "
            "a compatible cross-animal anatomical transfer pair."
        ),
        "",
        f"- target mode: `{report['target_mode']}`",
        f"- feature mode: `{report['feature_mode']}`",
        f"- region granularity: `{report['region_granularity']}`",
        f"- source-target pairs: `{summary['n_pairs']}`",
        f"- candidates: `{summary['n_candidates']}`",
        f"- positive centered-delta pairs: `{summary['n_positive_delta_pairs']}`",
        f"- mean bidirectional recording fraction: `{summary['mean_bidirectional_recording_fraction']:.3f}`",
        f"- decision: `{summary['decision']}`",
        "",
        "## Top Pairs",
        "",
        "| source | target | decision | centered delta | target0 | target1 | positive recs | bidirectional recs | train trials | eval trials |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    rows = sorted(
        report["pairs"],
        key=lambda row: (
            row["recording_bidirectional_decision"] == "candidate",
            row["summary"]["delta_centered_auc"],
            row["recording_bidirectional"]["bidirectional_recording_fraction"],
        ),
        reverse=True,
    )
    for row in rows[: report["top_pairs"]]:
        row_summary = row["summary"]
        paired = row_summary["paired_true_vs_shuffle"]
        bidir = row["recording_bidirectional"]
        lines.append(
            f"| {row['source_subject']} | {row['target_subject']} | "
            f"{row['recording_bidirectional_decision']} | "
            f"{row_summary['delta_centered_auc']:+.3f} | "
            f"{paired['target0_improved_fraction']:.3f} | "
            f"{paired['target1_improved_fraction']:.3f} | "
            f"{row_summary['recordings_positive_true_minus_shuffle']}/{row_summary['n_recordings']} | "
            f"{bidir['n_bidirectional_recordings']}/{bidir['n_evaluable_recordings']} | "
            f"{row['n_train_trials']} | {row['n_eval_trials']} |"
        )
    lines += [
        "",
        "## Decision",
        "",
        (
            "Do not promote source-target pair training unless at least one pair clears "
            "the same centered-delta, global target0/target1, and same-recording "
            "bidirectionality gates used by the matched-panel screens."
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
    parser.add_argument("--source", nargs="*", default=None)
    parser.add_argument("--target", nargs="*", default=None)
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
    parser.add_argument("--top-pairs", type=int, default=16)
    parser.add_argument(
        "--out-json",
        type=Path,
        default=REPO_ROOT / "docs/model_free_source_target_pair_gate.json",
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=REPO_ROOT / "docs/model_free_source_target_pair_gate.md",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    subjects = manifest_subjects(args.manifest)
    sources = args.source or subjects
    targets = args.target or subjects
    ds = Dataset(dataset_dir=args.data_dir, keep_files_open=True)
    selected_recording_ids = select_recording_ids(ds, args.manifest, args.data_dir)
    vocab = build_vocab(ds, args.region_granularity, selected_recording_ids)
    rows = []
    for source in sources:
        for target in targets:
            if source == target:
                continue
            row = audit_pair(args, ds, vocab, source, target)
            if row is not None:
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
        "top_pairs": args.top_pairs,
        "summary": summarize_pairs(rows),
        "pairs": rows,
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
