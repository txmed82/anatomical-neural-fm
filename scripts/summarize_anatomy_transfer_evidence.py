"""Summarize completed LSO anatomy-transfer evidence across holdouts."""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class HoldoutEvidence:
    holdout: str
    gate_pass: bool
    passing_seeds: int
    n_seeds: int
    paired_true_vs_shuffle: float
    paired_shuffle_vs_shared: float
    paired_specificity_gap: float
    centered_auc_region_only: float
    centered_auc_region_shuffle: float
    centered_auc_delta_vs_shuffle: float
    full_auc_region_only: float
    full_auc_region_shuffle: float
    full_auc_delta_vs_shuffle: float
    recordings_true_beats_shuffle: int
    n_recordings: int


def read_json(path: Path) -> dict:
    return json.loads(path.read_text())


def evidence_for_paths(gate_path: Path, ensemble_path: Path) -> HoldoutEvidence:
    gate = read_json(gate_path)
    ensemble = read_json(ensemble_path)
    metrics = ensemble["ensemble_metrics"]
    paired = ensemble["ensemble_paired"]
    region_recordings = metrics["region_only"]["recording_auc"]
    shuffle_recordings = metrics["region_shuffle"]["recording_auc"]
    recording_ids = sorted(set(region_recordings) & set(shuffle_recordings))
    recordings_true_beats_shuffle = sum(
        region_recordings[recording_id]["auc"] > shuffle_recordings[recording_id]["auc"]
        for recording_id in recording_ids
    )
    paired_true = paired["region_only_vs_shuffle"]["improved_fraction"]
    paired_shuffle = paired["shuffle_vs_shared"]["improved_fraction"]
    centered_true = metrics["region_only"]["centered_auc"]
    centered_shuffle = metrics["region_shuffle"]["centered_auc"]
    full_true = metrics["region_only"]["full_auc"]
    full_shuffle = metrics["region_shuffle"]["full_auc"]
    return HoldoutEvidence(
        holdout=gate["holdout"],
        gate_pass=bool(gate["pass"]),
        passing_seeds=int(gate["n_passing_seeds"]),
        n_seeds=int(gate["n_seeds"]),
        paired_true_vs_shuffle=float(paired_true),
        paired_shuffle_vs_shared=float(paired_shuffle),
        paired_specificity_gap=float(paired_true - paired_shuffle),
        centered_auc_region_only=float(centered_true),
        centered_auc_region_shuffle=float(centered_shuffle),
        centered_auc_delta_vs_shuffle=float(centered_true - centered_shuffle),
        full_auc_region_only=float(full_true),
        full_auc_region_shuffle=float(full_shuffle),
        full_auc_delta_vs_shuffle=float(full_true - full_shuffle),
        recordings_true_beats_shuffle=recordings_true_beats_shuffle,
        n_recordings=len(recording_ids),
    )


def evidence_to_dict(row: HoldoutEvidence) -> dict:
    return {
        "holdout": row.holdout,
        "gate_pass": row.gate_pass,
        "passing_seeds": row.passing_seeds,
        "n_seeds": row.n_seeds,
        "paired_true_vs_shuffle": row.paired_true_vs_shuffle,
        "paired_shuffle_vs_shared": row.paired_shuffle_vs_shared,
        "paired_specificity_gap": row.paired_specificity_gap,
        "centered_auc_region_only": row.centered_auc_region_only,
        "centered_auc_region_shuffle": row.centered_auc_region_shuffle,
        "centered_auc_delta_vs_shuffle": row.centered_auc_delta_vs_shuffle,
        "full_auc_region_only": row.full_auc_region_only,
        "full_auc_region_shuffle": row.full_auc_region_shuffle,
        "full_auc_delta_vs_shuffle": row.full_auc_delta_vs_shuffle,
        "recordings_true_beats_shuffle": row.recordings_true_beats_shuffle,
        "n_recordings": row.n_recordings,
    }


def summarize(rows: list[HoldoutEvidence]) -> dict:
    any_gate_fail = any(not row.gate_pass for row in rows)
    any_negative_specificity = any(row.paired_specificity_gap <= 0 for row in rows)
    any_weak_recording_support = any(
        row.recordings_true_beats_shuffle < max(1, row.n_recordings)
        for row in rows
    )
    demo_ready = bool(rows) and not any_gate_fail and not any_negative_specificity and not any_weak_recording_support
    if demo_ready:
        decision = "demo_ready"
        next_action = "Package the replicated anatomy-transfer result and broaden only after preserving the gate artifacts."
    else:
        decision = "redesign_before_more_spend"
        next_action = (
            "Do not run more same-setup GPU sweeps. Redesign the anatomy-specific objective or gate, "
            "then rerun a bounded two-holdout confirmation."
        )
    return {
        "decision": decision,
        "demo_ready": demo_ready,
        "next_action": next_action,
        "holdouts": [evidence_to_dict(row) for row in rows],
    }


def render_markdown(summary: dict) -> str:
    lines = [
        "# Anatomy Transfer Evidence Summary",
        "",
        f"Decision: `{summary['decision']}`",
        "",
        summary["next_action"],
        "",
        "| holdout | gate | passing_seeds | paired_true_vs_shuffle | shuffle_vs_shared | specificity_gap | centered_delta_vs_shuffle | full_delta_vs_shuffle | recording_support |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary["holdouts"]:
        lines.append(
            "| "
            f"{row['holdout']} | {row['gate_pass']} | {row['passing_seeds']}/{row['n_seeds']} | "
            f"{row['paired_true_vs_shuffle']:.3f} | {row['paired_shuffle_vs_shared']:.3f} | "
            f"{row['paired_specificity_gap']:+.3f} | {row['centered_auc_delta_vs_shuffle']:+.3f} | "
            f"{row['full_auc_delta_vs_shuffle']:+.3f} | "
            f"{row['recordings_true_beats_shuffle']}/{row['n_recordings']} |"
        )
    lines += [
        "",
        "A holdout is not considered demo-ready unless the executable gate passes,",
        "the paired true-vs-shuffle improvement is specific against shuffle-vs-shared,",
        "and the recording-level AUC support is not localized to a single recording.",
        "",
    ]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--pair",
        nargs=2,
        action="append",
        metavar=("GATE_JSON", "ENSEMBLE_JSON"),
        required=True,
        help="Gate JSON and ensemble diagnostic JSON for one holdout.",
    )
    parser.add_argument("--out-json", type=Path)
    parser.add_argument("--out-md", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows = [evidence_for_paths(Path(gate), Path(ensemble)) for gate, ensemble in args.pair]
    summary = summarize(rows)
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
        print(f"wrote {args.out_json}")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(render_markdown(summary))
        print(f"wrote {args.out_md}")
    if not args.out_json and not args.out_md:
        print(render_markdown(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
