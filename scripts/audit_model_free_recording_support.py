"""Aggregate recording-level bidirectional support across model-free gates."""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from audit_model_free_gate_blockers import DEFAULT_REPORTS


@dataclass(frozen=True)
class RecordingObservation:
    report: str
    context: str
    target_subject: str
    recording: str
    target0: float
    target1: float
    improved_fraction: float
    mean_true_class_delta: float
    n_trials: int


def context_for_row(row: dict) -> tuple[str, str]:
    if "holdout" in row:
        return row["holdout"], row["holdout"]
    return f"{row['source_subject']} -> {row['target_subject']}", row["target_subject"]


def load_observations(report_label: str, path: Path) -> list[RecordingObservation]:
    payload = json.loads(path.read_text())
    raw_rows = payload.get("holdouts") or payload.get("pairs") or []
    observations = []
    for row in raw_rows:
        context, target_subject = context_for_row(row)
        for rec_row in row.get("recording_target_rows", []):
            observations.append(
                RecordingObservation(
                    report=report_label,
                    context=context,
                    target_subject=target_subject,
                    recording=rec_row["recording"],
                    target0=float(rec_row["target0_improved"]),
                    target1=float(rec_row["target1_improved"]),
                    improved_fraction=float(rec_row["improved_fraction"]),
                    mean_true_class_delta=float(rec_row["mean_true_class_delta"]),
                    n_trials=int(rec_row["n_trials"]),
                )
            )
    return observations


def is_bidirectional(obs: RecordingObservation, *, min_target_improvement: float) -> bool:
    return obs.target0 >= min_target_improvement and obs.target1 >= min_target_improvement


def summarize_recordings(observations: list[RecordingObservation], *, min_target_improvement: float) -> list[dict]:
    by_recording: dict[str, list[RecordingObservation]] = {}
    for obs in observations:
        by_recording.setdefault(obs.recording, []).append(obs)
    rows = []
    for recording, rec_obs in by_recording.items():
        bidir = [obs for obs in rec_obs if is_bidirectional(obs, min_target_improvement=min_target_improvement)]
        rows.append({
            "recording": recording,
            "target_subjects": sorted({obs.target_subject for obs in rec_obs}),
            "n_observations": len(rec_obs),
            "n_bidirectional_observations": len(bidir),
            "bidirectional_observation_fraction": len(bidir) / len(rec_obs) if rec_obs else 0.0,
            "mean_target0": sum(obs.target0 for obs in rec_obs) / len(rec_obs),
            "mean_target1": sum(obs.target1 for obs in rec_obs) / len(rec_obs),
            "mean_improved_fraction": sum(obs.improved_fraction for obs in rec_obs) / len(rec_obs),
            "mean_true_class_delta": sum(obs.mean_true_class_delta for obs in rec_obs) / len(rec_obs),
            "top_bidirectional_contexts": [
                {
                    "report": obs.report,
                    "context": obs.context,
                    "target0": obs.target0,
                    "target1": obs.target1,
                    "improved_fraction": obs.improved_fraction,
                    "mean_true_class_delta": obs.mean_true_class_delta,
                }
                for obs in sorted(bidir, key=lambda item: min(item.target0, item.target1), reverse=True)[:8]
            ],
        })
    return sorted(
        rows,
        key=lambda row: (
            row["n_bidirectional_observations"],
            row["bidirectional_observation_fraction"],
            min(row["mean_target0"], row["mean_target1"]),
        ),
        reverse=True,
    )


def summarize_subjects(recording_rows: list[dict]) -> list[dict]:
    by_subject: dict[str, list[dict]] = {}
    for row in recording_rows:
        for subject in row["target_subjects"]:
            by_subject.setdefault(subject, []).append(row)
    subject_rows = []
    for subject, rows in by_subject.items():
        subject_rows.append({
            "subject": subject,
            "n_recordings": len(rows),
            "recordings_with_bidirectional_support": sum(1 for row in rows if row["n_bidirectional_observations"] > 0),
            "total_bidirectional_observations": sum(row["n_bidirectional_observations"] for row in rows),
            "max_bidirectional_observations": max((row["n_bidirectional_observations"] for row in rows), default=0),
        })
    return sorted(
        subject_rows,
        key=lambda row: (
            row["recordings_with_bidirectional_support"],
            row["total_bidirectional_observations"],
            row["max_bidirectional_observations"],
        ),
        reverse=True,
    )


def render_markdown(report: dict) -> str:
    summary = report["summary"]
    lines = [
        "# Model-Free Recording Support Audit",
        "",
        (
            "Aggregates per-recording target0/target1 support across the current "
            "model-free holdout and source-target artifacts."
        ),
        "",
        f"- observations: `{summary['n_observations']}`",
        f"- recordings: `{summary['n_recordings']}`",
        f"- bidirectional observations: `{summary['n_bidirectional_observations']}`",
        f"- recordings with any bidirectional support: `{summary['recordings_with_any_bidirectional_support']}`",
        f"- max bidirectional observations for one recording: `{summary['max_bidirectional_observations_per_recording']}`",
        "",
        "## Top Recording Support",
        "",
        "| recording | subjects | observations | bidir obs | bidir frac | mean target0 | mean target1 | mean true-class delta |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary["top_recordings"][:12]:
        lines.append(
            f"| {row['recording']} | {', '.join(row['target_subjects'])} | "
            f"{row['n_observations']} | {row['n_bidirectional_observations']} | "
            f"{row['bidirectional_observation_fraction']:.3f} | "
            f"{row['mean_target0']:.3f} | {row['mean_target1']:.3f} | "
            f"{row['mean_true_class_delta']:+.3f} |"
        )
    lines += [
        "",
        "## Subject-Level Recording Support",
        "",
        "| subject | recordings | recordings with support | total bidir obs | max bidir obs/recording |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in summary["subject_rows"]:
        lines.append(
            f"| {row['subject']} | {row['n_recordings']} | "
            f"{row['recordings_with_bidirectional_support']} | "
            f"{row['total_bidirectional_observations']} | "
            f"{row['max_bidirectional_observations']} |"
        )
    lines += [
        "",
        "## Decision",
        "",
        (
            "Rare bidirectional observations are not concentrated enough to define a "
            "stable subject-level demo subset. A recording-level inclusion rule would "
            "be post hoc under the current cache; the next benchmark redesign should "
            "seek recordings with bidirectional target evidence prospectively, then "
            "rerun the same true-vs-shuffled local gate before GPU training."
        ),
        "",
    ]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-json", type=Path, default=REPO_ROOT / "docs/model_free_recording_support_audit.json")
    parser.add_argument("--out-md", type=Path, default=REPO_ROOT / "docs/model_free_recording_support_audit.md")
    parser.add_argument("--min-target-improvement", type=float, default=0.55)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    observations = []
    sources = []
    for label, rel_path in DEFAULT_REPORTS:
        path = REPO_ROOT / rel_path
        if not path.exists():
            continue
        observations.extend(load_observations(label, path))
        sources.append(rel_path)
    recording_rows = summarize_recordings(observations, min_target_improvement=args.min_target_improvement)
    bidir_observations = [
        obs for obs in observations
        if is_bidirectional(obs, min_target_improvement=args.min_target_improvement)
    ]
    report = {
        "sources": sources,
        "thresholds": {"min_target_improvement": args.min_target_improvement},
        "summary": {
            "n_observations": len(observations),
            "n_recordings": len(recording_rows),
            "n_bidirectional_observations": len(bidir_observations),
            "recordings_with_any_bidirectional_support": sum(
                1 for row in recording_rows if row["n_bidirectional_observations"] > 0
            ),
            "max_bidirectional_observations_per_recording": max(
                (row["n_bidirectional_observations"] for row in recording_rows),
                default=0,
            ),
            "top_recordings": recording_rows[:20],
            "subject_rows": summarize_subjects(recording_rows),
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
