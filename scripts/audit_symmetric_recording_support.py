"""Rank model-free rows by symmetric recording-level target support."""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from audit_model_free_gate_blockers import DEFAULT_REPORTS  # noqa: E402
from audit_model_free_recording_directionality import EXTRA_REPORTS, classify_target_direction, context_for_row  # noqa: E402


@dataclass(frozen=True)
class SymmetricRow:
    report: str
    context: str
    target_subject: str
    centered_delta: float | None
    global_target0: float | None
    global_target1: float | None
    n_recordings: int
    n_bidirectional_recordings: int
    bidirectional_fraction: float
    mean_symmetric_support: float
    min_symmetric_support: float
    max_symmetric_support: float
    mean_target_imbalance: float
    n_target0_only: int
    n_target1_only: int
    n_neither: int
    decision: str


def row_global_metrics(row: dict) -> tuple[float | None, float | None, float | None]:
    summary = row.get("summary", {})
    paired = summary.get("paired_true_vs_shuffle", {})
    centered = summary.get("delta_centered_auc")
    if centered is None:
        centered = row.get("centered_delta_vs_shuffle")
    return (
        None if centered is None else float(centered),
        None if paired.get("target0_improved_fraction") is None else float(paired["target0_improved_fraction"]),
        None if paired.get("target1_improved_fraction") is None else float(paired["target1_improved_fraction"]),
    )


def summarize_gate_row(
    report_label: str,
    row: dict,
    *,
    min_target_improvement: float,
    min_bidirectional_recording_fraction: float,
) -> SymmetricRow | None:
    recording_rows = row.get("recording_target_rows", [])
    if not recording_rows:
        return None
    context, target_subject = context_for_row(row)
    symmetric = [min(float(rec["target0_improved"]), float(rec["target1_improved"])) for rec in recording_rows]
    imbalances = [abs(float(rec["target1_improved"]) - float(rec["target0_improved"])) for rec in recording_rows]
    classes = [
        classify_target_direction(
            float(rec["target0_improved"]),
            float(rec["target1_improved"]),
            min_target_improvement=min_target_improvement,
        )
        for rec in recording_rows
    ]
    n_recordings = len(recording_rows)
    n_bidirectional = sum(1 for value in classes if value == "bidirectional")
    bidirectional_fraction = n_bidirectional / n_recordings if n_recordings else 0.0
    centered_delta, global_target0, global_target1 = row_global_metrics(row)
    decision = (
        "symmetric_recording_candidate"
        if (
            n_recordings
            and bidirectional_fraction >= min_bidirectional_recording_fraction
            and (global_target0 is None or global_target0 >= min_target_improvement)
            and (global_target1 is None or global_target1 >= min_target_improvement)
        )
        else "not_symmetric_recording_candidate"
    )
    return SymmetricRow(
        report=report_label,
        context=context,
        target_subject=target_subject,
        centered_delta=centered_delta,
        global_target0=global_target0,
        global_target1=global_target1,
        n_recordings=n_recordings,
        n_bidirectional_recordings=n_bidirectional,
        bidirectional_fraction=bidirectional_fraction,
        mean_symmetric_support=sum(symmetric) / n_recordings,
        min_symmetric_support=min(symmetric),
        max_symmetric_support=max(symmetric),
        mean_target_imbalance=sum(imbalances) / n_recordings,
        n_target0_only=sum(1 for value in classes if value == "target0_only"),
        n_target1_only=sum(1 for value in classes if value == "target1_only"),
        n_neither=sum(1 for value in classes if value == "neither"),
        decision=decision,
    )


def load_rows(
    report_specs: tuple[tuple[str, str], ...],
    *,
    min_target_improvement: float,
    min_bidirectional_recording_fraction: float,
) -> tuple[list[SymmetricRow], list[str]]:
    rows = []
    sources = []
    for label, rel_path in report_specs:
        path = REPO_ROOT / rel_path
        if not path.exists():
            continue
        payload = json.loads(path.read_text())
        raw_rows = payload.get("holdouts") or payload.get("pairs") or payload.get("rows") or []
        for row in raw_rows:
            summary = summarize_gate_row(
                label,
                row,
                min_target_improvement=min_target_improvement,
                min_bidirectional_recording_fraction=min_bidirectional_recording_fraction,
            )
            if summary is not None:
                rows.append(summary)
        sources.append(rel_path)
    return rows, sources


def row_to_dict(row: SymmetricRow) -> dict:
    return {
        "report": row.report,
        "context": row.context,
        "target_subject": row.target_subject,
        "centered_delta": row.centered_delta,
        "global_target0": row.global_target0,
        "global_target1": row.global_target1,
        "n_recordings": row.n_recordings,
        "n_bidirectional_recordings": row.n_bidirectional_recordings,
        "bidirectional_fraction": row.bidirectional_fraction,
        "mean_symmetric_support": row.mean_symmetric_support,
        "min_symmetric_support": row.min_symmetric_support,
        "max_symmetric_support": row.max_symmetric_support,
        "mean_target_imbalance": row.mean_target_imbalance,
        "n_target0_only": row.n_target0_only,
        "n_target1_only": row.n_target1_only,
        "n_neither": row.n_neither,
        "decision": row.decision,
    }


def summarize(rows: list[SymmetricRow]) -> dict:
    candidates = [row for row in rows if row.decision == "symmetric_recording_candidate"]
    ranked = sorted(
        rows,
        key=lambda row: (
            row.decision == "symmetric_recording_candidate",
            row.n_bidirectional_recordings,
            row.bidirectional_fraction,
            row.mean_symmetric_support,
            row.min_symmetric_support,
            -(row.mean_target_imbalance),
        ),
        reverse=True,
    )
    return {
        "n_rows": len(rows),
        "n_candidates": len(candidates),
        "max_bidirectional_recordings": max((row.n_bidirectional_recordings for row in rows), default=0),
        "max_bidirectional_fraction": max((row.bidirectional_fraction for row in rows), default=0.0),
        "max_mean_symmetric_support": max((row.mean_symmetric_support for row in rows), default=0.0),
        "min_mean_target_imbalance_top10": min((row.mean_target_imbalance for row in ranked[:10]), default=0.0),
        "top_rows": [row_to_dict(row) for row in ranked[:16]],
        "decision": "symmetric_recording_candidate_found" if candidates else "no_symmetric_recording_candidate",
    }


def render_markdown(report: dict) -> str:
    summary = report["summary"]
    lines = [
        "# Symmetric Recording Support Audit",
        "",
        (
            "Ranks current model-free rows by symmetric recording-local support: each "
            "recording contributes `min(target0_improved, target1_improved)`, so "
            "one-sided global wins cannot dominate the ranking."
        ),
        "",
        f"- rows: `{summary['n_rows']}`",
        f"- candidates: `{summary['n_candidates']}`",
        f"- max bidirectional recordings: `{summary['max_bidirectional_recordings']}`",
        f"- max bidirectional recording fraction: `{summary['max_bidirectional_fraction']:.3f}`",
        f"- max mean symmetric support: `{summary['max_mean_symmetric_support']:.3f}`",
        f"- decision: `{summary['decision']}`",
        "",
        "## Top Symmetric Rows",
        "",
        "| report | context | decision | centered delta | global target0 | global target1 | bidir recs | mean sym | min sym | target imbalance | one-sided |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary["top_rows"][:14]:
        centered = "n/a" if row["centered_delta"] is None else f"{row['centered_delta']:+.3f}"
        target0 = "n/a" if row["global_target0"] is None else f"{row['global_target0']:.3f}"
        target1 = "n/a" if row["global_target1"] is None else f"{row['global_target1']:.3f}"
        lines.append(
            f"| {row['report']} | {row['context']} | {row['decision']} | "
            f"{centered} | {target0} | {target1} | "
            f"{row['n_bidirectional_recordings']}/{row['n_recordings']} | "
            f"{row['mean_symmetric_support']:.3f} | {row['min_symmetric_support']:.3f} | "
            f"{row['mean_target_imbalance']:.3f} | "
            f"{row['n_target0_only'] + row['n_target1_only']} |"
        )
    lines += [
        "",
        "## Decision",
        "",
        (
            "Use this ranking before any future GPU trigger. A candidate should be near "
            "the top by symmetric recording support and should not be driven by many "
            "target0-only or target1-only recordings."
        ),
        "",
    ]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-json", type=Path, default=REPO_ROOT / "docs/symmetric_recording_support_audit.json")
    parser.add_argument("--out-md", type=Path, default=REPO_ROOT / "docs/symmetric_recording_support_audit.md")
    parser.add_argument("--min-target-improvement", type=float, default=0.55)
    parser.add_argument("--min-bidirectional-recording-fraction", type=float, default=0.75)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows, sources = load_rows(
        DEFAULT_REPORTS + EXTRA_REPORTS,
        min_target_improvement=args.min_target_improvement,
        min_bidirectional_recording_fraction=args.min_bidirectional_recording_fraction,
    )
    report = {
        "sources": sources,
        "thresholds": {
            "min_target_improvement": args.min_target_improvement,
            "min_bidirectional_recording_fraction": args.min_bidirectional_recording_fraction,
        },
        "summary": summarize(rows),
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
