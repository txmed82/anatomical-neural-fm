"""Batch builder: list BWM insertions and build an HDF5 per (eid, probe).

Usage:
    uv run python scripts/build_ibl_brainset_batch.py [N]
    uv run python scripts/build_ibl_brainset_batch.py --manifest manifests/ibl_bwm_phase4.json

Defaults to N=3. Skips any HDF5 that already exists. Sequential for first cut.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import traceback
from pathlib import Path
from typing import Sequence

# import the single-session builder
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from build_ibl_brainset import (  # noqa: E402
    OPEN_ALYX, PUBLIC_PASS, PUBLIC_USER, build_recording,
)
from one.api import ONE  # noqa: E402

OUT_DIR = Path("data/brainsets/ibl_bwm")
BWM_PROJECT = "ibl_neuropixel_brainwide_01"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("target", nargs="?", type=int, default=3)
    p.add_argument("--manifest", type=Path, default=None,
                   help="JSON manifest with recordings entries containing session_id/eid and probe_name/name.")
    p.add_argument("--num-shards", type=int, default=1,
                   help="Split the insertion list into this many deterministic contiguous shards.")
    p.add_argument("--shard-index", type=int, default=0,
                   help="Zero-based shard index to build when --num-shards > 1.")
    p.add_argument("--max-builds", type=int, default=None,
                   help="Optional cap on recordings to build from the selected shard.")
    p.add_argument("--allow-partial", action="store_true",
                   help="Exit successfully if at least one selected recording is available.")
    p.add_argument("--report", type=Path, default=None,
                   help="Optional markdown report summarizing selected, built, and failed recordings.")
    p.add_argument("--no-wheel", action="store_true",
                   help="Omit wheel samples for training-only choice/stimulus decoding caches.")
    p.add_argument("--trial-window-only", action="store_true",
                   help="Keep only spikes inside trial-aligned windows used by scripts/train.py.")
    p.add_argument("--window-len", type=float, default=1.0,
                   help="Trial-window spike retention length for --trial-window-only.")
    return p.parse_args()


def _manifest_insertions(path: Path) -> list[dict]:
    payload = json.loads(path.read_text())
    rows = payload["recordings"] if isinstance(payload, dict) else payload
    out = []
    for row in rows:
        eid = row.get("session_id") or row.get("eid") or row.get("session")
        probe = row.get("probe_name") or row.get("probe") or row.get("name")
        if not eid or not probe:
            raise ValueError(f"bad manifest row missing session/probe: {row}")
        out.append({"session": eid, "name": probe})
    return out


def select_shard(insertions: Sequence[dict], *, num_shards: int, shard_index: int) -> list[dict]:
    if num_shards < 1:
        raise ValueError("--num-shards must be >= 1")
    if shard_index < 0 or shard_index >= num_shards:
        raise ValueError("--shard-index must satisfy 0 <= shard_index < --num-shards")
    n = len(insertions)
    start = (n * shard_index) // num_shards
    end = (n * (shard_index + 1)) // num_shards
    return list(insertions[start:end])


def write_report(
    path: Path,
    *,
    manifest: Path | None,
    selected: Sequence[dict],
    built_rows: Sequence[dict],
    failed_rows: Sequence[dict],
    skipped_existing: Sequence[dict],
    elapsed_seconds: float,
    num_shards: int,
    shard_index: int,
    include_wheel: bool,
    trial_window_only: bool,
    window_len: float,
) -> None:
    lines = [
        "# IBL BrainSet Batch Build",
        "",
        f"Manifest: `{manifest}`" if manifest is not None else "Manifest: Alyx selection",
        f"Shard: {shard_index + 1}/{num_shards}",
        f"Selected recordings: {len(selected)}",
        f"Available recordings: {len(built_rows)}",
        f"Skipped existing: {len(skipped_existing)}",
        f"Failures: {len(failed_rows)}",
        f"Elapsed seconds: {elapsed_seconds:.0f}",
        f"Include wheel: `{include_wheel}`",
        f"Trial-window-only spikes: `{trial_window_only}`",
        f"Window length: `{window_len}`",
        "",
        "## Available",
        "",
        "| session | probe | path |",
        "|---|---|---|",
    ]
    for row in built_rows:
        lines.append(f"| {row['session']} | {row['name']} | `{row['path']}` |")
    if failed_rows:
        lines += [
            "",
            "## Failures",
            "",
            "| session | probe | error |",
            "|---|---|---|",
        ]
        for row in failed_rows:
            lines.append(f"| {row['session']} | {row['name']} | {row['error']} |")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def main() -> int:
    args = parse_args()
    target = args.target
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    ONE.setup(base_url=OPEN_ALYX, silent=True)
    one = ONE(base_url=OPEN_ALYX, username=PUBLIC_USER, password=PUBLIC_PASS)

    if args.manifest is not None:
        insertions = _manifest_insertions(args.manifest)
        target = len(insertions)
        print(f"Loaded fixed manifest {args.manifest} ({target} recordings)")
    else:
        print(f"Listing BWM probe insertions (target {target})...")
        # Pull more than `target` so we have headroom for failures
        insertions = one.alyx.rest(
            "insertions", "list",
            project=BWM_PROJECT,
            limit=target * 4,
        )
        print(f"  got {len(insertions)} insertions")

    insertions = select_shard(
        insertions,
        num_shards=args.num_shards,
        shard_index=args.shard_index,
    )
    if args.max_builds is not None:
        insertions = insertions[:args.max_builds]
    target = len(insertions)
    print(
        f"Selected shard {args.shard_index + 1}/{args.num_shards} "
        f"({target} recordings)"
    )

    built = 0
    attempted = 0
    built_rows: list[dict] = []
    skipped_existing: list[dict] = []
    failed_rows: list[dict] = []
    start = time.time()

    for ins in insertions:
        if built >= target:
            break
        eid = ins["session"]
        probe = ins["name"]
        out_path = OUT_DIR / f"{eid}_{probe}.h5"

        if out_path.exists():
            print(f"  [{built + 1}/{target}] skip (exists): {eid} {probe}")
            built += 1
            row = {"session": eid, "name": probe, "path": str(out_path)}
            built_rows.append(row)
            skipped_existing.append(row)
            continue

        attempted += 1
        print(f"\n=== [{attempted}] Building {eid} probe={probe} ===")
        try:
            built_path = build_recording(
                eid,
                probe,
                OUT_DIR,
                include_wheel=not args.no_wheel,
                trial_window_only=args.trial_window_only,
                window_len=args.window_len,
            )
            built += 1
            built_rows.append({"session": eid, "name": probe, "path": str(built_path)})
        except Exception:
            tb = traceback.format_exc().splitlines()[-1]
            print(f"  FAILED: {tb}")
            failed_rows.append({"session": eid, "name": probe, "error": tb})

    dt = time.time() - start
    print(f"\nBuilt {built}/{target} in {dt:.0f}s "
          f"({attempted} attempted, {len(failed_rows)} failed)")
    if failed_rows:
        print("Failures:")
        for row in failed_rows:
            print(f"  {row['session']} {row['name']}: {row['error']}")
    print(f"\nFiles in {OUT_DIR}:")
    for p in sorted(OUT_DIR.glob("*.h5")):
        size_mb = p.stat().st_size / 1024 / 1024
        print(f"  {size_mb:>6.1f} MB  {p.name}")
    if args.report is not None:
        write_report(
            args.report,
            manifest=args.manifest,
            selected=insertions,
            built_rows=built_rows,
            failed_rows=failed_rows,
            skipped_existing=skipped_existing,
            elapsed_seconds=dt,
            num_shards=args.num_shards,
            shard_index=args.shard_index,
            include_wheel=not args.no_wheel,
            trial_window_only=args.trial_window_only,
            window_len=args.window_len,
        )
        print(f"\nWrote report {args.report}")
    if built == target:
        return 0
    if args.allow_partial and built > 0:
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
