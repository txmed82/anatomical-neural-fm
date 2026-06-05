"""Validate prospect-lead derived candidates across feature modes."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from audit_prospect_lead_candidate_validation import build_report  # noqa: E402

DEFAULT_GATE_PAIRS = {
    "recording_centered": {
        "prospect": "docs/derived_target_family_gate_prospect_leads.json",
        "full": "docs/derived_target_family_gate.json",
    },
    "counts": {
        "prospect": "docs/derived_target_family_gate_prospect_leads_counts.json",
        "full": "docs/derived_target_family_gate_counts.json",
    },
    "fractions": {
        "prospect": "docs/derived_target_family_gate_prospect_leads_fractions.json",
        "full": "docs/derived_target_family_gate_fractions.json",
    },
    "unit_residuals": {
        "prospect": "docs/derived_target_family_gate_prospect_leads_unit_residuals.json",
        "full": "docs/derived_target_family_gate_unit_residuals.json",
    },
}


def build_feature_mode_report(
    gate_pairs: dict[str, dict[str, str]],
    *,
    min_candidate_recordings: int = 3,
) -> dict:
    mode_rows = []
    prospect_candidates = []
    validated_candidates = []
    for mode, paths in gate_pairs.items():
        prospect_path = REPO_ROOT / paths["prospect"]
        full_path = REPO_ROOT / paths["full"]
        prospect_gate = json.loads(prospect_path.read_text())
        full_gate = json.loads(full_path.read_text())
        validation = build_report(
            prospect_gate,
            full_gate,
            min_candidate_recordings=min_candidate_recordings,
        )
        prospect_summary = prospect_gate["summary"]
        full_summary = full_gate["summary"]
        mode_rows.append({
            "feature_mode": mode,
            "prospect_gate": paths["prospect"],
            "full_gate": paths["full"],
            "prospect_candidates": prospect_summary["n_candidates"],
            "full_candidates": full_summary["n_candidates"],
            "validated_candidates": validation["summary"]["n_validated_candidates"],
            "single_recording_candidates": validation["summary"]["n_single_recording_candidates"],
            "subset_only_candidates": validation["summary"]["n_subset_only_candidates"],
            "prospect_max_bidirectional_recordings": prospect_summary["max_bidirectional_recordings"],
            "prospect_max_bidirectional_recording_fraction": prospect_summary[
                "max_bidirectional_recording_fraction"
            ],
            "full_max_bidirectional_recordings": full_summary["max_bidirectional_recordings"],
            "full_max_bidirectional_recording_fraction": full_summary["max_bidirectional_recording_fraction"],
        })
        for row in validation["prospect_candidates"]:
            prospect_candidates.append(row | {"feature_mode": mode})
        for row in validation["validated_candidates"]:
            validated_candidates.append(row | {"feature_mode": mode})
    decision = (
        "prospect_lead_feature_mode_candidate_validated"
        if validated_candidates else
        "no_validated_prospect_lead_feature_mode_candidate"
    )
    return {
        "thresholds": {"min_candidate_recordings": min_candidate_recordings},
        "summary": {
            "decision": decision,
            "n_feature_modes": len(mode_rows),
            "n_prospect_candidates": sum(row["prospect_candidates"] for row in mode_rows),
            "n_full_candidates": sum(row["full_candidates"] for row in mode_rows),
            "n_validated_candidates": len(validated_candidates),
            "n_single_recording_candidates": sum(row["single_recording_candidates"] for row in mode_rows),
            "n_subset_only_candidates": sum(row["subset_only_candidates"] for row in mode_rows),
            "gpu_training_ready": False,
            "next_action": (
                "Do not spend on prospect-lead derived candidates; they fail full-manifest feature-mode validation."
                if not validated_candidates
                else "Pre-register a held-out validation split before any GPU training."
            ),
        },
        "feature_mode_rows": mode_rows,
        "prospect_candidates": prospect_candidates,
        "validated_candidates": validated_candidates,
    }


def render_markdown(report: dict) -> str:
    summary = report["summary"]
    lines = [
        "# Prospect-Lead Feature-Mode Validation",
        "",
        "Validates prospect-lead derived target candidates across all tested feature modes.",
        "",
        f"- feature modes: `{summary['n_feature_modes']}`",
        f"- prospect candidates: `{summary['n_prospect_candidates']}`",
        f"- full-manifest candidates: `{summary['n_full_candidates']}`",
        f"- validated candidates: `{summary['n_validated_candidates']}`",
        f"- single-recording candidates: `{summary['n_single_recording_candidates']}`",
        f"- subset-only candidates: `{summary['n_subset_only_candidates']}`",
        f"- decision: `{summary['decision']}`",
        "",
        "## Feature Modes",
        "",
        "| feature mode | prospect candidates | full candidates | validated | single-rec | subset-only | prospect max bidir | full max bidir |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["feature_mode_rows"]:
        lines.append(
            f"| {row['feature_mode']} | {row['prospect_candidates']} | "
            f"{row['full_candidates']} | {row['validated_candidates']} | "
            f"{row['single_recording_candidates']} | {row['subset_only_candidates']} | "
            f"{row['prospect_max_bidirectional_recordings']} | {row['full_max_bidirectional_recordings']} |"
        )
    lines += [
        "",
        "## Prospect Candidates",
        "",
        "| feature mode | target | family | holdout | full decision | bidir recs |",
        "|---|---|---|---|---|---:|",
    ]
    for row in report["prospect_candidates"]:
        lines.append(
            f"| {row['feature_mode']} | {row['target_mode']} | {row['family']} | "
            f"{row['holdout']} | {row['full_manifest_decision']} | "
            f"{row['prospect_n_bidirectional_recordings']}/{row['prospect_n_recordings']} |"
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
    parser.add_argument("--min-candidate-recordings", type=int, default=3)
    parser.add_argument(
        "--out-json",
        type=Path,
        default=REPO_ROOT / "docs/prospect_lead_feature_mode_validation.json",
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=REPO_ROOT / "docs/prospect_lead_feature_mode_validation.md",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_feature_mode_report(
        DEFAULT_GATE_PAIRS,
        min_candidate_recordings=args.min_candidate_recordings,
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
