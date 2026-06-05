"""Audit signed wheel-direction targets under the shared-family model-free gate."""
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
from audit_wheel_target_family_gate import (  # noqa: E402
    _wheel_arrays,
    precompute_target,
    render_markdown as render_wheel_markdown,
    screen_precomputed,
    summarize as summarize_wheel,
)
from torch_brain.dataset import Dataset  # noqa: E402
from train import build_vocab, select_recording_ids  # noqa: E402


TARGET_NAME = "signed_wheel_direction"


def per_recording_signed_wheel_direction_labels(
    rec,
    *,
    window_len: float = 1.0,
    min_abs_displacement: float = 1e-6,
) -> np.ndarray:
    stim_on = _finite_array(rec.trials.stim_on_times)
    labels = np.full(len(stim_on), np.nan, dtype=np.float64)
    wheel_arrays = _wheel_arrays(rec)
    if wheel_arrays is None:
        return labels
    wheel_t, wheel_position = wheel_arrays
    for idx, t0 in enumerate(stim_on):
        if not np.isfinite(t0):
            continue
        t1 = t0 + window_len
        position_mask = (wheel_t >= t0) & (wheel_t <= t1)
        if np.count_nonzero(position_mask) < 2:
            continue
        displacement = float(wheel_position[position_mask][-1] - wheel_position[position_mask][0])
        if abs(displacement) <= min_abs_displacement:
            continue
        labels[idx] = 1.0 if displacement > 0.0 else 0.0
    return labels


def build_signed_wheel_direction_trial_samples(
    recs: dict[str, object],
    rids: list[str],
    *,
    window_len: float,
    target_name: str,
) -> list[tuple[str, float, float]]:
    if target_name != TARGET_NAME:
        raise ValueError(f"unknown signed wheel target {target_name!r}")
    rows = []
    for rid in rids:
        rec = recs[rid]
        labels = per_recording_signed_wheel_direction_labels(rec, window_len=window_len)
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


def precompute_signed_wheel_direction(**kwargs) -> dict:
    import audit_wheel_target_family_gate as wheel_gate

    original_builder = wheel_gate.build_wheel_trial_samples
    wheel_gate.build_wheel_trial_samples = build_signed_wheel_direction_trial_samples
    try:
        return precompute_target(**kwargs)
    finally:
        wheel_gate.build_wheel_trial_samples = original_builder


def summarize(rows: list[dict], balances: dict[str, dict]) -> dict:
    base = summarize_wheel(rows, balances)
    base["decision"] = (
        "signed_wheel_direction_family_candidate"
        if base["n_candidates"]
        else "no_signed_wheel_direction_family_candidate"
    )
    base["gpu_training_ready"] = False
    base["next_action"] = (
        "Validate signed wheel-direction candidates across shuffle seeds before GPU training."
        if base["n_candidates"]
        else "Do not train: signed wheel-direction targets do not pass the strict local gate."
    )
    return base


def render_markdown(report: dict) -> str:
    text = render_wheel_markdown(report)
    text = text.replace("# Wheel Target Family Gate", "# Signed Wheel-Direction Family Gate", 1)
    text = text.replace(
        "No-spend audit for target definitions derived from cached wheel position,",
        "No-spend audit for post-stimulus signed wheel-direction targets derived from cached wheel position,",
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
    parser.add_argument("--out-json", type=Path, default=REPO_ROOT / "docs/signed_wheel_direction_family_gate.json")
    parser.add_argument("--out-md", type=Path, default=REPO_ROOT / "docs/signed_wheel_direction_family_gate.md")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ds = Dataset(dataset_dir=args.data_dir, keep_files_open=True)
    selected_rids = select_recording_ids(ds, args.manifest, args.data_dir)
    vocab = build_vocab(ds, args.region_granularity, selected_rids)
    holdouts = sorted(set(vocab["subject_by_rid"].values()))
    payload = precompute_signed_wheel_direction(
        ds=ds,
        vocab=vocab,
        selected_rids=selected_rids,
        target_name=TARGET_NAME,
        families=tuple(args.family),
        feature_mode=args.feature_mode,
        region_granularity=args.region_granularity,
        window_len=args.window_len,
        seed=args.seed,
        min_class_trials=args.min_class_trials,
    )
    rows = screen_precomputed(
        payload,
        holdouts=holdouts,
        l2=args.l2,
        min_centered_delta=args.min_centered_delta,
        min_total_delta=args.min_total_delta,
        min_target_improvement=args.min_target_improvement,
        min_bidirectional_recording_fraction=args.min_bidirectional_recording_fraction,
    )
    report = {
        "manifest": str(args.manifest),
        "targets": [TARGET_NAME],
        "families": list(args.family),
        "feature_mode": args.feature_mode,
        "thresholds": {
            "min_class_trials": args.min_class_trials,
            "min_centered_delta": args.min_centered_delta,
            "min_total_delta": args.min_total_delta,
            "min_target_improvement": args.min_target_improvement,
            "min_bidirectional_recording_fraction": args.min_bidirectional_recording_fraction,
        },
        "summary": summarize(rows, {TARGET_NAME: payload["balance"]}),
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
