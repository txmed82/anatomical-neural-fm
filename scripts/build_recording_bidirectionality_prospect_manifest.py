"""Build a manifest from recording-bidirectionality prospectus leads."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BASE_MANIFEST = REPO_ROOT / "manifests/ibl_bwm_region_matched_candidates_s3_present_support80_hdf5_scored.json"
DEFAULT_PROSPECTUS = REPO_ROOT / "docs/recording_bidirectionality_prospectus.json"
DEFAULT_OUT = REPO_ROOT / "manifests/ibl_bwm_recording_bidirectionality_prospect_leads.json"


def recording_id(row: dict) -> str | None:
    eid = row.get("session_id") or row.get("eid") or row.get("session")
    probe = row.get("probe_name") or row.get("probe") or row.get("name")
    if not eid or not probe:
        return None
    return f"{eid}_{probe}"


def load_prospect_recording_ids(path: Path, *, limit: int | None = None) -> list[str]:
    payload = json.loads(path.read_text())
    rows = payload["summary"]["prospect_recordings"]
    if limit is not None:
        rows = rows[:limit]
    return [row["recording"] for row in rows]


def build_manifest(base_manifest: dict, prospect_recording_ids: list[str]) -> dict:
    requested = list(dict.fromkeys(prospect_recording_ids))
    requested_set = set(requested)
    base_rows = base_manifest["recordings"] if isinstance(base_manifest, dict) else base_manifest
    selected = []
    present = set()
    for row in base_rows:
        rid = recording_id(row)
        if rid in requested_set:
            selected.append(row | {"recording_id": rid})
            present.add(rid)
    missing = [rid for rid in requested if rid not in present]
    subjects = sorted({row.get("subject_id", "unknown") for row in selected})
    return {
        "project": "anatomical-neural-fm",
        "dataset": "ibl_bwm",
        "selection": {
            "source": "recording_bidirectionality_prospectus",
            "base_manifest": str(DEFAULT_BASE_MANIFEST),
            "rule": (
                "recordings with repeated bidirectional target0+target1 support across "
                "at least six observations, two target modes, and two sources"
            ),
        },
        "n_recordings": len(selected),
        "n_subjects": len(subjects),
        "subjects": subjects,
        "missing_recording_ids": missing,
        "recordings": selected,
    }


def render_markdown(report: dict) -> str:
    lines = [
        "# Recording Bidirectionality Prospect Manifest",
        "",
        "Concrete local manifest generated from the bidirectionality prospectus lead recordings.",
        "",
        f"- recordings: `{report['n_recordings']}`",
        f"- subjects: `{report['n_subjects']}`",
        f"- missing requested recordings: `{len(report['missing_recording_ids'])}`",
        "",
        "| recording_id | subject | lab | qc |",
        "|---|---|---|---|",
    ]
    for row in report["recordings"]:
        lines.append(
            f"| {row['recording_id']} | {row.get('subject_id', 'unknown')} | "
            f"{row.get('lab', 'unknown')} | {row.get('qc', 'unknown')} |"
        )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-manifest", type=Path, default=DEFAULT_BASE_MANIFEST)
    parser.add_argument("--prospectus", type=Path, default=DEFAULT_PROSPECTUS)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--out-json", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--out-md", type=Path, default=REPO_ROOT / "docs/recording_bidirectionality_prospect_manifest.md")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    base = json.loads(args.base_manifest.read_text())
    prospect_ids = load_prospect_recording_ids(args.prospectus, limit=args.limit)
    report = build_manifest(base, prospect_ids)
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text(render_markdown(report))
    print(f"wrote {args.out_json}")
    print(f"wrote {args.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
