"""Audit derived target definitions under the shared-family model-free gate."""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "vendor" / "torch_brain"))

from torch_brain.dataset import Dataset  # noqa: E402
from audit_model_free_positive_holdouts import recording_target_rows  # noqa: E402
from audit_model_free_recording_bidirectional_gate import recording_bidirectional_summary  # noqa: E402
from audit_model_free_region_signal import (  # noqa: E402
    build_region_vocab,
    evaluate_feature_set,
    make_feature_matrix,
    paired_improvement,
    recording_region_unit_fractions,
    total_spike_feature,
    transform_region_features,
)
from audit_shared_family_target_control_gate import family_gate_decision, summarize_rows  # noqa: E402
from scan_model_free_region_family_candidates import aggregate_features, present_family_definitions  # noqa: E402
from train import build_vocab, select_recording_ids  # noqa: E402


DERIVED_TARGETS = ("contrast_strength", "response_latency", "prior_engaged")
DEFAULT_FAMILIES = ("broad_named_anatomy", "thalamic", "hippocampal_formation", "fiber_tracts")
DEFAULT_MIN_CLASS_TRIALS = 40


def _finite_array(values) -> np.ndarray:
    return np.asarray(values, dtype=np.float64)


def per_recording_derived_labels(rec, target_name: str) -> np.ndarray:
    stim_on = _finite_array(rec.trials.stim_on_times)
    n = len(stim_on)
    labels = np.full(n, np.nan, dtype=np.float64)
    if target_name == "contrast_strength":
        left = _finite_array(rec.trials.contrast_left)
        right = _finite_array(rec.trials.contrast_right)
        left = np.where(np.isfinite(left), left, 0.0)
        right = np.where(np.isfinite(right), right, 0.0)
        strength = np.maximum(np.abs(left), np.abs(right))
        valid = np.isfinite(stim_on) & np.isfinite(strength) & (strength > 0.0)
        values = strength[valid]
        if len(values) == 0:
            return labels
        threshold = float(np.median(values))
        labels[valid & (strength < threshold)] = 0.0
        labels[valid & (strength > threshold)] = 1.0
        return labels
    if target_name == "response_latency":
        response = _finite_array(rec.trials.response_times)
        latency = response - stim_on
        valid = np.isfinite(stim_on) & np.isfinite(latency) & (latency > 0.0)
        values = latency[valid]
        if len(values) == 0:
            return labels
        threshold = float(np.median(values))
        labels[valid & (latency < threshold)] = 1.0
        labels[valid & (latency > threshold)] = 0.0
        return labels
    if target_name == "prior_engaged":
        probability_left = _finite_array(rec.trials.probability_left)
        valid = np.isfinite(stim_on) & np.isfinite(probability_left)
        labels[valid & (probability_left == 0.5)] = 0.0
        labels[valid & (probability_left != 0.5)] = 1.0
        return labels
    raise ValueError(f"unknown derived target {target_name!r}")


def build_derived_trial_samples(
    recs: dict[str, object],
    rids: list[str],
    *,
    window_len: float,
    target_name: str,
) -> list[tuple[str, float, float]]:
    rows = []
    for rid in rids:
        rec = recs[rid]
        labels = per_recording_derived_labels(rec, target_name)
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


def target_balance(trials: list[tuple[str, float, float]], subject_by_rid: dict[str, str], *, min_class_trials: int) -> dict:
    by_recording: dict[str, Counter[int]] = defaultdict(Counter)
    for rid, _t0, target in trials:
        by_recording[rid][int(target)] += 1
    rec_rows = []
    by_subject: dict[str, list[dict]] = defaultdict(list)
    for rid, counts in sorted(by_recording.items()):
        target0 = counts[0]
        target1 = counts[1]
        row = {
            "recording": rid,
            "subject": subject_by_rid[rid],
            "target0": target0,
            "target1": target1,
            "n_trials": target0 + target1,
            "min_class": min(target0, target1),
            "eligible": min(target0, target1) >= min_class_trials,
        }
        rec_rows.append(row)
        by_subject[row["subject"]].append(row)
    subject_rows = []
    for subject, rows in sorted(by_subject.items()):
        subject_rows.append({
            "subject": subject,
            "n_recordings": len(rows),
            "eligible_recordings": sum(1 for row in rows if row["eligible"]),
            "n_trials": sum(row["n_trials"] for row in rows),
            "target0": sum(row["target0"] for row in rows),
            "target1": sum(row["target1"] for row in rows),
        })
    return {
        "n_recordings": len(rec_rows),
        "eligible_recordings": sum(1 for row in rec_rows if row["eligible"]),
        "n_trials": sum(row["n_trials"] for row in rec_rows),
        "recording_rows": rec_rows,
        "subject_rows": subject_rows,
    }


def evaluate_family_row(
    *,
    target_name: str,
    family: str,
    holdout: str,
    family_index: int,
    train_family_true: np.ndarray,
    eval_family_true: np.ndarray,
    train_family_shuffle: np.ndarray,
    eval_family_shuffle: np.ndarray,
    train_total: np.ndarray,
    eval_total: np.ndarray,
    train_y: np.ndarray,
    eval_y: np.ndarray,
    eval_recordings: list[str],
    l2: float,
    min_centered_delta: float,
    min_total_delta: float,
    min_target_improvement: float,
    min_bidirectional_recording_fraction: float,
) -> dict:
    true = evaluate_feature_set(
        name=f"{family}_true",
        train_x=train_family_true[:, [family_index]],
        train_y=train_y,
        eval_x=eval_family_true[:, [family_index]],
        eval_y=eval_y,
        eval_recording_ids=eval_recordings,
        l2=l2,
    )
    shuffle = evaluate_feature_set(
        name=f"{family}_shuffle",
        train_x=train_family_shuffle[:, [family_index]],
        train_y=train_y,
        eval_x=eval_family_shuffle[:, [family_index]],
        eval_y=eval_y,
        eval_recording_ids=eval_recordings,
        l2=l2,
    )
    total = evaluate_feature_set(
        name="total_spikes",
        train_x=train_total,
        train_y=train_y,
        eval_x=eval_total,
        eval_y=eval_y,
        eval_recording_ids=eval_recordings,
        l2=l2,
    )
    paired_shuffle = paired_improvement(true["eval_scores"], shuffle["eval_scores"], eval_y)
    paired_total = paired_improvement(true["eval_scores"], total["eval_scores"], eval_y)
    rec_target_rows = recording_target_rows(true["eval_scores"], shuffle["eval_scores"], eval_y, eval_recordings)
    bidirectional = recording_bidirectional_summary(rec_target_rows, min_target_improvement=min_target_improvement)
    row = {
        "target_mode": target_name,
        "family": family,
        "holdout": holdout,
        "train_auc": true["train_auc"],
        "eval_auc": true["eval_auc"],
        "eval_centered_auc": true["eval_centered_auc"],
        "shuffle_centered_auc": shuffle["eval_centered_auc"],
        "total_centered_auc": total["eval_centered_auc"],
        "centered_delta_vs_shuffle": true["eval_centered_auc"] - shuffle["eval_centered_auc"],
        "centered_delta_vs_total": true["eval_centered_auc"] - total["eval_centered_auc"],
        "paired_improved_vs_shuffle": paired_shuffle["improved_fraction"],
        "target0_improved_vs_shuffle": paired_shuffle["target0_improved_fraction"],
        "target1_improved_vs_shuffle": paired_shuffle["target1_improved_fraction"],
        "paired_improved_vs_total": paired_total["improved_fraction"],
        "target0_improved_vs_total": paired_total["target0_improved_fraction"],
        "target1_improved_vs_total": paired_total["target1_improved_fraction"],
        "n_recordings": bidirectional["n_evaluable_recordings"],
        "n_bidirectional_recordings": bidirectional["n_bidirectional_recordings"],
        "bidirectional_recording_fraction": bidirectional["bidirectional_recording_fraction"],
        "recording_target_rows": rec_target_rows,
    }
    row["decision"] = family_gate_decision(
        row,
        min_centered_delta=min_centered_delta,
        min_total_delta=min_total_delta,
        min_target_improvement=min_target_improvement,
        min_bidirectional_recording_fraction=min_bidirectional_recording_fraction,
    )
    return row


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
    trials = build_derived_trial_samples(vocab["recs"], selected_rids, window_len=window_len, target_name=target_name)
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
    base["decision"] = "derived_target_family_candidate" if base["n_candidates"] else "no_derived_target_family_candidate"
    return base


def render_markdown(report: dict) -> str:
    summary = report["summary"]
    lines = [
        "# Derived Target Family Gate",
        "",
        (
            "No-spend audit for new benchmark/control target definitions derived from "
            "cached trial fields, using the same shared-family model-free promotion gate."
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
            "A derived target is only a training trigger if it passes the same local "
            "gate as prior audits: nonnegative true-vs-shuffle and true-vs-total "
            "deltas, both global target classes >=0.55, and at least 3/4 same-recording "
            "bidirectional support."
        ),
        "",
    ]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=REPO_ROOT / "data/brainsets/ibl_bwm")
    parser.add_argument("--manifest", type=Path, default=REPO_ROOT / "manifests/ibl_bwm_region_matched_candidates_s3_present_support80_hdf5_scored.json")
    parser.add_argument("--target", nargs="*", default=list(DERIVED_TARGETS), choices=list(DERIVED_TARGETS))
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
    parser.add_argument("--out-json", type=Path, default=REPO_ROOT / "docs/derived_target_family_gate.json")
    parser.add_argument("--out-md", type=Path, default=REPO_ROOT / "docs/derived_target_family_gate.md")
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
