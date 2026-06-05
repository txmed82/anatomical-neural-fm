"""Validate prospect-lead local candidates against the full-manifest gate."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def row_key(row: dict) -> tuple[str, str, str]:
    return (str(row.get("target_mode")), str(row.get("family")), str(row.get("holdout")))


def candidate_rows(payload: dict) -> list[dict]:
    return [row for row in payload.get("rows", []) if row.get("decision") == "candidate"]


def summarize_candidate(row: dict, *, full_row: dict | None) -> dict:
    return {
        "target_mode": row.get("target_mode"),
        "family": row.get("family"),
        "holdout": row.get("holdout"),
        "prospect_decision": row.get("decision"),
        "full_manifest_decision": None if full_row is None else full_row.get("decision"),
        "prospect_centered_delta_vs_shuffle": row.get("centered_delta_vs_shuffle"),
        "prospect_centered_delta_vs_total": row.get("centered_delta_vs_total"),
        "prospect_target0": row.get("target0_improved_vs_shuffle"),
        "prospect_target1": row.get("target1_improved_vs_shuffle"),
        "prospect_n_bidirectional_recordings": row.get("n_bidirectional_recordings"),
        "prospect_n_recordings": row.get("n_recordings"),
        "prospect_bidirectional_recording_fraction": row.get("bidirectional_recording_fraction"),
        "full_n_bidirectional_recordings": None if full_row is None else full_row.get("n_bidirectional_recordings"),
        "full_n_recordings": None if full_row is None else full_row.get("n_recordings"),
        "full_bidirectional_recording_fraction": None if full_row is None else full_row.get("bidirectional_recording_fraction"),
    }


def build_report(
    prospect_gate: dict,
    full_gate: dict,
    *,
    min_candidate_recordings: int = 3,
) -> dict:
    full_by_key = {row_key(row): row for row in full_gate.get("rows", [])}
    candidates = [
        summarize_candidate(row, full_row=full_by_key.get(row_key(row)))
        for row in candidate_rows(prospect_gate)
    ]
    validated = [
        row for row in candidates
        if row["full_manifest_decision"] == "candidate"
        and int(row["prospect_n_recordings"] or 0) >= min_candidate_recordings
    ]
    single_recording = [row for row in candidates if int(row["prospect_n_recordings"] or 0) < min_candidate_recordings]
    subset_only = [
        row for row in candidates
        if row["full_manifest_decision"] != "candidate"
    ]
    decision = "prospect_lead_candidate_validated" if validated else "no_validated_prospect_lead_candidate"
    return {
        "thresholds": {"min_candidate_recordings": min_candidate_recordings},
        "summary": {
            "decision": decision,
            "n_prospect_candidates": len(candidates),
            "n_validated_candidates": len(validated),
            "n_single_recording_candidates": len(single_recording),
            "n_subset_only_candidates": len(subset_only),
            "gpu_training_ready": False,
            "next_action": (
                "Treat prospect-lead rows as design leads only; require full-manifest or held-out validation before GPU training."
                if not validated
                else "Run a pre-registered validation gate on held-out recordings before any GPU training."
            ),
        },
        "prospect_candidates": candidates,
        "validated_candidates": validated,
        "single_recording_candidates": single_recording,
        "subset_only_candidates": subset_only,
    }


def render_markdown(report: dict) -> str:
    summary = report["summary"]
    lines = [
        "# Prospect-Lead Candidate Validation",
        "",
        "Compares candidate rows from the prospect-lead manifest against the full-manifest local gate.",
        "",
        f"- prospect candidates: `{summary['n_prospect_candidates']}`",
        f"- validated candidates: `{summary['n_validated_candidates']}`",
        f"- single-recording candidates: `{summary['n_single_recording_candidates']}`",
        f"- subset-only candidates: `{summary['n_subset_only_candidates']}`",
        f"- decision: `{summary['decision']}`",
        "",
        "| target | family | holdout | full decision | prospect delta shuffle | prospect delta total | target0 | target1 | bidir recs |",
        "|---|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in report["prospect_candidates"]:
        lines.append(
            f"| {row['target_mode']} | {row['family']} | {row['holdout']} | "
            f"{row['full_manifest_decision']} | "
            f"{row['prospect_centered_delta_vs_shuffle']:+.3f} | "
            f"{row['prospect_centered_delta_vs_total']:+.3f} | "
            f"{row['prospect_target0']:.3f} | {row['prospect_target1']:.3f} | "
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
    parser.add_argument(
        "--prospect-gate",
        type=Path,
        default=REPO_ROOT / "docs/derived_target_family_gate_prospect_leads.json",
    )
    parser.add_argument("--full-gate", type=Path, default=REPO_ROOT / "docs/derived_target_family_gate.json")
    parser.add_argument("--min-candidate-recordings", type=int, default=3)
    parser.add_argument("--out-json", type=Path, default=REPO_ROOT / "docs/prospect_lead_candidate_validation.json")
    parser.add_argument("--out-md", type=Path, default=REPO_ROOT / "docs/prospect_lead_candidate_validation.md")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(
        json.loads(args.prospect_gate.read_text()),
        json.loads(args.full_gate.read_text()),
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
