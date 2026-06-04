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

    built = 0
    attempted = 0
    failures: list[tuple[str, str, str]] = []
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
            continue

        attempted += 1
        print(f"\n=== [{attempted}] Building {eid} probe={probe} ===")
        try:
            build_recording(eid, probe, OUT_DIR)
            built += 1
        except Exception:
            tb = traceback.format_exc().splitlines()[-1]
            print(f"  FAILED: {tb}")
            failures.append((eid, probe, tb))

    dt = time.time() - start
    print(f"\nBuilt {built}/{target} in {dt:.0f}s "
          f"({attempted} attempted, {len(failures)} failed)")
    if failures:
        print("Failures:")
        for eid, probe, err in failures:
            print(f"  {eid} {probe}: {err}")
    print(f"\nFiles in {OUT_DIR}:")
    for p in sorted(OUT_DIR.glob("*.h5")):
        size_mb = p.stat().st_size / 1024 / 1024
        print(f"  {size_mb:>6.1f} MB  {p.name}")
    return 0 if built == target else 1


if __name__ == "__main__":
    sys.exit(main())
