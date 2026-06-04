"""Sync built BrainSet HDF5 files to/from an S3-compatible cache.

This is meant for sharded cloud data builds. Each pod can download any
previously built recordings, build its shard, upload the resulting `.h5` files,
and exit without losing work when the container is deleted.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Iterable

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

try:
    from scripts.runpod_first_a100 import S3_ENDPOINTS
except ModuleNotFoundError:
    from runpod_first_a100 import S3_ENDPOINTS


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATA_DIR = REPO_ROOT / "data" / "brainsets" / "ibl_bwm"
DEFAULT_PREFIX = "brainsets/ibl_bwm"


def load_dotenv(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("\"'")
    return values


def env_value(env: dict[str, str], *keys: str) -> str | None:
    for key in keys:
        value = os.environ.get(key) or env.get(key)
        if value:
            return value
    return None


def required(value: str | None, label: str) -> str:
    if not value:
        raise SystemExit(f"Missing {label}; pass an argument or add it to .env.")
    return value


def endpoint_from_args(args: argparse.Namespace, env: dict[str, str]) -> str:
    explicit = args.endpoint_url or env_value(env, "BRAINSET_S3_ENDPOINT", "RUNPOD_S3_ENDPOINT")
    if explicit:
        return explicit
    datacenter = args.datacenter or env_value(env, "BRAINSET_S3_DATACENTER", "RUNPOD_DATACENTER")
    if datacenter:
        try:
            return S3_ENDPOINTS[datacenter]
        except KeyError as exc:
            known = ", ".join(sorted(S3_ENDPOINTS))
            raise SystemExit(f"Unsupported S3 datacenter {datacenter!r}. Known: {known}") from exc
    raise SystemExit("Missing S3 endpoint; pass --endpoint-url or --datacenter.")


def region_from_args(args: argparse.Namespace, env: dict[str, str]) -> str:
    datacenter = args.datacenter or env_value(env, "BRAINSET_S3_DATACENTER", "RUNPOD_DATACENTER")
    return datacenter.lower() if datacenter else "auto"


def s3_client(args: argparse.Namespace):
    env = load_dotenv(REPO_ROOT / ".env")
    access_key = required(
        args.access_key or env_value(env, "BRAINSET_S3_ACCESS_KEY", "RUNPOD_S3_ACCESS_KEY"),
        "S3 access key",
    )
    secret_key = required(
        args.secret_key or env_value(env, "BRAINSET_S3_SECRET_KEY", "RUNPOD_S3_SECRET_KEY"),
        "S3 secret key",
    )
    endpoint_url = endpoint_from_args(args, env)
    return boto3.client(
        "s3",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region_from_args(args, env),
        endpoint_url=endpoint_url,
        config=Config(retries={"max_attempts": 5, "mode": "standard"}, read_timeout=7200),
    )


def bucket_from_args(args: argparse.Namespace) -> str:
    env = load_dotenv(REPO_ROOT / ".env")
    return required(
        args.bucket or env_value(env, "BRAINSET_S3_BUCKET", "RUNPOD_S3_BUCKET", "RUNPOD_NETWORK_VOLUME_ID"),
        "S3 bucket",
    )


def manifest_recording_names(path: Path) -> set[str]:
    payload = json.loads(path.read_text())
    rows = payload["recordings"] if isinstance(payload, dict) else payload
    names: set[str] = set()
    for row in rows:
        eid = row.get("session_id") or row.get("eid") or row.get("session")
        probe = row.get("probe_name") or row.get("probe") or row.get("name")
        if eid and probe:
            names.add(f"{eid}_{probe}.h5")
    return names


def local_h5_files(data_dir: Path, names: set[str] | None) -> list[Path]:
    files = sorted(data_dir.glob("*.h5"))
    if names is None:
        return files
    return [path for path in files if path.name in names]


def s3_key(prefix: str, filename: str) -> str:
    clean = prefix.strip("/")
    return f"{clean}/{filename}" if clean else filename


def upload_files(client, *, bucket: str, prefix: str, files: Iterable[Path]) -> int:
    count = 0
    for path in files:
        key = s3_key(prefix, path.name)
        print(f"upload {path} -> s3://{bucket}/{key}", flush=True)
        client.upload_file(str(path), bucket, key)
        count += 1
    return count


def upload_log_file(client, *, bucket: str, prefix: str, local_path: Path, key: str) -> int:
    if not local_path.exists():
        raise SystemExit(f"Missing log file: {local_path}")
    remote_key = s3_key(prefix, key)
    print(f"upload {local_path} -> s3://{bucket}/{remote_key}", flush=True)
    client.upload_file(str(local_path), bucket, remote_key)
    return 1


def iter_remote_h5_keys(client, *, bucket: str, prefix: str):
    token = None
    clean_prefix = prefix.strip("/")
    list_prefix = f"{clean_prefix}/" if clean_prefix else ""
    while True:
        kwargs = {"Bucket": bucket, "Prefix": list_prefix}
        if token:
            kwargs["ContinuationToken"] = token
        response = client.list_objects_v2(**kwargs)
        for obj in response.get("Contents", []):
            key = obj["Key"]
            if key.endswith(".h5"):
                yield key
        if not response.get("IsTruncated"):
            return
        token = response.get("NextContinuationToken")


def download_files(client, *, bucket: str, prefix: str, data_dir: Path, names: set[str] | None) -> int:
    data_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    for key in iter_remote_h5_keys(client, bucket=bucket, prefix=prefix):
        filename = Path(key).name
        if names is not None and filename not in names:
            continue
        out = data_dir / filename
        if out.exists():
            print(f"skip exists {out}", flush=True)
            continue
        print(f"download s3://{bucket}/{key} -> {out}", flush=True)
        client.download_file(bucket, key, str(out))
        count += 1
    return count


def remote_h5_filenames(client, *, bucket: str, prefix: str) -> set[str]:
    return {Path(key).name for key in iter_remote_h5_keys(client, bucket=bucket, prefix=prefix)}


def cache_audit_rows(expected: set[str], present: set[str]) -> tuple[list[str], list[str]]:
    matched = sorted(expected & present)
    missing = sorted(expected - present)
    return matched, missing


def verify_local_cache_rows(local_files: Iterable[Path], present: set[str]) -> tuple[list[str], list[str]]:
    expected = {path.name for path in local_files}
    return cache_audit_rows(expected, present)


def write_audit_report(
    path: Path,
    *,
    manifest: Path,
    bucket: str,
    prefix: str,
    matched: list[str],
    missing: list[str],
) -> None:
    total = len(matched) + len(missing)
    pct = (len(matched) / total * 100.0) if total else 0.0
    lines = [
        "# BrainSet S3 Cache Audit",
        "",
        f"Manifest: `{manifest}`",
        f"Cache: `s3://{bucket}/{prefix.strip('/')}`",
        f"Present: {len(matched)}/{total} ({pct:.1f}%)",
        "",
        "## Missing",
        "",
    ]
    if missing:
        lines += ["| filename |", "|---|"]
        lines += [f"| `{name}` |" for name in missing]
    else:
        lines.append("none")
    lines += [
        "",
        "## Present",
        "",
    ]
    if matched:
        lines += ["| filename |", "|---|"]
        lines += [f"| `{name}` |" for name in matched]
    else:
        lines.append("none")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("command", choices=["upload", "download", "list", "audit", "verify-local", "upload-log"])
    p.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    p.add_argument("--manifest", type=Path, default=None,
                   help="Optional manifest used to filter local/remote HDF5 filenames.")
    p.add_argument("--bucket", default=None)
    p.add_argument("--prefix", default=DEFAULT_PREFIX)
    p.add_argument("--local-path", type=Path, default=None,
                   help="Local file to upload for the upload-log command.")
    p.add_argument("--key", default=None,
                   help="Remote key, relative to --prefix, for the upload-log command.")
    p.add_argument("--endpoint-url", default=None)
    p.add_argument("--datacenter", default=None)
    p.add_argument("--access-key", default=None)
    p.add_argument("--secret-key", default=None)
    p.add_argument("--report", type=Path, default=None,
                   help="Optional markdown report path for the audit command.")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    names = manifest_recording_names(args.manifest) if args.manifest else None
    client = s3_client(args)
    bucket = bucket_from_args(args)
    try:
        if args.command == "upload":
            count = upload_files(
                client,
                bucket=bucket,
                prefix=args.prefix,
                files=local_h5_files(args.data_dir, names),
            )
        elif args.command == "upload-log":
            if args.local_path is None:
                raise SystemExit("upload-log requires --local-path")
            if not args.key:
                raise SystemExit("upload-log requires --key")
            count = upload_log_file(
                client,
                bucket=bucket,
                prefix=args.prefix,
                local_path=args.local_path,
                key=args.key,
            )
        elif args.command == "download":
            count = download_files(
                client,
                bucket=bucket,
                prefix=args.prefix,
                data_dir=args.data_dir,
                names=names,
            )
        elif args.command == "list":
            count = 0
            for key in iter_remote_h5_keys(client, bucket=bucket, prefix=args.prefix):
                if names is None or Path(key).name in names:
                    print(key)
                    count += 1
        elif args.command == "audit":
            if args.manifest is None:
                raise SystemExit("audit requires --manifest")
            expected = manifest_recording_names(args.manifest)
            present = remote_h5_filenames(client, bucket=bucket, prefix=args.prefix)
            matched, missing = cache_audit_rows(expected, present)
            count = len(matched)
            total = len(expected)
            pct = (count / total * 100.0) if total else 0.0
            print(f"present: {count}/{total} ({pct:.1f}%)")
            if missing:
                print("missing:")
                for name in missing:
                    print(f"  {name}")
            if args.report is not None:
                write_audit_report(
                    args.report,
                    manifest=args.manifest,
                    bucket=bucket,
                    prefix=args.prefix,
                    matched=matched,
                    missing=missing,
                )
                print(f"wrote {args.report}")
        else:
            local_files = local_h5_files(args.data_dir, names)
            present = remote_h5_filenames(client, bucket=bucket, prefix=args.prefix)
            matched, missing = verify_local_cache_rows(local_files, present)
            count = len(matched)
            total = len(matched) + len(missing)
            pct = (count / total * 100.0) if total else 0.0
            print(f"local files present remotely: {count}/{total} ({pct:.1f}%)")
            if missing:
                print("missing remote copies:")
                for name in missing:
                    print(f"  {name}")
            if args.report is not None:
                manifest = args.manifest if args.manifest is not None else Path("<all local h5>")
                write_audit_report(
                    args.report,
                    manifest=manifest,
                    bucket=bucket,
                    prefix=args.prefix,
                    matched=matched,
                    missing=missing,
                )
                print(f"wrote {args.report}")
            if missing:
                return 1
    except ClientError as exc:
        print(f"S3 sync failed: {exc}", file=sys.stderr)
        return 1
    print(f"{args.command} count: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
