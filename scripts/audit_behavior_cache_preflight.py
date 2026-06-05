"""Preflight the next behavior-cache or external-target branch."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import h5py

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MANIFEST = REPO_ROOT / "manifests/ibl_bwm_region_matched_candidates_s3_present_support80_hdf5_scored.json"
DEFAULT_DATA_DIR = REPO_ROOT / "data/brainsets/ibl_bwm"
DEFAULT_REQUIRED_STREAMS = ("wheel",)


def manifest_rows(path: Path) -> list[dict]:
    payload = json.loads(path.read_text())
    rows = payload["recordings"] if isinstance(payload, dict) else payload
    return list(rows)


def recording_name(row: dict) -> str:
    eid = row.get("session_id") or row.get("eid") or row.get("session")
    probe = row.get("probe_name") or row.get("probe") or row.get("name")
    if not eid or not probe:
        raise ValueError(f"manifest row lacks session/probe keys: {row}")
    return f"{eid}_{probe}.h5"


def h5_streams(path: Path) -> set[str]:
    if not path.exists():
        return set()
    with h5py.File(path, "r") as h5:
        return set(h5.keys())


def audit_cache(
    *,
    data_dir: Path,
    manifest: Path,
    required_streams: tuple[str, ...],
) -> dict:
    rows = manifest_rows(manifest)
    recording_rows = []
    stream_counts = {stream: 0 for stream in required_streams}
    present = 0
    missing_files = []
    for row in rows:
        name = recording_name(row)
        path = data_dir / name
        exists = path.exists()
        streams = h5_streams(path)
        if exists:
            present += 1
        else:
            missing_files.append(name)
        missing_streams = [stream for stream in required_streams if stream not in streams]
        for stream in required_streams:
            if stream in streams:
                stream_counts[stream] += 1
        recording_rows.append({
            "recording": name[:-3],
            "path": str(path),
            "exists": exists,
            "streams": sorted(streams),
            "missing_streams": missing_streams,
            "needs_behavior_rebuild": bool(missing_streams),
        })
    needs_rebuild = [row for row in recording_rows if row["needs_behavior_rebuild"]]
    return {
        "manifest": str(manifest),
        "data_dir": str(data_dir),
        "required_streams": list(required_streams),
        "summary": {
            "n_manifest_recordings": len(rows),
            "n_present_files": present,
            "n_missing_files": len(missing_files),
            "stream_counts": stream_counts,
            "n_recordings_with_all_required_streams": len(rows) - len(needs_rebuild),
            "n_recordings_needing_behavior_rebuild": len(needs_rebuild),
            "decision": "behavior_cache_rebuild_required" if needs_rebuild else "behavior_cache_ready",
            "next_gate": (
                "After building a behavior-inclusive cache, define the behavior target "
                "and rerun the local true-vs-shuffle, total-baseline, global target, "
                "and same-recording bidirectional gate before any GPU training."
            ),
        },
        "missing_files": missing_files,
        "recording_rows": recording_rows,
    }


def build_commands(manifest: Path, *, num_shards: int, out_dir: Path) -> list[str]:
    manifest_text = _display_path(manifest)
    out_dir_text = _display_path(out_dir)
    commands = []
    for shard in range(num_shards):
        commands.append(
            "uv run python scripts/build_ibl_brainset_batch.py "
            f"--manifest {manifest_text} "
            f"--num-shards {num_shards} "
            f"--shard-index {shard} "
            f"--report docs/behavior_cache_build_shard{shard:02d}.md "
            "--trial-window-only --window-len 1.0 "
            f"# writes {out_dir_text}"
        )
    return commands


def _display_path(path: Path) -> str:
    path = path.expanduser()
    if not path.is_absolute():
        return str(path)
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def render_markdown(report: dict, commands: list[str]) -> str:
    summary = report["summary"]
    stream_counts = ", ".join(
        f"{stream}={count}/{summary['n_manifest_recordings']}"
        for stream, count in summary["stream_counts"].items()
    )
    lines = [
        "# Behavior Cache Preflight",
        "",
        "No-spend preflight for the next branch after cached trial targets failed.",
        "",
        f"- manifest recordings: `{summary['n_manifest_recordings']}`",
        f"- present files: `{summary['n_present_files']}`",
        f"- missing files: `{summary['n_missing_files']}`",
        f"- required stream coverage: `{stream_counts}`",
        f"- recordings needing behavior rebuild: `{summary['n_recordings_needing_behavior_rebuild']}`",
        f"- decision: `{summary['decision']}`",
        "",
        "## Build Plan",
        "",
        (
            "The current compact cache was built for trial-window decoding. Rebuild "
            "without `--no-wheel` so `scripts/build_ibl_brainset.py` stores the "
            "`wheel` stream from Open Alyx."
        ),
        "",
        "```bash",
    ]
    lines.extend(commands)
    lines += [
        "```",
        "",
        "## Target Gate After Rebuild",
        "",
        summary["next_gate"],
        "",
        "Candidate behavior targets to test first:",
        "",
        "- wheel movement onset versus quiescence in trial-aligned windows",
        "- high versus low absolute wheel velocity after stimulus onset",
        "- signed wheel velocity consistent with left/right action",
        "",
        "## First Rows Needing Rebuild",
        "",
        "| recording | missing streams |",
        "|---|---|",
    ]
    rebuild_rows = [row for row in report["recording_rows"] if row["needs_behavior_rebuild"]]
    for row in rebuild_rows[:12]:
        missing = ", ".join(row["missing_streams"]) or "none"
        lines.append(f"| {row['recording']} | {missing} |")
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--required-stream", nargs="*", default=list(DEFAULT_REQUIRED_STREAMS))
    parser.add_argument("--num-shards", type=int, default=4)
    parser.add_argument("--out-json", type=Path, default=REPO_ROOT / "docs/behavior_cache_preflight.json")
    parser.add_argument("--out-md", type=Path, default=REPO_ROOT / "docs/behavior_cache_preflight.md")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    required_streams = tuple(args.required_stream)
    report = audit_cache(data_dir=args.data_dir, manifest=args.manifest, required_streams=required_streams)
    commands = build_commands(args.manifest, num_shards=args.num_shards, out_dir=args.data_dir)
    report["build_commands"] = commands
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text(render_markdown(report, commands))
    print(f"wrote {args.out_json}")
    print(f"wrote {args.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
