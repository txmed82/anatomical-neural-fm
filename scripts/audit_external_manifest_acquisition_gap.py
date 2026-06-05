"""Audit which externally scored manifest recordings are worth acquiring next."""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def recording_id(row: dict) -> str:
    eid = row.get("session_id") or row.get("eid") or row.get("session")
    probe = row.get("probe_name") or row.get("probe") or row.get("name")
    if not eid or not probe:
        raise ValueError(f"manifest row lacks session/probe fields: {row}")
    return f"{eid}_{probe}"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def local_recording_ids(local_candidates: dict) -> set[str]:
    for panel in local_candidates.get("panels", []):
        if panel.get("label") == "all_local_cached":
            return set(panel.get("recording_ids", []))
    return set()


def subject_rows(manifest: dict) -> dict[str, list[dict]]:
    by_subject: dict[str, list[dict]] = defaultdict(list)
    for row in manifest.get("recordings", []):
        by_subject[str(row["subject_id"])].append(row)
    return dict(sorted(by_subject.items()))


def is_support_qualified(subject: str, support: dict, n_recordings: int, *, min_support: float, min_recordings: int) -> bool:
    row = support.get(subject, {})
    value = row.get("unit_support_frac")
    return value is not None and float(value) >= min_support and n_recordings >= min_recordings


def build_subject_gap_rows(
    broad_manifest: dict,
    local_ids: set[str],
    *,
    min_support: float,
    min_recordings: int,
) -> list[dict]:
    support = broad_manifest.get("region_support", {})
    rows = []
    for subject, recs in subject_rows(broad_manifest).items():
        ids = [recording_id(row) for row in recs]
        present = [rid for rid in ids if rid in local_ids]
        missing = [rid for rid in ids if rid not in local_ids]
        support_row = support.get(subject, {})
        rows.append({
            "subject": subject,
            "n_recordings": len(ids),
            "local_hdf5_recordings": len(present),
            "missing_hdf5_recordings": len(missing),
            "unit_support_frac": support_row.get("unit_support_frac"),
            "top_supported": support_row.get("top_supported"),
            "top_total": support_row.get("top_total"),
            "missing_top": support_row.get("missing_top", []),
            "support_qualified": is_support_qualified(
                subject,
                support,
                len(ids),
                min_support=min_support,
                min_recordings=min_recordings,
            ),
            "recording_ids": ids,
            "missing_recording_ids": missing,
        })
    return sorted(
        rows,
        key=lambda row: (
            row["support_qualified"],
            row["missing_hdf5_recordings"] > 0,
            row["unit_support_frac"] or 0.0,
            row["n_recordings"],
        ),
        reverse=True,
    )


def rows_for_recording_ids(manifest: dict, recording_ids: set[str]) -> list[dict]:
    return [row for row in manifest["recordings"] if recording_id(row) in recording_ids]


def manifest_payload(label: str, rows: list[dict], *, source_manifest: Path, note: str) -> dict:
    return {
        "dataset": "ibl_bwm",
        "project": "anatomical-neural-fm",
        "selection": {
            "label": label,
            "source_manifest": str(source_manifest),
            "note": note,
        },
        "n_recordings": len(rows),
        "n_subjects": len({str(row["subject_id"]) for row in rows}),
        "labs": sorted({str(row.get("lab", "unknown")) for row in rows}),
        "recordings": rows,
    }


def write_manifest(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def summarize(report: dict) -> dict:
    rows = report["subject_rows"]
    qualified = [row for row in rows if row["support_qualified"]]
    missing_qualified = [row for row in qualified if row["missing_hdf5_recordings"] > 0]
    return {
        "n_broad_recordings": report["n_broad_recordings"],
        "n_broad_subjects": report["n_broad_subjects"],
        "n_local_hdf5_recordings_in_broad_manifest": report["n_local_hdf5_recordings_in_broad_manifest"],
        "support_qualified_subjects": len(qualified),
        "support_qualified_subjects_missing_hdf5": len(missing_qualified),
        "missing_hdf5_recordings_for_qualified_subjects": sum(
            row["missing_hdf5_recordings"] for row in missing_qualified
        ),
        "projected_manifest_recordings": report["projected_manifest"]["n_recordings"],
        "projected_manifest_subjects": report["projected_manifest"]["n_subjects"],
        "decision": (
            "external_support80_acquisition_candidate"
            if missing_qualified
            else "no_external_support80_acquisition_gap"
        ),
    }


def render_markdown(report: dict) -> str:
    summary = report["summary"]
    lines = [
        "# External Manifest Acquisition Gap Audit",
        "",
        (
            "No-spend audit that compares the broader S3-present metadata-scored "
            "manifest against local HDF5 coverage. It identifies support-qualified "
            "subjects whose recordings should be acquired before another local "
            "model-free gate."
        ),
        "",
        f"- broad manifest recordings: `{summary['n_broad_recordings']}`",
        f"- broad manifest subjects: `{summary['n_broad_subjects']}`",
        f"- local HDF5 recordings in broad manifest: `{summary['n_local_hdf5_recordings_in_broad_manifest']}`",
        f"- support-qualified subjects: `{summary['support_qualified_subjects']}`",
        f"- support-qualified subjects missing HDF5: `{summary['support_qualified_subjects_missing_hdf5']}`",
        f"- missing HDF5 recordings for qualified subjects: `{summary['missing_hdf5_recordings_for_qualified_subjects']}`",
        f"- projected manifest: `{summary['projected_manifest_recordings']}` recordings, `{summary['projected_manifest_subjects']}` subjects",
        f"- decision: `{summary['decision']}`",
        "",
        "## Subject Gaps",
        "",
        "| subject | support | broad recs | local HDF5 | missing HDF5 | qualified | missing top regions |",
        "|---|---:|---:|---:|---:|---|---|",
    ]
    for row in report["subject_rows"]:
        support = "n/a" if row["unit_support_frac"] is None else f"{row['unit_support_frac']:.3f}"
        lines.append(
            f"| {row['subject']} | {support} | {row['n_recordings']} | "
            f"{row['local_hdf5_recordings']} | {row['missing_hdf5_recordings']} | "
            f"{row['support_qualified']} | {', '.join(row['missing_top']) or 'none'} |"
        )
    lines += [
        "",
        "## Written Manifests",
        "",
    ]
    for key, path in report["written_manifests"].items():
        lines.append(f"- `{key}`: `{path}`")
    lines += [
        "",
        "## Decision",
        "",
        (
            "This is a data-acquisition trigger, not a training trigger. After these "
            "recordings are available as local HDF5s, rerun the local manifest candidate "
            "audit and then the same model-free true-vs-shuffle, total-baseline, "
            "target0/target1, and same-recording bidirectional gate before any GPU run."
        ),
        "",
    ]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--broad-manifest",
        type=Path,
        default=REPO_ROOT / "manifests/ibl_bwm_region_matched_candidates_s3_present_scored.json",
    )
    parser.add_argument(
        "--local-candidates",
        type=Path,
        default=REPO_ROOT / "docs/local_cached_manifest_candidates.json",
    )
    parser.add_argument("--min-support", type=float, default=0.8)
    parser.add_argument("--min-recordings-per-subject", type=int, default=2)
    parser.add_argument("--out-json", type=Path, default=REPO_ROOT / "docs/external_manifest_acquisition_gap.json")
    parser.add_argument("--out-md", type=Path, default=REPO_ROOT / "docs/external_manifest_acquisition_gap.md")
    parser.add_argument(
        "--out-missing-manifest",
        type=Path,
        default=REPO_ROOT / "manifests/ibl_bwm_external_support80_missing_hdf5.json",
    )
    parser.add_argument(
        "--out-projected-manifest",
        type=Path,
        default=REPO_ROOT / "manifests/ibl_bwm_external_support80_projected_hdf5.json",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    broad_manifest = load_json(args.broad_manifest)
    local_candidates = load_json(args.local_candidates)
    local_ids = local_recording_ids(local_candidates)
    broad_ids = {recording_id(row) for row in broad_manifest["recordings"]}
    subject_gap_rows = build_subject_gap_rows(
        broad_manifest,
        local_ids,
        min_support=args.min_support,
        min_recordings=args.min_recordings_per_subject,
    )
    qualified_ids = {
        rid
        for row in subject_gap_rows
        if row["support_qualified"]
        for rid in row["recording_ids"]
    }
    missing_qualified_ids = qualified_ids - local_ids
    missing_manifest = manifest_payload(
        "external_support80_missing_hdf5",
        rows_for_recording_ids(broad_manifest, missing_qualified_ids),
        source_manifest=args.broad_manifest,
        note="Support-qualified broad-manifest recordings missing from local HDF5 cache.",
    )
    projected_manifest = manifest_payload(
        "external_support80_projected_hdf5",
        rows_for_recording_ids(broad_manifest, qualified_ids),
        source_manifest=args.broad_manifest,
        note="Projected support-qualified HDF5 panel after acquiring the missing recordings.",
    )
    write_manifest(args.out_missing_manifest, missing_manifest)
    write_manifest(args.out_projected_manifest, projected_manifest)
    report = {
        "thresholds": {
            "min_support": args.min_support,
            "min_recordings_per_subject": args.min_recordings_per_subject,
        },
        "broad_manifest": str(args.broad_manifest),
        "local_candidates": str(args.local_candidates),
        "n_broad_recordings": len(broad_ids),
        "n_broad_subjects": broad_manifest["n_subjects"],
        "n_local_hdf5_recordings_in_broad_manifest": len(local_ids & broad_ids),
        "subject_rows": subject_gap_rows,
        "missing_manifest": missing_manifest,
        "projected_manifest": projected_manifest,
        "written_manifests": {
            "missing_hdf5": str(args.out_missing_manifest.relative_to(REPO_ROOT)),
            "projected_hdf5": str(args.out_projected_manifest.relative_to(REPO_ROOT)),
        },
    }
    report["summary"] = summarize(report)
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text(render_markdown(report))
    print(f"wrote {args.out_json}")
    print(f"wrote {args.out_md}")
    print(f"wrote {args.out_missing_manifest}")
    print(f"wrote {args.out_projected_manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
