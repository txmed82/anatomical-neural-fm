"""Model-free audit of cross-animal anatomical region signal.

This diagnostic removes the transformer and optimizer from the loop. It builds
trial-level parent-region spike-count features, fits a closed-form ridge
classifier on training animals, and evaluates the held-out animal against a
within-recording shuffled-region control.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "vendor" / "torch_brain"))

from torch_brain.dataset import Dataset, DatasetIndex  # noqa: E402
from train import (  # noqa: E402
    _auc,
    build_trial_samples,
    build_vocab,
    map_region_acronyms,
    select_recording_ids,
    split_recordings_by_subject,
    trial_indices_by_recording_target,
)


@dataclass(frozen=True)
class FeatureSpec:
    name: str
    region_control: str


def stable_seed(text: str, seed: int) -> int:
    digest = hashlib.sha256(f"{seed}:{text}".encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "little") % (2**32)


def recording_region_labels(rec, granularity: str, control: str, recording_id: str, seed: int) -> np.ndarray:
    labels = np.asarray(map_region_acronyms(rec.units.region_acronym.astype(str), granularity), dtype=object)
    if control == "none":
        return labels
    if control != "within_recording_shuffle":
        raise ValueError(f"unknown region control {control!r}")
    rng = np.random.default_rng(stable_seed(recording_id, seed))
    shuffled = labels.copy()
    rng.shuffle(shuffled)
    return shuffled


def build_region_vocab(recs, rids: list[str], granularity: str) -> list[str]:
    regions: set[str] = set()
    for rid in rids:
        regions.update(map_region_acronyms(recs[rid].units.region_acronym.astype(str), granularity))
    return sorted(regions)


def make_feature_matrix(
    ds: Dataset,
    recs,
    trials: list[tuple[str, float, float]],
    *,
    regions: list[str],
    region_granularity: str,
    region_control: str,
    seed: int,
    window_len: float,
) -> tuple[np.ndarray, np.ndarray, list[str]]:
    region_to_col = {region: idx for idx, region in enumerate(regions)}
    labels_by_recording = {
        rid: recording_region_labels(recs[rid], region_granularity, region_control, rid, seed)
        for rid in sorted({rid for rid, _t0, _target in trials})
    }
    features = np.zeros((len(trials), len(regions)), dtype=np.float32)
    targets = np.zeros(len(trials), dtype=np.int64)
    recording_ids = []
    for row_idx, (rid, t0, target) in enumerate(trials):
        sample = ds[DatasetIndex(recording_id=rid, start=t0, end=t0 + window_len)]
        spike_units = np.asarray(sample.spikes.unit_index, dtype=np.int64)
        unit_regions = labels_by_recording[rid]
        if spike_units.size:
            spike_regions = unit_regions[spike_units]
            for region, count in zip(*np.unique(spike_regions, return_counts=True)):
                col = region_to_col.get(str(region))
                if col is not None:
                    features[row_idx, col] = float(count)
        targets[row_idx] = int(target)
        recording_ids.append(str(rid))
    return features, targets, recording_ids


def total_spike_feature(region_features: np.ndarray) -> np.ndarray:
    return region_features.sum(axis=1, keepdims=True)


def transform_region_features(region_features: np.ndarray, feature_mode: str) -> np.ndarray:
    if feature_mode == "counts":
        return region_features
    if feature_mode == "fractions":
        totals = total_spike_feature(region_features).astype(np.float32)
        out = np.zeros_like(region_features, dtype=np.float32)
        np.divide(region_features, totals, out=out, where=totals > 0.0)
        return out
    raise ValueError(f"unknown feature_mode {feature_mode!r}")


def zscore_train_eval(train_x: np.ndarray, eval_x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mean = train_x.mean(axis=0, keepdims=True)
    std = train_x.std(axis=0, keepdims=True)
    std[std < 1e-6] = 1.0
    return (train_x - mean) / std, (eval_x - mean) / std


def fit_ridge_scores(
    train_x: np.ndarray,
    train_y: np.ndarray,
    eval_x: np.ndarray,
    *,
    l2: float,
) -> tuple[np.ndarray, np.ndarray]:
    y = np.where(train_y > 0, 1.0, -1.0).astype(np.float64)
    train_z, eval_z = zscore_train_eval(train_x.astype(np.float64), eval_x.astype(np.float64))
    train_design = np.concatenate([train_z, np.ones((train_z.shape[0], 1), dtype=np.float64)], axis=1)
    eval_design = np.concatenate([eval_z, np.ones((eval_z.shape[0], 1), dtype=np.float64)], axis=1)
    penalty = np.eye(train_design.shape[1], dtype=np.float64) * l2
    penalty[-1, -1] = 0.0
    weights = np.linalg.solve(train_design.T @ train_design + penalty, train_design.T @ y)
    return train_design @ weights, eval_design @ weights


def centered_auc(scores: np.ndarray, labels: np.ndarray, recording_ids: list[str]) -> float:
    centered_scores = scores.copy()
    for rid in sorted(set(recording_ids)):
        idx = np.asarray([i for i, value in enumerate(recording_ids) if value == rid], dtype=np.int64)
        if idx.size:
            centered_scores[idx] -= centered_scores[idx].mean()
    return _auc(centered_scores, labels)


def per_recording_auc(scores: np.ndarray, labels: np.ndarray, recording_ids: list[str]) -> dict[str, float]:
    out = {}
    for rid in sorted(set(recording_ids)):
        idx = np.asarray([i for i, value in enumerate(recording_ids) if value == rid], dtype=np.int64)
        out[rid] = _auc(scores[idx], labels[idx])
    return out


def paired_improvement(candidate_scores: np.ndarray, baseline_scores: np.ndarray, labels: np.ndarray) -> dict:
    candidate_true = np.where(labels > 0, candidate_scores, -candidate_scores)
    baseline_true = np.where(labels > 0, baseline_scores, -baseline_scores)
    delta = candidate_true - baseline_true
    target0 = labels <= 0
    target1 = labels > 0
    return {
        "improved_fraction": float(np.mean(delta > 0.0)),
        "target0_improved_fraction": float(np.mean(delta[target0] > 0.0)) if np.any(target0) else float("nan"),
        "target1_improved_fraction": float(np.mean(delta[target1] > 0.0)) if np.any(target1) else float("nan"),
        "mean_true_class_delta": float(np.mean(delta)),
    }


def evaluate_feature_set(
    *,
    name: str,
    train_x: np.ndarray,
    train_y: np.ndarray,
    eval_x: np.ndarray,
    eval_y: np.ndarray,
    eval_recording_ids: list[str],
    l2: float,
) -> dict:
    train_scores, eval_scores = fit_ridge_scores(train_x, train_y, eval_x, l2=l2)
    return {
        "name": name,
        "train_auc": _auc(train_scores, train_y),
        "eval_auc": _auc(eval_scores, eval_y),
        "eval_centered_auc": centered_auc(eval_scores, eval_y, eval_recording_ids),
        "eval_scores": eval_scores,
        "per_recording_auc": per_recording_auc(eval_scores, eval_y, eval_recording_ids),
    }


def summarize_results(results: dict[str, dict], eval_y: np.ndarray, eval_recording_ids: list[str]) -> dict:
    true = results["region_true"]
    shuffle = results["region_shuffle"]
    total = results["total_spikes"]
    recording_deltas = {
        rid: true["per_recording_auc"][rid] - shuffle["per_recording_auc"][rid]
        for rid in sorted(true["per_recording_auc"])
    }
    return {
        "metrics": {
            name: {
                "train_auc": row["train_auc"],
                "eval_auc": row["eval_auc"],
                "eval_centered_auc": row["eval_centered_auc"],
                "per_recording_auc": row["per_recording_auc"],
            }
            for name, row in results.items()
        },
        "deltas": {
            "true_minus_shuffle_auc": true["eval_auc"] - shuffle["eval_auc"],
            "true_minus_shuffle_centered_auc": true["eval_centered_auc"] - shuffle["eval_centered_auc"],
            "true_minus_total_auc": true["eval_auc"] - total["eval_auc"],
            "true_minus_total_centered_auc": true["eval_centered_auc"] - total["eval_centered_auc"],
        },
        "paired_true_vs_shuffle": paired_improvement(true["eval_scores"], shuffle["eval_scores"], eval_y),
        "paired_true_vs_total": paired_improvement(true["eval_scores"], total["eval_scores"], eval_y),
        "recording_deltas_true_minus_shuffle": recording_deltas,
        "recordings_positive_true_minus_shuffle": int(sum(delta > 0.0 for delta in recording_deltas.values())),
        "n_recordings": len(recording_deltas),
        "recording_support_fraction": float(np.mean([delta > 0.0 for delta in recording_deltas.values()])),
    }


def interpret(summary: dict) -> str:
    deltas = summary["deltas"]
    paired = summary["paired_true_vs_shuffle"]
    if (
        deltas["true_minus_shuffle_centered_auc"] >= 0.01
        and paired["target0_improved_fraction"] >= 0.55
        and paired["target1_improved_fraction"] >= 0.55
        and summary["recording_support_fraction"] >= 0.75
    ):
        return "model_free_anatomy_candidate"
    if deltas["true_minus_shuffle_centered_auc"] <= 0.0:
        return "no_model_free_true_region_advantage"
    return "weak_model_free_true_region_advantage"


def render_markdown(report: dict) -> str:
    summary = report["summary"]
    metrics = summary["metrics"]
    lines = [
        "# CSH Model-Free Region Signal Audit",
        "",
        (
            "Closed-form ridge classifier on trial-level parent-region spike counts. "
            "This tests whether the anatomical feature representation has a cross-animal "
            "signal before transformer training."
        ),
        "",
        f"Holdout: `{', '.join(report['holdout'])}`",
        f"Train trials: `{report['n_train_trials']}`",
        f"Eval trials: `{report['n_eval_trials']}`",
        f"Regions: `{report['n_regions']}`",
        "",
        "| feature_set | train_AUC | eval_AUC | eval_centered_AUC |",
        "|---|---:|---:|---:|",
    ]
    for name in ("total_spikes", "region_true", "region_shuffle"):
        row = metrics[name]
        lines.append(
            f"| {name} | {row['train_auc']:.3f} | {row['eval_auc']:.3f} | {row['eval_centered_auc']:.3f} |"
        )
    paired = summary["paired_true_vs_shuffle"]
    lines += [
        "",
        "## True vs Shuffled Region Labels",
        "",
        f"- centered AUC delta: `{summary['deltas']['true_minus_shuffle_centered_auc']:+.3f}`",
        f"- full AUC delta: `{summary['deltas']['true_minus_shuffle_auc']:+.3f}`",
        f"- paired true-class improved: `{paired['improved_fraction']:.3f}`",
        f"- target0 improved: `{paired['target0_improved_fraction']:.3f}`",
        f"- target1 improved: `{paired['target1_improved_fraction']:.3f}`",
        f"- positive recordings: `{summary['recordings_positive_true_minus_shuffle']}/{summary['n_recordings']}`",
        f"- decision: `{summary['decision']}`",
        "",
    ]
    lines += [
        "| recording | true_AUC | shuffle_AUC | delta |",
        "|---|---:|---:|---:|",
    ]
    true_recordings = metrics["region_true"]["per_recording_auc"]
    shuffle_recordings = metrics["region_shuffle"]["per_recording_auc"]
    for rid, delta in summary["recording_deltas_true_minus_shuffle"].items():
        lines.append(f"| {rid} | {true_recordings[rid]:.3f} | {shuffle_recordings[rid]:.3f} | {delta:+.3f} |")
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=REPO_ROOT / "data/brainsets/ibl_bwm")
    parser.add_argument("--manifest", type=Path, default=REPO_ROOT / "manifests/ibl_bwm_region_matched_support80_best6.json")
    parser.add_argument("--holdout", nargs="*", default=["CSH_ZAD_019"])
    parser.add_argument("--target-mode", default="stimulus_side", choices=["choice", "stimulus_side", "feedback", "prior_side"])
    parser.add_argument("--feature-mode", default="counts", choices=["counts", "fractions"])
    parser.add_argument("--region-granularity", default="parent", choices=["fine", "parent", "grandparent"])
    parser.add_argument("--window-len", type=float, default=1.0)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--l2", type=float, default=10.0)
    parser.add_argument("--out-json", type=Path, default=REPO_ROOT / "docs/csh_model_free_region_signal_audit.json")
    parser.add_argument("--out-md", type=Path, default=REPO_ROOT / "docs/csh_model_free_region_signal_audit.md")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ds = Dataset(dataset_dir=args.data_dir, keep_files_open=True)
    selected_recording_ids = select_recording_ids(ds, args.manifest, args.data_dir)
    vocab = build_vocab(ds, args.region_granularity, selected_recording_ids)
    split = split_recordings_by_subject(vocab["subject_by_rid"], args.holdout)
    train_trials = build_trial_samples(vocab["recs"], split.train_rids, args.window_len, args.target_mode)
    eval_trials = build_trial_samples(vocab["recs"], split.eval_rids, args.window_len, args.target_mode)
    regions = build_region_vocab(vocab["recs"], split.train_rids + split.eval_rids, args.region_granularity)

    train_true_x, train_y, _train_recordings = make_feature_matrix(
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
    train_model_x = transform_region_features(train_true_x, args.feature_mode)
    eval_model_x = transform_region_features(eval_true_x, args.feature_mode)
    train_shuffle_model_x = transform_region_features(train_shuffle_x, args.feature_mode)
    eval_shuffle_model_x = transform_region_features(eval_shuffle_x, args.feature_mode)

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
    summary["decision"] = interpret(summary)
    by_recording_target = trial_indices_by_recording_target(train_trials)
    report = {
        "holdout": split.holdout_subjects,
        "train_subjects": split.train_subjects,
        "target_mode": args.target_mode,
        "feature_mode": args.feature_mode,
        "region_granularity": args.region_granularity,
        "window_len": args.window_len,
        "seed": args.seed,
        "l2": args.l2,
        "n_train_trials": len(train_trials),
        "n_eval_trials": len(eval_trials),
        "n_train_recordings": len(by_recording_target),
        "n_eval_recordings": len(set(eval_recordings)),
        "n_regions": len(regions),
        "regions": regions,
        "summary": summary,
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
