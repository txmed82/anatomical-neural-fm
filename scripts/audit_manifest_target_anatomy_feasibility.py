"""Audit manifest feasibility for target/control redesign before GPU training."""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "vendor" / "torch_brain"))

from torch_brain.dataset import Dataset  # noqa: E402
from scan_model_free_region_family_candidates import FAMILY_DEFINITIONS  # noqa: E402
from train import (  # noqa: E402
    TARGET_MODES,
    build_trial_samples,
    build_vocab,
    map_region_acronyms,
    select_recording_ids,
)


DEFAULT_MANIFESTS = (
    (
        "support80_hdf5_scored",
        "manifests/ibl_bwm_region_matched_candidates_s3_present_support80_hdf5_scored.json",
    ),
    (
        "support80_hdf5_iterative_pass",
        "manifests/ibl_bwm_region_matched_candidates_s3_present_support80_hdf5_iterative_pass.json",
    ),
)


@dataclass(frozen=True)
class RecordingTargetBalance:
    recording: str
    subject: str
    n_trials: int
    target0: int
    target1: int
    min_class: int
    target1_fraction: float
    balance_fraction: float
    eligible: bool


def trial_balance(
    trials: list[tuple[str, float, float]],
    *,
    subject_by_rid: dict[str, str],
    min_class_trials: int,
) -> list[RecordingTargetBalance]:
    counts: dict[str, Counter[int]] = defaultdict(Counter)
    for rid, _t0, target in trials:
        counts[str(rid)][int(target)] += 1
    rows = []
    for rid in sorted(counts):
        target0 = counts[rid][0]
        target1 = counts[rid][1]
        n_trials = target0 + target1
        min_class = min(target0, target1)
        rows.append(
            RecordingTargetBalance(
                recording=rid,
                subject=subject_by_rid[rid],
                n_trials=n_trials,
                target0=target0,
                target1=target1,
                min_class=min_class,
                target1_fraction=target1 / n_trials if n_trials else 0.0,
                balance_fraction=min_class / n_trials if n_trials else 0.0,
                eligible=min_class >= min_class_trials,
            )
        )
    return rows


def summarize_target_rows(rows: list[RecordingTargetBalance], *, min_recordings_per_subject: int) -> dict:
    by_subject: dict[str, list[RecordingTargetBalance]] = defaultdict(list)
    for row in rows:
        by_subject[row.subject].append(row)
    subject_rows = []
    for subject, subject_recs in sorted(by_subject.items()):
        eligible = [row for row in subject_recs if row.eligible]
        subject_rows.append({
            "subject": subject,
            "n_recordings": len(subject_recs),
            "eligible_recordings": len(eligible),
            "n_trials": sum(row.n_trials for row in subject_recs),
            "target0": sum(row.target0 for row in subject_recs),
            "target1": sum(row.target1 for row in subject_recs),
            "mean_balance_fraction": float(np.mean([row.balance_fraction for row in subject_recs]))
            if subject_recs else 0.0,
            "passes_recording_floor": len(eligible) >= min_recordings_per_subject,
        })
    passing_subjects = [row for row in subject_rows if row["passes_recording_floor"]]
    return {
        "n_recordings": len(rows),
        "eligible_recordings": sum(1 for row in rows if row.eligible),
        "n_subjects": len(subject_rows),
        "subjects_passing_recording_floor": len(passing_subjects),
        "all_subjects_pass_recording_floor": len(passing_subjects) == len(subject_rows) and bool(subject_rows),
        "subject_rows": subject_rows,
    }


def recording_family_counts(rec) -> Counter[str]:
    parent_regions = map_region_acronyms(rec.units.region_acronym, "parent")
    parent_counts = Counter(str(region) for region in parent_regions)
    family_counts: Counter[str] = Counter()
    for family, members in FAMILY_DEFINITIONS.items():
        count = sum(parent_counts[member] for member in members)
        if count:
            family_counts[family] = count
    return family_counts


def summarize_family_support(
    recs: dict[str, object],
    rids: list[str],
    subject_by_rid: dict[str, str],
    *,
    min_family_units: int,
    min_family_recordings_per_subject: int,
) -> dict:
    by_subject_family_units: dict[str, Counter[str]] = defaultdict(Counter)
    by_subject_family_recordings: dict[str, Counter[str]] = defaultdict(Counter)
    for rid in rids:
        subject = subject_by_rid[rid]
        family_counts = recording_family_counts(recs[rid])
        for family, count in family_counts.items():
            by_subject_family_units[subject][family] += count
            if count >= min_family_units:
                by_subject_family_recordings[subject][family] += 1
    subjects = sorted(set(subject_by_rid[rid] for rid in rids))
    family_rows = []
    for family in sorted(FAMILY_DEFINITIONS):
        subject_support = []
        for subject in subjects:
            units = by_subject_family_units[subject][family]
            recordings = by_subject_family_recordings[subject][family]
            subject_support.append({
                "subject": subject,
                "units": units,
                "recordings_with_min_units": recordings,
                "passes": recordings >= min_family_recordings_per_subject,
            })
        passing_subjects = sum(1 for row in subject_support if row["passes"])
        total_units = sum(row["units"] for row in subject_support)
        if total_units:
            family_rows.append({
                "family": family,
                "total_units": total_units,
                "subjects_passing": passing_subjects,
                "all_subjects_pass": passing_subjects == len(subjects),
                "min_subject_units": min(row["units"] for row in subject_support),
                "subject_support": subject_support,
            })
    family_rows.sort(
        key=lambda row: (
            row["all_subjects_pass"],
            row["subjects_passing"],
            row["min_subject_units"],
            row["total_units"],
        ),
        reverse=True,
    )
    return {
        "n_families_with_units": len(family_rows),
        "n_families_all_subjects_pass": sum(1 for row in family_rows if row["all_subjects_pass"]),
        "top_families": family_rows[:12],
    }


def audit_manifest(
    label: str,
    manifest: Path,
    *,
    data_dir: Path,
    window_len: float,
    min_class_trials: int,
    min_recordings_per_subject: int,
    min_family_units: int,
    min_family_recordings_per_subject: int,
) -> dict:
    ds = Dataset(dataset_dir=data_dir, keep_files_open=True)
    selected_rids = select_recording_ids(ds, manifest, data_dir)
    vocab = build_vocab(ds, "parent", selected_rids)
    target_modes = {}
    for target_mode in TARGET_MODES:
        trials = build_trial_samples(vocab["recs"], selected_rids, window_len, target_mode)
        rows = trial_balance(
            trials,
            subject_by_rid=vocab["subject_by_rid"],
            min_class_trials=min_class_trials,
        )
        target_modes[target_mode] = {
            "summary": summarize_target_rows(rows, min_recordings_per_subject=min_recordings_per_subject),
            "recording_rows": [asdict(row) for row in rows],
        }
    anatomy = summarize_family_support(
        vocab["recs"],
        selected_rids,
        vocab["subject_by_rid"],
        min_family_units=min_family_units,
        min_family_recordings_per_subject=min_family_recordings_per_subject,
    )
    promotable_targets = [
        target
        for target, payload in target_modes.items()
        if payload["summary"]["all_subjects_pass_recording_floor"]
    ]
    decision = (
        "manifest_has_target_and_family_feasibility"
        if promotable_targets and anatomy["n_families_all_subjects_pass"] > 0
        else "manifest_feasibility_gap"
    )
    return {
        "label": label,
        "manifest": str(manifest),
        "n_recordings": len(selected_rids),
        "n_subjects": len(set(vocab["subject_by_rid"].values())),
        "target_modes": target_modes,
        "anatomy": anatomy,
        "promotable_targets": promotable_targets,
        "decision": decision,
    }


def render_markdown(report: dict) -> str:
    lines = [
        "# Manifest Target/Anatomy Feasibility Audit",
        "",
        (
            "No-spend prerequisite audit for benchmark redesign. It checks whether "
            "candidate manifests have balanced within-recording trials for each target "
            "mode and enough shared anatomical family support across subjects."
        ),
        "",
        f"- min class trials per eligible recording: `{report['thresholds']['min_class_trials']}`",
        f"- min eligible recordings per subject: `{report['thresholds']['min_recordings_per_subject']}`",
        f"- min family units per recording: `{report['thresholds']['min_family_units']}`",
        f"- min family recordings per subject: `{report['thresholds']['min_family_recordings_per_subject']}`",
        "",
    ]
    for manifest in report["manifests"]:
        lines += [
            f"## {manifest['label']}",
            "",
            f"- recordings: `{manifest['n_recordings']}`",
            f"- subjects: `{manifest['n_subjects']}`",
            f"- promotable targets by balance floor: `{', '.join(manifest['promotable_targets']) or 'none'}`",
            f"- shared families passing floor: `{manifest['anatomy']['n_families_all_subjects_pass']}`",
            f"- decision: `{manifest['decision']}`",
            "",
            "| target | eligible recordings | subjects passing floor | all subjects pass |",
            "|---|---:|---:|---|",
        ]
        for target, payload in manifest["target_modes"].items():
            summary = payload["summary"]
            lines.append(
                f"| {target} | {summary['eligible_recordings']}/{summary['n_recordings']} | "
                f"{summary['subjects_passing_recording_floor']}/{summary['n_subjects']} | "
                f"{summary['all_subjects_pass_recording_floor']} |"
            )
        lines += [
            "",
            "| family | all subjects pass | subjects passing | min subject units | total units |",
            "|---|---|---:|---:|---:|",
        ]
        for family in manifest["anatomy"]["top_families"][:8]:
            lines.append(
                f"| {family['family']} | {family['all_subjects_pass']} | "
                f"{family['subjects_passing']} | {family['min_subject_units']} | "
                f"{family['total_units']} |"
            )
        lines.append("")
    lines += [
        "## Decision",
        "",
        report["decision"],
        "",
    ]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=REPO_ROOT / "data/brainsets/ibl_bwm")
    parser.add_argument("--window-len", type=float, default=1.0)
    parser.add_argument("--min-class-trials", type=int, default=40)
    parser.add_argument("--min-recordings-per-subject", type=int, default=2)
    parser.add_argument("--min-family-units", type=int, default=25)
    parser.add_argument("--min-family-recordings-per-subject", type=int, default=1)
    parser.add_argument("--out-json", type=Path, default=REPO_ROOT / "docs/manifest_target_anatomy_feasibility.json")
    parser.add_argument("--out-md", type=Path, default=REPO_ROOT / "docs/manifest_target_anatomy_feasibility.md")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifests = [
        audit_manifest(
            label,
            REPO_ROOT / rel_path,
            data_dir=args.data_dir,
            window_len=args.window_len,
            min_class_trials=args.min_class_trials,
            min_recordings_per_subject=args.min_recordings_per_subject,
            min_family_units=args.min_family_units,
            min_family_recordings_per_subject=args.min_family_recordings_per_subject,
        )
        for label, rel_path in DEFAULT_MANIFESTS
        if (REPO_ROOT / rel_path).exists()
    ]
    any_ready = any(manifest["decision"] == "manifest_has_target_and_family_feasibility" for manifest in manifests)
    report = {
        "thresholds": {
            "window_len": args.window_len,
            "min_class_trials": args.min_class_trials,
            "min_recordings_per_subject": args.min_recordings_per_subject,
            "min_family_units": args.min_family_units,
            "min_family_recordings_per_subject": args.min_family_recordings_per_subject,
        },
        "manifests": manifests,
        "decision": (
            "At least one manifest has basic target balance and shared family support. "
            "Use its strongest target/family combinations for the next local model-free "
            "control redesign before any GPU launch."
            if any_ready else (
                "No audited manifest clears both target-balance and shared-family "
                "feasibility floors. Build or fetch a broader matched manifest before "
                "testing another anatomy-transfer training run."
            )
        ),
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
