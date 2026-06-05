"""Apply a recording-local bidirectional gate to model-free anatomy audits."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from audit_model_free_positive_holdouts import audit_holdout  # noqa: E402


def manifest_subjects(path: Path) -> list[str]:
    payload = json.loads(path.read_text())
    rows = payload["recordings"] if isinstance(payload, dict) else payload
    subjects = {
        row.get("subject_id") or row.get("subject") or row.get("subject_nickname")
        for row in rows
    }
    return sorted(subject for subject in subjects if subject)


def recording_bidirectional_summary(
    recording_rows: list[dict],
    *,
    min_target_improvement: float,
) -> dict:
    passing = []
    evaluable = []
    for row in recording_rows:
        target0 = row.get("target0_improved")
        target1 = row.get("target1_improved")
        if target0 != target0 or target1 != target1:
            continue
        evaluable.append(row)
        if target0 >= min_target_improvement and target1 >= min_target_improvement:
            passing.append(row)
    n_evaluable = len(evaluable)
    n_passing = len(passing)
    return {
        "n_evaluable_recordings": n_evaluable,
        "n_bidirectional_recordings": n_passing,
        "bidirectional_recording_fraction": 0.0 if n_evaluable == 0 else n_passing / n_evaluable,
        "bidirectional_recordings": [row["recording"] for row in passing],
    }


def gate_decision(
    holdout: dict,
    bidirectional: dict,
    *,
    min_centered_delta: float,
    min_target_improvement: float,
    min_bidirectional_recording_fraction: float,
) -> str:
    summary = holdout["summary"]
    paired = summary["paired_true_vs_shuffle"]
    if summary["delta_centered_auc"] < min_centered_delta:
        return "reject: centered delta"
    if paired["target0_improved_fraction"] < min_target_improvement:
        return "reject: global target0"
    if paired["target1_improved_fraction"] < min_target_improvement:
        return "reject: global target1"
    if bidirectional["bidirectional_recording_fraction"] < min_bidirectional_recording_fraction:
        return "reject: recording bidirectionality"
    return "candidate"


def summarize_panel(rows: list[dict]) -> dict:
    candidates = [row for row in rows if row["recording_bidirectional_decision"] == "candidate"]
    positive_delta = [row for row in rows if row["summary"]["delta_centered_auc"] > 0.0]
    mean_bidirectional_fraction = (
        sum(row["recording_bidirectional"]["bidirectional_recording_fraction"] for row in rows) / len(rows)
        if rows else 0.0
    )
    return {
        "n_holdouts": len(rows),
        "n_candidates": len(candidates),
        "candidate_holdouts": [row["holdout"] for row in candidates],
        "n_positive_delta_holdouts": len(positive_delta),
        "positive_delta_holdouts": [row["holdout"] for row in positive_delta],
        "mean_bidirectional_recording_fraction": mean_bidirectional_fraction,
        "decision": (
            "recording_bidirectional_panel_candidate"
            if candidates else "no_recording_bidirectional_model_free_signal"
        ),
    }


def render_markdown(report: dict) -> str:
    lines = [
        "# Model-Free Recording-Bidirectional Gate",
        "",
        (
            "Closed-form parent-region ridge audit with a stricter support rule: "
            "a recording counts only when true region labels beat the within-recording "
            "shuffle for target0 and target1 in that same recording."
        ),
        "",
        f"- holdouts: `{report['summary']['n_holdouts']}`",
        f"- candidates: `{report['summary']['n_candidates']}`",
        f"- positive centered-delta holdouts: `{report['summary']['n_positive_delta_holdouts']}`",
        f"- mean bidirectional recording fraction: `{report['summary']['mean_bidirectional_recording_fraction']:.3f}`",
        f"- decision: `{report['summary']['decision']}`",
        "",
        "| holdout | centered delta | target0 | target1 | positive recs | bidirectional recs | decision |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in report["holdouts"]:
        summary = row["summary"]
        paired = summary["paired_true_vs_shuffle"]
        bidir = row["recording_bidirectional"]
        lines.append(
            f"| {row['holdout']} | {summary['delta_centered_auc']:+.3f} | "
            f"{paired['target0_improved_fraction']:.3f} | "
            f"{paired['target1_improved_fraction']:.3f} | "
            f"{summary['recordings_positive_true_minus_shuffle']}/{summary['n_recordings']} | "
            f"{bidir['n_bidirectional_recordings']}/{bidir['n_evaluable_recordings']} | "
            f"{row['recording_bidirectional_decision']} |"
        )
    lines += [
        "",
        "## Decision",
        "",
        (
            "Do not promote a model-free or neural training run unless at least one "
            "holdout clears this recording-local bidirectional gate. Positive centered "
            "deltas that split target0 and target1 wins across different recordings are "
            "not evidence for a cross-animal anatomical transfer mechanism."
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
    parser.add_argument("--holdout", nargs="*", default=None)
    parser.add_argument("--target-mode", default="stimulus_side", choices=["choice", "stimulus_side"])
    parser.add_argument("--region-granularity", default="parent", choices=["fine", "parent", "grandparent"])
    parser.add_argument("--window-len", type=float, default=1.0)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--l2", type=float, default=10.0)
    parser.add_argument("--top-regions", type=int, default=12)
    parser.add_argument("--min-centered-delta", type=float, default=0.01)
    parser.add_argument("--min-target-improvement", type=float, default=0.55)
    parser.add_argument("--min-bidirectional-recording-fraction", type=float, default=0.75)
    parser.add_argument(
        "--out-json",
        type=Path,
        default=REPO_ROOT / "docs/model_free_recording_bidirectional_gate.json",
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=REPO_ROOT / "docs/model_free_recording_bidirectional_gate.md",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    holdouts = args.holdout or manifest_subjects(args.manifest)
    rows = []
    for holdout in holdouts:
        row = audit_holdout(args, holdout)
        bidirectional = recording_bidirectional_summary(
            row["recording_target_rows"],
            min_target_improvement=args.min_target_improvement,
        )
        row["recording_bidirectional"] = bidirectional
        row["recording_bidirectional_decision"] = gate_decision(
            row,
            bidirectional,
            min_centered_delta=args.min_centered_delta,
            min_target_improvement=args.min_target_improvement,
            min_bidirectional_recording_fraction=args.min_bidirectional_recording_fraction,
        )
        rows.append(row)
    report = {
        "manifest": str(args.manifest),
        "target_mode": args.target_mode,
        "region_granularity": args.region_granularity,
        "thresholds": {
            "min_centered_delta": args.min_centered_delta,
            "min_target_improvement": args.min_target_improvement,
            "min_bidirectional_recording_fraction": args.min_bidirectional_recording_fraction,
        },
        "summary": summarize_panel(rows),
        "holdouts": rows,
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
