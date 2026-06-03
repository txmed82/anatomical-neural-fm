"""Launch the first bounded A100 pilot on RunPod.

The launcher creates a small network volume, uploads the current repo snapshot,
starts one A100 pod, and uses a timeout/self-termination guard to cap spend.
Secrets are loaded from .env and are never printed.
"""
from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError


REPO_ROOT = Path(__file__).resolve().parent.parent
REST_BASE = "https://rest.runpod.io/v1"
ARCHIVE_NAME = "anatomical-neural-fm-pilot.tar.gz"

S3_ENDPOINTS = {
    "EU-CZ-1": "https://s3api-eu-cz-1.runpod.io/",
    "EU-RO-1": "https://s3api-eu-ro-1.runpod.io/",
    "EUR-IS-1": "https://s3api-eur-is-1.runpod.io/",
    "EUR-NO-1": "https://s3api-eur-no-1.runpod.io/",
    "US-CA-2": "https://s3api-us-ca-2.runpod.io/",
    "US-GA-2": "https://s3api-us-ga-2.runpod.io/",
    "US-IL-1": "https://s3api-us-il-1.runpod.io/",
    "US-KS-2": "https://s3api-us-ks-2.runpod.io/",
    "US-MD-1": "https://s3api-us-md-1.runpod.io/",
    "US-MO-1": "https://s3api-us-mo-1.runpod.io/",
    "US-MO-2": "https://s3api-us-mo-2.runpod.io/",
    "US-NC-1": "https://s3api-us-nc-1.runpod.io/",
    "US-NC-2": "https://s3api-us-nc-2.runpod.io/",
    "US-NE-1": "https://s3api-us-ne-1.runpod.io/",
    "US-WA-1": "https://s3api-us-wa-1.runpod.io/",
}


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


def require_env(env: dict[str, str], key: str) -> str:
    value = os.environ.get(key) or env.get(key)
    if not value:
        raise SystemExit(f"Missing {key}; add it to .env or export it.")
    return value


@dataclass(frozen=True)
class RunpodConfig:
    datacenter: str
    gpu_type: str
    volume_gb: int
    container_disk_gb: int
    max_runtime_seconds: int
    image_name: str


def s3_endpoint(datacenter: str) -> str:
    try:
        return S3_ENDPOINTS[datacenter]
    except KeyError as exc:
        known = ", ".join(sorted(S3_ENDPOINTS))
        raise ValueError(f"Unsupported S3 datacenter {datacenter!r}. Known: {known}") from exc


class RunpodClient:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def request(self, method: str, path: str, body: dict[str, Any] | None = None) -> Any:
        data = None if body is None else json.dumps(body).encode("utf-8")
        req = urllib.request.Request(
            REST_BASE + path,
            data=data,
            method=method,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                payload = resp.read()
        except urllib.error.HTTPError as exc:
            message = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"RunPod {method} {path} failed: {exc.code} {message}") from exc
        if not payload:
            return None
        return json.loads(payload.decode("utf-8"))

    def create_network_volume(self, name: str, size: int, datacenter: str) -> dict[str, Any]:
        return self.request(
            "POST",
            "/networkvolumes",
            {"name": name, "size": size, "dataCenterId": datacenter},
        )

    def create_pod(self, body: dict[str, Any]) -> dict[str, Any]:
        return self.request("POST", "/pods", body)

    def get_pod(self, pod_id: str) -> dict[str, Any]:
        return self.request("GET", f"/pods/{pod_id}")

    def terminate_pod(self, pod_id: str) -> None:
        self.request("DELETE", f"/pods/{pod_id}")

    def delete_network_volume(self, volume_id: str) -> None:
        self.request("DELETE", f"/networkvolumes/{volume_id}")


def build_archive(archive_path: Path) -> None:
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "tar",
        "-czf",
        str(archive_path),
        "--exclude=.git",
        "--exclude=.venv",
        "--exclude=.env",
        "--exclude=ContextPool",
        "--exclude=runs",
        "--exclude=data/abc_atlas_cache",
        "--exclude=__pycache__",
        "--exclude=.pytest_cache",
        "--exclude=.ruff_cache",
        "--exclude=.mypy_cache",
        "-C",
        str(REPO_ROOT.parent),
        REPO_ROOT.name,
    ]
    subprocess.run(cmd, check=True)


def upload_archive(
    archive_path: Path,
    volume_id: str,
    datacenter: str,
    access_key: str,
    secret_key: str,
) -> None:
    client = boto3.client(
        "s3",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=datacenter,
        endpoint_url=s3_endpoint(datacenter),
        config=Config(retries={"max_attempts": 10, "mode": "standard"}, read_timeout=7200),
    )
    client.upload_file(str(archive_path), volume_id, ARCHIVE_NAME)


def wait_for_s3_volume(
    volume_id: str,
    datacenter: str,
    access_key: str,
    secret_key: str,
    timeout_seconds: int = 180,
) -> None:
    client = boto3.client(
        "s3",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=datacenter,
        endpoint_url=s3_endpoint(datacenter),
        config=Config(retries={"max_attempts": 3, "mode": "standard"}, connect_timeout=10, read_timeout=20),
    )
    deadline = time.time() + timeout_seconds
    last_error: Exception | None = None
    while time.time() < deadline:
        try:
            client.list_objects_v2(Bucket=volume_id, MaxKeys=1)
            return
        except ClientError as exc:
            last_error = exc
            message = str(exc)
            if "transport endpoint is not connected" not in message and "NoSuchBucket" not in message:
                raise
        except Exception as exc:
            last_error = exc
        time.sleep(10)
    raise RuntimeError(f"RunPod S3 volume {volume_id} was not ready after {timeout_seconds}s") from last_error


def build_start_script(max_runtime_seconds: int) -> str:
    run_cmd = (
        f"timeout {max_runtime_seconds} "
        "bash scripts/run_phase2_cloud_a100.sh"
    )
    return f"""set -euo pipefail
cleanup() {{
  if [ -n "${{RUNPOD_POD_ID:-}}" ] && [ -n "${{RUNPOD_API_KEY:-}}" ]; then
    python - <<'PY' || true
import os
import urllib.request

pod_id = os.environ.get("RUNPOD_POD_ID")
api_key = os.environ.get("RUNPOD_API_KEY")
if pod_id and api_key:
    req = urllib.request.Request(
        f"https://rest.runpod.io/v1/pods/{{pod_id}}",
        method="DELETE",
        headers={{"Authorization": "Bearer " + api_key}},
    )
    urllib.request.urlopen(req, timeout=30).read()
PY
  fi
}}
trap cleanup EXIT

cd /workspace
rm -rf anatomical-neural-fm
tar -xzf {shlex.quote(ARCHIVE_NAME)}
cd anatomical-neural-fm
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
export UV_LINK_MODE=copy
export WANDB_MODE=offline
uv sync --dev
uv run pytest -q
{run_cmd}
"""


def build_pod_body(
    name: str,
    volume_id: str,
    config: RunpodConfig,
    api_key: str,
) -> dict[str, Any]:
    return {
        "name": name,
        "imageName": config.image_name,
        "cloudType": "SECURE",
        "computeType": "GPU",
        "gpuTypeIds": [config.gpu_type],
        "gpuTypePriority": "availability",
        "gpuCount": 1,
        "dataCenterIds": [config.datacenter],
        "dataCenterPriority": "custom",
        "containerDiskInGb": config.container_disk_gb,
        "volumeInGb": 0,
        "volumeMountPath": "/workspace",
        "networkVolumeId": volume_id,
        "ports": [],
        "interruptible": False,
        "env": {
            "RUNPOD_API_KEY": api_key,
            "PILOT_MAX_RUNTIME_SECONDS": str(config.max_runtime_seconds),
        },
        "dockerStartCmd": ["bash", "-lc", build_start_script(config.max_runtime_seconds)],
    }


def summarize_pod(pod: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": pod.get("id"),
        "name": pod.get("name"),
        "desiredStatus": pod.get("desiredStatus"),
        "costPerHr": pod.get("costPerHr"),
        "machineId": pod.get("machineId"),
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--datacenter", default="US-MO-1")
    p.add_argument("--gpu-type", default="NVIDIA A100 80GB PCIe")
    p.add_argument("--volume-gb", type=int, default=40)
    p.add_argument("--container-disk-gb", type=int, default=30)
    p.add_argument("--max-runtime-seconds", type=int, default=10_800)
    p.add_argument("--image-name", default="runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04")
    p.add_argument("--name-prefix", default="anfm-a100-pilot")
    p.add_argument("--archive-path", type=Path, default=Path("/tmp") / ARCHIVE_NAME)
    p.add_argument("--skip-archive", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--poll", action="store_true")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    env = load_dotenv(REPO_ROOT / ".env")
    runpod_key = require_env(env, "RUNPOD_API_KEY")
    s3_access_key = require_env(env, "RUNPOD_S3_ACCESS_KEY")
    s3_secret_key = require_env(env, "RUNPOD_S3_SECRET_KEY")
    config = RunpodConfig(
        datacenter=args.datacenter,
        gpu_type=args.gpu_type,
        volume_gb=args.volume_gb,
        container_disk_gb=args.container_disk_gb,
        max_runtime_seconds=args.max_runtime_seconds,
        image_name=args.image_name,
    )
    name = f"{args.name_prefix}-{time.strftime('%Y%m%d-%H%M%S')}"

    if args.dry_run:
        body = build_pod_body(name, "dry-run-volume", config, "<redacted>")
        print(json.dumps({k: v for k, v in body.items() if k != "env"}, indent=2))
        return 0

    if not args.skip_archive:
        print(f"Building archive: {args.archive_path}", flush=True)
        build_archive(args.archive_path)
        print(f"Archive size: {args.archive_path.stat().st_size / 1024**3:.2f} GiB", flush=True)

    client = RunpodClient(runpod_key)
    print(f"Creating {config.volume_gb}GB network volume in {config.datacenter}", flush=True)
    volume = client.create_network_volume(name=name, size=config.volume_gb, datacenter=config.datacenter)
    volume_id = volume["id"]
    print(f"Created network volume: {volume_id}", flush=True)

    print("Waiting for RunPod S3 volume readiness", flush=True)
    try:
        wait_for_s3_volume(volume_id, config.datacenter, s3_access_key, s3_secret_key)
    except Exception:
        print("S3 readiness failed; deleting the newly created network volume.", flush=True)
        client.delete_network_volume(volume_id)
        raise

    print("Uploading archive to RunPod network volume", flush=True)
    try:
        upload_archive(args.archive_path, volume_id, config.datacenter, s3_access_key, s3_secret_key)
    except Exception:
        print("Upload failed; deleting the newly created network volume.", flush=True)
        client.delete_network_volume(volume_id)
        raise
    print("Upload complete", flush=True)

    print(f"Creating A100 pod ({config.gpu_type})", flush=True)
    try:
        pod = client.create_pod(build_pod_body(name, volume_id, config, runpod_key))
    except Exception:
        print("Pod creation failed; deleting the newly created network volume.", flush=True)
        client.delete_network_volume(volume_id)
        raise
    print(json.dumps(summarize_pod(pod), indent=2))

    if args.poll:
        pod_id = pod["id"]
        print("Polling pod status; the pod also has a self-termination trap.")
        while True:
            time.sleep(30)
            try:
                current = client.get_pod(pod_id)
            except RuntimeError as exc:
                print(str(exc))
                break
            print(json.dumps(summarize_pod(current), indent=2))
            if current.get("desiredStatus") in {"EXITED", "TERMINATED"}:
                break
    return 0


if __name__ == "__main__":
    sys.exit(main())
