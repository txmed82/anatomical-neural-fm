"""Build and upload IBL BrainSet HDF5 files one recording at a time.

This wrapper is intended for fragile cloud data-cache runs. Unlike the batch
builder, it uploads each successful HDF5 before moving to the next recording, so
one slow or failing OpenAlyx download does not lose earlier work when a pod
exits.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

try:
    from scripts.sync_brainset_s3 import manifest_recording_name, manifest_recording_rows
except ModuleNotFoundError:
    from sync_brainset_s3 import manifest_recording_name, manifest_recording_rows


REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data" / "brainsets" / "ibl_bwm"
ONE_CACHE_ROOT = Path.home() / "Downloads" / "ONE" / "openalyx.internationalbrainlab.org"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--filenames", nargs="*", default=None)
    parser.add_argument("--filenames-file", type=Path, default=None)
    parser.add_argument("--bucket", default="rppfvo6ifn")
    parser.add_argument("--prefix", default="brainsets/ibl_bwm")
    parser.add_argument("--datacenter", default="US-IL-1")
    parser.add_argument("--per-record-timeout", type=int, default=900)
    parser.add_argument("--report-dir", type=Path, default=Path("/tmp/ibl_incremental"))
    parser.add_argument("--clear-one-cache", action="store_true")
    parser.add_argument("--no-wheel", action="store_true")
    parser.add_argument("--trial-window-only", action="store_true")
    parser.add_argument("--window-len", type=float, default=1.0)
    return parser.parse_args()


def requested_filenames(args: argparse.Namespace) -> list[str] | None:
    names: list[str] = []
    if args.filenames:
        names.extend(args.filenames)
    if args.filenames_file:
        payload = args.filenames_file.read_text().strip()
        if payload:
            if payload.startswith("["):
                names.extend(json.loads(payload))
            else:
                names.extend(line.strip() for line in payload.splitlines() if line.strip())
    return names or None


def write_single_manifest(path: Path, row: dict) -> None:
    path.write_text(json.dumps({"recordings": [row]}, indent=2) + "\n")


def run_command(cmd: list[str], *, timeout_seconds: int | None = None) -> int:
    effective_cmd = cmd
    if timeout_seconds is not None:
        effective_cmd = ["timeout", str(timeout_seconds), *cmd]
    print("$ " + " ".join(effective_cmd), flush=True)
    return subprocess.run(effective_cmd).returncode


def clear_local_cache() -> None:
    for path in DATA_DIR.glob("*.h5"):
        path.unlink(missing_ok=True)
    if ONE_CACHE_ROOT.exists():
        shutil.rmtree(ONE_CACHE_ROOT)


def main() -> int:
    args = parse_args()
    rows = manifest_recording_rows(args.manifest)
    rows_by_name = {manifest_recording_name(row): row for row in rows}
    names = requested_filenames(args) or sorted(name for name in rows_by_name if name)
    selected = [(name, rows_by_name.get(name)) for name in names]
    missing_rows = [name for name, row in selected if row is None]
    if missing_rows:
        raise SystemExit(f"manifest does not contain requested filenames: {missing_rows}")

    args.report_dir.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    success: list[str] = []
    failed: list[dict[str, str | int]] = []
    start = time.time()
    print(f"incremental selected: {len(selected)}", flush=True)

    for index, (name, row) in enumerate(selected, 1):
        assert row is not None
        print(f"=== record {index}/{len(selected)} {name} ===", flush=True)
        single_manifest = args.report_dir / "one_recording_manifest.json"
        write_single_manifest(single_manifest, row)
        build_report = args.report_dir / f"{Path(name).stem}_build.md"
        build_cmd = [
            sys.executable,
            "scripts/build_ibl_brainset_batch.py",
            "--manifest",
            str(single_manifest),
            "--allow-partial",
            "--report",
            str(build_report),
        ]
        if args.no_wheel:
            build_cmd.append("--no-wheel")
        if args.trial_window_only:
            build_cmd.append("--trial-window-only")
        build_cmd += ["--window-len", str(args.window_len)]

        build_rc = run_command(build_cmd, timeout_seconds=args.per_record_timeout)
        print(f"build rc {build_rc} {name}", flush=True)
        if build_rc == 0:
            upload_rc = run_command([
                sys.executable,
                "scripts/sync_brainset_s3.py",
                "upload",
                "--manifest",
                str(single_manifest),
                "--bucket",
                args.bucket,
                "--prefix",
                args.prefix,
                "--datacenter",
                args.datacenter,
                "--skip-existing",
            ])
            verify_rc = run_command([
                sys.executable,
                "scripts/sync_brainset_s3.py",
                "verify-local",
                "--manifest",
                str(single_manifest),
                "--bucket",
                args.bucket,
                "--prefix",
                args.prefix,
                "--datacenter",
                args.datacenter,
                "--report",
                str(args.report_dir / f"{Path(name).stem}_verify.md"),
            ])
            print(f"upload rc {upload_rc} {name}", flush=True)
            print(f"verify rc {verify_rc} {name}", flush=True)
            if upload_rc == 0 and verify_rc == 0:
                success.append(name)
            else:
                failed.append({"filename": name, "build_rc": build_rc, "upload_rc": upload_rc, "verify_rc": verify_rc})
        else:
            failed.append({"filename": name, "build_rc": build_rc})

        if args.clear_one_cache:
            clear_local_cache()

    summary = {
        "success": success,
        "failed": failed,
        "elapsed_seconds": round(time.time() - start, 1),
    }
    (args.report_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print("INCREMENTAL_SUCCESS " + json.dumps(success), flush=True)
    print("INCREMENTAL_FAILED " + json.dumps(failed), flush=True)
    print(f"incremental elapsed seconds: {summary['elapsed_seconds']}", flush=True)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
