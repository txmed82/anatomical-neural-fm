"""Inspect the strongest family-aggregate near miss by family contribution."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from audit_model_free_family_bidirectional_gate import audit_family_holdout  # noqa: E402
from audit_model_free_positive_holdouts import fit_region_weights  # noqa: E402
from audit_model_free_region_signal import zscore_train_eval  # noqa: E402


def true_class_delta(candidate: np.ndarray, baseline: np.ndarray, labels: np.ndarray) -> np.ndarray:
    delta = candidate - baseline
    return np.where(labels > 0, delta, -delta)


def family_contribution_rows(
    family_names: list[str],
    true_contrib: np.ndarray,
    shuffle_contrib: np.ndarray,
    labels: np.ndarray,
    recording_ids: list[str],
) -> list[dict]:
    rows = []
    contribution_delta = true_class_delta(true_contrib, shuffle_contrib, labels[:, None])
    target0 = labels <= 0
    target1 = labels > 0
    for idx, family in enumerate(family_names):
        values = contribution_delta[:, idx]
        recording_means = {}
        for rid in sorted(set(recording_ids)):
            mask = np.asarray([value == rid for value in recording_ids], dtype=bool)
            recording_means[rid] = float(np.mean(values[mask])) if np.any(mask) else float("nan")
        rows.append({
            "family": family,
            "mean_true_class_delta": float(np.mean(values)),
            "mean_abs_true_class_delta": float(np.mean(np.abs(values))),
            "improved_fraction": float(np.mean(values > 0.0)),
            "target0_mean_delta": float(np.mean(values[target0])) if np.any(target0) else float("nan"),
            "target1_mean_delta": float(np.mean(values[target1])) if np.any(target1) else float("nan"),
            "target0_improved": float(np.mean(values[target0] > 0.0)) if np.any(target0) else float("nan"),
            "target1_improved": float(np.mean(values[target1] > 0.0)) if np.any(target1) else float("nan"),
            "positive_recordings": int(sum(value > 0.0 for value in recording_means.values())),
            "n_recordings": len(recording_means),
            "recording_mean_deltas": recording_means,
        })
    return sorted(rows, key=lambda row: row["mean_abs_true_class_delta"], reverse=True)


def recording_family_rows(
    family_rows: list[dict],
    *,
    top_n: int,
) -> dict[str, list[dict]]:
    recording_ids = sorted({
        rid
        for row in family_rows
        for rid in row["recording_mean_deltas"]
    })
    out = {}
    for rid in recording_ids:
        rows = [
            {
                "family": row["family"],
                "mean_true_class_delta": row["recording_mean_deltas"][rid],
            }
            for row in family_rows
        ]
        out[rid] = sorted(rows, key=lambda row: abs(row["mean_true_class_delta"]), reverse=True)[:top_n]
    return out


def classify_family_row(row: dict, *, min_target_improvement: float) -> str:
    if row["target0_improved"] >= min_target_improvement and row["target1_improved"] >= min_target_improvement:
        return "bidirectional_family_candidate"
    if row["target0_improved"] >= min_target_improvement:
        return "target0_only"
    if row["target1_improved"] >= min_target_improvement:
        return "target1_only"
    return "weak_or_mixed"


def render_markdown(report: dict) -> str:
    lines = [
        "# Family Near-Miss Mechanism Audit",
        "",
        (
            "Contribution audit for the strongest family-aggregate recording-centered "
            "near miss. Family rows decompose true-vs-shuffle true-class movement in "
            "the held-out animal."
        ),
        "",
        f"- holdout: `{report['holdout']}`",
        f"- target mode: `{report['target_mode']}`",
        f"- feature mode: `{report['feature_mode']}`",
        f"- centered delta: `{report['gate_summary']['delta_centered_auc']:+.3f}`",
        f"- target0 improved: `{report['gate_summary']['paired_true_vs_shuffle']['target0_improved_fraction']:.3f}`",
        f"- target1 improved: `{report['gate_summary']['paired_true_vs_shuffle']['target1_improved_fraction']:.3f}`",
        f"- bidirectional recordings: `{report['recording_bidirectional']['n_bidirectional_recordings']}/{report['recording_bidirectional']['n_evaluable_recordings']}`",
        "",
        "| family | class | mean delta | target0 delta | target1 delta | target0 | target1 | recs |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["family_rows"][: report["top_families"]]:
        lines.append(
            f"| {row['family']} | {row['classification']} | "
            f"{row['mean_true_class_delta']:+.3f} | "
            f"{row['target0_mean_delta']:+.3f} | {row['target1_mean_delta']:+.3f} | "
            f"{row['target0_improved']:.3f} | {row['target1_improved']:.3f} | "
            f"{row['positive_recordings']}/{row['n_recordings']} |"
        )
    lines += [
        "",
        "## Recording-Level Largest Families",
        "",
    ]
    for rid, rows in report["recording_family_rows"].items():
        lines += [
            f"### {rid}",
            "",
            "| family | mean true-class delta |",
            "|---|---:|",
        ]
        for row in rows:
            lines.append(f"| {row['family']} | {row['mean_true_class_delta']:+.3f} |")
        lines.append("")
    lines += [
        "## Decision",
        "",
        report["decision"],
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
    parser.add_argument("--holdout", default="KS014")
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
    parser.add_argument("--top-families", type=int, default=8)
    parser.add_argument("--top-recording-families", type=int, default=5)
    parser.add_argument("--min-target-improvement", type=float, default=0.55)
    parser.add_argument(
        "--out-json",
        type=Path,
        default=REPO_ROOT / "docs/model_free_family_ks014_near_miss_mechanism.json",
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=REPO_ROOT / "docs/model_free_family_ks014_near_miss_mechanism.md",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    gate_row = audit_family_holdout(args, args.holdout)

    # Reuse the gate internals by rerunning the final fit data from JSON is not enough
    # for contribution decomposition, so reconstruct from the saved family feature names
    # with the same audit path.
    from audit_model_free_family_bidirectional_gate import aggregate_unit_fraction_map  # noqa: PLC0415
    from audit_model_free_region_signal import (  # noqa: PLC0415
        build_region_vocab,
        make_feature_matrix,
        recording_region_unit_fractions,
        transform_region_features,
    )
    from audit_model_free_recording_bidirectional_gate import recording_bidirectional_summary  # noqa: PLC0415
    from scan_model_free_region_family_candidates import aggregate_features, present_family_definitions  # noqa: PLC0415
    from torch_brain.dataset import Dataset  # noqa: PLC0415
    from train import build_trial_samples, build_vocab, select_recording_ids, split_recordings_by_subject  # noqa: PLC0415

    ds = Dataset(dataset_dir=args.data_dir, keep_files_open=True)
    selected_recording_ids = select_recording_ids(ds, args.manifest, args.data_dir)
    vocab = build_vocab(ds, args.region_granularity, selected_recording_ids)
    split = split_recordings_by_subject(vocab["subject_by_rid"], [args.holdout])
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
    true_family_unit_fractions = aggregate_unit_fraction_map(
        recording_region_unit_fractions(
            vocab["recs"],
            split.train_rids + split.eval_rids,
            regions=regions,
            region_granularity=args.region_granularity,
            region_control="none",
            seed=args.seed,
        ),
        regions=regions,
        families=family_definitions,
    )
    shuffle_family_unit_fractions = aggregate_unit_fraction_map(
        recording_region_unit_fractions(
            vocab["recs"],
            split.train_rids + split.eval_rids,
            regions=regions,
            region_granularity=args.region_granularity,
            region_control="within_recording_shuffle",
            seed=args.seed,
        ),
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
    true_weights = fit_region_weights(train_model_x, train_y, l2=args.l2)
    shuffle_weights = fit_region_weights(train_shuffle_model_x, train_y, l2=args.l2)
    _train_z, eval_true_z = zscore_train_eval(train_model_x.astype(np.float64), eval_model_x.astype(np.float64))
    _train_shuffle_z, eval_shuffle_z = zscore_train_eval(
        train_shuffle_model_x.astype(np.float64),
        eval_shuffle_model_x.astype(np.float64),
    )
    true_contrib = eval_true_z * true_weights
    shuffle_contrib = eval_shuffle_z * shuffle_weights
    rows = family_contribution_rows(family_names, true_contrib, shuffle_contrib, eval_y, eval_recordings)
    for row in rows:
        row["classification"] = classify_family_row(row, min_target_improvement=args.min_target_improvement)
    bidirectional_family_candidates = [
        row["family"] for row in rows if row["classification"] == "bidirectional_family_candidate"
    ]
    recording_bidirectional = recording_bidirectional_summary(
        gate_row["recording_target_rows"],
        min_target_improvement=args.min_target_improvement,
    )
    decision = (
        "At least one family contribution is bidirectional; run a stricter family-specific "
        "confirmation gate before GPU training."
        if bidirectional_family_candidates else
        "No family contribution is bidirectional enough to explain a promotable signal. "
        "The KS014 near miss is still a mixture of one-sided family movements."
    )
    report = {
        "holdout": args.holdout,
        "target_mode": args.target_mode,
        "feature_mode": args.feature_mode,
        "gate_summary": gate_row["summary"],
        "recording_bidirectional": recording_bidirectional,
        "top_families": args.top_families,
        "family_rows": rows,
        "bidirectional_family_candidates": bidirectional_family_candidates,
        "recording_family_rows": recording_family_rows(rows, top_n=args.top_recording_families),
        "decision": decision,
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
