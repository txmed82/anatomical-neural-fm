"""Audit ABC cell-type-prior features under the local model-free gate."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "vendor" / "torch_brain"))

from torch_brain.dataset import Dataset  # noqa: E402
from audit_derived_target_family_gate import evaluate_family_row  # noqa: E402
from audit_model_free_region_signal import (  # noqa: E402
    build_region_vocab,
    make_feature_matrix,
    recording_region_unit_fractions,
    total_spike_feature,
    transform_region_features,
)
from audit_shared_family_target_control_gate import summarize_rows  # noqa: E402
from train import TARGET_MODES, build_trial_samples, build_vocab, select_recording_ids, split_recordings_by_subject  # noqa: E402


CELL_CLASS_GROUPS = ("glutamatergic", "gabaergic", "non_neuronal", "modulatory")


def subclass_group(subclass: str) -> str:
    name = subclass.lower()
    if "glut" in name:
        return "glutamatergic"
    if "gaba" in name:
        return "gabaergic"
    if "nn" in name:
        return "non_neuronal"
    return "modulatory"


def load_region_group_priors(path: Path, groups: tuple[str, ...] = CELL_CLASS_GROUPS) -> pd.DataFrame:
    priors = pd.read_parquet(path)
    required = {"region_acronym", "subclass", "proportion"}
    missing = required - set(priors.columns)
    if missing:
        raise ValueError(f"missing prior columns: {sorted(missing)}")
    priors = priors.copy()
    priors["group"] = priors["subclass"].map(subclass_group)
    grouped = (
        priors[priors["group"].isin(groups)]
        .groupby(["region_acronym", "group"], observed=True)["proportion"]
        .sum()
        .reset_index()
    )
    return grouped


def prior_matrix_for_regions(regions: list[str], priors: pd.DataFrame, groups: tuple[str, ...]) -> tuple[np.ndarray, dict]:
    group_to_col = {group: idx for idx, group in enumerate(groups)}
    matrix = np.zeros((len(regions), len(groups)), dtype=np.float32)
    matched = set()
    for row in priors.itertuples(index=False):
        try:
            region_idx = regions.index(str(row.region_acronym))
        except ValueError:
            continue
        group_idx = group_to_col.get(str(row.group))
        if group_idx is None:
            continue
        matrix[region_idx, group_idx] = float(row.proportion)
        matched.add(str(row.region_acronym))
    unknown = [region for region in regions if region not in matched]
    return matrix, {
        "n_regions": len(regions),
        "n_regions_with_priors": len(matched),
        "n_regions_without_priors": len(unknown),
        "regions_without_priors": unknown[:24],
    }


def project_cell_type_features(region_features: np.ndarray, prior_matrix: np.ndarray) -> np.ndarray:
    return region_features.astype(np.float32) @ prior_matrix.astype(np.float32)


def screen_target_holdout(
    *,
    ds: Dataset,
    vocab: dict,
    selected_rids: list[str],
    target_mode: str,
    holdout: str,
    priors: pd.DataFrame,
    groups: tuple[str, ...],
    feature_mode: str,
    window_len: float,
    seed: int,
    l2: float,
    min_centered_delta: float,
    min_total_delta: float,
    min_target_improvement: float,
    min_bidirectional_recording_fraction: float,
) -> tuple[list[dict], dict]:
    split = split_recordings_by_subject(vocab["subject_by_rid"], [holdout])
    train_trials = build_trial_samples(vocab["recs"], split.train_rids, window_len, target_mode)
    eval_trials = build_trial_samples(vocab["recs"], split.eval_rids, window_len, target_mode)
    regions = build_region_vocab(vocab["recs"], selected_rids, "fine")
    prior_matrix, coverage = prior_matrix_for_regions(regions, priors, groups)

    train_true_x, train_y, train_recordings = make_feature_matrix(
        ds,
        vocab["recs"],
        train_trials,
        regions=regions,
        region_granularity="fine",
        region_control="none",
        seed=seed,
        window_len=window_len,
    )
    eval_true_x, eval_y, eval_recordings = make_feature_matrix(
        ds,
        vocab["recs"],
        eval_trials,
        regions=regions,
        region_granularity="fine",
        region_control="none",
        seed=seed,
        window_len=window_len,
    )
    train_shuffle_x, _train_y, _ = make_feature_matrix(
        ds,
        vocab["recs"],
        train_trials,
        regions=regions,
        region_granularity="fine",
        region_control="within_recording_shuffle",
        seed=seed,
        window_len=window_len,
    )
    eval_shuffle_x, _eval_y, _ = make_feature_matrix(
        ds,
        vocab["recs"],
        eval_trials,
        regions=regions,
        region_granularity="fine",
        region_control="within_recording_shuffle",
        seed=seed,
        window_len=window_len,
    )
    true_unit_fractions = recording_region_unit_fractions(
        vocab["recs"],
        selected_rids,
        regions=regions,
        region_granularity="fine",
        region_control="none",
        seed=seed,
    )
    shuffle_unit_fractions = recording_region_unit_fractions(
        vocab["recs"],
        selected_rids,
        regions=regions,
        region_granularity="fine",
        region_control="within_recording_shuffle",
        seed=seed,
    )
    train_true_model = transform_region_features(
        train_true_x,
        feature_mode,
        recording_ids=train_recordings,
        unit_region_fractions=true_unit_fractions,
    )
    eval_true_model = transform_region_features(
        eval_true_x,
        feature_mode,
        recording_ids=eval_recordings,
        unit_region_fractions=true_unit_fractions,
    )
    train_shuffle_model = transform_region_features(
        train_shuffle_x,
        feature_mode,
        recording_ids=train_recordings,
        unit_region_fractions=shuffle_unit_fractions,
    )
    eval_shuffle_model = transform_region_features(
        eval_shuffle_x,
        feature_mode,
        recording_ids=eval_recordings,
        unit_region_fractions=shuffle_unit_fractions,
    )
    train_cell_true = project_cell_type_features(train_true_model, prior_matrix)
    eval_cell_true = project_cell_type_features(eval_true_model, prior_matrix)
    train_cell_shuffle = project_cell_type_features(train_shuffle_model, prior_matrix)
    eval_cell_shuffle = project_cell_type_features(eval_shuffle_model, prior_matrix)
    train_total = total_spike_feature(train_true_x)
    eval_total = total_spike_feature(eval_true_x)

    rows = []
    for group_idx, group in enumerate(groups):
        rows.append(evaluate_family_row(
            target_name=target_mode,
            family=group,
            holdout=holdout,
            family_index=group_idx,
            train_family_true=train_cell_true,
            eval_family_true=eval_cell_true,
            train_family_shuffle=train_cell_shuffle,
            eval_family_shuffle=eval_cell_shuffle,
            train_total=train_total,
            eval_total=eval_total,
            train_y=train_y,
            eval_y=eval_y,
            eval_recordings=eval_recordings,
            l2=l2,
            min_centered_delta=min_centered_delta,
            min_total_delta=min_total_delta,
            min_target_improvement=min_target_improvement,
            min_bidirectional_recording_fraction=min_bidirectional_recording_fraction,
        ))
    return rows, coverage


def precompute_target(
    *,
    ds: Dataset,
    vocab: dict,
    selected_rids: list[str],
    target_mode: str,
    priors: pd.DataFrame,
    groups: tuple[str, ...],
    feature_mode: str,
    window_len: float,
    seed: int,
) -> dict:
    trials = build_trial_samples(vocab["recs"], selected_rids, window_len, target_mode)
    regions = build_region_vocab(vocab["recs"], selected_rids, "fine")
    prior_matrix, coverage = prior_matrix_for_regions(regions, priors, groups)
    true_x, y, recording_ids = make_feature_matrix(
        ds,
        vocab["recs"],
        trials,
        regions=regions,
        region_granularity="fine",
        region_control="none",
        seed=seed,
        window_len=window_len,
    )
    shuffle_x, _shuffle_y, _shuffle_recordings = make_feature_matrix(
        ds,
        vocab["recs"],
        trials,
        regions=regions,
        region_granularity="fine",
        region_control="within_recording_shuffle",
        seed=seed,
        window_len=window_len,
    )
    true_unit_fractions = recording_region_unit_fractions(
        vocab["recs"],
        selected_rids,
        regions=regions,
        region_granularity="fine",
        region_control="none",
        seed=seed,
    )
    shuffle_unit_fractions = recording_region_unit_fractions(
        vocab["recs"],
        selected_rids,
        regions=regions,
        region_granularity="fine",
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
        "target_mode": target_mode,
        "cell_true": project_cell_type_features(true_model_x, prior_matrix),
        "cell_shuffle": project_cell_type_features(shuffle_model_x, prior_matrix),
        "total": total_spike_feature(true_x),
        "y": y,
        "recording_ids": recording_ids,
        "subject_ids": [vocab["subject_by_rid"][rid] for rid in recording_ids],
        "coverage": coverage,
    }


def screen_precomputed(
    payload: dict,
    *,
    holdouts: list[str],
    groups: tuple[str, ...],
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
        for group_idx, group in enumerate(groups):
            rows.append(evaluate_family_row(
                target_name=payload["target_mode"],
                family=group,
                holdout=holdout,
                family_index=group_idx,
                train_family_true=payload["cell_true"][train_mask],
                eval_family_true=payload["cell_true"][eval_mask],
                train_family_shuffle=payload["cell_shuffle"][train_mask],
                eval_family_shuffle=payload["cell_shuffle"][eval_mask],
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


def summarize(rows: list[dict], coverage_rows: list[dict]) -> dict:
    base = summarize_rows(rows)
    base["prior_coverage"] = {
        "min_regions_with_priors": min((row["n_regions_with_priors"] for row in coverage_rows), default=0),
        "max_regions_without_priors": max((row["n_regions_without_priors"] for row in coverage_rows), default=0),
        "example_regions_without_priors": next(
            (row["regions_without_priors"] for row in coverage_rows if row["regions_without_priors"]),
            [],
        ),
    }
    base["decision"] = "cell_type_prior_target_candidate" if base["n_candidates"] else "no_cell_type_prior_target_candidate"
    return base


def render_markdown(report: dict) -> str:
    summary = report["summary"]
    coverage = summary["prior_coverage"]
    lines = [
        "# Cell-Type Prior Target/Control Gate",
        "",
        (
            "No-spend model-free screen that projects fine-region trial spike counts "
            "through ABC Atlas subclass priors, then tests broad cell-class channels "
            "against within-recording shuffled region labels and the total-spike baseline."
        ),
        "",
        f"- rows: `{summary['n_rows']}`",
        f"- candidates: `{summary['n_candidates']}`",
        f"- positive centered-delta rows: `{summary['n_positive_centered_delta']}`",
        f"- max bidirectional recordings: `{summary['max_bidirectional_recordings']}`",
        f"- max bidirectional recording fraction: `{summary['max_bidirectional_recording_fraction']:.3f}`",
        f"- decision: `{summary['decision']}`",
        f"- prior coverage: min regions with priors `{coverage['min_regions_with_priors']}`, max missing `{coverage['max_regions_without_priors']}`",
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
        "## Cell-Class Summary",
        "",
        "| cell class | rows | candidates | positive centered delta | max bidir frac |",
        "|---|---:|---:|---:|---:|",
    ]
    for family, row in summary["by_family"].items():
        lines.append(
            f"| {family} | {row['n_rows']} | {row['n_candidates']} | "
            f"{row['n_positive_centered_delta']} | {row['max_bidirectional_recording_fraction']:.3f} |"
        )
    lines += [
        "",
        "## Top Rows",
        "",
        "| target | cell class | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs |",
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
            "A cell-type-prior feature is only a training trigger if it passes the "
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
    parser.add_argument("--priors-path", type=Path, default=REPO_ROOT / "data/cell_type_priors/region_subclass_priors.parquet")
    parser.add_argument("--target-mode", nargs="*", default=list(TARGET_MODES), choices=list(TARGET_MODES))
    parser.add_argument("--feature-mode", default="recording_centered", choices=["counts", "fractions", "recording_centered", "unit_residuals"])
    parser.add_argument("--window-len", type=float, default=1.0)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--l2", type=float, default=10.0)
    parser.add_argument("--min-centered-delta", type=float, default=0.0)
    parser.add_argument("--min-total-delta", type=float, default=0.0)
    parser.add_argument("--min-target-improvement", type=float, default=0.55)
    parser.add_argument("--min-bidirectional-recording-fraction", type=float, default=0.75)
    parser.add_argument("--out-json", type=Path, default=REPO_ROOT / "docs/cell_type_prior_target_control_gate.json")
    parser.add_argument("--out-md", type=Path, default=REPO_ROOT / "docs/cell_type_prior_target_control_gate.md")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    priors = load_region_group_priors(args.priors_path)
    groups = CELL_CLASS_GROUPS
    ds = Dataset(dataset_dir=args.data_dir, keep_files_open=True)
    selected_rids = select_recording_ids(ds, args.manifest, args.data_dir)
    vocab = build_vocab(ds, "fine", selected_rids)
    holdouts = sorted(set(vocab["subject_by_rid"].values()))
    rows = []
    coverage_rows = []
    for target_mode in args.target_mode:
        payload = precompute_target(
            ds=ds,
            vocab=vocab,
            selected_rids=selected_rids,
            target_mode=target_mode,
            priors=priors,
            groups=groups,
            feature_mode=args.feature_mode,
            window_len=args.window_len,
            seed=args.seed,
        )
        rows.extend(screen_precomputed(
            payload,
            holdouts=holdouts,
            groups=groups,
            l2=args.l2,
            min_centered_delta=args.min_centered_delta,
            min_total_delta=args.min_total_delta,
            min_target_improvement=args.min_target_improvement,
            min_bidirectional_recording_fraction=args.min_bidirectional_recording_fraction,
        ))
        coverage_rows.append(payload["coverage"])
    report = {
        "manifest": str(args.manifest),
        "targets": list(args.target_mode),
        "cell_class_groups": list(groups),
        "feature_mode": args.feature_mode,
        "thresholds": {
            "min_centered_delta": args.min_centered_delta,
            "min_total_delta": args.min_total_delta,
            "min_target_improvement": args.min_target_improvement,
            "min_bidirectional_recording_fraction": args.min_bidirectional_recording_fraction,
        },
        "summary": summarize(rows, coverage_rows),
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
