"""Audit waveform-derived unit features under the local model-free gate."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "vendor" / "torch_brain"))

from torch_brain.dataset import Dataset, DatasetIndex  # noqa: E402
from audit_derived_target_family_gate import evaluate_family_row  # noqa: E402
from audit_model_free_region_signal import stable_seed, total_spike_feature  # noqa: E402
from audit_shared_family_target_control_gate import summarize_rows  # noqa: E402
from train import TARGET_MODES, build_trial_samples, build_vocab, select_recording_ids  # noqa: E402


WAVEFORM_CHANNELS = ("amp", "depth", "peak_to_trough")


def recording_waveform_features(rec, *, control: str, recording_id: str, seed: int) -> np.ndarray:
    features = np.stack(
        [
            np.asarray(rec.units.amps, dtype=np.float32),
            np.asarray(rec.units.depths, dtype=np.float32),
            np.asarray(rec.units.peak_to_trough, dtype=np.float32),
        ],
        axis=-1,
    )
    finite = np.isfinite(features)
    clean = np.where(finite, features, np.nan)
    mean = np.nanmean(clean, axis=0, keepdims=True)
    std = np.nanstd(clean, axis=0, keepdims=True)
    mean = np.where(np.isfinite(mean), mean, 0.0)
    std = np.where((np.isfinite(std)) & (std > 1e-6), std, 1.0)
    z = np.where(finite, (features - mean) / std, 0.0).astype(np.float32)
    if control == "none":
        return z
    if control != "within_recording_shuffle":
        raise ValueError(f"unknown waveform control {control!r}")
    rng = np.random.default_rng(stable_seed(f"waveform:{recording_id}", seed))
    shuffled = z.copy()
    rng.shuffle(shuffled, axis=0)
    return shuffled


def make_waveform_feature_matrix(
    ds: Dataset,
    recs,
    trials: list[tuple[str, float, float]],
    *,
    control: str,
    seed: int,
    window_len: float,
) -> tuple[np.ndarray, np.ndarray, list[str]]:
    features_by_recording = {
        rid: recording_waveform_features(recs[rid], control=control, recording_id=rid, seed=seed)
        for rid in sorted({rid for rid, _t0, _target in trials})
    }
    features = np.zeros((len(trials), len(WAVEFORM_CHANNELS)), dtype=np.float32)
    targets = np.zeros(len(trials), dtype=np.int64)
    recording_ids = []
    for row_idx, (rid, t0, target) in enumerate(trials):
        sample = ds[DatasetIndex(recording_id=rid, start=t0, end=t0 + window_len)]
        spike_units = np.asarray(sample.spikes.unit_index, dtype=np.int64)
        if spike_units.size:
            features[row_idx] = features_by_recording[rid][spike_units].sum(axis=0)
        targets[row_idx] = int(target)
        recording_ids.append(str(rid))
    return features, targets, recording_ids


def transform_waveform_features(features: np.ndarray, feature_mode: str, *, recording_ids: list[str]) -> np.ndarray:
    if feature_mode == "sums":
        return features
    if feature_mode == "recording_centered":
        out = features.astype(np.float32).copy()
        for rid in sorted(set(recording_ids)):
            mask = np.asarray([value == rid for value in recording_ids], dtype=bool)
            if np.any(mask):
                out[mask] -= out[mask].mean(axis=0, keepdims=True)
        return out
    if feature_mode == "trial_means":
        totals = total_spike_feature(np.abs(features)).astype(np.float32)
        out = np.zeros_like(features, dtype=np.float32)
        np.divide(features, totals, out=out, where=totals > 0.0)
        return out
    raise ValueError(f"unknown feature_mode {feature_mode!r}")


def precompute_target(
    *,
    ds: Dataset,
    vocab: dict,
    selected_rids: list[str],
    target_mode: str,
    feature_mode: str,
    window_len: float,
    seed: int,
) -> dict:
    trials = build_trial_samples(vocab["recs"], selected_rids, window_len, target_mode)
    true_x, y, recording_ids = make_waveform_feature_matrix(
        ds,
        vocab["recs"],
        trials,
        control="none",
        seed=seed,
        window_len=window_len,
    )
    shuffle_x, _shuffle_y, _shuffle_recordings = make_waveform_feature_matrix(
        ds,
        vocab["recs"],
        trials,
        control="within_recording_shuffle",
        seed=seed,
        window_len=window_len,
    )
    return {
        "target_mode": target_mode,
        "waveform_true": transform_waveform_features(true_x, feature_mode, recording_ids=recording_ids),
        "waveform_shuffle": transform_waveform_features(shuffle_x, feature_mode, recording_ids=recording_ids),
        "total": total_spike_feature(np.abs(true_x)),
        "y": y,
        "recording_ids": recording_ids,
        "subject_ids": [vocab["subject_by_rid"][rid] for rid in recording_ids],
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
        for channel_idx, channel in enumerate(WAVEFORM_CHANNELS):
            rows.append(evaluate_family_row(
                target_name=payload["target_mode"],
                family=channel,
                holdout=holdout,
                family_index=channel_idx,
                train_family_true=payload["waveform_true"][train_mask],
                eval_family_true=payload["waveform_true"][eval_mask],
                train_family_shuffle=payload["waveform_shuffle"][train_mask],
                eval_family_shuffle=payload["waveform_shuffle"][eval_mask],
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


def summarize(rows: list[dict]) -> dict:
    base = summarize_rows(rows)
    base["decision"] = "waveform_target_control_candidate" if base["n_candidates"] else "no_waveform_target_control_candidate"
    return base


def render_markdown(report: dict) -> str:
    summary = report["summary"]
    lines = [
        "# Waveform Target/Control Gate",
        "",
        (
            "No-spend model-free screen for waveform-derived unit features. Per-unit "
            "amp, depth, and peak-to-trough features are z-scored within recording, "
            "summed over trial-window spikes, and compared against a within-recording "
            "shuffled waveform assignment plus a total-spike baseline."
        ),
        "",
        f"- rows: `{summary['n_rows']}`",
        f"- candidates: `{summary['n_candidates']}`",
        f"- positive centered-delta rows: `{summary['n_positive_centered_delta']}`",
        f"- max bidirectional recordings: `{summary['max_bidirectional_recordings']}`",
        f"- max bidirectional recording fraction: `{summary['max_bidirectional_recording_fraction']:.3f}`",
        f"- decision: `{summary['decision']}`",
        "",
        "## Target Summary",
        "",
        "| target | rows | candidates | positive centered delta | max bidir frac |",
        "|---|---:|---:|---:|---:|",
    ]
    for target, row in summary["by_target"].items():
        lines.append(
            f"| {target} | {row['n_rows']} | {row['n_candidates']} | "
            f"{row['n_positive_centered_delta']} | {row['max_bidirectional_recording_fraction']:.3f} |"
        )
    lines += [
        "",
        "## Waveform Channel Summary",
        "",
        "| channel | rows | candidates | positive centered delta | max bidir frac |",
        "|---|---:|---:|---:|---:|",
    ]
    for channel, row in summary["by_family"].items():
        lines.append(
            f"| {channel} | {row['n_rows']} | {row['n_candidates']} | "
            f"{row['n_positive_centered_delta']} | {row['max_bidirectional_recording_fraction']:.3f} |"
        )
    lines += [
        "",
        "## Top Rows",
        "",
        "| target | channel | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs |",
        "|---|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in summary["top_rows"][:14]:
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
        (
            "A waveform feature is only a training trigger if it passes the same "
            "local gate as prior audits: nonnegative true-vs-shuffle and "
            "true-vs-total deltas, both global target classes >=0.55, and at least "
            "3/4 same-recording bidirectional support."
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
    parser.add_argument("--target-mode", nargs="*", default=list(TARGET_MODES), choices=list(TARGET_MODES))
    parser.add_argument("--feature-mode", default="recording_centered", choices=["sums", "recording_centered", "trial_means"])
    parser.add_argument("--window-len", type=float, default=1.0)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--l2", type=float, default=10.0)
    parser.add_argument("--min-centered-delta", type=float, default=0.0)
    parser.add_argument("--min-total-delta", type=float, default=0.0)
    parser.add_argument("--min-target-improvement", type=float, default=0.55)
    parser.add_argument("--min-bidirectional-recording-fraction", type=float, default=0.75)
    parser.add_argument("--out-json", type=Path, default=REPO_ROOT / "docs/waveform_target_control_gate.json")
    parser.add_argument("--out-md", type=Path, default=REPO_ROOT / "docs/waveform_target_control_gate.md")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ds = Dataset(dataset_dir=args.data_dir, keep_files_open=True)
    selected_rids = select_recording_ids(ds, args.manifest, args.data_dir)
    vocab = build_vocab(ds, "fine", selected_rids)
    holdouts = sorted(set(vocab["subject_by_rid"].values()))
    rows = []
    for target_mode in args.target_mode:
        payload = precompute_target(
            ds=ds,
            vocab=vocab,
            selected_rids=selected_rids,
            target_mode=target_mode,
            feature_mode=args.feature_mode,
            window_len=args.window_len,
            seed=args.seed,
        )
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
        "targets": list(args.target_mode),
        "waveform_channels": list(WAVEFORM_CHANNELS),
        "feature_mode": args.feature_mode,
        "thresholds": {
            "min_centered_delta": args.min_centered_delta,
            "min_total_delta": args.min_total_delta,
            "min_target_improvement": args.min_target_improvement,
            "min_bidirectional_recording_fraction": args.min_bidirectional_recording_fraction,
        },
        "summary": summarize(rows),
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
