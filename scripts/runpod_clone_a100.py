"""Launch the phase 3-5 A100 pilot without RunPod network-volume S3.

This path is for accounts where network-volume S3 is unavailable or flaky. The
pod clones the pushed branch, rebuilds public data on the pod, runs the bounded
cloud sweep, commits summaries back to the branch, and self-terminates.
"""
from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from scripts.runpod_first_a100 import REPO_ROOT, RunpodClient, load_dotenv, require_env
except ModuleNotFoundError:
    from runpod_first_a100 import REPO_ROOT, RunpodClient, load_dotenv, require_env


@dataclass(frozen=True)
class ClonePilotConfig:
    branch: str
    repo_url: str
    datacenter: str
    gpu_type: str
    image_name: str
    container_disk_gb: int
    volume_gb: int
    max_runtime_seconds: int
    build_recordings: int
    max_steps: int
    eval_batches: int
    manifest_path: str
    seeds: str
    target_mode: str


def current_branch() -> str:
    return subprocess.check_output(["git", "branch", "--show-current"], text=True).strip()


def github_token() -> str:
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        return token
    try:
        return subprocess.check_output(["gh", "auth", "token"], text=True).strip()
    except Exception as exc:
        raise SystemExit("Missing GITHUB_TOKEN and `gh auth token` failed.") from exc


def authenticated_repo_url(repo_url: str) -> str:
    if not repo_url.startswith("https://github.com/"):
        raise ValueError("Only https://github.com/... repo URLs are supported")
    return repo_url.replace("https://github.com/", "https://x-access-token:${GITHUB_TOKEN}@github.com/", 1)


def build_start_script(config: ClonePilotConfig) -> str:
    repo_dir = Path(config.repo_url).stem.removesuffix(".git")
    clone_url = authenticated_repo_url(config.repo_url)
    branch = shlex.quote(config.branch)
    branch_raw = config.branch
    run_timeout = shlex.quote(str(config.max_runtime_seconds))
    build_recordings = shlex.quote(str(config.build_recordings))
    max_steps = shlex.quote(str(config.max_steps))
    eval_batches = shlex.quote(str(config.eval_batches))
    manifest_path = shlex.quote(config.manifest_path)
    seeds = shlex.quote(config.seeds)
    target_mode = shlex.quote(config.target_mode)
    repo_dir_q = shlex.quote(repo_dir)
    return f"""set -uo pipefail
LOG_PATH=/tmp/runpod_phase3_5.log
REPO_DIR=/workspace/{repo_dir_q}
touch "$LOG_PATH"
exec > >(tee -a "$LOG_PATH") 2>&1

push_artifacts() {{
  status="$1"
  if [ -d "$REPO_DIR/.git" ]; then
    cd "$REPO_DIR"
    mkdir -p docs
    cp "$LOG_PATH" docs/cloud_phase3_5_runpod.log || true
    cat > docs/cloud_phase3_5_results.md <<EOF
# Cloud Phase 3-5 Results

Date: $(date -u +"%Y-%m-%dT%H:%M:%SZ")

RunPod target: A100 pilot.

Exit status: $status

Configuration:

- branch: {branch_raw}
- build recordings: {config.build_recordings}
- max steps: {config.max_steps}
- eval batches: {config.eval_batches}
- target mode: {config.target_mode}
- max runtime seconds: {config.max_runtime_seconds}
- output root: \`runs/phase2_cloud_a100\`

## Within-Animal Summary

EOF
    cat runs/phase2_cloud_a100/within_summary.md >> docs/cloud_phase3_5_results.md 2>/dev/null || true
    cat >> docs/cloud_phase3_5_results.md <<EOF

## Cross-Animal Summary

EOF
    cat runs/phase2_cloud_a100/cross_summary.md >> docs/cloud_phase3_5_results.md 2>/dev/null || true

    git add docs/cloud_phase3_5_results.md docs/cloud_phase3_5_runpod.log manifests/ibl_bwm.local.json 2>/dev/null || true
    git commit -m "Add cloud phase 3-5 pilot results" || true
    git push origin HEAD:{branch_raw} || true
  fi
}}

cleanup() {{
  status="$?"
  push_artifacts "$status" || true
  if [ -n "${{RUNPOD_POD_ID:-}}" ] && [ -n "${{RUNPOD_API_KEY:-}}" ]; then
    python3 - <<'PY' || true
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

set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y --no-install-recommends git curl ca-certificates

cd /workspace
rm -rf {repo_dir_q}
git clone --branch {branch} --single-branch "{clone_url}"
cd {repo_dir_q}
git config user.name "RunPod Pilot"
git config user.email "runpod-pilot@example.invalid"

curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
export UV_LINK_MODE=copy
export WANDB_MODE=offline

cat > /tmp/run_phase3_5_body.sh <<'RUNSCRIPT'
  set -euo pipefail
  echo "=== syncing environment ==="
  uv sync --dev
  echo "=== running local verification ==="
  uv run pytest -q
  uv run python scripts/00_ibl_smoke_test.py
  uv run python scripts/build_cell_type_priors.py
  if [ ! -f {manifest_path} ]; then
    uv run python scripts/select_ibl_manifest.py --target {build_recordings} --out {manifest_path}
  fi
  echo "=== building BrainSet data ==="
  uv run python scripts/build_ibl_brainset_batch.py --manifest {manifest_path}
  uv run python scripts/write_dataset_manifest.py
  echo "=== running phase 3-5 sweep ==="
  export SEEDS={seeds}
  export MAX_STEPS={max_steps}
  export EVAL_BATCHES={eval_batches}
  export TARGET_MODE={target_mode}
  bash scripts/run_phase2_cloud_a100.sh
RUNSCRIPT
timeout {run_timeout} bash /tmp/run_phase3_5_body.sh
"""


def build_pod_body(name: str, config: ClonePilotConfig, runpod_key: str, github_key: str) -> dict[str, Any]:
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
        "volumeInGb": config.volume_gb,
        "volumeMountPath": "/workspace",
        "ports": [],
        "interruptible": False,
        "env": {
            "RUNPOD_API_KEY": runpod_key,
            "GITHUB_TOKEN": github_key,
        },
        "dockerStartCmd": ["bash", "-lc", build_start_script(config)],
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
    p.add_argument("--branch", default=current_branch())
    p.add_argument("--repo-url", default="https://github.com/txmed82/anatomical-neural-fm.git")
    p.add_argument("--datacenter", default="US-MO-1")
    p.add_argument("--gpu-type", default="NVIDIA A100 80GB PCIe")
    p.add_argument("--image-name", default="runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04")
    p.add_argument("--container-disk-gb", type=int, default=80)
    p.add_argument("--volume-gb", type=int, default=0)
    p.add_argument("--max-runtime-seconds", type=int, default=10_800)
    p.add_argument("--build-recordings", type=int, default=6)
    p.add_argument("--max-steps", type=int, default=600)
    p.add_argument("--eval-batches", type=int, default=50)
    p.add_argument("--manifest-path", default="manifests/ibl_bwm_phase4.json")
    p.add_argument("--seeds", default="0 1 2")
    p.add_argument("--target-mode", default="choice", choices=["choice", "stimulus_side"])
    p.add_argument("--name-prefix", default="anfm-a100-clone-pilot")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--poll", action="store_true")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    config = ClonePilotConfig(
        branch=args.branch,
        repo_url=args.repo_url,
        datacenter=args.datacenter,
        gpu_type=args.gpu_type,
        image_name=args.image_name,
        container_disk_gb=args.container_disk_gb,
        volume_gb=args.volume_gb,
        max_runtime_seconds=args.max_runtime_seconds,
        build_recordings=args.build_recordings,
        max_steps=args.max_steps,
        eval_batches=args.eval_batches,
        manifest_path=args.manifest_path,
        seeds=args.seeds,
        target_mode=args.target_mode,
    )
    env = load_dotenv(REPO_ROOT / ".env")
    runpod_key = require_env(env, "RUNPOD_API_KEY")
    gh_key = github_token()
    name = f"{args.name_prefix}-{time.strftime('%Y%m%d-%H%M%S')}"
    body = build_pod_body(name, config, runpod_key, gh_key)
    if args.dry_run:
        safe_body = {k: v for k, v in body.items() if k != "env"}
        print(json.dumps(safe_body, indent=2))
        return 0

    client = RunpodClient(runpod_key)
    print(f"Creating A100 clone pilot pod on {config.datacenter}", flush=True)
    pod = client.create_pod(body)
    print(json.dumps(summarize_pod(pod), indent=2), flush=True)

    if args.poll:
        pod_id = pod["id"]
        print("Polling pod status; the pod has a self-termination trap.", flush=True)
        while True:
            time.sleep(30)
            try:
                current = client.get_pod(pod_id)
            except RuntimeError as exc:
                print(str(exc), flush=True)
                break
            print(json.dumps(summarize_pod(current), indent=2), flush=True)
            if current.get("desiredStatus") in {"EXITED", "TERMINATED"}:
                break
    return 0


if __name__ == "__main__":
    sys.exit(main())
