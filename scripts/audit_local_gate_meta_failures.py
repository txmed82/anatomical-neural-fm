"""Aggregate local gate failures into a benchmark redesign rule."""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


DEFAULT_ARTIFACTS = {
    "shared_family": "docs/shared_family_target_control_gate.json",
    "derived_targets": "docs/derived_target_family_gate.json",
    "contextual_targets": "docs/contextual_target_family_gate.json",
    "wheel_targets": "docs/wheel_target_family_gate.json",
    "reaction_dynamics": "docs/reaction_dynamics_target_family_gate.json",
    "cell_type_priors": "docs/cell_type_prior_target_control_gate.json",
    "waveform": "docs/waveform_target_control_gate.json",
    "projected_support80_all_families": "docs/shared_family_target_control_gate_projected_support80_all_families.json",
    "projected_support80_counts": "docs/shared_family_target_control_gate_projected_support80_all_families_counts.json",
    "projected_support80_fractions": "docs/shared_family_target_control_gate_projected_support80_all_families_fractions.json",
    "projected_support80_unit_residuals": "docs/shared_family_target_control_gate_projected_support80_all_families_unit_residuals.json",
}


THRESHOLDS = {
    "centered_delta_vs_shuffle": 0.0,
    "centered_delta_vs_total": 0.0,
    "target0_improved_vs_shuffle": 0.55,
    "target1_improved_vs_shuffle": 0.55,
    "bidirectional_recording_fraction": 0.75,
}


def read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text())


def row_failures(row: dict, thresholds: dict[str, float] = THRESHOLDS) -> list[str]:
    failures = []
    if row.get("centered_delta_vs_shuffle", float("-inf")) < thresholds["centered_delta_vs_shuffle"]:
        failures.append("shuffle")
    if row.get("centered_delta_vs_total", float("-inf")) < thresholds["centered_delta_vs_total"]:
        failures.append("total_baseline")
    if row.get("target0_improved_vs_shuffle", float("-inf")) < thresholds["target0_improved_vs_shuffle"]:
        failures.append("target0")
    if row.get("target1_improved_vs_shuffle", float("-inf")) < thresholds["target1_improved_vs_shuffle"]:
        failures.append("target1")
    if row.get("bidirectional_recording_fraction", float("-inf")) < thresholds["bidirectional_recording_fraction"]:
        failures.append("recording_bidirectionality")
    return failures


def row_gate_score(row: dict, thresholds: dict[str, float] = THRESHOLDS) -> float:
    margins = [
        row.get("centered_delta_vs_shuffle", float("-inf")) - thresholds["centered_delta_vs_shuffle"],
        row.get("centered_delta_vs_total", float("-inf")) - thresholds["centered_delta_vs_total"],
        row.get("target0_improved_vs_shuffle", float("-inf")) - thresholds["target0_improved_vs_shuffle"],
        row.get("target1_improved_vs_shuffle", float("-inf")) - thresholds["target1_improved_vs_shuffle"],
        row.get("bidirectional_recording_fraction", float("-inf")) - thresholds["bidirectional_recording_fraction"],
    ]
    return min(margins)


def normalized_row(source: str, row: dict) -> dict:
    failures = row_failures(row)
    out = {
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
    }
    return out


def build_report(artifact_paths: dict[str, str] = DEFAULT_ARTIFACTS) -> dict:
    rows = []
    artifact_summaries = {}
    for name, rel_path in artifact_paths.items():
        payload = read_json(REPO_ROOT / rel_path)
        if payload is None:
            artifact_summaries[name] = {"present": False}
            continue
        source_rows = [normalized_row(name, row) for row in payload.get("rows", [])]
        rows.extend(source_rows)
        summary = payload.get("summary", {})
        artifact_summaries[name] = {
            "present": True,
            "path": rel_path,
            "n_rows": len(source_rows),
            "n_candidates": summary.get("n_candidates", 0),
            "max_bidirectional_recording_fraction": summary.get("max_bidirectional_recording_fraction", 0.0),
            "decision": summary.get("decision"),
        }

    failure_counts = Counter(failure for row in rows for failure in row["failures"])
    first_failure_counts = Counter((row["decision"] or "").replace("reject: ", "") for row in rows)
    by_source = {}
    for source in sorted({row["source"] for row in rows}):
        source_rows = [row for row in rows if row["source"] == source]
        by_source[source] = {
            "n_rows": len(source_rows),
            "n_one_failure_rows": sum(1 for row in source_rows if row["n_failures"] == 1),
            "n_two_or_fewer_failure_rows": sum(1 for row in source_rows if row["n_failures"] <= 2),
            "best_gate_score": max((row["gate_score"] for row in source_rows), default=float("-inf")),
            "max_bidirectional_recording_fraction": max(
                (row["bidirectional_recording_fraction"] or 0.0 for row in source_rows),
                default=0.0,
            ),
        }
    near_misses = sorted(
        [row for row in rows if row["n_failures"] <= 2],
        key=lambda row: (
            row["n_failures"],
            -row["gate_score"],
            -(row.get("bidirectional_recording_fraction") or 0.0),
            -(row.get("centered_delta_vs_shuffle") or float("-inf")),
        ),
    )
    one_failure_rows = [row for row in rows if row["n_failures"] == 1]
    one_failure_by_type: dict[str, int] = defaultdict(int)
    for row in one_failure_rows:
        one_failure_by_type[row["failures"][0]] += 1
    summary = {
        "n_artifacts_present": sum(1 for row in artifact_summaries.values() if row.get("present")),
        "n_rows": len(rows),
        "n_candidates": sum(1 for row in rows if not row["failures"]),
        "n_one_failure_rows": len(one_failure_rows),
        "n_two_or_fewer_failure_rows": sum(1 for row in rows if row["n_failures"] <= 2),
        "failure_counts": dict(failure_counts),
        "first_failure_counts": dict(first_failure_counts),
        "one_failure_by_type": dict(sorted(one_failure_by_type.items())),
        "max_bidirectional_recording_fraction": max(
            (row["bidirectional_recording_fraction"] or 0.0 for row in rows),
            default=0.0,
        ),
        "decision": "no_local_gate_candidate",
        "redesign_rule": (
            "Do not run GPU training until a prospectively defined target/control produces "
            "same-recording bidirectional support, not just global centered deltas. The next "
            "target should be designed around within-recording target0+target1 evidence and "
            "must pass the unchanged local true-vs-shuffle, total-baseline, global target, "
            "and bidirectional-recording gate before training."
        ),
    }
    return {
        "thresholds": THRESHOLDS,
        "artifacts": artifact_summaries,
        "summary": summary,
        "by_source": by_source,
        "near_misses": near_misses[:24],
        "rows": rows,
    }


def fmt(value, digits: int = 3) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def render_markdown(report: dict) -> str:
    summary = report["summary"]
    lines = [
        "# Local Gate Meta-Failure Audit",
        "",
        (
            "Aggregates closed no-spend target/control gates and ranks near misses "
            "against the unchanged GPU promotion criteria."
        ),
        "",
        f"- artifacts present: `{summary['n_artifacts_present']}`",
        f"- rows audited: `{summary['n_rows']}`",
        f"- candidates: `{summary['n_candidates']}`",
        f"- one-failure rows: `{summary['n_one_failure_rows']}`",
        f"- two-or-fewer-failure rows: `{summary['n_two_or_fewer_failure_rows']}`",
        f"- max bidirectional recording fraction: `{summary['max_bidirectional_recording_fraction']:.3f}`",
        f"- decision: `{summary['decision']}`",
        "",
        "## Failure Counts",
        "",
        "| failure | rows | one-failure rows |",
        "|---|---:|---:|",
    ]
    one_failure = summary["one_failure_by_type"]
    for failure, count in sorted(summary["failure_counts"].items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"| {failure} | {count} | {one_failure.get(failure, 0)} |")
    lines += [
        "",
        "## Source Summary",
        "",
        "| source | rows | <=1 fail | <=2 fails | best score | max bidir |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for source, row in sorted(report["by_source"].items()):
        lines.append(
            f"| {source} | {row['n_rows']} | {row['n_one_failure_rows']} | "
            f"{row['n_two_or_fewer_failure_rows']} | {fmt(row['best_gate_score'])} | "
            f"{fmt(row['max_bidirectional_recording_fraction'])} |"
        )
    lines += [
        "",
        "## Top Near Misses",
        "",
        "| fails | source | target | feature | holdout | failures | delta shuffle | delta total | target0 | target1 | bidir |",
        "|---:|---|---|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in report["near_misses"][:16]:
        lines.append(
            f"| {row['n_failures']} | {row['source']} | {row['target_mode']} | {row['feature']} | "
            f"{row['holdout']} | {', '.join(row['failures']) or 'none'} | "
            f"{fmt(row['centered_delta_vs_shuffle'])} | {fmt(row['centered_delta_vs_total'])} | "
            f"{fmt(row['target0_improved_vs_shuffle'])} | {fmt(row['target1_improved_vs_shuffle'])} | "
            f"{row['n_bidirectional_recordings']}/{row['n_recordings']} |"
        )
    lines += [
        "",
        "## Redesign Rule",
        "",
        summary["redesign_rule"],
        "",
    ]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-json", type=Path, default=REPO_ROOT / "docs/local_gate_meta_failure_audit.json")
    parser.add_argument("--out-md", type=Path, default=REPO_ROOT / "docs/local_gate_meta_failure_audit.md")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report()
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text(render_markdown(report))
    print(f"wrote {args.out_json}")
    print(f"wrote {args.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
