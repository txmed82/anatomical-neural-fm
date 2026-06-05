"""Audit left/right anatomical family features under the local model-free gate."""
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
from audit_model_free_positive_holdouts import recording_target_rows  # noqa: E402
from audit_model_free_recording_bidirectional_gate import recording_bidirectional_summary  # noqa: E402
from audit_model_free_region_signal import (  # noqa: E402
    centered_auc,
    evaluate_feature_set,
    fit_ridge_scores,
    paired_improvement,
    recording_region_labels,
    total_spike_feature,
    transform_region_features,
)
from audit_shared_family_target_control_gate import family_gate_decision, summarize_rows  # noqa: E402
from audit_signed_wheel_direction_family_gate import (  # noqa: E402
    TARGET_NAME as SIGNED_WHEEL_TARGET,
    build_signed_wheel_direction_trial_samples,
)
from scan_model_free_region_family_candidates import present_family_definitions  # noqa: E402
from train import (  # noqa: E402
    TARGET_MODES,
    build_trial_samples,
    build_vocab,
    select_recording_ids,
    split_recordings_by_subject,
)


DIRECTION_TARGETS = ("choice", "stimulus_side", SIGNED_WHEEL_TARGET)
DEFAULT_FAMILIES = (
    "broad_named_anatomy",
    "thalamic",
    "hippocampal_formation",
    "fiber_tracts",
    "midbrain",
    "cortical_visual",
    "cortical_sensorimotor",
    "cortical_retrosplenial",
    "basal_ganglia",
    "brainstem_interbrain",
)


def unit_hemisphere(mlapdv: np.ndarray) -> np.ndarray:
    ml = np.asarray(mlapdv, dtype=np.float64)[:, 0]
    out = np.full(len(ml), -1, dtype=np.int8)
    finite = np.isfinite(ml)
    out[finite & (ml <= 0.0)] = 0
    out[finite & (ml > 0.0)] = 1
    return out


def lateralized_feature_names(families: list[str]) -> list[str]:
    return [f"{family}_{side}" for family in families for side in ("left", "right")]


def recording_unit_lateralized_cols(
    rec,
    *,
    families: dict[str, tuple[str, ...]],
    family_names: list[str],
    region_granularity: str,
    region_control: str,
    recording_id: str,
    seed: int,
) -> list[list[int]]:
    labels = recording_region_labels(rec, region_granularity, region_control, recording_id, seed)
    hemispheres = unit_hemisphere(rec.units.mlapdv)
    memberships = {family: set(regions) for family, regions in families.items()}
    cols: list[list[int]] = []
    for label, hemi in zip(labels, hemispheres):
        unit_cols = []
        if hemi >= 0:
            for family_idx, family in enumerate(family_names):
                if str(label) in memberships[family]:
                    unit_cols.append(2 * family_idx + int(hemi))
        cols.append(unit_cols)
    return cols


def make_lateralized_family_feature_matrix(
    ds: Dataset,
    recs,
    trials: list[tuple[str, float, float]],
    *,
    families: dict[str, tuple[str, ...]],
    family_names: list[str],
    region_granularity: str,
    region_control: str,
    seed: int,
    window_len: float,
) -> tuple[np.ndarray, np.ndarray, list[str]]:
    unit_cols_by_recording = {
        rid: recording_unit_lateralized_cols(
            recs[rid],
            families=families,
            family_names=family_names,
            region_granularity=region_granularity,
            region_control=region_control,
            recording_id=rid,
            seed=seed,
        )
        for rid in sorted({rid for rid, _t0, _target in trials})
    }
    features = np.zeros((len(trials), 2 * len(family_names)), dtype=np.float32)
    targets = np.zeros(len(trials), dtype=np.int64)
    recording_ids = []
    for row_idx, (rid, t0, target) in enumerate(trials):
        sample = ds[DatasetIndex(recording_id=rid, start=t0, end=t0 + window_len)]
        spike_units = np.asarray(sample.spikes.unit_index, dtype=np.int64)
        unit_cols = unit_cols_by_recording[rid]
        for unit_idx in spike_units:
            if unit_idx < 0 or unit_idx >= len(unit_cols):
                continue
            for col in unit_cols[int(unit_idx)]:
                features[row_idx, col] += 1.0
        targets[row_idx] = int(target)
        recording_ids.append(str(rid))
    return features, targets, recording_ids


def build_target_samples(recs, rids: list[str], *, target_name: str, window_len: float) -> list[tuple[str, float, float]]:
    if target_name in TARGET_MODES:
        return build_trial_samples(recs, rids, window_len, target_name)
    if target_name == SIGNED_WHEEL_TARGET:
        return build_signed_wheel_direction_trial_samples(
            recs,
            rids,
            window_len=window_len,
            target_name=target_name,
        )
    raise ValueError(f"unknown target {target_name!r}")


def evaluate_lateralized_family_row(
    *,
    target_name: str,
    family: str,
    holdout: str,
    family_index: int,
    train_true: np.ndarray,
    eval_true: np.ndarray,
    train_shuffle: np.ndarray,
    eval_shuffle: np.ndarray,
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
    cols = [2 * family_index, 2 * family_index + 1]
    true = evaluate_feature_set(
        name=f"{family}_lateralized_true",
        train_x=train_true[:, cols],
        train_y=train_y,
        eval_x=eval_true[:, cols],
        eval_y=eval_y,
        eval_recording_ids=eval_recordings,
        l2=l2,
    )
    shuffle = evaluate_feature_set(
        name=f"{family}_lateralized_shuffle",
        train_x=train_shuffle[:, cols],
        train_y=train_y,
        eval_x=eval_shuffle[:, cols],
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
    true_lr_scores_train, true_lr_scores_eval = fit_ridge_scores(
        train_true[:, cols],
        train_y,
        eval_true[:, cols],
        l2=l2,
    )
    left_only = evaluate_feature_set(
        name=f"{family}_left",
        train_x=train_true[:, [cols[0]]],
        train_y=train_y,
        eval_x=eval_true[:, [cols[0]]],
        eval_y=eval_y,
        eval_recording_ids=eval_recordings,
        l2=l2,
    )
    right_only = evaluate_feature_set(
        name=f"{family}_right",
        train_x=train_true[:, [cols[1]]],
        train_y=train_y,
        eval_x=eval_true[:, [cols[1]]],
        eval_y=eval_y,
        eval_recording_ids=eval_recordings,
        l2=l2,
    )
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
        "target0_improved_vs_shuffle": paired_shuffle["target0_improved_fraction"],
        "target1_improved_vs_shuffle": paired_shuffle["target1_improved_fraction"],
        "target0_improved_vs_total": paired_total["target0_improved_fraction"],
        "target1_improved_vs_total": paired_total["target1_improved_fraction"],
        "n_recordings": bidirectional["n_evaluable_recordings"],
        "n_bidirectional_recordings": bidirectional["n_bidirectional_recordings"],
        "bidirectional_recording_fraction": bidirectional["bidirectional_recording_fraction"],
        "left_centered_auc": left_only["eval_centered_auc"],
        "right_centered_auc": right_only["eval_centered_auc"],
        "lateralized_centered_auc": centered_auc(true_lr_scores_eval, eval_y, eval_recordings),
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
) -> dict:
    trials = build_target_samples(vocab["recs"], selected_rids, target_name=target_name, window_len=window_len)
    regions = sorted({
        region
        for rid in selected_rids
        for region in recording_region_labels(vocab["recs"][rid], region_granularity, "none", rid, seed)
    })
    family_defs = present_family_definitions(regions)
    selected_family_defs = {family: family_defs[family] for family in families if family in family_defs}
    family_names = list(selected_family_defs)
    true_x, y, recording_ids = make_lateralized_family_feature_matrix(
        ds,
        vocab["recs"],
        trials,
        families=selected_family_defs,
        family_names=family_names,
        region_granularity=region_granularity,
        region_control="none",
        seed=seed,
        window_len=window_len,
    )
    shuffle_x, _shuffle_y, _shuffle_recordings = make_lateralized_family_feature_matrix(
        ds,
        vocab["recs"],
        trials,
        families=selected_family_defs,
        family_names=family_names,
        region_granularity=region_granularity,
        region_control="within_recording_shuffle",
        seed=seed,
        window_len=window_len,
    )
    true_model_x = transform_region_features(true_x, feature_mode, recording_ids=recording_ids)
    shuffle_model_x = transform_region_features(shuffle_x, feature_mode, recording_ids=recording_ids)
    return {
        "target_mode": target_name,
        "family_names": family_names,
        "feature_names": lateralized_feature_names(family_names),
        "family_true": true_model_x,
        "family_shuffle": shuffle_model_x,
        "total": total_spike_feature(true_x),
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
        for family_idx, family in enumerate(payload["family_names"]):
            rows.append(evaluate_lateralized_family_row(
                target_name=payload["target_mode"],
                family=family,
                holdout=holdout,
                family_index=family_idx,
                train_true=payload["family_true"][train_mask],
                eval_true=payload["family_true"][eval_mask],
                train_shuffle=payload["family_shuffle"][train_mask],
                eval_shuffle=payload["family_shuffle"][eval_mask],
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
    base["decision"] = (
        "lateralized_family_target_candidate"
        if base["n_candidates"]
        else "no_lateralized_family_target_candidate"
    )
    base["gpu_training_ready"] = False
    base["next_action"] = (
        "Validate lateralized-family candidates across shuffle seeds before GPU training."
        if base["n_candidates"]
        else "Do not train: lateralized family features do not pass the strict local gate."
    )
    return base


def render_markdown(report: dict) -> str:
    summary = report["summary"]
    lines = [
        "# Lateralized Family Target Gate",
        "",
        (
            "No-spend model-free screen for left/right anatomical family count channels. "
            "Each family contributes two features, left and right hemisphere, and is tested "
            "against within-recording shuffled anatomy and total-spike controls."
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
        "## Top Rows",
        "",
        "| target | family | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs | left/right auc |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary["top_rows"][:14]:
        lines.append(
            f"| {row['target_mode']} | {row['family']} | {row['holdout']} | {row['decision']} | "
            f"{row['centered_delta_vs_shuffle']:+.3f} | {row['centered_delta_vs_total']:+.3f} | "
            f"{row['target0_improved_vs_shuffle']:.3f} | {row['target1_improved_vs_shuffle']:.3f} | "
            f"{row['n_bidirectional_recordings']}/{row['n_recordings']} | "
            f"{row['left_centered_auc']:.3f}/{row['right_centered_auc']:.3f} |"
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
    parser.add_argument("--target", nargs="*", default=list(DIRECTION_TARGETS), choices=list(DIRECTION_TARGETS))
    parser.add_argument("--family", nargs="*", default=list(DEFAULT_FAMILIES))
    parser.add_argument(
        "--feature-mode",
        default="recording_centered",
        choices=["counts", "fractions", "recording_centered", "recording_zscore"],
    )
    parser.add_argument("--region-granularity", default="parent", choices=["fine", "parent", "grandparent"])
    parser.add_argument("--window-len", type=float, default=1.0)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--l2", type=float, default=10.0)
    parser.add_argument("--min-centered-delta", type=float, default=0.0)
    parser.add_argument("--min-total-delta", type=float, default=0.0)
    parser.add_argument("--min-target-improvement", type=float, default=0.55)
    parser.add_argument("--min-bidirectional-recording-fraction", type=float, default=0.75)
    parser.add_argument("--out-json", type=Path, default=REPO_ROOT / "docs/lateralized_family_target_gate.json")
    parser.add_argument("--out-md", type=Path, default=REPO_ROOT / "docs/lateralized_family_target_gate.md")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ds = Dataset(dataset_dir=args.data_dir, keep_files_open=True)
    selected_rids = select_recording_ids(ds, args.manifest, args.data_dir)
    vocab = build_vocab(ds, args.region_granularity, selected_rids)
    holdouts = sorted(set(vocab["subject_by_rid"].values()))
    rows = []
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
        "targets": list(args.target),
        "families": list(args.family),
        "feature_mode": args.feature_mode,
        "region_granularity": args.region_granularity,
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
