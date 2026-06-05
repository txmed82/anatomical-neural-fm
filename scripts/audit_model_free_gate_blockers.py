"""Summarize what blocks current model-free anatomy-transfer gates."""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_REPORTS = (
    ("panel counts", "docs/model_free_recording_bidirectional_gate.json"),
    ("panel fractions", "docs/model_free_recording_bidirectional_gate_fractions.json"),
    ("panel recording centered", "docs/model_free_recording_bidirectional_gate_recording_centered.json"),
    ("panel grandparent centered", "docs/model_free_recording_bidirectional_gate_grandparent_recording_centered.json"),
    ("panel unit residuals", "docs/model_free_recording_bidirectional_gate_unit_residuals.json"),
    ("panel prior side", "docs/model_free_recording_bidirectional_gate_prior_side.json"),
    ("panel feedback", "docs/model_free_recording_bidirectional_gate_feedback.json"),
    ("family centered", "docs/model_free_family_bidirectional_gate_recording_centered.json"),
    ("family centered l2=1", "docs/model_free_family_bidirectional_gate_recording_centered_l2_1.json"),
    ("family centered l2=100", "docs/model_free_family_bidirectional_gate_recording_centered_l2_100.json"),
    ("family prior side", "docs/model_free_family_bidirectional_gate_prior_side_recording_centered.json"),
    ("family feedback", "docs/model_free_family_bidirectional_gate_feedback_recording_centered.json"),
    ("source-target centered", "docs/model_free_source_target_pair_gate_recording_centered.json"),
    ("source-target families", "docs/model_free_source_target_pair_gate_families_recording_centered.json"),
)


@dataclass(frozen=True)
class GateRow:
    report: str
    label: str
    decision: str
    centered_delta: float
    target0: float
    target1: float
    bidirectional_fraction: float
    positive_recording_fraction: float
    n_bidirectional_recordings: int
    n_recordings: int


def load_rows(report_label: str, path: Path) -> list[GateRow]:
    payload = json.loads(path.read_text())
    raw_rows = payload.get("holdouts") or payload.get("pairs") or []
    rows = []
    for row in raw_rows:
        summary = row["summary"]
        paired = summary["paired_true_vs_shuffle"]
        bidir = row["recording_bidirectional"]
        if "holdout" in row:
            label = row["holdout"]
        else:
            label = f"{row['source_subject']} -> {row['target_subject']}"
        rows.append(
            GateRow(
                report=report_label,
                label=label,
                decision=row["recording_bidirectional_decision"],
                centered_delta=float(summary["delta_centered_auc"]),
                target0=float(paired["target0_improved_fraction"]),
                target1=float(paired["target1_improved_fraction"]),
                bidirectional_fraction=float(bidir["bidirectional_recording_fraction"]),
                positive_recording_fraction=(
                    float(summary["recordings_positive_true_minus_shuffle"]) / float(summary["n_recordings"])
                    if summary["n_recordings"] else 0.0
                ),
                n_bidirectional_recordings=int(bidir["n_bidirectional_recordings"]),
                n_recordings=int(bidir["n_evaluable_recordings"]),
            )
        )
    return rows


def missing_checks(row: GateRow, thresholds: dict[str, float]) -> list[str]:
    missing = []
    if row.centered_delta < thresholds["min_centered_delta"]:
        missing.append("centered_delta")
    if row.target0 < thresholds["min_target_improvement"]:
        missing.append("target0")
    if row.target1 < thresholds["min_target_improvement"]:
        missing.append("target1")
    if row.bidirectional_fraction < thresholds["min_bidirectional_recording_fraction"]:
        missing.append("recording_bidirectionality")
    return missing


def closeness(row: GateRow, thresholds: dict[str, float]) -> float:
    margins = [
        row.centered_delta - thresholds["min_centered_delta"],
        row.target0 - thresholds["min_target_improvement"],
        row.target1 - thresholds["min_target_improvement"],
        row.bidirectional_fraction - thresholds["min_bidirectional_recording_fraction"],
    ]
    return min(margins)


def summarize(rows: list[GateRow], thresholds: dict[str, float]) -> dict:
    candidates = [row for row in rows if not missing_checks(row, thresholds)]
    positive = [row for row in rows if row.centered_delta > 0.0]
    blockers = {"centered_delta": 0, "target0": 0, "target1": 0, "recording_bidirectionality": 0}
    blocker_combinations: dict[str, int] = {}
    for row in rows:
        missing = missing_checks(row, thresholds)
        for item in missing:
            blockers[item] += 1
        key = ", ".join(missing) if missing else "candidate"
        blocker_combinations[key] = blocker_combinations.get(key, 0) + 1
    top_rows = sorted(
        rows,
        key=lambda row: (
            row.n_bidirectional_recordings,
            row.bidirectional_fraction,
            row.centered_delta,
            min(row.target0, row.target1),
        ),
        reverse=True,
    )
    closest_rows = sorted(rows, key=lambda row: closeness(row, thresholds), reverse=True)
    return {
        "n_rows": len(rows),
        "n_candidates": len(candidates),
        "n_positive_centered_delta": len(positive),
        "max_bidirectional_recordings": max((row.n_bidirectional_recordings for row in rows), default=0),
        "max_bidirectional_fraction": max((row.bidirectional_fraction for row in rows), default=0.0),
        "blocker_counts": blockers,
        "blocker_combinations": dict(sorted(blocker_combinations.items())),
        "top_bidirectional_rows": top_rows[:10],
        "closest_rows": closest_rows[:10],
    }


def row_to_dict(row: GateRow, thresholds: dict[str, float]) -> dict:
    return {
        "report": row.report,
        "label": row.label,
        "decision": row.decision,
        "centered_delta": row.centered_delta,
        "target0": row.target0,
        "target1": row.target1,
        "bidirectional_fraction": row.bidirectional_fraction,
        "positive_recording_fraction": row.positive_recording_fraction,
        "n_bidirectional_recordings": row.n_bidirectional_recordings,
        "n_recordings": row.n_recordings,
        "missing_checks": missing_checks(row, thresholds),
        "closest_margin": closeness(row, thresholds),
    }


def render_markdown(report: dict) -> str:
    summary = report["summary"]
    lines = [
        "# Model-Free Gate Blocker Audit",
        "",
        (
            "Aggregates current model-free holdout and source-target gate artifacts to "
            "identify which promotion checks actually block the cross-animal anatomy claim."
        ),
        "",
        f"- rows audited: `{summary['n_rows']}`",
        f"- candidates: `{summary['n_candidates']}`",
        f"- positive centered-delta rows: `{summary['n_positive_centered_delta']}`",
        f"- max bidirectional recordings: `{summary['max_bidirectional_recordings']}`",
        f"- max bidirectional recording fraction: `{summary['max_bidirectional_fraction']:.3f}`",
        "",
        "## Blocker Counts",
        "",
        "| blocker | rows missing check |",
        "|---|---:|",
    ]
    for key, value in summary["blocker_counts"].items():
        lines.append(f"| {key} | {value} |")
    lines += [
        "",
        "## Top Same-Recording Bidirectional Rows",
        "",
        "| report | label | decision | centered delta | target0 | target1 | bidir recs | positive rec frac | missing checks |",
        "|---|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in summary["top_bidirectional_rows"]:
        lines.append(
            f"| {row['report']} | {row['label']} | {row['decision']} | "
            f"{row['centered_delta']:+.3f} | {row['target0']:.3f} | {row['target1']:.3f} | "
            f"{row['n_bidirectional_recordings']}/{row['n_recordings']} | "
            f"{row['positive_recording_fraction']:.3f} | {', '.join(row['missing_checks']) or 'none'} |"
        )
    lines += [
        "",
        "## Closest Rows By Worst Gate Margin",
        "",
        "| report | label | decision | worst margin | centered delta | target0 | target1 | bidir frac | missing checks |",
        "|---|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in summary["closest_rows"]:
        lines.append(
            f"| {row['report']} | {row['label']} | {row['decision']} | "
            f"{row['closest_margin']:+.3f} | {row['centered_delta']:+.3f} | "
            f"{row['target0']:.3f} | {row['target1']:.3f} | "
            f"{row['bidirectional_fraction']:.3f} | {', '.join(row['missing_checks']) or 'none'} |"
        )
    lines += [
        "",
        "## Decision",
        "",
        (
            "The limiting condition is no longer just centered AUC or ridge tuning. "
            "Across all audited local model-free variants, no row reaches more than "
            "two bidirectional recordings, and the closest rows still miss global "
            "target0/target1 or same-recording bidirectionality. The next plan should "
            "change the benchmark/control definition enough to create same-recording "
            "bidirectional evidence before any GPU run."
        ),
        "",
    ]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-json", type=Path, default=REPO_ROOT / "docs/model_free_gate_blocker_audit.json")
    parser.add_argument("--out-md", type=Path, default=REPO_ROOT / "docs/model_free_gate_blocker_audit.md")
    parser.add_argument("--min-centered-delta", type=float, default=0.01)
    parser.add_argument("--min-target-improvement", type=float, default=0.55)
    parser.add_argument("--min-bidirectional-recording-fraction", type=float, default=0.75)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    thresholds = {
        "min_centered_delta": args.min_centered_delta,
        "min_target_improvement": args.min_target_improvement,
        "min_bidirectional_recording_fraction": args.min_bidirectional_recording_fraction,
    }
    rows = []
    sources = []
    for label, rel_path in DEFAULT_REPORTS:
        path = REPO_ROOT / rel_path
        if not path.exists():
            continue
        rows.extend(load_rows(label, path))
        sources.append(rel_path)
    summary = summarize(rows, thresholds)
    report = {
        "thresholds": thresholds,
        "sources": sources,
        "summary": {
            key: (
                [row_to_dict(row, thresholds) for row in value]
                if key in {"top_bidirectional_rows", "closest_rows"}
                else value
            )
            for key, value in summary.items()
        },
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
