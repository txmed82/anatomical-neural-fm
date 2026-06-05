"""Audit reaction-dynamics target definitions under the shared-family gate."""
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
from audit_derived_target_family_gate import (  # noqa: E402
    DEFAULT_FAMILIES,
    DEFAULT_MIN_CLASS_TRIALS,
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
from audit_wheel_target_family_gate import _finite_array, _median_split_labels, _wheel_arrays, screen_precomputed  # noqa: E402
from scan_model_free_region_family_candidates import aggregate_features, present_family_definitions  # noqa: E402
from train import build_vocab, select_recording_ids  # noqa: E402


REACTION_TARGETS = ("pre_stim_quiescence", "post_stim_speedup", "wheel_reaction_latency")


def _window_mean_abs_velocity(velocity_t: np.ndarray, velocity: np.ndarray, lo: float, hi: float) -> float:
    mask = (velocity_t >= lo) & (velocity_t < hi)
    if not np.any(mask):
        return np.nan
    return float(np.mean(np.abs(velocity[mask])))


def per_recording_reaction_labels(
    rec,
    target_name: str,
    *,
    window_len: float = 1.0,
    pre_window_len: float = 0.5,
) -> np.ndarray:
    stim_on = _finite_array(rec.trials.stim_on_times)
    labels = np.full(len(stim_on), np.nan, dtype=np.float64)
    wheel_arrays = _wheel_arrays(rec)
    if wheel_arrays is None:
        return labels
    wheel_t, wheel_position = wheel_arrays
    velocity_t = 0.5 * (wheel_t[:-1] + wheel_t[1:])
    velocity = np.diff(wheel_position) / np.diff(wheel_t)
    abs_velocity = np.abs(velocity)
    finite_abs_velocity = abs_velocity[np.isfinite(abs_velocity)]
    if len(finite_abs_velocity) == 0:
        return labels
    movement_threshold = max(float(np.percentile(finite_abs_velocity, 75)), 1e-6)

    pre_velocity = np.full(len(stim_on), np.nan, dtype=np.float64)
    post_velocity = np.full(len(stim_on), np.nan, dtype=np.float64)
    first_latency = np.full(len(stim_on), np.nan, dtype=np.float64)
    valid_pre = np.zeros(len(stim_on), dtype=bool)
    valid_post = np.zeros(len(stim_on), dtype=bool)
    valid_latency = np.zeros(len(stim_on), dtype=bool)
    for idx, t0 in enumerate(stim_on):
        if not np.isfinite(t0):
            continue
        pre = _window_mean_abs_velocity(velocity_t, velocity, t0 - pre_window_len, t0)
        post = _window_mean_abs_velocity(velocity_t, velocity, t0, t0 + window_len)
        if np.isfinite(pre):
            pre_velocity[idx] = pre
            valid_pre[idx] = True
        if np.isfinite(post):
            post_velocity[idx] = post
            valid_post[idx] = True
        latency_mask = (velocity_t >= t0) & (velocity_t < t0 + window_len) & (abs_velocity >= movement_threshold - 1e-12)
        if np.any(latency_mask):
            first_latency[idx] = float(velocity_t[latency_mask][0] - t0)
            valid_latency[idx] = True

    if target_name == "pre_stim_quiescence":
        active = _median_split_labels(pre_velocity, valid_pre)
        return 1.0 - active
    if target_name == "post_stim_speedup":
        values = post_velocity - pre_velocity
        return _median_split_labels(values, valid_pre & valid_post)
    if target_name == "wheel_reaction_latency":
        fast = _median_split_labels(-first_latency, valid_latency)
        return fast
    raise ValueError(f"unknown reaction target {target_name!r}")


def build_reaction_trial_samples(
    recs: dict[str, object],
    rids: list[str],
    *,
    window_len: float,
    pre_window_len: float,
    target_name: str,
) -> list[tuple[str, float, float]]:
    rows = []
    for rid in rids:
        rec = recs[rid]
        labels = per_recording_reaction_labels(
            rec,
            target_name,
            window_len=window_len,
            pre_window_len=pre_window_len,
        )
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


def precompute_target(
    *,
    ds: Dataset,
    vocab: dict,
    selected_rids: list[str],
    target_name: str,
    families: tuple[str, ...],
    feature_mode: str,
    region_granularity: str,
    window_len: float,
    pre_window_len: float,
    seed: int,
    min_class_trials: int,
) -> dict:
    trials = build_reaction_trial_samples(
        vocab["recs"],
        selected_rids,
        window_len=window_len,
        pre_window_len=pre_window_len,
        target_name=target_name,
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
        "target_mode": target_name,
        "family_names": family_names,
        "family_true": aggregate_features(true_model_x, regions, selected_family_defs),
        "family_shuffle": aggregate_features(shuffle_model_x, regions, selected_family_defs),
        "total": total_spike_feature(true_x),
        "y": y,
        "recording_ids": recording_ids,
        "subject_ids": [vocab["subject_by_rid"][rid] for rid in recording_ids],
        "balance": target_balance(trials, vocab["subject_by_rid"], min_class_trials=min_class_trials),
    }


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
    base["decision"] = "reaction_dynamics_target_family_candidate" if base["n_candidates"] else "no_reaction_dynamics_target_family_candidate"
    return base


def render_markdown(report: dict) -> str:
    summary = report["summary"]
    lines = [
        "# Reaction-Dynamics Target Family Gate",
        "",
        (
            "No-spend audit for wheel-derived reaction dynamics around stimulus onset, "
            "using the same shared-family model-free promotion gate."
        ),
        "",
        f"- rows: `{summary['n_rows']}`",
        f"- candidates: `{summary['n_candidates']}`",
        f"- positive centered-delta rows: `{summary['n_positive_centered_delta']}`",
        f"- max bidirectional recordings: `{summary['max_bidirectional_recordings']}`",
        f"- max bidirectional recording fraction: `{summary['max_bidirectional_recording_fraction']:.3f}`",
        f"- decision: `{summary['decision']}`",
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
            "A reaction-dynamics target is only a training trigger if it passes the "
            "same local gate as prior audits: nonnegative true-vs-shuffle and "
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
    parser.add_argument("--target", nargs="*", default=list(REACTION_TARGETS), choices=list(REACTION_TARGETS))
    parser.add_argument("--family", nargs="*", default=list(DEFAULT_FAMILIES))
    parser.add_argument("--feature-mode", default="recording_centered", choices=["counts", "fractions", "recording_centered", "unit_residuals"])
    parser.add_argument("--region-granularity", default="parent", choices=["fine", "parent", "grandparent"])
    parser.add_argument("--window-len", type=float, default=1.0)
    parser.add_argument("--pre-window-len", type=float, default=0.5)
    parser.add_argument("--min-class-trials", type=int, default=DEFAULT_MIN_CLASS_TRIALS)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--l2", type=float, default=10.0)
    parser.add_argument("--min-centered-delta", type=float, default=0.0)
    parser.add_argument("--min-total-delta", type=float, default=0.0)
    parser.add_argument("--min-target-improvement", type=float, default=0.55)
    parser.add_argument("--min-bidirectional-recording-fraction", type=float, default=0.75)
    parser.add_argument("--out-json", type=Path, default=REPO_ROOT / "docs/reaction_dynamics_target_family_gate.json")
    parser.add_argument("--out-md", type=Path, default=REPO_ROOT / "docs/reaction_dynamics_target_family_gate.md")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ds = Dataset(dataset_dir=args.data_dir, keep_files_open=True)
    selected_rids = select_recording_ids(ds, args.manifest, args.data_dir)
    vocab = build_vocab(ds, args.region_granularity, selected_rids)
    holdouts = sorted(set(vocab["subject_by_rid"].values()))
    rows = []
    balances = {}
    for target in args.target:
        payload = precompute_target(
            ds=ds,
            vocab=vocab,
            selected_rids=selected_rids,
            target_name=target,
            families=tuple(args.family),
            feature_mode=args.feature_mode,
            region_granularity=args.region_granularity,
            window_len=args.window_len,
            pre_window_len=args.pre_window_len,
            seed=args.seed,
            min_class_trials=args.min_class_trials,
        )
        balances[target] = payload["balance"]
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
        "targets": list(args.target),
        "families": list(args.family),
        "feature_mode": args.feature_mode,
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
