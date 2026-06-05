"""Audit neutral-prior low-contrast choice targets under the shared-family gate."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "vendor" / "torch_brain"))

from audit_derived_target_family_gate import DEFAULT_FAMILIES, DEFAULT_MIN_CLASS_TRIALS, _finite_array  # noqa: E402
from audit_low_contrast_choice_family_gate import (  # noqa: E402
    DEFAULT_CONTRAST_THRESHOLDS,
    precompute_threshold,
    render_markdown as render_low_contrast_markdown,
    screen_precomputed,
    summarize as summarize_low_contrast,
)
from torch_brain.dataset import Dataset  # noqa: E402
from train import build_vocab, select_recording_ids  # noqa: E402


def target_name_for_threshold(threshold: float) -> str:
    return f"neutral_prior_low_contrast_choice_le_{threshold:g}"


def per_recording_neutral_prior_low_contrast_choice_labels(rec, *, max_contrast: float) -> np.ndarray:
    stim_on = _finite_array(rec.trials.stim_on_times)
    labels = np.full(len(stim_on), np.nan, dtype=np.float64)
    left = _finite_array(rec.trials.contrast_left)
    right = _finite_array(rec.trials.contrast_right)
    choice = _finite_array(rec.trials.choice)
    probability_left = _finite_array(rec.trials.probability_left)
    if (
        len(left) != len(stim_on)
        or len(right) != len(stim_on)
        or len(choice) != len(stim_on)
        or len(probability_left) != len(stim_on)
    ):
        return labels
    left = np.where(np.isfinite(left), left, 0.0)
    right = np.where(np.isfinite(right), right, 0.0)
    strength = np.maximum(np.abs(left), np.abs(right))
    valid = (
        np.isfinite(stim_on)
        & np.isfinite(choice)
        & (choice != 0.0)
        & np.isfinite(probability_left)
        & (probability_left == 0.5)
        & np.isfinite(strength)
        & (strength <= max_contrast)
    )
    labels[valid & (choice < 0.0)] = 0.0
    labels[valid & (choice > 0.0)] = 1.0
    return labels


def build_neutral_prior_low_contrast_choice_trial_samples(
    recs: dict[str, object],
    rids: list[str],
    *,
    window_len: float,
    max_contrast: float,
) -> list[tuple[str, float, float]]:
    rows = []
    for rid in rids:
        rec = recs[rid]
        labels = per_recording_neutral_prior_low_contrast_choice_labels(rec, max_contrast=max_contrast)
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


def precompute_neutral_prior_threshold(**kwargs) -> dict:
    import audit_low_contrast_choice_family_gate as low_contrast

    original_builder = low_contrast.build_low_contrast_choice_trial_samples
    original_name = low_contrast.target_name_for_threshold
    low_contrast.build_low_contrast_choice_trial_samples = build_neutral_prior_low_contrast_choice_trial_samples
    low_contrast.target_name_for_threshold = target_name_for_threshold
    try:
        return precompute_threshold(**kwargs)
    finally:
        low_contrast.build_low_contrast_choice_trial_samples = original_builder
        low_contrast.target_name_for_threshold = original_name


def summarize(rows: list[dict], balances: dict[str, dict]) -> dict:
    base = summarize_low_contrast(rows, balances)
    base["decision"] = (
        "neutral_prior_low_contrast_choice_family_candidate"
        if base["n_candidates"]
        else "no_neutral_prior_low_contrast_choice_family_candidate"
    )
    base["next_action"] = (
        "Validate neutral-prior low-contrast choice candidates across shuffle seeds before GPU training."
        if base["n_candidates"]
        else "Do not train: neutral-prior low-contrast choice targets do not pass the strict local gate."
    )
    return base


def render_markdown(report: dict) -> str:
    text = render_low_contrast_markdown(report)
    text = text.replace(
        "# Low-Contrast Choice Family Gate",
        "# Neutral-Prior Low-Contrast Choice Family Gate",
        1,
    )
    text = text.replace(
        "restrict trials by absolute stimulus contrast and classify left-vs-right choice",
        "restrict trials by absolute stimulus contrast and neutral block prior, then classify left-vs-right choice",
        1,
    )
    return text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=REPO_ROOT / "data/brainsets/ibl_bwm")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=REPO_ROOT / "manifests/ibl_bwm_region_matched_candidates_s3_present_support80_hdf5_scored.json",
    )
    parser.add_argument("--max-contrast", nargs="*", type=float, default=list(DEFAULT_CONTRAST_THRESHOLDS) + [1.0])
    parser.add_argument("--family", nargs="*", default=list(DEFAULT_FAMILIES))
    parser.add_argument(
        "--feature-mode",
        default="recording_centered",
        choices=["counts", "fractions", "recording_centered", "recording_zscore", "unit_residuals"],
    )
    parser.add_argument("--region-granularity", default="parent", choices=["fine", "parent", "grandparent"])
    parser.add_argument("--window-len", type=float, default=1.0)
    parser.add_argument("--min-class-trials", type=int, default=DEFAULT_MIN_CLASS_TRIALS)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--l2", type=float, default=10.0)
    parser.add_argument("--min-centered-delta", type=float, default=0.0)
    parser.add_argument("--min-total-delta", type=float, default=0.0)
    parser.add_argument("--min-target-improvement", type=float, default=0.55)
    parser.add_argument("--min-bidirectional-recording-fraction", type=float, default=0.75)
    parser.add_argument(
        "--out-json",
        type=Path,
        default=REPO_ROOT / "docs/neutral_prior_low_contrast_choice_family_gate.json",
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=REPO_ROOT / "docs/neutral_prior_low_contrast_choice_family_gate.md",
    )
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
        payload = precompute_neutral_prior_threshold(
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
