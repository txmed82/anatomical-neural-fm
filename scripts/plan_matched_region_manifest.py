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
from itertools import combinations
from pathlib import Path
from typing import Any

import numpy as np

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


def local_subject_row(
    out: dict[str, dict],
    *,
    subject: str,
    recording_id: str,
    regions: list[str],
) -> None:
    row = out.setdefault(subject, {
        "subject": subject,
        "recording_ids": [],
        "n_units": 0,
        "regions": Counter(),
    })
    row["recording_ids"].append(recording_id)
    row["n_units"] += len(regions)
    row["regions"].update(regions)


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
        local_subject_row(out, subject=subject, recording_id=rid, regions=regions)
    return out


def _probe_collection(one, eid: str, probe_name: str) -> str:
    collections = one.list_collections(eid)
    probe_collections = [str(c) for c in collections if probe_name in str(c)]
    coll = next((c for c in probe_collections if "pykilosort" in c), None)
    if coll is None:
        raise ValueError(f"No pykilosort collection for {eid} {probe_name}; got {probe_collections}")
    return coll


def _subject_from_details(one, eid: str) -> str:
    details = one.get_details(eid)
    if isinstance(details, dict):
        return str(details.get("subject", "unknown"))
    return str(getattr(details, "subject", "unknown"))


def summarize_manifest_regions_from_alyx(
    manifest: dict[str, Any],
    region_granularity: str,
    *,
    max_recordings: int | None = None,
) -> tuple[dict[str, dict], list[dict[str, str]]]:
    """Score region support from small ALF metadata, without full spike HDF5s."""
    from iblatlas.regions import BrainRegions
    from one.api import ONE

    ONE.setup(base_url=OPEN_ALYX, silent=True)
    one = ONE(base_url=OPEN_ALYX, username=PUBLIC_USER, password=PUBLIC_PASS)
    br = BrainRegions()
    out: dict[str, dict] = {}
    failures: list[dict[str, str]] = []
    rows = manifest["recordings"]
    if max_recordings is not None:
        rows = rows[:max_recordings]
    for row in rows:
        eid = str(row.get("session_id") or row.get("eid") or row.get("session"))
        probe_name = str(row.get("probe_name") or row.get("probe") or row.get("name"))
        try:
            subject = str(row.get("subject_id") or "") or _subject_from_details(one, eid)
            coll = _probe_collection(one, eid, probe_name)
            cluster_channels = np.asarray(
                one.load_dataset(eid, "clusters.channels.npy", collection=coll),
                dtype=np.int64,
            )
            channel_region_ids = np.asarray(
                one.load_dataset(eid, "channels.brainLocationIds_ccf_2017.npy", collection=coll),
                dtype=np.int64,
            )
            valid = (
                (cluster_channels >= 0)
                & (cluster_channels < len(channel_region_ids))
            )
            if not valid.any():
                raise ValueError("no valid cluster channel indices")
            region_ids = channel_region_ids[cluster_channels[valid]]
            fine_regions = [str(r) for r in br.id2acronym(region_ids)]
            regions = map_region_acronyms(fine_regions, region_granularity)
            recording_id = f"{eid}_{probe_name}"
            local_subject_row(out, subject=subject, recording_id=recording_id, regions=regions)
        except Exception as exc:
            failures.append({"session": eid, "probe": probe_name, "error": str(exc)})
    return out, failures


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


def support_summary(local_subjects: dict[str, dict]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for subject in sorted(local_subjects):
        row = local_subjects[subject]
        support = support_against_others(local_subjects, subject)
        out[subject] = {
            "cached_recordings": len(row["recording_ids"]),
            "n_units": int(row["n_units"]),
            "n_region_families": len(row["regions"]),
            "unit_support_frac": None if support is None else support["unit_support_frac"],
            "top_supported": None if support is None else support["top_supported"],
            "top_total": None if support is None else support["top_total"],
            "missing_top": [] if support is None else support["missing_top"],
        }
    return out


def subjects_passing_support_gate(
    local_subjects: dict[str, dict],
    min_support: float,
    *,
    iterative: bool = True,
) -> set[str]:
    active = set(local_subjects)
    while True:
        scoped = {subject: local_subjects[subject] for subject in active}
        failing = {
            subject
            for subject in active
            if (
                (support := support_against_others(scoped, subject)) is None
                or support["unit_support_frac"] < min_support
            )
        }
        if not iterative:
            return active - failing
        if not failing:
            return active
        next_active = active - failing
        if next_active == active:
            return active
        if len(next_active) < 2:
            return next_active
        active = next_active


def filter_manifest_to_subjects(
    manifest: dict[str, Any],
    subjects: set[str],
    *,
    min_support: float,
) -> dict[str, Any]:
    selected = [
        row for row in manifest["recordings"]
        if str(row["subject_id"]) in subjects
    ]
    filtered = dict(manifest)
    filtered["selection"] = dict(manifest.get("selection", {}))
    filtered["selection"]["filter_min_support"] = min_support
    filtered["selection"]["pre_filter_recordings"] = manifest["n_recordings"]
    filtered["selection"]["pre_filter_subjects"] = manifest["n_subjects"]
    filtered["recordings"] = selected
    filtered["n_recordings"] = len(selected)
    filtered["n_subjects"] = len({str(row["subject_id"]) for row in selected})
    filtered["labs"] = sorted({str(row["lab"]) for row in selected})
    return filtered


def filter_metadata_failures_to_manifest(
    failures: list[dict[str, str]],
    manifest: dict[str, Any],
) -> list[dict[str, str]]:
    selected_keys = {
        (
            str(row.get("session_id") or row.get("eid") or row.get("session")),
            str(row.get("probe_name") or row.get("probe") or row.get("name")),
        )
        for row in manifest["recordings"]
    }
    return [
        row for row in failures
        if (str(row["session"]), str(row["probe"])) in selected_keys
    ]


def best_support_subset(
    local_subjects: dict[str, dict],
    *,
    min_support: float,
    min_subjects: int,
) -> tuple[set[str], dict[str, Any]]:
    subjects = sorted(local_subjects)
    best_subjects: set[str] = set()
    best_meta: dict[str, Any] = {}
    best_score: tuple = (-1.0, -1, -1.0, -1, -1)
    for size in range(min_subjects, len(subjects) + 1):
        for combo in combinations(subjects, size):
            scoped = {subject: local_subjects[subject] for subject in combo}
            summary = support_summary(scoped)
            fracs = [
                row["unit_support_frac"]
                for row in summary.values()
                if row["unit_support_frac"] is not None
            ]
            if len(fracs) != len(combo):
                continue
            pass_count = sum(1 for frac in fracs if frac >= min_support)
            pass_frac = pass_count / len(combo)
            min_frac = min(fracs)
            total_units = sum(int(scoped[subject]["n_units"]) for subject in combo)
            score = (pass_frac, pass_count, min_frac, len(combo), total_units)
            if score > best_score:
                best_score = score
                best_subjects = set(combo)
                best_meta = {
                    "min_support": min_support,
                    "min_subjects": min_subjects,
                    "pass_count": pass_count,
                    "subject_count": len(combo),
                    "pass_frac": pass_frac,
                    "min_unit_support_frac": min_frac,
                    "total_units": total_units,
                }
    return best_subjects, best_meta


def write_report(
    *,
    manifest: dict[str, Any],
    local_subjects: dict[str, dict],
    out_path: Path,
    data_dir: Path,
    region_source: str,
    metadata_failures: list[dict[str, str]] | None = None,
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
        f"Region source: {region_source}",
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
            f"The region source covers {len(cached_subjects)} subjects and "
            f"{sum(len(v['recording_ids']) for v in local_subjects.values())} recordings."
        ),
        "",
    ]
    if not full_cache:
        missing = [subject for subject in subjects if subject not in local_subjects]
        lines += [
            "The candidate manifest is not fully covered by the selected region source, so region-family matching is partial.",
            "",
            f"Missing candidate subjects in region source: {', '.join(missing[:20])}"
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
    if metadata_failures:
        lines += [
            "",
            "## Metadata Region Failures",
            "",
            "| session | probe | error |",
            "|---|---|---|",
        ]
        for row in metadata_failures:
            lines.append(f"| {row['session']} | {row['probe']} | {row['error']} |")
    lines += [
        "",
        "## Decision Gate",
        "",
        "Build this candidate manifest only if we are ready to spend on data construction, not training.",
        "Before launching another seed sweep, require at least 80% held-out unit support for most subjects.",
        "If this report used metadata-only scoring, use it to choose the cache target, then confirm support again after the HDF5 build.",
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
    p.add_argument("--score-from-alyx-metadata", action="store_true",
                   help="Score unit region support from small OpenAlyx cluster/channel metadata instead of local HDF5s.")
    p.add_argument("--metadata-max-recordings", type=int, default=None,
                   help="Optional cap for metadata scoring smoke tests.")
    p.add_argument("--filter-min-support", type=float, default=None,
                   help="Drop subjects below this held-out unit support fraction before writing outputs.")
    p.add_argument("--filter-support-mode", choices=["initial", "iterative"], default="initial",
                   help="initial filters by support in the full candidate set; iterative recomputes until stable.")
    p.add_argument("--optimize-support-subset", type=float, default=None,
                   help="Search subject subsets and keep the one maximizing support-pass fraction at this threshold.")
    p.add_argument("--optimize-min-subjects", type=int, default=6,
                   help="Minimum subjects for --optimize-support-subset.")
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
    metadata_failures: list[dict[str, str]] = []
    if args.score_from_alyx_metadata:
        local_subjects, metadata_failures = summarize_manifest_regions_from_alyx(
            manifest,
            args.region_granularity,
            max_recordings=args.metadata_max_recordings,
        )
        region_source = "OpenAlyx cluster/channel metadata"
    else:
        local_subjects = summarize_local_regions(args.data_dir, args.region_granularity)
        region_source = "local BrainSet HDF5 cache"
    if args.filter_min_support is not None:
        keep_subjects = subjects_passing_support_gate(
            local_subjects,
            args.filter_min_support,
            iterative=args.filter_support_mode == "iterative",
        )
        manifest = filter_manifest_to_subjects(
            manifest,
            keep_subjects,
            min_support=args.filter_min_support,
        )
        local_subjects = {
            subject: row for subject, row in local_subjects.items()
            if subject in keep_subjects
        }
    if args.optimize_support_subset is not None:
        keep_subjects, subset_meta = best_support_subset(
            local_subjects,
            min_support=args.optimize_support_subset,
            min_subjects=args.optimize_min_subjects,
        )
        manifest = filter_manifest_to_subjects(
            manifest,
            keep_subjects,
            min_support=args.optimize_support_subset,
        )
        manifest["selection"]["optimized_support_subset"] = subset_meta
        local_subjects = {
            subject: row for subject, row in local_subjects.items()
            if subject in keep_subjects
        }
    manifest["region_support"] = support_summary(local_subjects)
    metadata_failures = filter_metadata_failures_to_manifest(metadata_failures, manifest)
    args.out_manifest.parent.mkdir(parents=True, exist_ok=True)
    args.out_manifest.write_text(json.dumps(manifest, indent=2) + "\n")
    write_report(
        manifest=manifest,
        local_subjects=local_subjects,
        out_path=args.out_report,
        data_dir=args.data_dir,
        region_source=region_source,
        metadata_failures=metadata_failures,
    )
    print(f"wrote {args.out_manifest}")
    print(f"wrote {args.out_report}")
    print(
        f"selected recordings={manifest['n_recordings']} "
        f"subjects={manifest['n_subjects']} labs={len(manifest['labs'])}"
    )
    for subject, count in sorted(selected_subject_counts(manifest["recordings"]).items()):
        print(f"  {subject}: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
