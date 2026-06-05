"""Find subject-stable local-gate near misses across current artifacts."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from audit_local_gate_meta_failures import THRESHOLDS, row_failures, row_gate_score  # noqa: E402


DEFAULT_ARTIFACTS = {
    "shared_family": "docs/shared_family_target_control_gate.json",
    "derived_recording_centered": "docs/derived_target_family_gate.json",
    "derived_counts": "docs/derived_target_family_gate_counts.json",
    "derived_fractions": "docs/derived_target_family_gate_fractions.json",
    "derived_unit_residuals": "docs/derived_target_family_gate_unit_residuals.json",
    "contextual_targets": "docs/contextual_target_family_gate.json",
    "wheel_targets": "docs/wheel_target_family_gate.json",
    "reaction_recording_centered": "docs/reaction_dynamics_target_family_gate.json",
    "reaction_counts": "docs/reaction_dynamics_target_family_gate_counts.json",
    "reaction_fractions": "docs/reaction_dynamics_target_family_gate_fractions.json",
    "reaction_unit_residuals": "docs/reaction_dynamics_target_family_gate_unit_residuals.json",
    "cell_type_priors": "docs/cell_type_prior_target_control_gate.json",
    "waveform": "docs/waveform_target_control_gate.json",
    "projected_support80_recording_centered": (
        "docs/shared_family_target_control_gate_projected_support80_all_families.json"
    ),
    "projected_support80_counts": "docs/shared_family_target_control_gate_projected_support80_all_families_counts.json",
    "projected_support80_fractions": (
        "docs/shared_family_target_control_gate_projected_support80_all_families_fractions.json"
    ),
    "projected_support80_unit_residuals": (
        "docs/shared_family_target_control_gate_projected_support80_all_families_unit_residuals.json"
    ),
}


def read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text())


def normalize_row(source: str, row: dict) -> dict:
    failures = row_failures(row)
    return {
        "source": source,
        "target_mode": row.get("target_mode"),
        "feature": row.get("family") or row.get("region") or row.get("name"),
        "holdout": row.get("holdout"),
        "decision": row.get("decision"),
        "centered_delta_vs_shuffle": row.get("centered_delta_vs_shuffle"),
        "centered_delta_vs_total": row.get("centered_delta_vs_total"),
        "target0_improved_vs_shuffle": row.get("target0_improved_vs_shuffle"),
        "target1_improved_vs_shuffle": row.get("target1_improved_vs_shuffle"),
        "n_bidirectional_recordings": row.get("n_bidirectional_recordings"),
        "n_recordings": row.get("n_recordings"),
        "bidirectional_recording_fraction": row.get("bidirectional_recording_fraction"),
        "failures": failures,
        "n_failures": len(failures),
        "gate_score": row_gate_score(row),
        "recording_target_rows": row.get("recording_target_rows", []),
    }


def is_subject_stable(row: dict, *, min_recordings: int, min_bidirectional_fraction: float) -> bool:
    return (
        int(row.get("n_recordings") or 0) >= min_recordings
        and float(row.get("bidirectional_recording_fraction") or 0.0) >= min_bidirectional_fraction
    )


def build_report(
    artifact_paths: dict[str, str] = DEFAULT_ARTIFACTS,
    *,
    min_recordings: int = 3,
    min_bidirectional_fraction: float = 0.75,
) -> dict:
    rows = []
    artifact_summaries = {}
    for source, rel_path in artifact_paths.items():
        payload = read_json(REPO_ROOT / rel_path)
        if payload is None:
            artifact_summaries[source] = {"present": False, "path": rel_path}
            continue
        source_rows = [normalize_row(source, row) for row in payload.get("rows", [])]
        rows.extend(source_rows)
        stable_source_rows = [
            row for row in source_rows
            if is_subject_stable(
                row,
                min_recordings=min_recordings,
                min_bidirectional_fraction=min_bidirectional_fraction,
            )
        ]
        artifact_summaries[source] = {
            "present": True,
            "path": rel_path,
            "n_rows": len(source_rows),
            "n_subject_stable_rows": len(stable_source_rows),
            "n_subject_stable_candidates": sum(1 for row in stable_source_rows if row["n_failures"] == 0),
        }

    stable_rows = [
        row for row in rows
        if is_subject_stable(
            row,
            min_recordings=min_recordings,
            min_bidirectional_fraction=min_bidirectional_fraction,
        )
    ]
    stable_candidates = [row for row in stable_rows if row["n_failures"] == 0]
    stable_one_failure = [row for row in stable_rows if row["n_failures"] == 1]
    stable_rows = sorted(
        stable_rows,
        key=lambda row: (
            row["n_failures"],
            -row["gate_score"],
            -(row.get("centered_delta_vs_shuffle") or float("-inf")),
        ),
    )
    stable_holdouts = sorted({row["holdout"] for row in stable_rows})
    failure_counts: dict[str, int] = {}
    for row in stable_rows:
        for failure in row["failures"]:
            failure_counts[failure] = failure_counts.get(failure, 0) + 1
    decision = (
        "subject_stable_local_gate_candidate"
        if stable_candidates
        else "no_subject_stable_local_gate_candidate"
    )
    return {
        "thresholds": {
            **THRESHOLDS,
            "min_recordings": min_recordings,
            "min_bidirectional_fraction": min_bidirectional_fraction,
        },
        "artifacts": artifact_summaries,
        "summary": {
            "decision": decision,
            "n_rows": len(rows),
            "n_subject_stable_rows": len(stable_rows),
            "n_subject_stable_candidates": len(stable_candidates),
            "n_subject_stable_one_failure_rows": len(stable_one_failure),
            "subject_stable_holdouts": stable_holdouts,
            "failure_counts": failure_counts,
            "gpu_training_ready": False,
            "next_action": (
                "Do not train yet: subject-stable near misses exist, but they fail the unchanged local gate."
                if not stable_candidates
                else "Validate the subject-stable candidate on a pre-registered held-out manifest before training."
            ),
        },
        "subject_stable_rows": stable_rows,
        "subject_stable_candidates": stable_candidates,
        "subject_stable_one_failure_rows": stable_one_failure,
    }


def fmt(value) -> str:
    if value is None:
        return "n/a"
    return f"{float(value):.3f}"


def render_markdown(report: dict) -> str:
    summary = report["summary"]
    lines = [
        "# Subject-Stable Local Gate Prospectus",
        "",
        "Searches current local-gate artifacts for rows that are stable across multiple recordings in the held-out subject.",
        "",
        f"- rows: `{summary['n_rows']}`",
        f"- subject-stable rows: `{summary['n_subject_stable_rows']}`",
        f"- subject-stable candidates: `{summary['n_subject_stable_candidates']}`",
        f"- subject-stable one-failure rows: `{summary['n_subject_stable_one_failure_rows']}`",
        f"- subject-stable holdouts: `{', '.join(summary['subject_stable_holdouts']) or 'none'}`",
        f"- decision: `{summary['decision']}`",
        "",
        "## Stable Rows",
        "",
        "| source | target | feature | holdout | failures | delta shuffle | delta total | target0 | target1 | bidir recs |",
        "|---|---|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in report["subject_stable_rows"][:16]:
        lines.append(
            f"| {row['source']} | {row['target_mode']} | {row['feature']} | {row['holdout']} | "
            f"{', '.join(row['failures']) or 'none'} | "
            f"{fmt(row['centered_delta_vs_shuffle'])} | {fmt(row['centered_delta_vs_total'])} | "
            f"{fmt(row['target0_improved_vs_shuffle'])} | {fmt(row['target1_improved_vs_shuffle'])} | "
            f"{row['n_bidirectional_recordings']}/{row['n_recordings']} |"
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
    parser.add_argument("--min-recordings", type=int, default=3)
    parser.add_argument("--min-bidirectional-fraction", type=float, default=0.75)
    parser.add_argument(
        "--out-json",
        type=Path,
        default=REPO_ROOT / "docs/subject_stable_local_gate_prospectus.json",
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=REPO_ROOT / "docs/subject_stable_local_gate_prospectus.md",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(
        min_recordings=args.min_recordings,
        min_bidirectional_fraction=args.min_bidirectional_fraction,
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
