"""Audit bounded composite behavior targets under the shared-family gate."""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "vendor" / "torch_brain"))

from audit_contextual_target_family_gate import _block_slices  # noqa: E402
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


@dataclass(frozen=True)
class CompositeTarget:
    name: str
    label: str
    max_contrast: float | None = None
    prior: str = "any"
    previous_feedback: str = "any"
    feedback: str = "any"
    block_position: str = "any"
    latency_quantiles: tuple[float, float] | None = None


COMPOSITE_TARGETS: tuple[CompositeTarget, ...] = (
    CompositeTarget(
        "low_contrast_fast_response_le_0.25",
        label="fast_response",
        max_contrast=0.25,
    ),
    CompositeTarget(
        "neutral_prior_fast_response_le_1",
        label="fast_response",
        max_contrast=1.0,
        prior="neutral",
    ),
    CompositeTarget(
        "post_error_choice_le_1",
        label="choice_side",
        max_contrast=1.0,
        previous_feedback="error",
    ),
    CompositeTarget(
        "post_error_low_contrast_choice_le_0.25",
        label="choice_side",
        max_contrast=0.25,
        previous_feedback="error",
    ),
    CompositeTarget(
        "biased_prior_choice_le_0.25",
        label="choice_side",
        max_contrast=0.25,
        prior="biased",
    ),
    CompositeTarget(
        "prior_switch_choice_le_1",
        label="choice_side",
        max_contrast=1.0,
        block_position="switch",
    ),
    CompositeTarget(
        "post_error_fast_response_le_1",
        label="fast_response",
        max_contrast=1.0,
        previous_feedback="error",
    ),
    CompositeTarget(
        "post_error_response_extreme_33_67_le_1",
        label="fast_response",
        max_contrast=1.0,
        previous_feedback="error",
        latency_quantiles=(33.0, 67.0),
    ),
    CompositeTarget(
        "post_error_response_extreme_25_75_le_1",
        label="fast_response",
        max_contrast=1.0,
        previous_feedback="error",
        latency_quantiles=(25.0, 75.0),
    ),
    CompositeTarget(
        "correct_low_contrast_fast_response_le_0.25",
        label="fast_response",
        max_contrast=0.25,
        feedback="correct",
    ),
)

TARGET_BY_NAME = {target.name: target for target in COMPOSITE_TARGETS}


def _optional_trial_array(rec, name: str, n: int) -> np.ndarray:
    if not hasattr(rec.trials, name):
        return np.full(n, np.nan, dtype=np.float64)
    values = _finite_array(getattr(rec.trials, name))
    if len(values) != n:
        return np.full(n, np.nan, dtype=np.float64)
    return values


def _contrast_strength(rec, n: int) -> np.ndarray:
    left = _optional_trial_array(rec, "contrast_left", n)
    right = _optional_trial_array(rec, "contrast_right", n)
    left = np.where(np.isfinite(left), left, 0.0)
    right = np.where(np.isfinite(right), right, 0.0)
    return np.maximum(np.abs(left), np.abs(right))


def _prior_mask(probability_left: np.ndarray, mode: str) -> np.ndarray:
    valid = np.isfinite(probability_left)
    if mode == "any":
        return valid | ~valid
    if mode == "neutral":
        return valid & (probability_left == 0.5)
    if mode == "biased":
        return valid & (probability_left != 0.5)
    raise ValueError(f"unknown prior filter {mode!r}")


def _feedback_mask(feedback: np.ndarray, mode: str) -> np.ndarray:
    if mode == "any":
        return np.ones(len(feedback), dtype=bool)
    valid = np.isfinite(feedback)
    if mode == "correct":
        return valid & (feedback > 0.0)
    if mode == "error":
        return valid & (feedback < 0.0)
    raise ValueError(f"unknown feedback filter {mode!r}")


def _previous_feedback_mask(feedback: np.ndarray, mode: str) -> np.ndarray:
    if mode == "any":
        return np.ones(len(feedback), dtype=bool)
    prev = np.roll(feedback, 1)
    mask = _feedback_mask(prev, mode)
    mask[0] = False
    return mask


def _block_position_mask(probability_left: np.ndarray, mode: str) -> np.ndarray:
    if mode == "any":
        return np.ones(len(probability_left), dtype=bool)
    if mode != "switch":
        raise ValueError(f"unknown block-position filter {mode!r}")
    mask = np.zeros(len(probability_left), dtype=bool)
    for lo, hi in _block_slices(probability_left):
        if lo == 0 or hi - lo < 40:
            continue
        mask[lo:min(hi, lo + 10)] = True
    return mask


def _median_split_fast_latency(stim_on: np.ndarray, response: np.ndarray, valid: np.ndarray) -> np.ndarray:
    labels = np.full(len(stim_on), np.nan, dtype=np.float64)
    latency = response - stim_on
    valid = valid & np.isfinite(latency) & (latency > 0.0)
    values = latency[valid]
    if len(values) == 0:
        return labels
    threshold = float(np.median(values))
    labels[valid & (latency < threshold)] = 1.0
    labels[valid & (latency > threshold)] = 0.0
    return labels


def _extreme_split_fast_latency(
    stim_on: np.ndarray,
    response: np.ndarray,
    valid: np.ndarray,
    quantiles: tuple[float, float],
) -> np.ndarray:
    labels = np.full(len(stim_on), np.nan, dtype=np.float64)
    latency = response - stim_on
    valid = valid & np.isfinite(latency) & (latency > 0.0)
    values = latency[valid]
    if len(values) == 0:
        return labels
    lo, hi = np.percentile(values, quantiles)
    labels[valid & (latency <= lo)] = 1.0
    labels[valid & (latency >= hi)] = 0.0
    return labels


def per_recording_composite_labels(rec, target_name: str) -> np.ndarray:
    if target_name not in TARGET_BY_NAME:
        raise ValueError(f"unknown composite target {target_name!r}")
    target = TARGET_BY_NAME[target_name]
    stim_on = _finite_array(rec.trials.stim_on_times)
    n = len(stim_on)
    labels = np.full(n, np.nan, dtype=np.float64)
    choice = _optional_trial_array(rec, "choice", n)
    feedback = _optional_trial_array(rec, "feedback_type", n)
    probability_left = _optional_trial_array(rec, "probability_left", n)
    strength = _contrast_strength(rec, n)
    valid = np.isfinite(stim_on)
    if target.max_contrast is not None:
        valid &= np.isfinite(strength) & (strength <= target.max_contrast)
    valid &= _prior_mask(probability_left, target.prior)
    valid &= _feedback_mask(feedback, target.feedback)
    valid &= _previous_feedback_mask(feedback, target.previous_feedback)
    valid &= _block_position_mask(probability_left, target.block_position)

    if target.label == "choice_side":
        valid &= np.isfinite(choice) & (choice != 0.0)
        labels[valid & (choice < 0.0)] = 0.0
        labels[valid & (choice > 0.0)] = 1.0
        return labels
    if target.label == "fast_response":
        response = _optional_trial_array(rec, "response_times", n)
        if target.latency_quantiles is not None:
            return _extreme_split_fast_latency(stim_on, response, valid, target.latency_quantiles)
        return _median_split_fast_latency(stim_on, response, valid)
    raise ValueError(f"unknown composite label {target.label!r}")


def build_composite_trial_samples(
    recs: dict[str, object],
    rids: list[str],
    *,
    window_len: float,
    target_name: str,
) -> list[tuple[str, float, float]]:
    rows = []
    for rid in rids:
        rec = recs[rid]
        labels = per_recording_composite_labels(rec, target_name)
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
    seed: int,
    min_class_trials: int,
) -> dict:
    trials = build_composite_trial_samples(
        vocab["recs"],
        selected_rids,
        window_len=window_len,
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
    base["decision"] = (
        "composite_behavior_target_family_candidate"
        if base["n_candidates"]
        else "no_composite_behavior_target_family_candidate"
    )
    base["gpu_training_ready"] = False
    base["next_action"] = (
        "Validate composite behavior candidates on the projected manifest and across shuffle seeds before GPU training."
        if base["n_candidates"]
        else "Do not train: bounded composite behavior targets do not pass the strict local gate."
    )
    return base


def render_markdown(report: dict) -> str:
    summary = report["summary"]
    lines = [
        "# Composite Behavior Target Family Gate",
        "",
        (
            "No-spend bounded screen over prospective composite behavior targets. "
            "Targets combine low contrast, prior context, previous-trial outcome, "
            "correctness, block-switch context, and response-speed labels under the "
            "unchanged shared-family model-free promotion gate."
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
    parser.add_argument("--target", nargs="*", default=[target.name for target in COMPOSITE_TARGETS], choices=sorted(TARGET_BY_NAME))
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
    parser.add_argument("--out-json", type=Path, default=REPO_ROOT / "docs/composite_behavior_target_family_gate.json")
    parser.add_argument("--out-md", type=Path, default=REPO_ROOT / "docs/composite_behavior_target_family_gate.md")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ds = Dataset(dataset_dir=args.data_dir, keep_files_open=True)
    selected_rids = select_recording_ids(ds, args.manifest, args.data_dir)
    vocab = build_vocab(ds, args.region_granularity, selected_rids)
    holdouts = sorted(set(vocab["subject_by_rid"].values()))
    rows = []
    balances = {}
    for target_name in args.target:
        payload = precompute_target(
            ds=ds,
            vocab=vocab,
            selected_rids=selected_rids,
            target_name=target_name,
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
        "targets": list(args.target),
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
