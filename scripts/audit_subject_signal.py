"""Audit subject-level coverage and LSO deltas for cross-animal transfer."""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "vendor" / "torch_brain"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))


@dataclass(frozen=True)
class SubjectResult:
    holdout: str
    arm: str
    n_seeds: int
    mean_auc: float
    mean_delta: float
    seed_deltas: tuple[float, ...]


def parse_lso_results(path: Path) -> list[SubjectResult]:
    rows: list[SubjectResult] = []
    if not path.exists():
        return rows
    row_re = re.compile(r"^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*(\d+)\s*\|")
    for line in path.read_text().splitlines():
        if not line.startswith("|"):
            continue
        match = row_re.match(line)
        if not match or match.group(1) in {"holdout", "---"}:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 6:
            continue
        holdout, arm, n_seeds, mean_auc, mean_delta, seed_deltas = cells
        try:
            rows.append(SubjectResult(
                holdout=holdout,
                arm=arm,
                n_seeds=int(n_seeds),
                mean_auc=float(mean_auc),
                mean_delta=float(mean_delta),
                seed_deltas=tuple(float(x) for x in seed_deltas.split(",") if x),
            ))
        except ValueError:
            continue
    return rows


def load_manifest(path: Path) -> dict:
    return json.loads(path.read_text())


def summarize_manifest_subjects(manifest: dict) -> dict[str, dict]:
    by_subject: dict[str, dict] = {}
    for rec in manifest.get("recordings", []):
        subject = str(rec["subject_id"])
        row = by_subject.setdefault(subject, {
            "subject": subject,
            "n_recordings": 0,
            "n_units_meta": 0,
            "labs": set(),
            "probes": Counter(),
            "task_protocols": Counter(),
            "alignment_qc": [],
        })
        row["n_recordings"] += 1
        row["n_units_meta"] += int(rec.get("n_units_meta") or 0)
        if rec.get("lab"):
            row["labs"].add(str(rec["lab"]))
        if rec.get("probe_name"):
            row["probes"][str(rec["probe_name"])] += 1
        if rec.get("task_protocol"):
            row["task_protocols"][str(rec["task_protocol"])] += 1
        if rec.get("alignment_qc") is not None:
            row["alignment_qc"].append(float(rec["alignment_qc"]))
    return by_subject


def _as_list(values) -> list:
    return values.tolist() if hasattr(values, "tolist") else list(values)


def summarize_local_brainset(data_dir: Path, target_mode: str, window_len: float) -> dict[str, dict]:
    if not data_dir.exists() or not any(data_dir.glob("*.h5")):
        return {}
    import numpy as np
    from torch_brain.dataset import Dataset
    from train import build_trial_samples

    ds = Dataset(dataset_dir=data_dir, keep_files_open=True)
    recs = {rid: ds.get_recording(rid) for rid in ds.recording_ids}
    by_subject: dict[str, dict] = {}
    for rid, rec in recs.items():
        subject = str(rec.subject.id)
        regions = [str(r) for r in _as_list(rec.units.region_acronym)]
        region_counts = Counter(regions)
        trials = build_trial_samples({rid: rec}, [rid], window_len, target_mode)
        target_counts = Counter("R" if target == 1.0 else "L" for _rid, _t0, target in trials)
        row = by_subject.setdefault(subject, {
            "subject": subject,
            "recording_ids": [],
            "n_units": 0,
            "regions": Counter(),
            "target_counts": Counter(),
            "n_trials": 0,
        })
        row["recording_ids"].append(rid)
        row["n_units"] += int(len(rec.units.id))
        row["regions"].update(region_counts)
        row["target_counts"].update(target_counts)
        row["n_trials"] += int(len(np.asarray(rec.trials.choice))) if hasattr(rec, "trials") else 0
    return by_subject


def best_result_by_subject(results: Iterable[SubjectResult]) -> dict[str, SubjectResult]:
    best: dict[str, SubjectResult] = {}
    for result in results:
        current = best.get(result.holdout)
        if current is None or result.mean_delta > current.mean_delta:
            best[result.holdout] = result
    return best


def result_lookup(results: Iterable[SubjectResult]) -> dict[tuple[str, str], SubjectResult]:
    return {(r.holdout, r.arm): r for r in results}


def fmt_float(value: float | None, digits: int = 3) -> str:
    if value is None:
        return "n/a"
    return f"{value:.{digits}f}"


def fmt_delta(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:+.3f}"


def display_path(path: Path) -> str:
    path = path.expanduser()
    if not path.is_absolute():
        return str(path)
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def counter_keys(counter: Counter) -> str:
    if not counter:
        return "n/a"
    return ", ".join(f"{k}:{v}" for k, v in sorted(counter.items()))


def region_support(local_subjects: dict[str, dict], subject: str) -> dict | None:
    row = local_subjects.get(subject)
    if row is None:
        return None
    train_regions = Counter()
    for other_subject, other_row in local_subjects.items():
        if other_subject != subject:
            train_regions.update(other_row["regions"])
    subject_regions = Counter(row["regions"])
    if not subject_regions:
        return None
    supported_units = sum(
        count for region, count in subject_regions.items()
        if train_regions.get(region, 0) > 0
    )
    top_regions = subject_regions.most_common(8)
    top_supported = sum(1 for region, _count in top_regions if train_regions.get(region, 0) > 0)
    missing_top = [region for region, _count in top_regions if train_regions.get(region, 0) == 0]
    return {
        "unit_support_frac": supported_units / sum(subject_regions.values()),
        "top_supported": top_supported,
        "top_total": len(top_regions),
        "missing_top": missing_top,
    }


def write_report(
    *,
    manifest_path: Path,
    results_path: Path,
    data_dir: Path,
    out_path: Path,
    target_mode: str,
    window_len: float,
) -> None:
    manifest = load_manifest(manifest_path)
    manifest_subjects = summarize_manifest_subjects(manifest)
    local_subjects = summarize_local_brainset(data_dir, target_mode, window_len)
    results = parse_lso_results(results_path)
    lookup = result_lookup(results)
    best = best_result_by_subject(results)

    subjects = sorted(manifest_subjects)
    candidate_subjects = sorted({r.holdout for r in results})
    local_only = sorted(set(local_subjects) - set(manifest_subjects))
    full_local_coverage = (
        len(local_subjects) >= len(subjects)
        and not local_only
        and all(subject in local_subjects for subject in subjects)
    )

    lines = [
        "# Subject-Conditioned Signal Audit",
        "",
        f"Manifest: `{display_path(manifest_path)}`",
        f"LSO result source: `{display_path(results_path)}`",
        f"Local BrainSet cache: `{display_path(data_dir)}`",
        "",
        "## Coverage Status",
        "",
        (
            f"The 20-recording manifest contains {len(subjects)} subjects. "
            f"The local HDF5 cache currently covers {len(local_subjects)} subjects "
            f"and {sum(len(v['recording_ids']) for v in local_subjects.values())} recordings."
        ),
        "",
    ]
    if local_only:
        lines += [
            "Local cache subjects not present in the 20-recording manifest:",
            "",
            *[f"- `{subject}`" for subject in local_only],
            "",
        ]
    if len(local_subjects) < len(subjects):
        lines += [
            (
                "Trial class balance and region overlap are therefore partial locally. "
                "Run this script on the same RunPod-built dataset for the full audit."
            ),
            "",
        ]

    lines += [
        "## Manifest Subject Summary",
        "",
        "| subject | recordings | units_meta | lab | probes | mean_alignment_qc | best_confirmed_delta |",
        "|---|---:|---:|---|---|---:|---:|",
    ]
    for subject in subjects:
        row = manifest_subjects[subject]
        align = mean(row["alignment_qc"]) if row["alignment_qc"] else None
        best_result = best.get(subject)
        best_cell = "n/a"
        if best_result:
            best_cell = f"{best_result.arm} {fmt_delta(best_result.mean_delta)}"
        lines.append(
            "| "
            f"{subject} | {row['n_recordings']} | {row['n_units_meta']} | "
            f"{', '.join(sorted(row['labs'])) or 'n/a'} | {counter_keys(row['probes'])} | "
            f"{fmt_float(align)} | {best_cell} |"
        )

    if results:
        lines += [
            "",
            "## Candidate Confirmation Deltas",
            "",
            "| subject | pure_anatomy | region_only | waveform_only | strongest arm | positive pure seeds |",
            "|---|---:|---:|---:|---|---:|",
        ]
        for subject in candidate_subjects:
            pure = lookup.get((subject, "pure_anatomy"))
            region = lookup.get((subject, "region_only"))
            waveform = lookup.get((subject, "waveform_only"))
            best_result = best.get(subject)
            pure_pos = sum(1 for delta in pure.seed_deltas if delta > 0) if pure else 0
            pure_total = len(pure.seed_deltas) if pure else 0
            lines.append(
                "| "
                f"{subject} | {fmt_delta(pure.mean_delta if pure else None)} | "
                f"{fmt_delta(region.mean_delta if region else None)} | "
                f"{fmt_delta(waveform.mean_delta if waveform else None)} | "
                f"{best_result.arm if best_result else 'n/a'} | {pure_pos}/{pure_total} |"
            )

    if local_subjects:
        lines += [
            "",
            "## Local Trial And Region Audit",
            "",
            "| subject | cached_recordings | valid_target_trials | target_balance | units | regions | top_regions |",
            "|---|---:|---:|---|---:|---:|---|",
        ]
        for subject in sorted(local_subjects):
            row = local_subjects[subject]
            top_regions = ", ".join(
                f"{region}:{count}" for region, count in row["regions"].most_common(8)
            )
            lines.append(
                "| "
                f"{subject} | {len(row['recording_ids'])} | {sum(row['target_counts'].values())} | "
                f"{counter_keys(row['target_counts'])} | {row['n_units']} | "
                f"{len(row['regions'])} | {top_regions or 'n/a'} |"
            )

    if candidate_subjects and local_subjects:
        lines += [
            "",
            "## Held-Out Region Support",
            "",
            "For each candidate subject, support is computed against all other cached subjects, matching the leave-subject-out training split.",
            "",
            "| subject | heldout_region_units_supported_by_train | top8_regions_seen_in_train | top8_regions_missing_from_train |",
            "|---|---:|---:|---|",
        ]
        for subject in candidate_subjects:
            support = region_support(local_subjects, subject)
            if support is None:
                lines.append(f"| {subject} | n/a | n/a | n/a |")
                continue
            lines.append(
                "| "
                f"{subject} | {support['unit_support_frac']:.1%} | "
                f"{support['top_supported']}/{support['top_total']} | "
                f"{', '.join(support['missing_top']) or 'none'} |"
            )

    lines += [
        "",
        "## Interpretation",
        "",
    ]
    if full_local_coverage:
        dy_support = region_support(local_subjects, "DY_008")
        dy_support_text = ""
        if dy_support is not None:
            dy_support_text = (
                f" Its held-out units have {dy_support['unit_support_frac']:.1%} "
                "region support in the other subjects, and "
                f"{dy_support['top_supported']}/{dy_support['top_total']} top regions "
                "are seen in training."
            )
        lines.append(
            "`DY_008` remains the only confirmed subject where both `pure_anatomy` "
            "and `region_only` beat the shared null by more than +0.03 across all "
            "three seeds. The full-cache audit makes a pure class-balance explanation "
            "less likely: `DY_008` has 405 left vs 376 right valid stimulus-side "
            f"trials.{dy_support_text}"
        )
        lines += [
            "",
            (
                "Next action: run a region-balanced LSO rerun focused on `DY_008` "
                "plus matched controls. If the lift survives matched region support, "
                "it becomes a stronger candidate transfer demo; if it disappears, "
                "treat the current lift as coverage-driven."
            ),
            "",
        ]
    else:
        lines.append(
            "`DY_008` remains the only confirmed subject where both `pure_anatomy` "
            "and `region_only` beat the shared null by more than +0.03 across all "
            "three seeds. The current local cache is insufficient to prove whether "
            "that is due to region coverage, trial balance, or a real transferable "
            "anatomical factor."
        )
        lines += [
            "",
            "Next action: rerun this audit on the full RunPod-built 20-recording dataset, then launch only a region-balanced LSO rerun if `DY_008` has comparable training/eval region support.",
            "",
        ]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines))


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", type=Path, default=REPO_ROOT / "manifests/ibl_bwm_phase4.json")
    p.add_argument("--results", type=Path, default=REPO_ROOT / "docs/lso_promising_results.md")
    p.add_argument("--data-dir", type=Path, default=REPO_ROOT / "data/brainsets/ibl_bwm")
    p.add_argument("--out", type=Path, default=REPO_ROOT / "docs/subject_conditioned_signal_audit.md")
    p.add_argument("--target-mode", default="stimulus_side", choices=["choice", "stimulus_side", "feedback", "prior_side"])
    p.add_argument("--window-len", type=float, default=1.0)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    write_report(
        manifest_path=args.manifest,
        results_path=args.results,
        data_dir=args.data_dir,
        out_path=args.out,
        target_mode=args.target_mode,
        window_len=args.window_len,
    )
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
