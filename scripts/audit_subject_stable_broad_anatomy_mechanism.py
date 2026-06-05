"""Decompose subject-stable broad-anatomy near misses by family contribution."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "vendor" / "torch_brain"))

from audit_family_near_miss_mechanism import (  # noqa: E402
    classify_family_row,
    family_contribution_rows,
    recording_family_rows,
)
from audit_model_free_positive_holdouts import fit_region_weights  # noqa: E402
from audit_model_free_region_signal import zscore_train_eval  # noqa: E402
from audit_derived_target_family_gate import (  # noqa: E402
    evaluate_family_row,
    precompute_target as precompute_derived_target,
)
from audit_reaction_dynamics_target_family_gate import precompute_target as precompute_reaction_target  # noqa: E402
from audit_wheel_target_family_gate import precompute_target as precompute_wheel_target  # noqa: E402
from scan_model_free_region_family_candidates import FAMILY_DEFINITIONS  # noqa: E402
from torch_brain.dataset import Dataset  # noqa: E402
from train import build_vocab, select_recording_ids  # noqa: E402


SOURCE_PRECOMPUTERS = {
    "derived_recording_centered": precompute_derived_target,
    "reaction_recording_centered": precompute_reaction_target,
    "wheel_targets": precompute_wheel_target,
}


def source_feature_mode(source: str) -> str:
    if source.endswith("_recording_centered"):
        return "recording_centered"
    if source.endswith("_counts"):
        return "counts"
    if source.endswith("_fractions"):
        return "fractions"
    if source.endswith("_unit_residuals"):
        return "unit_residuals"
    if source == "wheel_targets":
        return "recording_centered"
    raise ValueError(f"unknown source feature mode for {source!r}")


def source_kind(source: str) -> str:
    if source.startswith("derived_"):
        return "derived"
    if source.startswith("reaction_"):
        return "reaction"
    if source == "wheel_targets":
        return "wheel"
    raise ValueError(f"unknown source kind for {source!r}")


def contribution_audit_row(
    payload: dict,
    stable_row: dict,
    *,
    l2: float,
    min_centered_delta: float,
    min_total_delta: float,
    min_target_improvement: float,
    min_bidirectional_recording_fraction: float,
    top_recording_families: int,
) -> dict:
    subject_ids = np.asarray(payload["subject_ids"], dtype=object)
    train_mask = subject_ids != stable_row["holdout"]
    eval_mask = subject_ids == stable_row["holdout"]
    if not np.any(train_mask) or not np.any(eval_mask):
        raise ValueError(f"holdout {stable_row['holdout']!r} has no train/eval split")
    train_y = payload["y"][train_mask]
    eval_y = payload["y"][eval_mask]
    if len(set(train_y)) < 2 or len(set(eval_y)) < 2:
        raise ValueError(f"holdout {stable_row['holdout']!r} lacks both target classes")

    true_weights = fit_region_weights(payload["family_true"][train_mask], train_y, l2=l2)
    shuffle_weights = fit_region_weights(payload["family_shuffle"][train_mask], train_y, l2=l2)
    _train_true_z, eval_true_z = zscore_train_eval(
        payload["family_true"][train_mask].astype(np.float64),
        payload["family_true"][eval_mask].astype(np.float64),
    )
    _train_shuffle_z, eval_shuffle_z = zscore_train_eval(
        payload["family_shuffle"][train_mask].astype(np.float64),
        payload["family_shuffle"][eval_mask].astype(np.float64),
    )
    eval_recordings = [rid for rid, use in zip(payload["recording_ids"], eval_mask) if bool(use)]
    family_rows = family_contribution_rows(
        payload["family_names"],
        eval_true_z * true_weights,
        eval_shuffle_z * shuffle_weights,
        eval_y,
        eval_recordings,
    )
    for row in family_rows:
        row["classification"] = classify_family_row(row, min_target_improvement=min_target_improvement)
    bidirectional = [
        row["family"] for row in family_rows if row["classification"] == "bidirectional_family_candidate"
    ]
    confirmations = []
    for family in bidirectional:
        family_index = payload["family_names"].index(family)
        confirmations.append(evaluate_family_row(
            target_name=payload["target_mode"],
            family=family,
            holdout=stable_row["holdout"],
            family_index=family_index,
            train_family_true=payload["family_true"][train_mask],
            eval_family_true=payload["family_true"][eval_mask],
            train_family_shuffle=payload["family_shuffle"][train_mask],
            eval_family_shuffle=payload["family_shuffle"][eval_mask],
            train_total=payload["total"][train_mask],
            eval_total=payload["total"][eval_mask],
            train_y=train_y,
            eval_y=eval_y,
            eval_recordings=eval_recordings,
            l2=l2,
            min_centered_delta=min_centered_delta,
            min_total_delta=min_total_delta,
            min_target_improvement=min_target_improvement,
            min_bidirectional_recording_fraction=min_bidirectional_recording_fraction,
        ))
    broad_rows = [row for row in family_rows if row["family"] == stable_row["feature"]]
    return {
        "source": stable_row["source"],
        "target_mode": stable_row["target_mode"],
        "feature_mode": source_feature_mode(stable_row["source"]),
        "holdout": stable_row["holdout"],
        "gate_row": stable_row,
        "n_families": len(family_rows),
        "bidirectional_family_candidates": bidirectional,
        "family_gate_confirmations": confirmations,
        "family_gate_candidates": [row for row in confirmations if row["decision"] == "candidate"],
        "broad_family_contribution": broad_rows[0] if broad_rows else None,
        "top_family_rows": family_rows,
        "recording_family_rows": recording_family_rows(family_rows, top_n=top_recording_families),
    }


def summarize_rows(rows: list[dict]) -> dict:
    rows_with_candidates = [row for row in rows if row["bidirectional_family_candidates"]]
    rows_with_gate_candidates = [row for row in rows if row["family_gate_candidates"]]
    broad_classes = {}
    for row in rows:
        broad = row.get("broad_family_contribution") or {}
        broad_classes[broad.get("classification", "missing")] = broad_classes.get(
            broad.get("classification", "missing"),
            0,
        ) + 1
    return {
        "n_subject_stable_rows": len(rows),
        "rows_with_bidirectional_family_candidates": len(rows_with_candidates),
        "n_bidirectional_family_candidates": sum(len(row["bidirectional_family_candidates"]) for row in rows),
        "rows_with_family_gate_candidates": len(rows_with_gate_candidates),
        "n_family_gate_candidates": sum(len(row["family_gate_candidates"]) for row in rows),
        "broad_family_classification_counts": broad_classes,
        "decision": (
            "subject_stable_family_gate_candidate"
            if rows_with_gate_candidates
            else "contribution_only_subject_stable_broad_family_mechanism"
            if rows_with_candidates
            else "no_subject_stable_broad_family_mechanism"
        ),
    }


def render_markdown(report: dict) -> str:
    summary = report["summary"]
    lines = [
        "# Subject-Stable Broad-Anatomy Mechanism Audit",
        "",
        (
            "Contribution audit for the five subject-stable broad-anatomy near misses. "
            "Each row rebuilds the matching target/features and decomposes held-out "
            "true-vs-shuffle true-class movement across predefined anatomical families."
        ),
        "",
        f"- subject-stable rows: `{summary['n_subject_stable_rows']}`",
        f"- rows with bidirectional family candidates: `{summary['rows_with_bidirectional_family_candidates']}`",
        f"- bidirectional family candidates: `{summary['n_bidirectional_family_candidates']}`",
        f"- exact family-gate candidates: `{summary['n_family_gate_candidates']}`",
        f"- decision: `{summary['decision']}`",
        "",
        "## Stable Rows",
        "",
        "| source | target | holdout | gate failures | gate delta shuffle | gate delta total | broad class | broad target0 | broad target1 | contribution candidates | exact gate candidates |",
        "|---|---|---|---|---:|---:|---|---:|---:|---|---|",
    ]
    for row in report["rows"]:
        gate = row["gate_row"]
        broad = row.get("broad_family_contribution") or {}
        candidates = ", ".join(row["bidirectional_family_candidates"]) or "none"
        gate_candidates = ", ".join(item["family"] for item in row["family_gate_candidates"]) or "none"
        lines.append(
            f"| {row['source']} | {row['target_mode']} | {row['holdout']} | "
            f"{', '.join(gate.get('failures', [])) or 'none'} | "
            f"{gate['centered_delta_vs_shuffle']:+.4f} | {gate['centered_delta_vs_total']:+.4f} | "
            f"{broad.get('classification', 'missing')} | "
            f"{broad.get('target0_improved', float('nan')):.3f} | "
            f"{broad.get('target1_improved', float('nan')):.3f} | {candidates} | {gate_candidates} |"
        )
    lines += [
        "",
        "## Top Contributions",
        "",
    ]
    for row in report["rows"]:
        lines += [
            f"### {row['source']} / {row['target_mode']} / {row['holdout']}",
            "",
            "| family | class | mean delta | target0 | target1 | recs |",
            "|---|---|---:|---:|---:|---:|",
        ]
        for family_row in row["top_family_rows"][: report["top_families"]]:
            lines.append(
                f"| {family_row['family']} | {family_row['classification']} | "
                f"{family_row['mean_true_class_delta']:+.4f} | "
                f"{family_row['target0_improved']:.3f} | {family_row['target1_improved']:.3f} | "
                f"{family_row['positive_recordings']}/{family_row['n_recordings']} |"
            )
        lines.append("")
        if row["family_gate_confirmations"]:
            lines += [
                "Exact candidate-family gate checks:",
                "",
                "| family | decision | delta shuffle | delta total | target0 | target1 | bidir recs |",
                "|---|---|---:|---:|---:|---:|---:|",
            ]
            for gate_row in row["family_gate_confirmations"]:
                lines.append(
                    f"| {gate_row['family']} | {gate_row['decision']} | "
                    f"{gate_row['centered_delta_vs_shuffle']:+.4f} | "
                    f"{gate_row['centered_delta_vs_total']:+.4f} | "
                    f"{gate_row['target0_improved_vs_shuffle']:.3f} | "
                    f"{gate_row['target1_improved_vs_shuffle']:.3f} | "
                    f"{gate_row['n_bidirectional_recordings']}/{gate_row['n_recordings']} |"
                )
            lines.append("")
    lines += [
        "## Decision",
        "",
        (
            "No subject-stable broad-anatomy near miss has a bidirectional predefined-family "
            "contribution that explains a promotable anatomical signal."
            if summary["decision"] == "no_subject_stable_broad_family_mechanism"
            else (
                "Family contribution checks found bidirectional movement, but exact "
                "single-family gates still do not pass the strict local promotion criteria."
                if summary["decision"] == "contribution_only_subject_stable_broad_family_mechanism"
                else (
                    "At least one subject-stable candidate family passes the exact local "
                    "gate; confirm shuffle-seed stability before any GPU training."
                )
            )
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
    parser.add_argument(
        "--subject-stable-json",
        type=Path,
        default=REPO_ROOT / "docs/subject_stable_local_gate_prospectus.json",
    )
    parser.add_argument("--region-granularity", default="parent", choices=["fine", "parent", "grandparent"])
    parser.add_argument("--window-len", type=float, default=1.0)
    parser.add_argument("--pre-window-len", type=float, default=0.5)
    parser.add_argument("--min-class-trials", type=int, default=40)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--l2", type=float, default=10.0)
    parser.add_argument("--min-centered-delta", type=float, default=0.0)
    parser.add_argument("--min-total-delta", type=float, default=0.0)
    parser.add_argument("--min-target-improvement", type=float, default=0.55)
    parser.add_argument("--min-bidirectional-recording-fraction", type=float, default=0.75)
    parser.add_argument("--top-families", type=int, default=8)
    parser.add_argument("--top-recording-families", type=int, default=5)
    parser.add_argument(
        "--out-json",
        type=Path,
        default=REPO_ROOT / "docs/subject_stable_broad_anatomy_mechanism.json",
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=REPO_ROOT / "docs/subject_stable_broad_anatomy_mechanism.md",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    stable_report = json.loads(args.subject_stable_json.read_text())
    stable_rows = [
        row for row in stable_report.get("subject_stable_rows", [])
        if row.get("feature") == "broad_named_anatomy"
    ]
    ds = Dataset(dataset_dir=args.data_dir, keep_files_open=True)
    selected_rids = select_recording_ids(ds, args.manifest, args.data_dir)
    vocab = build_vocab(ds, args.region_granularity, selected_rids)
    families = tuple(FAMILY_DEFINITIONS)
    payloads = {}
    rows = []
    for stable_row in stable_rows:
        key = (stable_row["source"], stable_row["target_mode"])
        if key not in payloads:
            precompute = SOURCE_PRECOMPUTERS[stable_row["source"]]
            kwargs = {
                "ds": ds,
                "vocab": vocab,
                "selected_rids": selected_rids,
                "target_name": stable_row["target_mode"],
                "families": families,
                "feature_mode": source_feature_mode(stable_row["source"]),
                "region_granularity": args.region_granularity,
                "window_len": args.window_len,
                "seed": args.seed,
                "min_class_trials": args.min_class_trials,
            }
            if source_kind(stable_row["source"]) == "reaction":
                kwargs["pre_window_len"] = args.pre_window_len
            payloads[key] = precompute(**kwargs)
        rows.append(contribution_audit_row(
            payloads[key],
            stable_row,
            l2=args.l2,
            min_centered_delta=args.min_centered_delta,
            min_total_delta=args.min_total_delta,
            min_target_improvement=args.min_target_improvement,
            min_bidirectional_recording_fraction=args.min_bidirectional_recording_fraction,
            top_recording_families=args.top_recording_families,
        ))
    report = {
        "manifest": str(args.manifest),
        "subject_stable_source": str(args.subject_stable_json),
        "thresholds": {
            "min_target_improvement": args.min_target_improvement,
            "min_centered_delta": args.min_centered_delta,
            "min_total_delta": args.min_total_delta,
            "min_bidirectional_recording_fraction": args.min_bidirectional_recording_fraction,
            "l2": args.l2,
            "seed": args.seed,
        },
        "top_families": args.top_families,
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
