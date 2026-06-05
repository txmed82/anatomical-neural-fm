"""Prospect for recording-level bidirectional support across local gate artifacts."""
from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


DEFAULT_ARTIFACTS = {
    "shared_family": "docs/shared_family_target_control_gate.json",
    "derived_targets": "docs/derived_target_family_gate.json",
    "contextual_targets": "docs/contextual_target_family_gate.json",
    "wheel_targets": "docs/wheel_target_family_gate.json",
    "reaction_dynamics_recording_centered": "docs/reaction_dynamics_target_family_gate.json",
    "reaction_dynamics_counts": "docs/reaction_dynamics_target_family_gate_counts.json",
    "reaction_dynamics_fractions": "docs/reaction_dynamics_target_family_gate_fractions.json",
    "reaction_dynamics_unit_residuals": "docs/reaction_dynamics_target_family_gate_unit_residuals.json",
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


@dataclass(frozen=True)
class RecordingObservation:
    source: str
    target_mode: str
    family: str
    feature_mode: str
    holdout: str
    recording: str
    target0: float
    target1: float
    improved_fraction: float
    mean_true_class_delta: float
    n_trials: int
    row_decision: str
    row_centered_delta_vs_shuffle: float | None
    row_centered_delta_vs_total: float | None
    row_bidirectional_fraction: float | None

    @property
    def symmetric_support(self) -> float:
        return min(self.target0, self.target1)


def as_float(value) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def artifact_rows(payload: dict) -> list[dict]:
    rows = payload.get("rows")
    if isinstance(rows, list):
        return rows
    rows = payload.get("holdouts")
    if isinstance(rows, list):
        return rows
    rows = payload.get("pairs")
    if isinstance(rows, list):
        return rows
    return []


def load_observations(source: str, path: Path) -> list[RecordingObservation]:
    payload = json.loads(path.read_text())
    default_feature_mode = str(payload.get("feature_mode", "unknown"))
    observations: list[RecordingObservation] = []
    for row in artifact_rows(payload):
        target_mode = str(row.get("target_mode") or row.get("target") or row.get("label") or "unknown")
        family = str(row.get("family") or row.get("feature_family") or row.get("feature") or "unknown")
        feature_mode = str(row.get("feature_mode") or default_feature_mode)
        holdout = str(row.get("holdout") or row.get("target_subject") or "unknown")
        for rec_row in row.get("recording_target_rows", []):
            target0 = as_float(rec_row.get("target0_improved"))
            target1 = as_float(rec_row.get("target1_improved"))
            if target0 is None or target1 is None:
                continue
            observations.append(
                RecordingObservation(
                    source=source,
                    target_mode=target_mode,
                    family=family,
                    feature_mode=feature_mode,
                    holdout=holdout,
                    recording=str(rec_row["recording"]),
                    target0=target0,
                    target1=target1,
                    improved_fraction=float(rec_row.get("improved_fraction", 0.0)),
                    mean_true_class_delta=float(rec_row.get("mean_true_class_delta", 0.0)),
                    n_trials=int(rec_row.get("n_trials", 0)),
                    row_decision=str(row.get("decision") or row.get("recording_bidirectional_decision") or "unknown"),
                    row_centered_delta_vs_shuffle=as_float(
                        row.get("centered_delta_vs_shuffle") or row.get("paired_improved_vs_shuffle")
                    ),
                    row_centered_delta_vs_total=as_float(
                        row.get("centered_delta_vs_total") or row.get("paired_improved_vs_total")
                    ),
                    row_bidirectional_fraction=as_float(
                        row.get("bidirectional_recording_fraction")
                        or (row.get("recording_bidirectional") or {}).get("bidirectional_recording_fraction")
                    ),
                )
            )
    return observations


def is_bidirectional(obs: RecordingObservation, *, min_target_improvement: float) -> bool:
    return obs.target0 >= min_target_improvement and obs.target1 >= min_target_improvement


def observation_dict(obs: RecordingObservation) -> dict:
    return {
        "source": obs.source,
        "target_mode": obs.target_mode,
        "family": obs.family,
        "feature_mode": obs.feature_mode,
        "holdout": obs.holdout,
        "recording": obs.recording,
        "target0": obs.target0,
        "target1": obs.target1,
        "symmetric_support": obs.symmetric_support,
        "improved_fraction": obs.improved_fraction,
        "mean_true_class_delta": obs.mean_true_class_delta,
        "n_trials": obs.n_trials,
        "row_decision": obs.row_decision,
        "row_centered_delta_vs_shuffle": obs.row_centered_delta_vs_shuffle,
        "row_centered_delta_vs_total": obs.row_centered_delta_vs_total,
        "row_bidirectional_fraction": obs.row_bidirectional_fraction,
    }


def summarize_recordings(
    observations: list[RecordingObservation],
    *,
    min_target_improvement: float,
) -> list[dict]:
    by_recording: dict[str, list[RecordingObservation]] = {}
    for obs in observations:
        by_recording.setdefault(obs.recording, []).append(obs)

    rows = []
    for recording, rec_obs in by_recording.items():
        bidir = [obs for obs in rec_obs if is_bidirectional(obs, min_target_improvement=min_target_improvement)]
        sources = sorted({obs.source for obs in rec_obs})
        target_modes = sorted({obs.target_mode for obs in bidir})
        families = sorted({obs.family for obs in bidir})
        holdouts = sorted({obs.holdout for obs in rec_obs})
        rows.append({
            "recording": recording,
            "holdouts": holdouts,
            "n_observations": len(rec_obs),
            "n_bidirectional_observations": len(bidir),
            "bidirectional_observation_fraction": len(bidir) / len(rec_obs) if rec_obs else 0.0,
            "n_sources": len(sources),
            "n_bidirectional_sources": len({obs.source for obs in bidir}),
            "n_bidirectional_target_modes": len(target_modes),
            "n_bidirectional_families": len(families),
            "mean_target0": sum(obs.target0 for obs in rec_obs) / len(rec_obs),
            "mean_target1": sum(obs.target1 for obs in rec_obs) / len(rec_obs),
            "mean_symmetric_support": sum(obs.symmetric_support for obs in rec_obs) / len(rec_obs),
            "max_symmetric_support": max((obs.symmetric_support for obs in rec_obs), default=0.0),
            "mean_bidirectional_symmetric_support": (
                sum(obs.symmetric_support for obs in bidir) / len(bidir) if bidir else 0.0
            ),
            "top_bidirectional_observations": [
                observation_dict(obs)
                for obs in sorted(
                    bidir,
                    key=lambda item: (
                        item.symmetric_support,
                        item.row_centered_delta_vs_shuffle or float("-inf"),
                        item.row_centered_delta_vs_total or float("-inf"),
                    ),
                    reverse=True,
                )[:10]
            ],
        })
    return sorted(
        rows,
        key=lambda row: (
            row["n_bidirectional_observations"],
            row["n_bidirectional_sources"],
            row["n_bidirectional_target_modes"],
            row["mean_bidirectional_symmetric_support"],
        ),
        reverse=True,
    )


def prospect_recordings(
    recording_rows: list[dict],
    *,
    min_bidirectional_observations: int,
    min_bidirectional_target_modes: int,
    min_bidirectional_sources: int,
) -> list[dict]:
    return [
        row for row in recording_rows
        if row["n_bidirectional_observations"] >= min_bidirectional_observations
        and row["n_bidirectional_target_modes"] >= min_bidirectional_target_modes
        and row["n_bidirectional_sources"] >= min_bidirectional_sources
    ]


def summarize_sources(observations: list[RecordingObservation], *, min_target_improvement: float) -> list[dict]:
    by_source: dict[str, list[RecordingObservation]] = {}
    for obs in observations:
        by_source.setdefault(obs.source, []).append(obs)
    rows = []
    for source, source_obs in by_source.items():
        bidir = [obs for obs in source_obs if is_bidirectional(obs, min_target_improvement=min_target_improvement)]
        rows.append({
            "source": source,
            "n_observations": len(source_obs),
            "n_bidirectional_observations": len(bidir),
            "recordings_with_bidirectional_support": len({obs.recording for obs in bidir}),
            "target_modes_with_bidirectional_support": len({obs.target_mode for obs in bidir}),
            "families_with_bidirectional_support": len({obs.family for obs in bidir}),
        })
    return sorted(rows, key=lambda row: row["n_bidirectional_observations"], reverse=True)


def build_report(
    artifacts: dict[str, str] | None = None,
    *,
    min_target_improvement: float = 0.55,
    min_bidirectional_observations: int = 6,
    min_bidirectional_target_modes: int = 2,
    min_bidirectional_sources: int = 2,
) -> dict:
    artifacts = artifacts or DEFAULT_ARTIFACTS
    observations: list[RecordingObservation] = []
    sources = []
    missing_sources = []
    for source, rel_path in artifacts.items():
        path = REPO_ROOT / rel_path
        if not path.exists():
            missing_sources.append(rel_path)
            continue
        sources.append(rel_path)
        observations.extend(load_observations(source, path))

    recording_rows = summarize_recordings(observations, min_target_improvement=min_target_improvement)
    leads = prospect_recordings(
        recording_rows,
        min_bidirectional_observations=min_bidirectional_observations,
        min_bidirectional_target_modes=min_bidirectional_target_modes,
        min_bidirectional_sources=min_bidirectional_sources,
    )
    bidir = [obs for obs in observations if is_bidirectional(obs, min_target_improvement=min_target_improvement)]
    target_counts = Counter(obs.target_mode for obs in bidir)
    family_counts = Counter(obs.family for obs in bidir)
    decision = (
        "prospective_recording_leads_present_not_training_ready"
        if leads
        else "no_stable_recording_bidirectionality_prospectus"
    )
    return {
        "sources": sources,
        "missing_sources": missing_sources,
        "thresholds": {
            "min_target_improvement": min_target_improvement,
            "min_bidirectional_observations": min_bidirectional_observations,
            "min_bidirectional_target_modes": min_bidirectional_target_modes,
            "min_bidirectional_sources": min_bidirectional_sources,
            "gpu_trigger_bidirectional_recording_fraction": 0.75,
        },
        "summary": {
            "decision": decision,
            "n_observations": len(observations),
            "n_recordings": len(recording_rows),
            "n_bidirectional_observations": len(bidir),
            "recordings_with_bidirectional_support": sum(
                1 for row in recording_rows if row["n_bidirectional_observations"] > 0
            ),
            "max_bidirectional_observations_per_recording": max(
                (row["n_bidirectional_observations"] for row in recording_rows), default=0
            ),
            "n_prospect_recordings": len(leads),
            "top_recordings": recording_rows[:20],
            "prospect_recordings": leads,
            "source_rows": summarize_sources(observations, min_target_improvement=min_target_improvement),
            "top_bidirectional_targets": target_counts.most_common(12),
            "top_bidirectional_families": family_counts.most_common(12),
            "next_action": (
                "Define a prospective target/control manifest from the lead recordings, then rerun the unchanged local gate."
                if leads
                else (
                    "Do not select a subset from current recordings; design a target/control that creates "
                    "same-recording target0+target1 evidence prospectively."
                )
            ),
            "gpu_training_ready": False,
        },
    }


def render_markdown(report: dict) -> str:
    summary = report["summary"]
    lines = [
        "# Recording Bidirectionality Prospectus",
        "",
        (
            "Aggregates per-recording target0/target1 support across the current local "
            "gate artifacts to see whether any recordings can anchor the next prospective "
            "manifest rule. This is a design prospectus, not a training trigger."
        ),
        "",
        f"- observations: `{summary['n_observations']}`",
        f"- recordings: `{summary['n_recordings']}`",
        f"- bidirectional observations: `{summary['n_bidirectional_observations']}`",
        f"- recordings with bidirectional support: `{summary['recordings_with_bidirectional_support']}`",
        f"- max bidirectional observations/recording: `{summary['max_bidirectional_observations_per_recording']}`",
        f"- prospect recordings: `{summary['n_prospect_recordings']}`",
        f"- decision: `{summary['decision']}`",
        "",
        "## Top Recordings",
        "",
        "| recording | holdouts | obs | bidir obs | bidir sources | bidir targets | bidir families | mean target0 | mean target1 | mean sym |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary["top_recordings"][:12]:
        lines.append(
            f"| {row['recording']} | {', '.join(row['holdouts'])} | "
            f"{row['n_observations']} | {row['n_bidirectional_observations']} | "
            f"{row['n_bidirectional_sources']} | {row['n_bidirectional_target_modes']} | "
            f"{row['n_bidirectional_families']} | {row['mean_target0']:.3f} | "
            f"{row['mean_target1']:.3f} | {row['mean_symmetric_support']:.3f} |"
        )
    lines += [
        "",
        "## Source Coverage",
        "",
        "| source | observations | bidir obs | recordings with bidir | targets with bidir | families with bidir |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in summary["source_rows"]:
        lines.append(
            f"| {row['source']} | {row['n_observations']} | "
            f"{row['n_bidirectional_observations']} | "
            f"{row['recordings_with_bidirectional_support']} | "
            f"{row['target_modes_with_bidirectional_support']} | "
            f"{row['families_with_bidirectional_support']} |"
        )
    lines += [
        "",
        "## Next Action",
        "",
        summary["next_action"],
        "",
        (
            "GPU training remains blocked until a prospectively defined local row clears "
            "delta_vs_shuffle>=0, delta_vs_total>=0, target0>=0.55, target1>=0.55, "
            "and bidirectional_recording_fraction>=0.75."
        ),
        "",
    ]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-json", type=Path, default=REPO_ROOT / "docs/recording_bidirectionality_prospectus.json")
    parser.add_argument("--out-md", type=Path, default=REPO_ROOT / "docs/recording_bidirectionality_prospectus.md")
    parser.add_argument("--min-target-improvement", type=float, default=0.55)
    parser.add_argument("--min-bidirectional-observations", type=int, default=6)
    parser.add_argument("--min-bidirectional-target-modes", type=int, default=2)
    parser.add_argument("--min-bidirectional-sources", type=int, default=2)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(
        min_target_improvement=args.min_target_improvement,
        min_bidirectional_observations=args.min_bidirectional_observations,
        min_bidirectional_target_modes=args.min_bidirectional_target_modes,
        min_bidirectional_sources=args.min_bidirectional_sources,
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
