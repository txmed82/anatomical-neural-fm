"""Audit whether prospect-lead candidates are stable within the same held-out subject."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from audit_prospect_lead_candidate_validation import row_key  # noqa: E402
from audit_prospect_lead_feature_mode_validation import DEFAULT_GATE_PAIRS  # noqa: E402

DEFAULT_PROSPECT_MANIFEST = REPO_ROOT / "manifests/ibl_bwm_recording_bidirectionality_prospect_leads.json"


def prospect_recording_ids(path: Path = DEFAULT_PROSPECT_MANIFEST) -> set[str]:
    payload = json.loads(path.read_text())
    return {row["recording_id"] for row in payload["recordings"]}


def candidate_rows(payload: dict) -> list[dict]:
    return [row for row in payload.get("rows", []) if row.get("decision") == "candidate"]


def summarize_recording_group(rows: list[dict], *, min_target_improvement: float) -> dict:
    if not rows:
        return {
            "n_recordings": 0,
            "n_bidirectional_recordings": 0,
            "bidirectional_fraction": 0.0,
            "mean_target0": None,
            "mean_target1": None,
            "mean_improved_fraction": None,
            "recordings": [],
        }
    bidir = [
        row for row in rows
        if row.get("target0_improved", 0.0) >= min_target_improvement
        and row.get("target1_improved", 0.0) >= min_target_improvement
    ]
    return {
        "n_recordings": len(rows),
        "n_bidirectional_recordings": len(bidir),
        "bidirectional_fraction": len(bidir) / len(rows),
        "mean_target0": sum(float(row["target0_improved"]) for row in rows) / len(rows),
        "mean_target1": sum(float(row["target1_improved"]) for row in rows) / len(rows),
        "mean_improved_fraction": sum(float(row["improved_fraction"]) for row in rows) / len(rows),
        "recordings": rows,
    }


def candidate_stability_row(
    *,
    feature_mode: str,
    prospect_row: dict,
    full_row: dict | None,
    lead_ids: set[str],
    min_target_improvement: float,
) -> dict:
    full_recording_rows = [] if full_row is None else list(full_row.get("recording_target_rows", []))
    lead_rows = [row for row in full_recording_rows if row["recording"] in lead_ids]
    nonlead_rows = [row for row in full_recording_rows if row["recording"] not in lead_ids]
    lead_summary = summarize_recording_group(lead_rows, min_target_improvement=min_target_improvement)
    nonlead_summary = summarize_recording_group(nonlead_rows, min_target_improvement=min_target_improvement)
    full_summary = summarize_recording_group(full_recording_rows, min_target_improvement=min_target_improvement)
    stable = (
        full_row is not None
        and full_row.get("decision") == "candidate"
        and nonlead_summary["n_recordings"] > 0
        and nonlead_summary["bidirectional_fraction"] >= 0.75
        and (nonlead_summary["mean_target0"] or 0.0) >= min_target_improvement
        and (nonlead_summary["mean_target1"] or 0.0) >= min_target_improvement
    )
    return {
        "feature_mode": feature_mode,
        "target_mode": prospect_row.get("target_mode"),
        "family": prospect_row.get("family"),
        "holdout": prospect_row.get("holdout"),
        "prospect_decision": prospect_row.get("decision"),
        "full_manifest_decision": None if full_row is None else full_row.get("decision"),
        "lead": lead_summary,
        "nonlead": nonlead_summary,
        "full": full_summary,
        "same_subject_stable": stable,
    }


def build_report(
    gate_pairs: dict[str, dict[str, str]],
    *,
    lead_ids: set[str],
    min_target_improvement: float = 0.55,
) -> dict:
    rows = []
    for feature_mode, paths in gate_pairs.items():
        prospect = json.loads((REPO_ROOT / paths["prospect"]).read_text())
        full = json.loads((REPO_ROOT / paths["full"]).read_text())
        full_by_key = {row_key(row): row for row in full.get("rows", [])}
        for prospect_row in candidate_rows(prospect):
            rows.append(candidate_stability_row(
                feature_mode=feature_mode,
                prospect_row=prospect_row,
                full_row=full_by_key.get(row_key(prospect_row)),
                lead_ids=lead_ids,
                min_target_improvement=min_target_improvement,
            ))
    stable = [row for row in rows if row["same_subject_stable"]]
    with_nonlead_failure = [
        row for row in rows
        if row["nonlead"]["n_recordings"] > 0 and not row["same_subject_stable"]
    ]
    decision = "same_subject_stable_prospect_candidate" if stable else "no_same_subject_stable_prospect_candidate"
    return {
        "thresholds": {"min_target_improvement": min_target_improvement},
        "summary": {
            "decision": decision,
            "n_prospect_candidates": len(rows),
            "n_same_subject_stable_candidates": len(stable),
            "n_candidates_with_nonlead_failure": len(with_nonlead_failure),
            "gpu_training_ready": False,
            "next_action": (
                "Do not train on prospect-lead candidates; same-subject non-lead recordings do not validate them."
                if not stable
                else "Pre-register a held-out same-subject validation split before any GPU training."
            ),
        },
        "rows": rows,
        "same_subject_stable_candidates": stable,
    }


def fmt(value) -> str:
    if value is None:
        return "n/a"
    return f"{float(value):.3f}"


def render_markdown(report: dict) -> str:
    summary = report["summary"]
    lines = [
        "# Prospect-Lead Subject Stability Audit",
        "",
        "Checks whether prospect-lead derived candidates also hold on same-subject non-lead recordings.",
        "",
        f"- prospect candidates: `{summary['n_prospect_candidates']}`",
        f"- same-subject stable candidates: `{summary['n_same_subject_stable_candidates']}`",
        f"- candidates with non-lead failure: `{summary['n_candidates_with_nonlead_failure']}`",
        f"- decision: `{summary['decision']}`",
        "",
        "| feature | target | family | holdout | full decision | lead bidir | nonlead bidir | lead targets | nonlead targets |",
        "|---|---|---|---|---|---:|---:|---:|---:|",
    ]
    for row in report["rows"]:
        lead = row["lead"]
        nonlead = row["nonlead"]
        lines.append(
            f"| {row['feature_mode']} | {row['target_mode']} | {row['family']} | "
            f"{row['holdout']} | {row['full_manifest_decision']} | "
            f"{lead['n_bidirectional_recordings']}/{lead['n_recordings']} | "
            f"{nonlead['n_bidirectional_recordings']}/{nonlead['n_recordings']} | "
            f"{fmt(lead['mean_target0'])}/{fmt(lead['mean_target1'])} | "
            f"{fmt(nonlead['mean_target0'])}/{fmt(nonlead['mean_target1'])} |"
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
    parser.add_argument("--prospect-manifest", type=Path, default=DEFAULT_PROSPECT_MANIFEST)
    parser.add_argument("--min-target-improvement", type=float, default=0.55)
    parser.add_argument(
        "--out-json",
        type=Path,
        default=REPO_ROOT / "docs/prospect_lead_subject_stability.json",
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=REPO_ROOT / "docs/prospect_lead_subject_stability.md",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(
        DEFAULT_GATE_PAIRS,
        lead_ids=prospect_recording_ids(args.prospect_manifest),
        min_target_improvement=args.min_target_improvement,
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
