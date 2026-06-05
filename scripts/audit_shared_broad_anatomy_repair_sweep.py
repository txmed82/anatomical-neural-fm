"""Sweep local repair knobs for the shared broad-anatomy near misses."""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "vendor" / "torch_brain"))

from torch_brain.dataset import Dataset  # noqa: E402
from audit_shared_family_target_control_gate import (  # noqa: E402
    family_gate_decision,
    precompute_target_mode,
    screen_precomputed_target,
    summarize_rows,
)
from train import build_vocab, select_recording_ids  # noqa: E402


TARGET_HOLDOUTS = {
    ("choice", "SWC_043"),
    ("feedback", "NYU-12"),
}
FEATURE_MODES = ("counts", "fractions", "recording_centered", "unit_residuals")
L2_VALUES = (1.0, 10.0, 100.0)
FAMILY = "broad_named_anatomy"


def target_holdout_rows(rows: list[dict]) -> list[dict]:
    return [
        row for row in rows
        if row["family"] == FAMILY and (row["target_mode"], row["holdout"]) in TARGET_HOLDOUTS
    ]


def missing_requirements(row: dict, *, min_target_improvement: float, min_bidirectional_recording_fraction: float) -> list[str]:
    missing = []
    if row["centered_delta_vs_shuffle"] < 0.0:
        missing.append("shuffle_delta")
    if row["centered_delta_vs_total"] < 0.0:
        missing.append("total_delta")
    if row["target0_improved_vs_shuffle"] < min_target_improvement:
        missing.append("target0")
    if row["target1_improved_vs_shuffle"] < min_target_improvement:
        missing.append("target1")
    if row["bidirectional_recording_fraction"] < min_bidirectional_recording_fraction:
        missing.append("recording_bidirectionality")
    return missing


def score_row(row: dict, *, min_target_improvement: float, min_bidirectional_recording_fraction: float) -> dict:
    required_bidirectional = math.ceil(row["n_recordings"] * min_bidirectional_recording_fraction)
    target0_margin = row["target0_improved_vs_shuffle"] - min_target_improvement
    target1_margin = row["target1_improved_vs_shuffle"] - min_target_improvement
    return row | {
        "required_bidirectional_recordings": required_bidirectional,
        "missing_bidirectional_recordings": max(0, required_bidirectional - row["n_bidirectional_recordings"]),
        "target0_margin": target0_margin,
        "target1_margin": target1_margin,
        "min_target_margin": min(target0_margin, target1_margin),
        "missing_requirements": missing_requirements(
            row,
            min_target_improvement=min_target_improvement,
            min_bidirectional_recording_fraction=min_bidirectional_recording_fraction,
        ),
    }


def rank_rows(rows: list[dict]) -> list[dict]:
    return sorted(
        rows,
        key=lambda row: (
            row["decision"] == "candidate",
            -row["missing_bidirectional_recordings"],
            row["min_target_margin"],
            row["centered_delta_vs_shuffle"],
            row["centered_delta_vs_total"],
            min(row["target0_improved_vs_shuffle"], row["target1_improved_vs_shuffle"]),
        ),
        reverse=True,
    )


def summarize_focus_rows(rows: list[dict]) -> dict:
    ranked = rank_rows(rows)
    candidates = [row for row in rows if row["decision"] == "candidate"]
    return {
        "n_rows": len(rows),
        "n_candidates": len(candidates),
        "max_bidirectional_recordings": max((row["n_bidirectional_recordings"] for row in rows), default=0),
        "max_min_target_margin": max((row["min_target_margin"] for row in rows), default=0.0),
        "max_centered_delta_vs_shuffle": max((row["centered_delta_vs_shuffle"] for row in rows), default=0.0),
        "top_rows": ranked[:12],
        "by_focus": {
            f"{target}/{holdout}": rank_rows([
                row for row in rows if row["target_mode"] == target and row["holdout"] == holdout
            ])[:6]
            for target, holdout in sorted(TARGET_HOLDOUTS)
        },
        "decision": "shared_broad_anatomy_repair_candidate" if candidates else "no_shared_broad_anatomy_repair_candidate",
    }


def build_report(args: argparse.Namespace) -> dict:
    ds = Dataset(args.data_dir)
    selected_rids = select_recording_ids(ds, args.manifest, args.data_dir)
    all_rows = []
    for feature_mode in args.feature_mode:
        vocab = build_vocab(ds, args.region_granularity, selected_rids)
        for target_mode in args.target_mode:
            payload = precompute_target_mode(
                ds=ds,
                vocab=vocab,
                selected_rids=selected_rids,
                target_mode=target_mode,
                families=(FAMILY,),
                feature_mode=feature_mode,
                region_granularity=args.region_granularity,
                window_len=args.window_len,
                seed=args.seed,
            )
            for l2 in args.l2:
                rows = screen_precomputed_target(
                    payload,
                    holdouts=args.holdout,
                    l2=l2,
                    min_centered_delta=args.min_centered_delta,
                    min_total_delta=args.min_total_delta,
                    min_target_improvement=args.min_target_improvement,
                    min_bidirectional_recording_fraction=args.min_bidirectional_recording_fraction,
                )
                for row in target_holdout_rows(rows):
                    row = row | {
                        "feature_mode": feature_mode,
                        "region_granularity": args.region_granularity,
                        "l2": l2,
                    }
                    row["decision"] = family_gate_decision(
                        row,
                        min_centered_delta=args.min_centered_delta,
                        min_total_delta=args.min_total_delta,
                        min_target_improvement=args.min_target_improvement,
                        min_bidirectional_recording_fraction=args.min_bidirectional_recording_fraction,
                    )
                    all_rows.append(score_row(
                        row,
                        min_target_improvement=args.min_target_improvement,
                        min_bidirectional_recording_fraction=args.min_bidirectional_recording_fraction,
                    ))
    return {
        "target_holdouts": [
            {"target_mode": target, "holdout": holdout}
            for target, holdout in sorted(TARGET_HOLDOUTS)
        ],
        "feature_modes": list(args.feature_mode),
        "l2_values": list(args.l2),
        "region_granularity": args.region_granularity,
        "window_len": args.window_len,
        "manifest": str(args.manifest),
        "data_dir": str(args.data_dir),
        "thresholds": {
            "min_centered_delta": args.min_centered_delta,
            "min_total_delta": args.min_total_delta,
            "min_target_improvement": args.min_target_improvement,
            "min_bidirectional_recording_fraction": args.min_bidirectional_recording_fraction,
        },
        "rows": all_rows,
        "summary": summarize_focus_rows(all_rows),
        "full_shared_family_summary": summarize_rows(all_rows),
    }


def render_markdown(report: dict) -> str:
    summary = report["summary"]
    lines = [
        "# Shared Broad-Anatomy Repair Sweep",
        "",
        (
            "Focused no-spend sweep for the two shared broad-anatomy rows identified "
            "by the strict symmetric failure-mode audit."
        ),
        "",
        f"- rows: `{summary['n_rows']}`",
        f"- candidates: `{summary['n_candidates']}`",
        f"- max bidirectional recordings: `{summary['max_bidirectional_recordings']}`",
        f"- max min target margin: `{summary['max_min_target_margin']:+.3f}`",
        f"- max centered delta vs shuffle: `{summary['max_centered_delta_vs_shuffle']:+.3f}`",
        f"- decision: `{summary['decision']}`",
        "",
        "## Top Sweep Rows",
        "",
        "| target | holdout | feature | l2 | decision | missing | delta shuffle | delta total | target0 | target1 | bidir recs |",
        "|---|---|---|---:|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in summary["top_rows"]:
        lines.append(
            f"| {row['target_mode']} | {row['holdout']} | {row['feature_mode']} | {row['l2']:.0f} | "
            f"{row['decision']} | {', '.join(row['missing_requirements']) or 'none'} | "
            f"{row['centered_delta_vs_shuffle']:+.3f} | {row['centered_delta_vs_total']:+.3f} | "
            f"{row['target0_improved_vs_shuffle']:.3f} | {row['target1_improved_vs_shuffle']:.3f} | "
            f"{row['n_bidirectional_recordings']}/{row['required_bidirectional_recordings']} |"
        )
    lines += [
        "",
        "## Decision",
        "",
        (
            "This sweep is a local repair attempt, not a relaxed gate. A GPU run remains "
            "unjustified unless a row clears true-vs-shuffle, total baseline, both "
            "global target floors, and at least three of four same-recording "
            "bidirectional hits."
        ),
        "",
    ]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=REPO_ROOT / "data/brainsets/ibl_bwm")
    parser.add_argument("--manifest", type=Path, default=REPO_ROOT / "manifests/ibl_bwm_region_matched_candidates_s3_present_support80_hdf5_scored.json")
    parser.add_argument("--target-mode", nargs="*", default=["choice", "feedback"], choices=["choice", "feedback"])
    parser.add_argument("--holdout", nargs="*", default=["SWC_043", "NYU-12"])
    parser.add_argument("--feature-mode", nargs="*", default=list(FEATURE_MODES), choices=list(FEATURE_MODES))
    parser.add_argument("--region-granularity", default="parent", choices=["fine", "parent", "grandparent"])
    parser.add_argument("--window-len", type=float, default=1.0)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--l2", nargs="*", type=float, default=list(L2_VALUES))
    parser.add_argument("--min-centered-delta", type=float, default=0.0)
    parser.add_argument("--min-total-delta", type=float, default=0.0)
    parser.add_argument("--min-target-improvement", type=float, default=0.55)
    parser.add_argument("--min-bidirectional-recording-fraction", type=float, default=0.75)
    parser.add_argument("--out-json", type=Path, default=REPO_ROOT / "docs/shared_broad_anatomy_repair_sweep.json")
    parser.add_argument("--out-md", type=Path, default=REPO_ROOT / "docs/shared_broad_anatomy_repair_sweep.md")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(args)
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text(render_markdown(report))
    print(f"wrote {args.out_json}")
    print(f"wrote {args.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
