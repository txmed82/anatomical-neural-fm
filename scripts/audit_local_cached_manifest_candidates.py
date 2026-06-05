"""Build and audit local cached manifest candidates before any new GPU spend."""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "vendor" / "torch_brain"))

from torch_brain.dataset import Dataset  # noqa: E402
from scan_model_free_region_family_candidates import FAMILY_DEFINITIONS  # noqa: E402
from train import TARGET_MODES, build_trial_samples, build_vocab, map_region_acronyms, manifest_recording_ids  # noqa: E402


def split_recording_id(recording_id: str) -> tuple[str, str]:
    session_id, probe_name = recording_id.rsplit("_", 1)
    return session_id, probe_name


def recording_manifest_row(recording_id: str, rec) -> dict:
    session_id, probe_name = split_recording_id(recording_id)
    return {
        "session_id": session_id,
        "probe_name": probe_name,
        "subject_id": str(rec.subject.id),
        "n_units": int(len(rec.units.id)),
    }


def target_counts_for_recordings(recs: dict[str, object], recording_ids: list[str], *, window_len: float) -> dict:
    out = {}
    for target_mode in TARGET_MODES:
        trials = build_trial_samples(recs, recording_ids, window_len, target_mode)
        counts: dict[str, Counter[int]] = defaultdict(Counter)
        for rid, _t0, target in trials:
            counts[rid][int(target)] += 1
        out[target_mode] = {
            rid: {
                "target0": int(counts[rid][0]),
                "target1": int(counts[rid][1]),
                "min_class": int(min(counts[rid][0], counts[rid][1])),
                "n_trials": int(counts[rid][0] + counts[rid][1]),
            }
            for rid in recording_ids
        }
    return out


def family_counts_for_recording(rec) -> dict[str, int]:
    parent_regions = map_region_acronyms(rec.units.region_acronym, "parent")
    parent_counts = Counter(str(region) for region in parent_regions)
    return {
        family: int(sum(parent_counts[member] for member in members))
        for family, members in FAMILY_DEFINITIONS.items()
    }


def candidate_panels(
    all_recording_ids: list[str],
    subject_by_rid: dict[str, str],
    *,
    baseline_recording_ids: list[str],
    min_subject_recordings: int,
) -> list[tuple[str, list[str]]]:
    panels = [("current_support80_hdf5", sorted(baseline_recording_ids))]
    panels.append(("all_local_cached", sorted(all_recording_ids)))
    eligible_subjects = {
        subject
        for subject, count in Counter(subject_by_rid[rid] for rid in all_recording_ids).items()
        if count >= min_subject_recordings
    }
    panels.append((
        f"local_cached_min{min_subject_recordings}_recordings_per_subject",
        sorted(rid for rid in all_recording_ids if subject_by_rid[rid] in eligible_subjects),
    ))
    seen = set()
    unique = []
    for label, rids in panels:
        key = tuple(rids)
        if key in seen:
            continue
        seen.add(key)
        unique.append((label, rids))
    return unique


def score_panel(
    label: str,
    recording_ids: list[str],
    *,
    subject_by_rid: dict[str, str],
    target_counts: dict,
    family_counts: dict[str, dict[str, int]],
    min_class_trials: int,
    min_family_units: int,
    min_subject_recordings: int,
) -> dict:
    subjects = sorted({subject_by_rid[rid] for rid in recording_ids})
    subject_counts = Counter(subject_by_rid[rid] for rid in recording_ids)
    target_family_rows = []
    for target_mode in TARGET_MODES:
        for family in sorted(FAMILY_DEFINITIONS):
            subject_rows = []
            for subject in subjects:
                subject_rids = [rid for rid in recording_ids if subject_by_rid[rid] == subject]
                eligible = [
                    rid for rid in subject_rids
                    if target_counts[target_mode][rid]["min_class"] >= min_class_trials
                    and family_counts[rid].get(family, 0) >= min_family_units
                ]
                subject_rows.append({
                    "subject": subject,
                    "recordings": len(subject_rids),
                    "eligible_recordings": len(eligible),
                    "passes": len(eligible) >= min_subject_recordings,
                })
            passing_subjects = sum(1 for row in subject_rows if row["passes"])
            min_eligible = min((row["eligible_recordings"] for row in subject_rows), default=0)
            target_family_rows.append({
                "target_mode": target_mode,
                "family": family,
                "passing_subjects": passing_subjects,
                "n_subjects": len(subjects),
                "all_subjects_pass": passing_subjects == len(subjects) and bool(subjects),
                "min_eligible_recordings_per_subject": min_eligible,
                "subject_rows": subject_rows,
            })
    target_family_rows.sort(
        key=lambda row: (
            row["all_subjects_pass"],
            row["passing_subjects"],
            row["min_eligible_recordings_per_subject"],
            row["target_mode"],
            row["family"],
        ),
        reverse=True,
    )
    passing_rows = [row for row in target_family_rows if row["all_subjects_pass"]]
    return {
        "label": label,
        "n_recordings": len(recording_ids),
        "n_subjects": len(subjects),
        "subject_counts": dict(sorted(subject_counts.items())),
        "recording_ids": recording_ids,
        "n_passing_target_family_rows": len(passing_rows),
        "top_target_family_rows": target_family_rows[:20],
        "decision": "candidate_panel_has_prospective_support" if passing_rows else "candidate_panel_support_gap",
    }


def write_manifest(path: Path, label: str, recording_ids: list[str], recs: dict[str, object]) -> None:
    rows = [recording_manifest_row(rid, recs[rid]) for rid in recording_ids]
    subjects = sorted({row["subject_id"] for row in rows})
    payload = {
        "dataset": "ibl_bwm",
        "project": "anatomical-neural-fm",
        "selection": {
            "source": "local BrainSet HDF5 cache",
            "label": label,
            "note": "Generated by scripts/audit_local_cached_manifest_candidates.py for no-spend local screening.",
        },
        "n_recordings": len(rows),
        "n_subjects": len(subjects),
        "recordings": rows,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def summarize(report: dict) -> dict:
    best = report["panels"][0] if report["panels"] else None
    passing_panels = [panel for panel in report["panels"] if panel["n_passing_target_family_rows"] > 0]
    passing_new_panels = [
        panel for panel in passing_panels
        if panel["label"] != "current_support80_hdf5"
    ]
    return {
        "n_local_recordings": report["n_local_recordings"],
        "n_local_subjects": report["n_local_subjects"],
        "n_panels": len(report["panels"]),
        "n_candidate_panels": len(passing_panels),
        "n_new_candidate_panels": len(passing_new_panels),
        "best_panel": None if best is None else best["label"],
        "best_panel_passing_rows": 0 if best is None else best["n_passing_target_family_rows"],
        "decision": (
            "local_expanded_candidate_ready_for_model_free_gate"
            if passing_new_panels
            else "local_expansion_support_gap"
            if passing_panels
            else "no_local_candidate_manifest"
        ),
    }


def render_markdown(report: dict) -> str:
    summary = report["summary"]
    lines = [
        "# Local Cached Manifest Candidate Audit",
        "",
        (
            "No-spend audit for the next manifest-redesign branch. It scores local "
            "cached recordings for within-recording target balance and anatomical "
            "family support before any new data fetch or GPU launch."
        ),
        "",
        f"- local recordings: `{summary['n_local_recordings']}`",
        f"- local subjects: `{summary['n_local_subjects']}`",
        f"- panels scored: `{summary['n_panels']}`",
        f"- candidate panels: `{summary['n_candidate_panels']}`",
        f"- new candidate panels: `{summary['n_new_candidate_panels']}`",
        f"- best panel: `{summary['best_panel']}`",
        f"- decision: `{summary['decision']}`",
        "",
        "## Panels",
        "",
        "| panel | recordings | subjects | passing target/family rows | decision |",
        "|---|---:|---:|---:|---|",
    ]
    for panel in report["panels"]:
        lines.append(
            f"| {panel['label']} | {panel['n_recordings']} | {panel['n_subjects']} | "
            f"{panel['n_passing_target_family_rows']} | `{panel['decision']}` |"
        )
    lines += [
        "",
        "## Top Prospective Rows",
        "",
        "| panel | target | family | passing subjects | min eligible recs/subject | all subjects pass |",
        "|---|---|---|---:|---:|---|",
    ]
    for panel in report["panels"]:
        for row in panel["top_target_family_rows"][:8]:
            lines.append(
                f"| {panel['label']} | {row['target_mode']} | {row['family']} | "
                f"{row['passing_subjects']}/{row['n_subjects']} | "
                f"{row['min_eligible_recordings_per_subject']} | {row['all_subjects_pass']} |"
            )
    lines += [
        "",
        "## Written Manifests",
        "",
    ]
    for label, path in report["written_manifests"].items():
        lines.append(f"- `{label}`: `{path}`")
    lines += [
        "",
        "## Decision",
        "",
        (
            "A panel passing this audit is not a training trigger. It only means the "
            "panel has enough per-subject target and family coverage to run the same "
            "local model-free true-vs-shuffle, total-baseline, target0/target1, and "
            "same-recording bidirectional gate."
        ),
        "",
    ]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=REPO_ROOT / "data/brainsets/ibl_bwm")
    parser.add_argument(
        "--baseline-manifest",
        type=Path,
        default=REPO_ROOT / "manifests/ibl_bwm_region_matched_candidates_s3_present_support80_hdf5_scored.json",
    )
    parser.add_argument("--window-len", type=float, default=1.0)
    parser.add_argument("--min-class-trials", type=int, default=40)
    parser.add_argument("--min-family-units", type=int, default=25)
    parser.add_argument("--min-subject-recordings", type=int, default=2)
    parser.add_argument("--out-json", type=Path, default=REPO_ROOT / "docs/local_cached_manifest_candidates.json")
    parser.add_argument("--out-md", type=Path, default=REPO_ROOT / "docs/local_cached_manifest_candidates.md")
    parser.add_argument(
        "--out-manifest-prefix",
        type=Path,
        default=REPO_ROOT / "manifests/ibl_bwm_local_cached",
    )
    return parser.parse_args()


def manifest_output_path(prefix: Path, label: str) -> Path:
    suffixes = {
        "all_local_cached": "all",
    }
    if label.startswith("local_cached_min") and label.endswith("_recordings_per_subject"):
        value = label.removeprefix("local_cached_min").removesuffix("_recordings_per_subject")
        suffixes[label] = f"min{value}_subjects"
    suffix = suffixes.get(label, label)
    return prefix.with_name(f"{prefix.name}_{suffix}.json")


def main() -> int:
    args = parse_args()
    ds = Dataset(dataset_dir=args.data_dir, keep_files_open=True)
    all_recording_ids = sorted(ds.recording_ids)
    vocab = build_vocab(ds, "parent", all_recording_ids)
    recs = vocab["recs"]
    subject_by_rid = vocab["subject_by_rid"]
    baseline_recording_ids = [
        rid for rid in manifest_recording_ids(args.baseline_manifest)
        if rid in set(all_recording_ids)
    ]
    target_counts = target_counts_for_recordings(recs, all_recording_ids, window_len=args.window_len)
    family_counts = {rid: family_counts_for_recording(recs[rid]) for rid in all_recording_ids}
    panels = []
    written_manifests = {}
    for label, rids in candidate_panels(
        all_recording_ids,
        subject_by_rid,
        baseline_recording_ids=baseline_recording_ids,
        min_subject_recordings=args.min_subject_recordings,
    ):
        panel = score_panel(
            label,
            rids,
            subject_by_rid=subject_by_rid,
            target_counts=target_counts,
            family_counts=family_counts,
            min_class_trials=args.min_class_trials,
            min_family_units=args.min_family_units,
            min_subject_recordings=args.min_subject_recordings,
        )
        panels.append(panel)
        if label != "current_support80_hdf5":
            out_path = manifest_output_path(args.out_manifest_prefix, label)
            write_manifest(out_path, label, rids, recs)
            written_manifests[label] = str(out_path.relative_to(REPO_ROOT))
    panels.sort(
        key=lambda panel: (
            panel["n_passing_target_family_rows"],
            panel["n_subjects"],
            panel["n_recordings"],
        ),
        reverse=True,
    )
    report = {
        "thresholds": {
            "window_len": args.window_len,
            "min_class_trials": args.min_class_trials,
            "min_family_units": args.min_family_units,
            "min_subject_recordings": args.min_subject_recordings,
        },
        "baseline_manifest": str(args.baseline_manifest),
        "n_local_recordings": len(all_recording_ids),
        "n_local_subjects": len(set(subject_by_rid.values())),
        "panels": panels,
        "written_manifests": written_manifests,
    }
    report["summary"] = summarize(report)
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text(render_markdown(report))
    print(f"wrote {args.out_json}")
    print(f"wrote {args.out_md}")
    for path in written_manifests.values():
        print(f"wrote {REPO_ROOT / path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
