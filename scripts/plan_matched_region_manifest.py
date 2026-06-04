"""Plan a larger manifest for region-matched cross-animal benchmarks.

This is an analysis-only step. It selects a larger balanced candidate manifest
from Alyx insertion metadata, then scores region-family support if the matching
HDF5 recordings are already present locally.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "vendor" / "torch_brain"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

try:
    from scripts.build_ibl_brainset import OPEN_ALYX, PUBLIC_PASS, PUBLIC_USER
    from scripts.build_ibl_brainset_batch import BWM_PROJECT
    from scripts.select_ibl_manifest import compact_insertion, select_balanced
    from scripts.train import map_region_acronyms
except ModuleNotFoundError:
    from build_ibl_brainset import OPEN_ALYX, PUBLIC_PASS, PUBLIC_USER
    from build_ibl_brainset_batch import BWM_PROJECT
    from select_ibl_manifest import compact_insertion, select_balanced
    from train import map_region_acronyms


def fetch_candidates(scan_limit: int) -> list[dict[str, Any]]:
    from one.api import ONE

    ONE.setup(base_url=OPEN_ALYX, silent=True)
    one = ONE(base_url=OPEN_ALYX, username=PUBLIC_USER, password=PUBLIC_PASS)
    raw = one.alyx.rest("insertions", "list", project=BWM_PROJECT, limit=scan_limit)
    return [row for ins in raw if (row := compact_insertion(ins)) is not None]


def write_manifest(
    *,
    selected: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
    args: argparse.Namespace,
) -> dict[str, Any]:
    return {
        "dataset": "ibl_bwm",
        "project": BWM_PROJECT,
        "selection": {
            "target": args.target,
            "scan_limit": args.scan_limit,
            "max_per_subject": args.max_per_subject,
            "min_units": args.min_units,
            "region_granularity": args.region_granularity,
            "candidate_pool_recordings": len(candidates),
            "candidate_pool_subjects": len({r["subject_id"] for r in candidates}),
        },
        "n_recordings": len(selected),
        "n_subjects": len({r["subject_id"] for r in selected}),
        "labs": sorted({r["lab"] for r in selected}),
        "recordings": selected,
    }


def manifest_from_existing(path: Path, region_granularity: str) -> dict[str, Any]:
    manifest = json.loads(path.read_text())
    manifest.setdefault("selection", {})
    manifest["selection"]["region_granularity"] = region_granularity
    return manifest


def _as_list(values) -> list:
    return values.tolist() if hasattr(values, "tolist") else list(values)


def summarize_local_regions(data_dir: Path, region_granularity: str) -> dict[str, dict]:
    if not data_dir.exists() or not any(data_dir.glob("*.h5")):
        return {}
    from torch_brain.dataset import Dataset

    ds = Dataset(dataset_dir=data_dir, keep_files_open=True)
    out: dict[str, dict] = {}
    for rid in ds.recording_ids:
        rec = ds.get_recording(rid)
        subject = str(rec.subject.id)
        fine_regions = [str(r) for r in _as_list(rec.units.region_acronym)]
        regions = map_region_acronyms(fine_regions, region_granularity)
        row = out.setdefault(subject, {
            "subject": subject,
            "recording_ids": [],
            "n_units": 0,
            "regions": Counter(),
        })
        row["recording_ids"].append(rid)
        row["n_units"] += len(regions)
        row["regions"].update(regions)
    return out


def support_against_others(local_subjects: dict[str, dict], subject: str) -> dict | None:
    row = local_subjects.get(subject)
    if row is None:
        return None
    heldout_regions = Counter(row["regions"])
    if not heldout_regions:
        return None
    train_regions = Counter()
    for other_subject, other_row in local_subjects.items():
        if other_subject != subject:
            train_regions.update(other_row["regions"])
    supported = sum(
        count for region, count in heldout_regions.items()
        if train_regions.get(region, 0) > 0
    )
    top_regions = heldout_regions.most_common(8)
    top_supported = [
        region for region, _count in top_regions
        if train_regions.get(region, 0) > 0
    ]
    return {
        "unit_support_frac": supported / sum(heldout_regions.values()),
        "n_regions": len(heldout_regions),
        "top_supported": len(top_supported),
        "top_total": len(top_regions),
        "missing_top": [
            region for region, _count in top_regions
            if train_regions.get(region, 0) == 0
        ],
    }


def selected_subject_counts(selected: list[dict[str, Any]]) -> Counter:
    return Counter(str(row["subject_id"]) for row in selected)


def lab_counts(selected: list[dict[str, Any]]) -> Counter:
    return Counter(str(row["lab"]) for row in selected)


def write_report(
    *,
    manifest: dict[str, Any],
    local_subjects: dict[str, dict],
    out_path: Path,
    data_dir: Path,
) -> None:
    selected = manifest["recordings"]
    subjects = sorted({str(row["subject_id"]) for row in selected})
    cached_subjects = sorted(set(local_subjects))
    full_cache = all(subject in local_subjects for subject in subjects)
    lines = [
        "# Matched-Region Manifest Plan",
        "",
        f"Candidate recordings: {manifest['n_recordings']}",
        f"Candidate subjects: {manifest['n_subjects']}",
        f"Region granularity: `{manifest['selection']['region_granularity']}`",
        f"Local BrainSet cache: `{data_dir}`",
        "",
        "## Metadata Balance",
        "",
        "| subject | selected_recordings | units_meta | labs | probes |",
        "|---|---:|---:|---|---|",
    ]
    by_subject: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in selected:
        by_subject[str(row["subject_id"])].append(row)
    for subject in subjects:
        rows = by_subject[subject]
        lines.append(
            "| "
            f"{subject} | {len(rows)} | {sum(int(r.get('n_units_meta') or 0) for r in rows)} | "
            f"{', '.join(sorted({str(r.get('lab', 'unknown')) for r in rows}))} | "
            f"{', '.join(f'{probe}:{n}' for probe, n in sorted(Counter(str(r.get('probe_name')) for r in rows).items()))} |"
        )
    lines += [
        "",
        "## Lab Counts",
        "",
        "| lab | selected_recordings |",
        "|---|---:|",
    ]
    for lab, count in sorted(lab_counts(selected).items()):
        lines.append(f"| {lab} | {count} |")

    lines += [
        "",
        "## Region-Family Scoring Status",
        "",
        (
            f"The local cache covers {len(cached_subjects)} subjects and "
            f"{sum(len(v['recording_ids']) for v in local_subjects.values())} recordings."
        ),
        "",
    ]
    if not full_cache:
        missing = [subject for subject in subjects if subject not in local_subjects]
        lines += [
            "The candidate manifest is not fully built locally, so region-family matching cannot be scored yet.",
            "",
            f"Missing candidate subjects in local cache: {', '.join(missing[:20])}"
            + (" ..." if len(missing) > 20 else ""),
            "",
        ]
    if local_subjects:
        lines += [
            "## Available Region Support",
            "",
            "| subject | cached_recordings | units | region_families | unit_support_vs_others | top8_supported | missing_top_regions |",
            "|---|---:|---:|---:|---:|---:|---|",
        ]
        for subject in sorted(local_subjects):
            row = local_subjects[subject]
            support = support_against_others(local_subjects, subject)
            if support is None:
                support_cells = "n/a | n/a | n/a"
            else:
                support_cells = (
                    f"{support['unit_support_frac']:.1%} | "
                    f"{support['top_supported']}/{support['top_total']} | "
                    f"{', '.join(support['missing_top']) or 'none'}"
                )
            lines.append(
                "| "
                f"{subject} | {len(row['recording_ids'])} | {row['n_units']} | "
                f"{len(row['regions'])} | {support_cells} |"
            )
    lines += [
        "",
        "## Decision Gate",
        "",
        "Build this candidate manifest only if we are ready to spend on data construction, not training.",
        "After build, rerun this planner and require at least 80% held-out unit support for most subjects before launching another seed sweep.",
        "",
    ]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines))


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--target", type=int, default=48)
    p.add_argument("--scan-limit", type=int, default=1000)
    p.add_argument("--max-per-subject", type=int, default=4)
    p.add_argument("--min-units", type=int, default=200)
    p.add_argument("--region-granularity", default="parent", choices=["fine", "parent", "grandparent"])
    p.add_argument("--input-manifest", type=Path, default=None,
                   help="Score an existing candidate manifest instead of selecting a new one from Alyx.")
    p.add_argument("--data-dir", type=Path, default=REPO_ROOT / "data/brainsets/ibl_bwm")
    p.add_argument("--out-manifest", type=Path, default=REPO_ROOT / "manifests/ibl_bwm_region_matched_candidates.json")
    p.add_argument("--out-report", type=Path, default=REPO_ROOT / "docs/matched_region_manifest_plan.md")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if args.input_manifest is not None:
        manifest = manifest_from_existing(args.input_manifest, args.region_granularity)
        selected = manifest["recordings"]
    else:
        candidates = fetch_candidates(args.scan_limit)
        selected = select_balanced(candidates, args.target, args.max_per_subject, args.min_units)
        if len(selected) < args.target:
            raise SystemExit(f"selected only {len(selected)}/{args.target}; lower filters or scan more")
        manifest = write_manifest(selected=selected, candidates=candidates, args=args)
    args.out_manifest.parent.mkdir(parents=True, exist_ok=True)
    args.out_manifest.write_text(json.dumps(manifest, indent=2) + "\n")
    local_subjects = summarize_local_regions(args.data_dir, args.region_granularity)
    write_report(
        manifest=manifest,
        local_subjects=local_subjects,
        out_path=args.out_report,
        data_dir=args.data_dir,
    )
    print(f"wrote {args.out_manifest}")
    print(f"wrote {args.out_report}")
    print(
        f"selected recordings={manifest['n_recordings']} "
        f"subjects={manifest['n_subjects']} labs={len(manifest['labs'])}"
    )
    for subject, count in sorted(selected_subject_counts(selected).items()):
        print(f"  {subject}: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
