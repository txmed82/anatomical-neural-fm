"""Screen shared anatomical families across targets under the local model-free gate."""
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
from audit_model_free_positive_holdouts import recording_target_rows  # noqa: E402
from audit_model_free_recording_bidirectional_gate import recording_bidirectional_summary  # noqa: E402
from audit_model_free_region_signal import (  # noqa: E402
    build_region_vocab,
    evaluate_feature_set,
    make_feature_matrix,
    paired_improvement,
    per_recording_auc,
    recording_region_unit_fractions,
    total_spike_feature,
    transform_region_features,
)
from scan_model_free_region_family_candidates import aggregate_features, present_family_definitions  # noqa: E402
from train import TARGET_MODES, build_trial_samples, build_vocab, select_recording_ids, split_recordings_by_subject  # noqa: E402


DEFAULT_FAMILIES = ("broad_named_anatomy", "thalamic", "hippocampal_formation", "fiber_tracts")


def family_gate_decision(
    row: dict,
    *,
    min_centered_delta: float,
    min_total_delta: float,
    min_target_improvement: float,
    min_bidirectional_recording_fraction: float,
) -> str:
    if row["centered_delta_vs_shuffle"] < min_centered_delta:
        return "reject: shuffle"
    if row["centered_delta_vs_total"] < min_total_delta:
        return "reject: total baseline"
    if row["target0_improved_vs_shuffle"] < min_target_improvement:
        return "reject: target0"
    if row["target1_improved_vs_shuffle"] < min_target_improvement:
        return "reject: target1"
    if row["bidirectional_recording_fraction"] < min_bidirectional_recording_fraction:
        return "reject: recording bidirectionality"
    return "candidate"


def summarize_rows(rows: list[dict]) -> dict:
    candidates = [row for row in rows if row["decision"] == "candidate"]
    positive = [row for row in rows if row["centered_delta_vs_shuffle"] > 0.0]
    by_target = {}
    for target in sorted({row["target_mode"] for row in rows}):
        target_rows = [row for row in rows if row["target_mode"] == target]
        by_target[target] = {
            "n_rows": len(target_rows),
            "n_candidates": sum(1 for row in target_rows if row["decision"] == "candidate"),
            "n_positive_centered_delta": sum(1 for row in target_rows if row["centered_delta_vs_shuffle"] > 0.0),
            "max_bidirectional_recording_fraction": max(
                (row["bidirectional_recording_fraction"] for row in target_rows),
                default=0.0,
            ),
        }
    by_family = {}
    for family in sorted({row["family"] for row in rows}):
        family_rows = [row for row in rows if row["family"] == family]
        by_family[family] = {
            "n_rows": len(family_rows),
            "n_candidates": sum(1 for row in family_rows if row["decision"] == "candidate"),
            "n_positive_centered_delta": sum(1 for row in family_rows if row["centered_delta_vs_shuffle"] > 0.0),
            "max_bidirectional_recording_fraction": max(
                (row["bidirectional_recording_fraction"] for row in family_rows),
                default=0.0,
            ),
        }
    top_rows = sorted(
        rows,
        key=lambda row: (
            row["decision"] == "candidate",
            row["n_bidirectional_recordings"],
            row["bidirectional_recording_fraction"],
            row["centered_delta_vs_shuffle"],
            min(row["target0_improved_vs_shuffle"], row["target1_improved_vs_shuffle"]),
        ),
        reverse=True,
    )
    return {
        "n_rows": len(rows),
        "n_candidates": len(candidates),
        "n_positive_centered_delta": len(positive),
        "max_bidirectional_recordings": max((row["n_bidirectional_recordings"] for row in rows), default=0),
        "max_bidirectional_recording_fraction": max(
            (row["bidirectional_recording_fraction"] for row in rows),
            default=0.0,
        ),
        "candidate_rows": [
            {"target_mode": row["target_mode"], "family": row["family"], "holdout": row["holdout"]}
            for row in candidates
        ],
        "by_target": by_target,
        "by_family": by_family,
        "top_rows": top_rows[:16],
        "decision": "shared_family_target_candidate" if candidates else "no_shared_family_target_candidate",
    }


def evaluate_family_row(
    *,
    target_mode: str,
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
    true_recording_auc = per_recording_auc(true["eval_scores"], eval_y, eval_recordings)
    shuffle_recording_auc = per_recording_auc(shuffle["eval_scores"], eval_y, eval_recordings)
    recording_deltas = {
        rid: true_recording_auc[rid] - shuffle_recording_auc[rid]
        for rid in sorted(true_recording_auc)
    }
    rec_target_rows = recording_target_rows(true["eval_scores"], shuffle["eval_scores"], eval_y, eval_recordings)
    bidirectional = recording_bidirectional_summary(
        rec_target_rows,
        min_target_improvement=min_target_improvement,
    )
    row = {
        "target_mode": target_mode,
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
        "recordings_positive_vs_shuffle": int(sum(delta > 0.0 for delta in recording_deltas.values())),
        "n_recordings": len(recording_deltas),
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


def screen_target_holdout(
    *,
    ds: Dataset,
    vocab: dict,
    selected_rids: list[str],
    target_mode: str,
    holdout: str,
    families: tuple[str, ...],
    feature_mode: str,
    region_granularity: str,
    window_len: float,
    seed: int,
    l2: float,
    min_centered_delta: float,
    min_total_delta: float,
    min_target_improvement: float,
    min_bidirectional_recording_fraction: float,
) -> list[dict]:
    split = split_recordings_by_subject(vocab["subject_by_rid"], [holdout])
    train_trials = build_trial_samples(vocab["recs"], split.train_rids, window_len, target_mode)
    eval_trials = build_trial_samples(vocab["recs"], split.eval_rids, window_len, target_mode)
    regions = build_region_vocab(vocab["recs"], split.train_rids + split.eval_rids, region_granularity)
    family_defs = present_family_definitions(regions)
    selected_family_defs = {family: family_defs[family] for family in families if family in family_defs}
    if not selected_family_defs:
        return []
    family_names = list(selected_family_defs)

    train_true_x, train_y, train_recordings = make_feature_matrix(
        ds,
        vocab["recs"],
        train_trials,
        regions=regions,
        region_granularity=region_granularity,
        region_control="none",
        seed=seed,
        window_len=window_len,
    )
    eval_true_x, eval_y, eval_recordings = make_feature_matrix(
        ds,
        vocab["recs"],
        eval_trials,
        regions=regions,
        region_granularity=region_granularity,
        region_control="none",
        seed=seed,
        window_len=window_len,
    )
    train_shuffle_x, _train_y, _ = make_feature_matrix(
        ds,
        vocab["recs"],
        train_trials,
        regions=regions,
        region_granularity=region_granularity,
        region_control="within_recording_shuffle",
        seed=seed,
        window_len=window_len,
    )
    eval_shuffle_x, _eval_y, _ = make_feature_matrix(
        ds,
        vocab["recs"],
        eval_trials,
        regions=regions,
        region_granularity=region_granularity,
        region_control="within_recording_shuffle",
        seed=seed,
        window_len=window_len,
    )
    true_unit_fractions = recording_region_unit_fractions(
        vocab["recs"],
        split.train_rids + split.eval_rids,
        regions=regions,
        region_granularity=region_granularity,
        region_control="none",
        seed=seed,
    )
    shuffle_unit_fractions = recording_region_unit_fractions(
        vocab["recs"],
        split.train_rids + split.eval_rids,
        regions=regions,
        region_granularity=region_granularity,
        region_control="within_recording_shuffle",
        seed=seed,
    )
    train_model_x = transform_region_features(
        train_true_x,
        feature_mode,
        recording_ids=train_recordings,
        unit_region_fractions=true_unit_fractions,
    )
    eval_model_x = transform_region_features(
        eval_true_x,
        feature_mode,
        recording_ids=eval_recordings,
        unit_region_fractions=true_unit_fractions,
    )
    train_shuffle_model_x = transform_region_features(
        train_shuffle_x,
        feature_mode,
        recording_ids=train_recordings,
        unit_region_fractions=shuffle_unit_fractions,
    )
    eval_shuffle_model_x = transform_region_features(
        eval_shuffle_x,
        feature_mode,
        recording_ids=eval_recordings,
        unit_region_fractions=shuffle_unit_fractions,
    )
    train_family_true = aggregate_features(train_model_x, regions, selected_family_defs)
    eval_family_true = aggregate_features(eval_model_x, regions, selected_family_defs)
    train_family_shuffle = aggregate_features(train_shuffle_model_x, regions, selected_family_defs)
    eval_family_shuffle = aggregate_features(eval_shuffle_model_x, regions, selected_family_defs)
    train_total = total_spike_feature(train_true_x)
    eval_total = total_spike_feature(eval_true_x)

    return [
        evaluate_family_row(
            target_mode=target_mode,
            family=family,
            holdout=holdout,
            family_index=family_idx,
            train_family_true=train_family_true,
            eval_family_true=eval_family_true,
            train_family_shuffle=train_family_shuffle,
            eval_family_shuffle=eval_family_shuffle,
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
        )
        for family_idx, family in enumerate(family_names)
    ]


def precompute_target_mode(
    *,
    ds: Dataset,
    vocab: dict,
    selected_rids: list[str],
    target_mode: str,
    families: tuple[str, ...],
    feature_mode: str,
    region_granularity: str,
    window_len: float,
    seed: int,
) -> dict:
    trials = build_trial_samples(vocab["recs"], selected_rids, window_len, target_mode)
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
        "target_mode": target_mode,
        "family_names": family_names,
        "family_true": aggregate_features(true_model_x, regions, selected_family_defs),
        "family_shuffle": aggregate_features(shuffle_model_x, regions, selected_family_defs),
        "total": total_spike_feature(true_x),
        "y": y,
        "recording_ids": recording_ids,
        "subject_ids": [vocab["subject_by_rid"][rid] for rid in recording_ids],
    }


def screen_precomputed_target(
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
        train_recordings = [rid for rid, use in zip(payload["recording_ids"], train_mask) if bool(use)]
        eval_recordings = [rid for rid, use in zip(payload["recording_ids"], eval_mask) if bool(use)]
        if len(set(train_recordings)) == 0 or len(set(eval_recordings)) == 0:
            continue
        for family_idx, family in enumerate(payload["family_names"]):
            rows.append(
                evaluate_family_row(
                    target_mode=payload["target_mode"],
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
                )
            )
    return rows


def render_markdown(report: dict) -> str:
    summary = report["summary"]
    lines = [
        "# Shared-Family Target/Control Gate",
        "",
        (
            "No-spend model-free screen for the next benchmark redesign. Each row is "
            "a single shared anatomical family, target mode, and held-out subject. "
            "The true family feature must beat within-recording shuffled labels, beat "
            "the total-spike baseline, and satisfy global plus same-recording "
            "bidirectional target support."
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
        "## Family Summary",
        "",
        "| family | rows | candidates | positive centered delta | max bidir frac |",
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
        "| target | family | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs |",
        "|---|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in summary["top_rows"][:14]:
        lines.append(
            f"| {row['target_mode']} | {row['family']} | {row['holdout']} | "
            f"{row['decision']} | {row['centered_delta_vs_shuffle']:+.3f} | "
            f"{row['centered_delta_vs_total']:+.3f} | "
            f"{row['target0_improved_vs_shuffle']:.3f} | "
            f"{row['target1_improved_vs_shuffle']:.3f} | "
            f"{row['n_bidirectional_recordings']}/{row['n_recordings']} |"
        )
    lines += [
        "",
        "## Decision",
        "",
        (
            "A GPU run is justified only if this screen yields a candidate or a very "
            "near miss with clear same-recording bidirectional support. Otherwise the "
            "next move is another local target/control redesign."
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
    parser.add_argument("--target-mode", nargs="*", default=list(TARGET_MODES), choices=TARGET_MODES)
    parser.add_argument("--family", nargs="*", default=list(DEFAULT_FAMILIES))
    parser.add_argument(
        "--feature-mode",
        default="recording_centered",
        choices=["counts", "fractions", "recording_centered", "recording_zscore", "unit_residuals"],
    )
    parser.add_argument("--region-granularity", default="parent", choices=["fine", "parent", "grandparent"])
    parser.add_argument("--window-len", type=float, default=1.0)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--l2", type=float, default=10.0)
    parser.add_argument("--min-centered-delta", type=float, default=0.01)
    parser.add_argument("--min-total-delta", type=float, default=0.0)
    parser.add_argument("--min-target-improvement", type=float, default=0.55)
    parser.add_argument("--min-bidirectional-recording-fraction", type=float, default=0.75)
    parser.add_argument("--out-json", type=Path, default=REPO_ROOT / "docs/shared_family_target_control_gate.json")
    parser.add_argument("--out-md", type=Path, default=REPO_ROOT / "docs/shared_family_target_control_gate.md")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ds = Dataset(dataset_dir=args.data_dir, keep_files_open=True)
    selected_rids = select_recording_ids(ds, args.manifest, args.data_dir)
    vocab = build_vocab(ds, args.region_granularity, selected_rids)
    holdouts = sorted(set(vocab["subject_by_rid"].values()))
    rows = []
    for target_mode in args.target_mode:
        payload = precompute_target_mode(
            ds=ds,
            vocab=vocab,
            selected_rids=selected_rids,
            target_mode=target_mode,
            families=tuple(args.family),
            feature_mode=args.feature_mode,
            region_granularity=args.region_granularity,
            window_len=args.window_len,
            seed=args.seed,
        )
        rows.extend(
            screen_precomputed_target(
                payload,
                holdouts=holdouts,
                l2=args.l2,
                min_centered_delta=args.min_centered_delta,
                min_total_delta=args.min_total_delta,
                min_target_improvement=args.min_target_improvement,
                min_bidirectional_recording_fraction=args.min_bidirectional_recording_fraction,
            )
        )
    report = {
        "manifest": str(args.manifest),
        "target_modes": list(args.target_mode),
        "families": list(args.family),
        "feature_mode": args.feature_mode,
        "region_granularity": args.region_granularity,
        "thresholds": {
            "min_centered_delta": args.min_centered_delta,
            "min_total_delta": args.min_total_delta,
            "min_target_improvement": args.min_target_improvement,
            "min_bidirectional_recording_fraction": args.min_bidirectional_recording_fraction,
        },
        "summary": summarize_rows(rows),
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
