"""Test whether recording-level support replicates across model-free report families."""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from audit_model_free_gate_blockers import DEFAULT_REPORTS  # noqa: E402
from audit_model_free_recording_support import (  # noqa: E402
    RecordingObservation,
    is_bidirectional,
    load_observations,
)


DISCOVERY_REPORTS = {
    "panel recording centered",
    "family centered",
    "family centered l2=1",
    "family centered l2=100",
}
VALIDATION_REPORTS = {
    "source-target centered",
    "source-target families",
    "family prior side",
    "family feedback",
}


@dataclass(frozen=True)
class RecordingReplicationRow:
    recording: str
    target_subject: str
    discovery_observations: int
    discovery_bidirectional_observations: int
    discovery_bidirectional_fraction: float
    discovery_mean_target0: float
    discovery_mean_target1: float
    validation_observations: int
    validation_bidirectional_observations: int
    validation_bidirectional_fraction: float
    validation_mean_target0: float
    validation_mean_target1: float
    selected: bool
    replicated: bool


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def summarize_group(observations: list[RecordingObservation], *, min_target_improvement: float) -> dict:
    bidirectional = [
        obs for obs in observations
        if is_bidirectional(obs, min_target_improvement=min_target_improvement)
    ]
    return {
        "n_observations": len(observations),
        "n_bidirectional_observations": len(bidirectional),
        "bidirectional_fraction": len(bidirectional) / len(observations) if observations else 0.0,
        "mean_target0": mean([obs.target0 for obs in observations]),
        "mean_target1": mean([obs.target1 for obs in observations]),
    }


def load_all_observations(report_specs: tuple[tuple[str, str], ...]) -> list[RecordingObservation]:
    observations = []
    for label, rel_path in report_specs:
        path = REPO_ROOT / rel_path
        if path.exists():
            observations.extend(load_observations(label, path))
    return observations


def build_replication_rows(
    observations: list[RecordingObservation],
    *,
    discovery_reports: set[str],
    validation_reports: set[str],
    min_target_improvement: float,
    min_discovery_bidirectional_fraction: float,
    min_validation_bidirectional_fraction: float,
    min_discovery_observations: int,
    min_validation_observations: int,
) -> list[RecordingReplicationRow]:
    by_recording_subject: dict[tuple[str, str], list[RecordingObservation]] = defaultdict(list)
    for obs in observations:
        by_recording_subject[(obs.recording, obs.target_subject)].append(obs)

    rows = []
    for (recording, target_subject), rec_obs in by_recording_subject.items():
        discovery = [obs for obs in rec_obs if obs.report in discovery_reports]
        validation = [obs for obs in rec_obs if obs.report in validation_reports]
        discovery_summary = summarize_group(discovery, min_target_improvement=min_target_improvement)
        validation_summary = summarize_group(validation, min_target_improvement=min_target_improvement)
        selected = (
            discovery_summary["n_observations"] >= min_discovery_observations
            and discovery_summary["bidirectional_fraction"] >= min_discovery_bidirectional_fraction
            and discovery_summary["mean_target0"] >= min_target_improvement
            and discovery_summary["mean_target1"] >= min_target_improvement
        )
        replicated = (
            selected
            and validation_summary["n_observations"] >= min_validation_observations
            and validation_summary["bidirectional_fraction"] >= min_validation_bidirectional_fraction
            and validation_summary["mean_target0"] >= min_target_improvement
            and validation_summary["mean_target1"] >= min_target_improvement
        )
        rows.append(
            RecordingReplicationRow(
                recording=recording,
                target_subject=target_subject,
                discovery_observations=discovery_summary["n_observations"],
                discovery_bidirectional_observations=discovery_summary["n_bidirectional_observations"],
                discovery_bidirectional_fraction=discovery_summary["bidirectional_fraction"],
                discovery_mean_target0=discovery_summary["mean_target0"],
                discovery_mean_target1=discovery_summary["mean_target1"],
                validation_observations=validation_summary["n_observations"],
                validation_bidirectional_observations=validation_summary["n_bidirectional_observations"],
                validation_bidirectional_fraction=validation_summary["bidirectional_fraction"],
                validation_mean_target0=validation_summary["mean_target0"],
                validation_mean_target1=validation_summary["mean_target1"],
                selected=selected,
                replicated=replicated,
            )
        )
    return sorted(
        rows,
        key=lambda row: (
            row.replicated,
            row.selected,
            row.discovery_bidirectional_fraction,
            min(row.validation_mean_target0, row.validation_mean_target1),
            row.validation_bidirectional_fraction,
        ),
        reverse=True,
    )


def summarize(rows: list[RecordingReplicationRow]) -> dict:
    selected = [row for row in rows if row.selected]
    replicated = [row for row in rows if row.replicated]
    subjects = sorted({row.target_subject for row in rows})
    return {
        "n_recording_subject_rows": len(rows),
        "n_subjects": len(subjects),
        "subjects": subjects,
        "n_selected_by_discovery_rule": len(selected),
        "n_replicated_in_validation": len(replicated),
        "selected_recordings": [
            {"recording": row.recording, "target_subject": row.target_subject}
            for row in selected
        ],
        "replicated_recordings": [
            {"recording": row.recording, "target_subject": row.target_subject}
            for row in replicated
        ],
        "decision": (
            "recording_rule_replicates"
            if replicated else "no_replicating_recording_rule"
        ),
    }


def render_markdown(report: dict) -> str:
    summary = report["summary"]
    lines = [
        "# Model-Free Recording Replication Audit",
        "",
        (
            "Prospective recording-level screen using fixed report families. A recording "
            "is selected only from discovery reports, then tested on held-out validation "
            "reports to avoid defining a demo subset after seeing every gate row."
        ),
        "",
        f"- discovery reports: `{', '.join(report['discovery_reports'])}`",
        f"- validation reports: `{', '.join(report['validation_reports'])}`",
        f"- recording-subject rows: `{summary['n_recording_subject_rows']}`",
        f"- selected by discovery rule: `{summary['n_selected_by_discovery_rule']}`",
        f"- replicated in validation: `{summary['n_replicated_in_validation']}`",
        f"- decision: `{summary['decision']}`",
        "",
        "## Top Recording Rules",
        "",
        "| subject | recording | selected | replicated | discovery bidir | discovery target0 | discovery target1 | validation bidir | validation target0 | validation target1 |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["rows"][:14]:
        lines.append(
            f"| {row['target_subject']} | {row['recording']} | "
            f"{row['selected']} | {row['replicated']} | "
            f"{row['discovery_bidirectional_observations']}/{row['discovery_observations']} "
            f"({row['discovery_bidirectional_fraction']:.3f}) | "
            f"{row['discovery_mean_target0']:.3f} | {row['discovery_mean_target1']:.3f} | "
            f"{row['validation_bidirectional_observations']}/{row['validation_observations']} "
            f"({row['validation_bidirectional_fraction']:.3f}) | "
            f"{row['validation_mean_target0']:.3f} | {row['validation_mean_target1']:.3f} |"
        )
    lines += [
        "",
        "## Decision",
        "",
        (
            "A recording subset is not a credible next benchmark unless it is selected "
            "by the discovery rule and keeps bidirectional target support in validation. "
            "If this audit has zero replicated recordings, the next step is to redesign "
            "the target/control or manifest rather than launch GPU training."
        ),
        "",
    ]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-json", type=Path, default=REPO_ROOT / "docs/model_free_recording_replication_audit.json")
    parser.add_argument("--out-md", type=Path, default=REPO_ROOT / "docs/model_free_recording_replication_audit.md")
    parser.add_argument("--min-target-improvement", type=float, default=0.55)
    parser.add_argument("--min-discovery-bidirectional-fraction", type=float, default=0.25)
    parser.add_argument("--min-validation-bidirectional-fraction", type=float, default=0.25)
    parser.add_argument("--min-discovery-observations", type=int, default=4)
    parser.add_argument("--min-validation-observations", type=int, default=4)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    observations = load_all_observations(DEFAULT_REPORTS)
    rows = build_replication_rows(
        observations,
        discovery_reports=DISCOVERY_REPORTS,
        validation_reports=VALIDATION_REPORTS,
        min_target_improvement=args.min_target_improvement,
        min_discovery_bidirectional_fraction=args.min_discovery_bidirectional_fraction,
        min_validation_bidirectional_fraction=args.min_validation_bidirectional_fraction,
        min_discovery_observations=args.min_discovery_observations,
        min_validation_observations=args.min_validation_observations,
    )
    report = {
        "sources": [rel_path for _label, rel_path in DEFAULT_REPORTS if (REPO_ROOT / rel_path).exists()],
        "discovery_reports": sorted(DISCOVERY_REPORTS),
        "validation_reports": sorted(VALIDATION_REPORTS),
        "thresholds": {
            "min_target_improvement": args.min_target_improvement,
            "min_discovery_bidirectional_fraction": args.min_discovery_bidirectional_fraction,
            "min_validation_bidirectional_fraction": args.min_validation_bidirectional_fraction,
            "min_discovery_observations": args.min_discovery_observations,
            "min_validation_observations": args.min_validation_observations,
        },
        "summary": summarize(rows),
        "rows": [asdict(row) for row in rows],
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
