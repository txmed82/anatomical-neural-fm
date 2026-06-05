"""Classify recording-level model-free effects by target direction."""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from audit_model_free_gate_blockers import DEFAULT_REPORTS  # noqa: E402
from audit_model_free_recording_support import RecordingObservation  # noqa: E402


EXTRA_REPORTS = (
    ("shared family target/control", "docs/shared_family_target_control_gate.json"),
)


@dataclass(frozen=True)
class DirectionalObservation(RecordingObservation):
    classification: str


def classify_target_direction(target0: float, target1: float, *, min_target_improvement: float) -> str:
    target0_pass = target0 >= min_target_improvement
    target1_pass = target1 >= min_target_improvement
    if target0_pass and target1_pass:
        return "bidirectional"
    if target0_pass:
        return "target0_only"
    if target1_pass:
        return "target1_only"
    return "neither"


def context_for_row(row: dict) -> tuple[str, str]:
    if "holdout" in row:
        context_parts = [row["holdout"]]
        if "target_mode" in row:
            context_parts.insert(0, row["target_mode"])
        if "family" in row:
            context_parts.insert(1 if "target_mode" in row else 0, row["family"])
        return " / ".join(context_parts), row["holdout"]
    if "source_subject" in row:
        context = f"{row['source_subject']} -> {row['target_subject']}"
        if "target_mode" in row:
            context = f"{row['target_mode']} / {context}"
        return context, row["target_subject"]
    return str(row.get("label", "unknown")), str(row.get("target_subject", "unknown"))


def load_directional_observations(
    report_label: str,
    path: Path,
    *,
    min_target_improvement: float,
) -> list[DirectionalObservation]:
    payload = json.loads(path.read_text())
    raw_rows = payload.get("holdouts") or payload.get("pairs") or payload.get("rows") or []
    observations = []
    for row in raw_rows:
        context, target_subject = context_for_row(row)
        for rec_row in row.get("recording_target_rows", []):
            target0 = float(rec_row["target0_improved"])
            target1 = float(rec_row["target1_improved"])
            observations.append(
                DirectionalObservation(
                    report=report_label,
                    context=context,
                    target_subject=target_subject,
                    recording=rec_row["recording"],
                    target0=target0,
                    target1=target1,
                    improved_fraction=float(rec_row["improved_fraction"]),
                    mean_true_class_delta=float(rec_row["mean_true_class_delta"]),
                    n_trials=int(rec_row["n_trials"]),
                    classification=classify_target_direction(
                        target0,
                        target1,
                        min_target_improvement=min_target_improvement,
                    ),
                )
            )
    return observations


def count_classes(observations: list[DirectionalObservation]) -> dict[str, int]:
    counts = Counter(obs.classification for obs in observations)
    return {key: counts.get(key, 0) for key in ("bidirectional", "target0_only", "target1_only", "neither")}


def summarize_group(observations: list[DirectionalObservation]) -> dict:
    counts = count_classes(observations)
    total = len(observations)
    target0_support = counts["bidirectional"] + counts["target0_only"]
    target1_support = counts["bidirectional"] + counts["target1_only"]
    return {
        "n_observations": total,
        "class_counts": counts,
        "bidirectional_fraction": counts["bidirectional"] / total if total else 0.0,
        "target0_support_fraction": target0_support / total if total else 0.0,
        "target1_support_fraction": target1_support / total if total else 0.0,
        "one_sided_fraction": (counts["target0_only"] + counts["target1_only"]) / total if total else 0.0,
        "target1_minus_target0_one_sided": counts["target1_only"] - counts["target0_only"],
        "mean_target0": sum(obs.target0 for obs in observations) / total if total else 0.0,
        "mean_target1": sum(obs.target1 for obs in observations) / total if total else 0.0,
    }


def summarize_by(observations: list[DirectionalObservation], key: str) -> list[dict]:
    groups: dict[str, list[DirectionalObservation]] = defaultdict(list)
    for obs in observations:
        groups[getattr(obs, key)].append(obs)
    rows = []
    for value, obs_rows in groups.items():
        row = summarize_group(obs_rows)
        row[key] = value
        rows.append(row)
    return sorted(
        rows,
        key=lambda row: (
            row["class_counts"]["bidirectional"],
            row["bidirectional_fraction"],
            row["target1_minus_target0_one_sided"],
        ),
        reverse=True,
    )


def top_one_sided(observations: list[DirectionalObservation]) -> list[dict]:
    one_sided = [obs for obs in observations if obs.classification in {"target0_only", "target1_only"}]
    rows = sorted(
        one_sided,
        key=lambda obs: (abs(obs.target1 - obs.target0), max(obs.target0, obs.target1)),
        reverse=True,
    )
    return [asdict(obs) for obs in rows[:16]]


def render_markdown(report: dict) -> str:
    summary = report["summary"]
    counts = summary["overall"]["class_counts"]
    lines = [
        "# Model-Free Recording Directionality Audit",
        "",
        (
            "Classifies each per-recording target-support observation as bidirectional, "
            "target0-only, target1-only, or neither across current model-free artifacts."
        ),
        "",
        f"- observations: `{summary['overall']['n_observations']}`",
        f"- bidirectional: `{counts['bidirectional']}`",
        f"- target0-only: `{counts['target0_only']}`",
        f"- target1-only: `{counts['target1_only']}`",
        f"- neither: `{counts['neither']}`",
        f"- one-sided fraction: `{summary['overall']['one_sided_fraction']:.3f}`",
        f"- decision: `{summary['decision']}`",
        "",
        "## By Report",
        "",
        "| report | observations | bidir | target0-only | target1-only | neither | mean target0 | mean target1 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary["by_report"]:
        classes = row["class_counts"]
        lines.append(
            f"| {row['report']} | {row['n_observations']} | {classes['bidirectional']} | "
            f"{classes['target0_only']} | {classes['target1_only']} | {classes['neither']} | "
            f"{row['mean_target0']:.3f} | {row['mean_target1']:.3f} |"
        )
    lines += [
        "",
        "## By Subject",
        "",
        "| subject | observations | bidir | target0-only | target1-only | neither | target1-target0 one-sided |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary["by_subject"]:
        classes = row["class_counts"]
        lines.append(
            f"| {row['target_subject']} | {row['n_observations']} | {classes['bidirectional']} | "
            f"{classes['target0_only']} | {classes['target1_only']} | {classes['neither']} | "
            f"{row['target1_minus_target0_one_sided']} |"
        )
    lines += [
        "",
        "## Strongest One-Sided Observations",
        "",
        "| report | context | recording | class | target0 | target1 | trials |",
        "|---|---|---|---|---:|---:|---:|",
    ]
    for row in summary["top_one_sided"]:
        lines.append(
            f"| {row['report']} | {row['context']} | {row['recording']} | "
            f"{row['classification']} | {row['target0']:.3f} | {row['target1']:.3f} | "
            f"{row['n_trials']} |"
        )
    lines += [
        "",
        "## Decision",
        "",
        (
            "Do not promote rows with positive global deltas unless target support is "
            "bidirectional inside recordings. Current artifacts contain substantial "
            "one-sided support, so future local gates should report target-direction "
            "classification before considering any GPU training trigger."
        ),
        "",
    ]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-json", type=Path, default=REPO_ROOT / "docs/model_free_recording_directionality_audit.json")
    parser.add_argument("--out-md", type=Path, default=REPO_ROOT / "docs/model_free_recording_directionality_audit.md")
    parser.add_argument("--min-target-improvement", type=float, default=0.55)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    observations = []
    sources = []
    for label, rel_path in DEFAULT_REPORTS + EXTRA_REPORTS:
        path = REPO_ROOT / rel_path
        if not path.exists():
            continue
        observations.extend(
            load_directional_observations(
                label,
                path,
                min_target_improvement=args.min_target_improvement,
            )
        )
        sources.append(rel_path)
    overall = summarize_group(observations)
    report = {
        "sources": sources,
        "thresholds": {"min_target_improvement": args.min_target_improvement},
        "summary": {
            "overall": overall,
            "by_report": summarize_by(observations, "report"),
            "by_subject": summarize_by(observations, "target_subject"),
            "top_one_sided": top_one_sided(observations),
            "decision": (
                "one_sided_recording_effects_are_common"
                if overall["one_sided_fraction"] > overall["bidirectional_fraction"]
                else "bidirectional_recording_effects_dominate"
            ),
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
