"""Explain why the closest symmetric rows miss the strict promotion gate."""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from audit_model_free_gate_blockers import DEFAULT_REPORTS  # noqa: E402
from audit_model_free_recording_directionality import EXTRA_REPORTS  # noqa: E402
from audit_symmetric_recording_support import SymmetricRow, load_rows, row_to_dict  # noqa: E402


STRICT_TARGET_THRESHOLD = 0.55
STRICT_BIDIRECTIONAL_FRACTION = 0.75


def required_bidirectional_recordings(n_recordings: int, fraction: float) -> int:
    if n_recordings <= 0:
        return 0
    return math.ceil(n_recordings * fraction)


def blocker_labels(row: SymmetricRow, *, target_threshold: float, bidirectional_fraction: float) -> list[str]:
    labels = []
    required = required_bidirectional_recordings(row.n_recordings, bidirectional_fraction)
    if row.n_bidirectional_recordings < required:
        labels.append("recording_bidirectionality")
    if row.global_target0 is not None and row.global_target0 < target_threshold:
        labels.append("global_target0")
    if row.global_target1 is not None and row.global_target1 < target_threshold:
        labels.append("global_target1")
    return labels


def score_row(row: SymmetricRow, *, target_threshold: float, bidirectional_fraction: float) -> dict:
    required = required_bidirectional_recordings(row.n_recordings, bidirectional_fraction)
    missing_bidirectional = max(0, required - row.n_bidirectional_recordings)
    target0_margin = None if row.global_target0 is None else row.global_target0 - target_threshold
    target1_margin = None if row.global_target1 is None else row.global_target1 - target_threshold
    known_margins = [margin for margin in (target0_margin, target1_margin) if margin is not None]
    min_global_target_margin = min(known_margins) if known_margins else None
    labels = blocker_labels(row, target_threshold=target_threshold, bidirectional_fraction=bidirectional_fraction)
    return row_to_dict(row) | {
        "required_bidirectional_recordings": required,
        "missing_bidirectional_recordings": missing_bidirectional,
        "target0_margin": target0_margin,
        "target1_margin": target1_margin,
        "min_global_target_margin": min_global_target_margin,
        "blockers": labels,
        "strict_pass": not labels,
    }


def rank_scored_rows(scored_rows: list[dict]) -> list[dict]:
    return sorted(
        scored_rows,
        key=lambda row: (
            -int(row["strict_pass"]),
            row["missing_bidirectional_recordings"],
            -(row["min_global_target_margin"] if row["min_global_target_margin"] is not None else -999.0),
            -row["n_bidirectional_recordings"],
            -row["mean_symmetric_support"],
            row["mean_target_imbalance"],
        ),
    )


def summarize(scored_rows: list[dict], *, target_threshold: float, bidirectional_fraction: float) -> dict:
    ranked = rank_scored_rows(scored_rows)
    blocker_counts: dict[str, int] = {}
    for row in scored_rows:
        for blocker in row["blockers"]:
            blocker_counts[blocker] = blocker_counts.get(blocker, 0) + 1
    one_recording_short = [
        row for row in scored_rows
        if row["missing_bidirectional_recordings"] == 1
        and "global_target0" not in row["blockers"]
        and "global_target1" not in row["blockers"]
    ]
    global_clear = [
        row for row in scored_rows
        if "global_target0" not in row["blockers"] and "global_target1" not in row["blockers"]
    ]
    return {
        "n_rows": len(scored_rows),
        "strict_candidates": sum(1 for row in scored_rows if row["strict_pass"]),
        "target_threshold": target_threshold,
        "bidirectional_fraction": bidirectional_fraction,
        "required_recordings_for_four_recording_rows": required_bidirectional_recordings(4, bidirectional_fraction),
        "blocker_counts": blocker_counts,
        "global_target_clear_rows": len(global_clear),
        "one_recording_short_and_global_clear_rows": len(one_recording_short),
        "closest_rows": ranked[:12],
        "decision": (
            "strict_symmetric_candidate_found"
            if any(row["strict_pass"] for row in scored_rows)
            else "strict_failure_modes_identified"
        ),
    }


def render_markdown(report: dict) -> str:
    summary = report["summary"]
    blockers = ", ".join(
        f"{name}={count}" for name, count in sorted(summary["blocker_counts"].items())
    )
    lines = [
        "# Symmetric Strict Failure Mode Audit",
        "",
        (
            "Ranks the closest current rows against the strict symmetric promotion "
            "gate and explains which requirement each row misses."
        ),
        "",
        f"- rows: `{summary['n_rows']}`",
        f"- strict candidates: `{summary['strict_candidates']}`",
        f"- target threshold: `{summary['target_threshold']:.3f}`",
        f"- bidirectional fraction: `{summary['bidirectional_fraction']:.2f}`",
        f"- required recordings for four-recording rows: `{summary['required_recordings_for_four_recording_rows']}`",
        f"- global-target-clear rows: `{summary['global_target_clear_rows']}`",
        f"- one-recording-short and global-clear rows: `{summary['one_recording_short_and_global_clear_rows']}`",
        f"- blocker counts: `{blockers}`",
        f"- decision: `{summary['decision']}`",
        "",
        "## Closest Strict-Gate Misses",
        "",
        "| report | context | blockers | global target0 | global target1 | margins | bidir recs | missing | mean sym | one-sided |",
        "|---|---|---|---:|---:|---|---:|---:|---:|---:|",
    ]
    for row in summary["closest_rows"]:
        target0 = "n/a" if row["global_target0"] is None else f"{row['global_target0']:.3f}"
        target1 = "n/a" if row["global_target1"] is None else f"{row['global_target1']:.3f}"
        target0_margin = "n/a" if row["target0_margin"] is None else f"{row['target0_margin']:+.3f}"
        target1_margin = "n/a" if row["target1_margin"] is None else f"{row['target1_margin']:+.3f}"
        lines.append(
            f"| {row['report']} | {row['context']} | {', '.join(row['blockers']) or 'none'} | "
            f"{target0} | {target1} | {target0_margin}/{target1_margin} | "
            f"{row['n_bidirectional_recordings']}/{row['required_bidirectional_recordings']} | "
            f"{row['missing_bidirectional_recordings']} | "
            f"{row['mean_symmetric_support']:.3f} | "
            f"{row['n_target0_only'] + row['n_target1_only']} |"
        )
    lines += [
        "",
        "## Decision",
        "",
        (
            "The next no-spend experiment should target the one-recording-short rows "
            "whose remaining global miss is marginal, especially target0 misses in "
            "the shared broad-anatomy rows. If a redesign cannot turn those rows into "
            "at least three of four bidirectional recordings while clearing both "
            "global target floors locally, it should not launch a paid neural "
            "training run."
        ),
        "",
    ]
    return "\n".join(lines)


def build_report(*, target_threshold: float, bidirectional_fraction: float) -> dict:
    rows, sources = load_rows(
        DEFAULT_REPORTS + EXTRA_REPORTS,
        min_target_improvement=target_threshold,
        min_bidirectional_recording_fraction=bidirectional_fraction,
    )
    scored_rows = [
        score_row(row, target_threshold=target_threshold, bidirectional_fraction=bidirectional_fraction)
        for row in rows
    ]
    return {
        "sources": sources,
        "summary": summarize(
            scored_rows,
            target_threshold=target_threshold,
            bidirectional_fraction=bidirectional_fraction,
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-json", type=Path, default=REPO_ROOT / "docs/symmetric_strict_failure_modes.json")
    parser.add_argument("--out-md", type=Path, default=REPO_ROOT / "docs/symmetric_strict_failure_modes.md")
    parser.add_argument("--target-threshold", type=float, default=STRICT_TARGET_THRESHOLD)
    parser.add_argument("--bidirectional-fraction", type=float, default=STRICT_BIDIRECTIONAL_FRACTION)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(
        target_threshold=args.target_threshold,
        bidirectional_fraction=args.bidirectional_fraction,
    )
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text(render_markdown(report))
    print(f"wrote {args.out_json}")
    print(f"wrote {args.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
