"""Audit low-contrast choice targets under the shared-family model-free gate."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "vendor" / "torch_brain"))

from audit_derived_target_family_gate import (  # noqa: E402
    DEFAULT_FAMILIES,
    DEFAULT_MIN_CLASS_TRIALS,
    _finite_array,
    evaluate_family_row,
    target_balance,
)
from audit_model_free_region_signal import (  # noqa: E402
    build_region_vocab,
    make_feature_matrix,
    recording_region_unit_fractions,
    total_spike_feature,
    transform_region_features,
)
from audit_shared_family_target_control_gate import summarize_rows  # noqa: E402
from scan_model_free_region_family_candidates import aggregate_features, present_family_definitions  # noqa: E402
from torch_brain.dataset import Dataset  # noqa: E402
from train import build_vocab, select_recording_ids  # noqa: E402


DEFAULT_CONTRAST_THRESHOLDS = (0.0625, 0.125, 0.25)


def target_name_for_threshold(threshold: float) -> str:
    return f"low_contrast_choice_le_{threshold:g}"


def per_recording_low_contrast_choice_labels(rec, *, max_contrast: float) -> np.ndarray:
    stim_on = _finite_array(rec.trials.stim_on_times)
    labels = np.full(len(stim_on), np.nan, dtype=np.float64)
    left = _finite_array(rec.trials.contrast_left)
    right = _finite_array(rec.trials.contrast_right)
    choice = _finite_array(rec.trials.choice)
    if len(left) != len(stim_on) or len(right) != len(stim_on) or len(choice) != len(stim_on):
        return labels
    left = np.where(np.isfinite(left), left, 0.0)
    right = np.where(np.isfinite(right), right, 0.0)
    strength = np.maximum(np.abs(left), np.abs(right))
    valid = (
        np.isfinite(stim_on)
        & np.isfinite(choice)
        & (choice != 0.0)
        & np.isfinite(strength)
        & (strength <= max_contrast)
    )
    labels[valid & (choice < 0.0)] = 0.0
    labels[valid & (choice > 0.0)] = 1.0
    return labels


def build_low_contrast_choice_trial_samples(
    recs: dict[str, object],
    rids: list[str],
    *,
    window_len: float,
    max_contrast: float,
) -> list[tuple[str, float, float]]:
    rows = []
    for rid in rids:
        rec = recs[rid]
        labels = per_recording_low_contrast_choice_labels(rec, max_contrast=max_contrast)
        stim_on = _finite_array(rec.trials.stim_on_times)
        domain_hi = float(rec.domain.end[-1])
        for idx, label in enumerate(labels):
            if not np.isfinite(label):
                continue
            t0 = stim_on[idx]
            if not np.isfinite(t0) or t0 + window_len > domain_hi:
                continue
            rows.append((rid, float(t0), float(label)))
    return rows


def precompute_threshold(
    *,
    ds: Dataset,
    vocab: dict,
    selected_rids: list[str],
    max_contrast: float,
    families: tuple[str, ...],
    feature_mode: str,
    region_granularity: str,
    window_len: float,
    seed: int,
    min_class_trials: int,
) -> dict:
    trials = build_low_contrast_choice_trial_samples(
        vocab["recs"],
        selected_rids,
        window_len=window_len,
        max_contrast=max_contrast,
    )
    regions = build_region_vocab(vocab["recs"], selected_rids, region_granularity)
    family_defs = present_family_definitions(regions)
    selected_family_defs = {family: family_defs[family] for family in families if family in family_defs}
    family_names = list(selected_family_defs)
    true_x, y, recording_ids = make_feature_matrix(
        ds,
        vocab["recs"],
        trials,
        regions=regions,
        region_granularity=region_granularity,
        region_control="none",
        seed=seed,
        window_len=window_len,
    )
    shuffle_x, _shuffle_y, _shuffle_recordings = make_feature_matrix(
        ds,
        vocab["recs"],
        trials,
        regions=regions,
        region_granularity=region_granularity,
        region_control="within_recording_shuffle",
        seed=seed,
        window_len=window_len,
    )
    true_unit_fractions = recording_region_unit_fractions(
        vocab["recs"],
        selected_rids,
        regions=regions,
        region_granularity=region_granularity,
        region_control="none",
        seed=seed,
    )
    shuffle_unit_fractions = recording_region_unit_fractions(
        vocab["recs"],
        selected_rids,
        regions=regions,
        region_granularity=region_granularity,
        region_control="within_recording_shuffle",
        seed=seed,
    )
    true_model_x = transform_region_features(
        true_x,
        feature_mode,
        recording_ids=recording_ids,
        unit_region_fractions=true_unit_fractions,
    )
    shuffle_model_x = transform_region_features(
        shuffle_x,
        feature_mode,
        recording_ids=recording_ids,
        unit_region_fractions=shuffle_unit_fractions,
    )
    return {
        "target_mode": target_name_for_threshold(max_contrast),
        "max_contrast": max_contrast,
        "family_names": family_names,
        "family_true": aggregate_features(true_model_x, regions, selected_family_defs),
        "family_shuffle": aggregate_features(shuffle_model_x, regions, selected_family_defs),
        "total": total_spike_feature(true_x),
        "y": y,
        "recording_ids": recording_ids,
        "subject_ids": [vocab["subject_by_rid"][rid] for rid in recording_ids],
        "balance": target_balance(trials, vocab["subject_by_rid"], min_class_trials=min_class_trials),
    }


def screen_precomputed(
    payload: dict,
    *,
    holdouts: list[str],
    l2: float,
    min_centered_delta: float,
    min_total_delta: float,
    min_target_improvement: float,
    min_bidirectional_recording_fraction: float,
) -> list[dict]:
    rows = []
    subject_ids = np.asarray(payload["subject_ids"], dtype=object)
    for holdout in holdouts:
        train_mask = subject_ids != holdout
        eval_mask = subject_ids == holdout
        if not np.any(train_mask) or not np.any(eval_mask):
            continue
        if len(set(payload["y"][train_mask])) < 2 or len(set(payload["y"][eval_mask])) < 2:
            continue
        eval_recordings = [rid for rid, use in zip(payload["recording_ids"], eval_mask) if bool(use)]
        for family_idx, family in enumerate(payload["family_names"]):
            rows.append(evaluate_family_row(
                target_name=payload["target_mode"],
                family=family,
                holdout=holdout,
                family_index=family_idx,
                train_family_true=payload["family_true"][train_mask],
                eval_family_true=payload["family_true"][eval_mask],
                train_family_shuffle=payload["family_shuffle"][train_mask],
                eval_family_shuffle=payload["family_shuffle"][eval_mask],
                train_total=payload["total"][train_mask],
                eval_total=payload["total"][eval_mask],
                train_y=payload["y"][train_mask],
                eval_y=payload["y"][eval_mask],
                eval_recordings=eval_recordings,
                l2=l2,
                min_centered_delta=min_centered_delta,
                min_total_delta=min_total_delta,
                min_target_improvement=min_target_improvement,
                min_bidirectional_recording_fraction=min_bidirectional_recording_fraction,
            ))
    return rows


def summarize(rows: list[dict], balances: dict[str, dict]) -> dict:
    base = summarize_rows(rows)
    base["target_balances"] = {
        target: {
            "n_trials": payload["n_trials"],
            "eligible_recordings": payload["eligible_recordings"],
            "n_recordings": payload["n_recordings"],
        }
        for target, payload in balances.items()
    }
    base["decision"] = "low_contrast_choice_family_candidate" if base["n_candidates"] else "no_low_contrast_choice_family_candidate"
    base["gpu_training_ready"] = False
    base["next_action"] = (
        "Validate low-contrast choice candidates across shuffle seeds before GPU training."
        if base["n_candidates"]
        else "Do not train: low-contrast choice targets do not pass the strict local gate."
    )
    return base


def render_markdown(report: dict) -> str:
    summary = report["summary"]
    lines = [
        "# Low-Contrast Choice Family Gate",
        "",
        (
            "Prospective no-spend target redesign: restrict trials by absolute stimulus "
            "contrast and classify left-vs-right choice under the unchanged shared-family "
            "model-free promotion gate."
        ),
        "",
        f"- rows: `{summary['n_rows']}`",
        f"- candidates: `{summary['n_candidates']}`",
        f"- positive centered-delta rows: `{summary['n_positive_centered_delta']}`",
        f"- max bidirectional recordings: `{summary['max_bidirectional_recordings']}`",
        f"- max bidirectional recording fraction: `{summary['max_bidirectional_recording_fraction']:.3f}`",
        f"- decision: `{summary['decision']}`",
        f"- gpu training ready: `{summary['gpu_training_ready']}`",
        "",
        "## Target Balance",
        "",
        "| target | trials | eligible recordings | recordings |",
        "|---|---:|---:|---:|",
    ]
    for target, row in summary["target_balances"].items():
        lines.append(f"| {target} | {row['n_trials']} | {row['eligible_recordings']} | {row['n_recordings']} |")
    lines += [
        "",
        "## Top Rows",
        "",
        "| target | family | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs |",
        "|---|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in summary["top_rows"][:16]:
        lines.append(
            f"| {row['target_mode']} | {row['family']} | {row['holdout']} | {row['decision']} | "
            f"{row['centered_delta_vs_shuffle']:+.3f} | {row['centered_delta_vs_total']:+.3f} | "
            f"{row['target0_improved_vs_shuffle']:.3f} | {row['target1_improved_vs_shuffle']:.3f} | "
            f"{row['n_bidirectional_recordings']}/{row['n_recordings']} |"
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
    parser.add_argument("--max-contrast", nargs="*", type=float, default=list(DEFAULT_CONTRAST_THRESHOLDS))
    parser.add_argument("--family", nargs="*", default=list(DEFAULT_FAMILIES))
    parser.add_argument("--feature-mode", default="recording_centered", choices=["counts", "fractions", "recording_centered", "unit_residuals"])
    parser.add_argument("--region-granularity", default="parent", choices=["fine", "parent", "grandparent"])
    parser.add_argument("--window-len", type=float, default=1.0)
    parser.add_argument("--min-class-trials", type=int, default=DEFAULT_MIN_CLASS_TRIALS)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--l2", type=float, default=10.0)
    parser.add_argument("--min-centered-delta", type=float, default=0.0)
    parser.add_argument("--min-total-delta", type=float, default=0.0)
    parser.add_argument("--min-target-improvement", type=float, default=0.55)
    parser.add_argument("--min-bidirectional-recording-fraction", type=float, default=0.75)
    parser.add_argument("--out-json", type=Path, default=REPO_ROOT / "docs/low_contrast_choice_family_gate.json")
    parser.add_argument("--out-md", type=Path, default=REPO_ROOT / "docs/low_contrast_choice_family_gate.md")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ds = Dataset(dataset_dir=args.data_dir, keep_files_open=True)
    selected_rids = select_recording_ids(ds, args.manifest, args.data_dir)
    vocab = build_vocab(ds, args.region_granularity, selected_rids)
    holdouts = sorted(set(vocab["subject_by_rid"].values()))
    rows = []
    balances = {}
    for threshold in args.max_contrast:
        payload = precompute_threshold(
            ds=ds,
            vocab=vocab,
            selected_rids=selected_rids,
            max_contrast=threshold,
            families=tuple(args.family),
            feature_mode=args.feature_mode,
            region_granularity=args.region_granularity,
            window_len=args.window_len,
            seed=args.seed,
            min_class_trials=args.min_class_trials,
        )
        balances[payload["target_mode"]] = payload["balance"]
        rows.extend(screen_precomputed(
            payload,
            holdouts=holdouts,
            l2=args.l2,
            min_centered_delta=args.min_centered_delta,
            min_total_delta=args.min_total_delta,
            min_target_improvement=args.min_target_improvement,
            min_bidirectional_recording_fraction=args.min_bidirectional_recording_fraction,
        ))
    report = {
        "manifest": str(args.manifest),
        "max_contrast": list(args.max_contrast),
        "families": list(args.family),
        "feature_mode": args.feature_mode,
        "region_granularity": args.region_granularity,
        "thresholds": {
            "min_class_trials": args.min_class_trials,
            "min_centered_delta": args.min_centered_delta,
            "min_total_delta": args.min_total_delta,
            "min_target_improvement": args.min_target_improvement,
            "min_bidirectional_recording_fraction": args.min_bidirectional_recording_fraction,
        },
        "summary": summarize(rows, balances),
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
