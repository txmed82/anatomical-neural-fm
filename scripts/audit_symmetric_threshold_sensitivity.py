"""Sweep symmetric recording-support thresholds over current model-free rows."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from audit_model_free_gate_blockers import DEFAULT_REPORTS  # noqa: E402
from audit_model_free_recording_directionality import EXTRA_REPORTS  # noqa: E402
from audit_symmetric_recording_support import load_rows, row_to_dict  # noqa: E402


TARGET_THRESHOLDS = (0.50, 0.525, 0.55, 0.575, 0.60)
BIDIRECTIONAL_FRACTIONS = (0.25, 0.50, 0.75, 1.00)


def candidate_rows(rows: list, *, min_global_target: float | None = None) -> list:
    candidates = []
    for row in rows:
        if row.decision != "symmetric_recording_candidate":
            continue
        if min_global_target is not None:
            if row.global_target0 is not None and row.global_target0 < min_global_target:
                continue
            if row.global_target1 is not None and row.global_target1 < min_global_target:
                continue
        candidates.append(row)
    return candidates


def sweep_thresholds(
    *,
    target_thresholds: tuple[float, ...],
    bidirectional_fractions: tuple[float, ...],
) -> list[dict]:
    rows = []
    for target_threshold in target_thresholds:
        for bidir_fraction in bidirectional_fractions:
            loaded_rows, _sources = load_rows(
                DEFAULT_REPORTS + EXTRA_REPORTS,
                min_target_improvement=target_threshold,
                min_bidirectional_recording_fraction=bidir_fraction,
            )
            candidates = candidate_rows(loaded_rows, min_global_target=target_threshold)
            top = sorted(
                loaded_rows,
                key=lambda row: (
                    row.decision == "symmetric_recording_candidate",
                    row.n_bidirectional_recordings,
                    row.mean_symmetric_support,
                    row.min_symmetric_support,
                ),
                reverse=True,
            )[:5]
            rows.append({
                "min_target_improvement": target_threshold,
                "min_bidirectional_recording_fraction": bidir_fraction,
                "n_rows": len(loaded_rows),
                "n_candidates": len(candidates),
                "max_bidirectional_recordings": max(
                    (row.n_bidirectional_recordings for row in loaded_rows),
                    default=0,
                ),
                "max_bidirectional_fraction": max((row.bidirectional_fraction for row in loaded_rows), default=0.0),
                "top_rows": [row_to_dict(row) for row in top],
            })
    return rows


def summarize(rows: list[dict]) -> dict:
    candidate_rows_by_threshold = [row for row in rows if row["n_candidates"] > 0]
    highest_target_candidate = None
    default_target_candidates = [
        row for row in candidate_rows_by_threshold
        if row["min_target_improvement"] == 0.55
    ]
    strongest_default_target_candidate = None
    if candidate_rows_by_threshold:
        highest_target_candidate = sorted(
            candidate_rows_by_threshold,
            key=lambda row: (
                row["min_target_improvement"],
                row["min_bidirectional_recording_fraction"],
                -row["n_candidates"],
            ),
            reverse=True,
        )[0]
    if default_target_candidates:
        strongest_default_target_candidate = sorted(
            default_target_candidates,
            key=lambda row: (
                row["min_bidirectional_recording_fraction"],
                -row["n_candidates"],
            ),
            reverse=True,
        )[0]
    strict = next(
        row for row in rows
        if row["min_target_improvement"] == 0.55 and row["min_bidirectional_recording_fraction"] == 0.75
    )
    return {
        "n_threshold_settings": len(rows),
        "n_settings_with_candidates": len(candidate_rows_by_threshold),
        "strict_candidates": strict["n_candidates"],
        "strict_max_bidirectional_recordings": strict["max_bidirectional_recordings"],
        "highest_target_candidate_setting": highest_target_candidate,
        "strongest_default_target_candidate_setting": strongest_default_target_candidate,
        "decision": (
            "threshold_relaxation_needed_for_candidates"
            if candidate_rows_by_threshold else "no_candidates_under_sensitivity_grid"
        ),
    }


def render_markdown(report: dict) -> str:
    summary = report["summary"]
    lines = [
        "# Symmetric Threshold Sensitivity Audit",
        "",
        (
            "Sweeps target-improvement and bidirectional-recording thresholds for the "
            "symmetric recording-support gate. This checks whether the current failure "
            "is a tiny threshold miss or a structurally weak signal."
        ),
        "",
        f"- threshold settings: `{summary['n_threshold_settings']}`",
        f"- settings with candidates: `{summary['n_settings_with_candidates']}`",
        f"- strict candidates at target>=0.55 and bidir>=0.75: `{summary['strict_candidates']}`",
        f"- strict max bidirectional recordings: `{summary['strict_max_bidirectional_recordings']}`",
        f"- decision: `{summary['decision']}`",
        "",
    ]
    if summary["highest_target_candidate_setting"] is not None:
        setting = summary["highest_target_candidate_setting"]
        lines += [
            (
                "Highest target threshold with any candidate: "
                f"`{setting['min_target_improvement']:.3f}` target, "
                f"`{setting['min_bidirectional_recording_fraction']:.2f}` bidir fraction "
                f"(`{setting['n_candidates']}` candidates)."
            ),
            "",
        ]
    if summary["strongest_default_target_candidate_setting"] is not None:
        setting = summary["strongest_default_target_candidate_setting"]
        lines += [
            (
                "At the default target threshold (`0.55`), candidates only appear when "
                "the bidirectional-recording fraction is relaxed to "
                f"`{setting['min_bidirectional_recording_fraction']:.2f}` "
                f"(`{setting['n_candidates']}` candidates)."
            ),
            "",
        ]
    lines += [
        "| target threshold | bidir fraction | candidates | max bidir recs | top row |",
        "|---:|---:|---:|---:|---|",
    ]
    for row in report["rows"]:
        top = row["top_rows"][0] if row["top_rows"] else None
        top_label = "none" if top is None else (
            f"{top['report']} / {top['context']} "
            f"({top['n_bidirectional_recordings']}/{top['n_recordings']}, "
            f"mean_sym={top['mean_symmetric_support']:.3f})"
        )
        lines.append(
            f"| {row['min_target_improvement']:.3f} | "
            f"{row['min_bidirectional_recording_fraction']:.2f} | "
            f"{row['n_candidates']} | {row['max_bidirectional_recordings']} | {top_label} |"
        )
    lines += [
        "",
        "## Decision",
        "",
        (
            "A scientifically useful demo should not require relaxing the symmetric "
            "recording gate below the preregistered target and recording-support floors. "
            "Use this audit to distinguish near misses from threshold artifacts before "
            "spending on model training."
        ),
        "",
    ]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-json", type=Path, default=REPO_ROOT / "docs/symmetric_threshold_sensitivity_audit.json")
    parser.add_argument("--out-md", type=Path, default=REPO_ROOT / "docs/symmetric_threshold_sensitivity_audit.md")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows = sweep_thresholds(
        target_thresholds=TARGET_THRESHOLDS,
        bidirectional_fractions=BIDIRECTIONAL_FRACTIONS,
    )
    report = {
        "target_thresholds": TARGET_THRESHOLDS,
        "bidirectional_fractions": BIDIRECTIONAL_FRACTIONS,
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
