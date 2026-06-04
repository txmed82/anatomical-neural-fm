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
    sweep_script: str
    output_root: str
    result_doc: str
    skip_verification: bool = False
    build_extra_args: str = ""
    s3_bucket: str = ""
    s3_prefix: str = "brainsets/ibl_bwm"
    s3_endpoint_url: str = ""
    s3_datacenter: str = ""
    skip_cell_type_priors: bool = False
    skip_sweep: bool = False


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
    sweep_script = shlex.quote(config.sweep_script)
    output_root = shlex.quote(config.output_root)
    result_doc = shlex.quote(config.result_doc)
    build_extra_args = config.build_extra_args.strip()
    build_extra = f" {build_extra_args}" if build_extra_args else ""
    sync_args = ""
    if config.s3_bucket:
        sync_args = f" --bucket {shlex.quote(config.s3_bucket)} --prefix {shlex.quote(config.s3_prefix)}"
        if config.s3_endpoint_url:
            sync_args += f" --endpoint-url {shlex.quote(config.s3_endpoint_url)}"
        if config.s3_datacenter:
            sync_args += f" --datacenter {shlex.quote(config.s3_datacenter)}"
    log_key = shlex.quote(f"logs/{config.result_doc.replace('/', '_').removesuffix('.md')}.log")
    repo_dir_q = shlex.quote(repo_dir)
    verification_block = (
        '  echo "=== skipping local verification ==="\n'
        if config.skip_verification
        else (
            '  echo "=== running local verification ==="\n'
            "  uv run pytest -q\n"
            "  uv run python scripts/00_ibl_smoke_test.py\n"
        )
    )
    dependency_sync_command = "uv sync --no-dev" if config.skip_verification else "uv sync --dev"
    startup_marker_block = (
        f"""echo "=== pushing data-build startup marker ==="
mkdir -p docs
cp "$LOG_PATH" docs/cloud_phase3_5_runpod.log || true
cat > {result_doc} <<EOF
# Cloud Phase 3-5 Results

Date: $(date -u +"%Y-%m-%dT%H:%M:%SZ")

RunPod target: data-build startup marker.

Configuration:

- branch: {branch_raw}
- output root: \`{config.output_root}\`
- skip cell-type priors: {config.skip_cell_type_priors}
- skip sweep: {config.skip_sweep}

The pod reached repository clone and dependency setup is starting.
EOF
git add {result_doc} docs/cloud_phase3_5_runpod.log 2>/dev/null || true
git commit -m "Add cloud data-build startup marker" || true
git push origin HEAD:{branch_raw} || true
"""
        if config.skip_sweep
        else ""
    )
    cell_type_priors_block = (
        '  echo "=== skipping cell-type priors ==="\n'
        if config.skip_cell_type_priors
        else "  uv run python scripts/build_cell_type_priors.py\n"
    )
    sweep_block = (
        '  echo "=== skipping phase 3-5 sweep ==="\n'
        if config.skip_sweep
        else (
            '  echo "=== running phase 3-5 sweep ==="\n'
            f"  export SEEDS={seeds}\n"
            f"  export MAX_STEPS={max_steps}\n"
            f"  export EVAL_BATCHES={eval_batches}\n"
            f"  export TARGET_MODE={target_mode}\n"
            f"  export OUT_ROOT={output_root}\n"
            f"  bash {sweep_script}\n"
        )
    )
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
    cat > {result_doc} <<EOF
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
- sweep script: {config.sweep_script}
- skip cell-type priors: {config.skip_cell_type_priors}
- skip sweep: {config.skip_sweep}
- max runtime seconds: {config.max_runtime_seconds}
- output root: \`{config.output_root}\`

EOF
    if [ -f {output_root}/build_report.md ]; then
      cat >> {result_doc} <<EOF
## Build Report

EOF
      cat {output_root}/build_report.md >> {result_doc} 2>/dev/null || true
      cat >> {result_doc} <<EOF

EOF
    fi
    if [ -f {output_root}/cache_audit.md ]; then
      cat >> {result_doc} <<EOF
## Cache Audit

EOF
      cat {output_root}/cache_audit.md >> {result_doc} 2>/dev/null || true
      cat >> {result_doc} <<EOF

EOF
    fi
    if [ -f {output_root}/summary.md ]; then
      cat >> {result_doc} <<EOF
## Summary

EOF
      cat {output_root}/summary.md >> {result_doc} 2>/dev/null || true
    else
      cat >> {result_doc} <<EOF
## Within-Animal Summary

EOF
      cat {output_root}/within_summary.md >> {result_doc} 2>/dev/null || true
      cat >> {result_doc} <<EOF

## Cross-Animal Summary

EOF
      cat {output_root}/cross_summary.md >> {result_doc} 2>/dev/null || true
    fi

    git add {result_doc} docs/cloud_phase3_5_runpod.log manifests/ibl_bwm.local.json 2>/dev/null || true
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
{startup_marker_block.rstrip()}

curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
export UV_LINK_MODE=copy
export WANDB_MODE=offline

cat > /tmp/run_phase3_5_body.sh <<'RUNSCRIPT'
  set -euo pipefail
  upload_log() {{
    if [ -n "{config.s3_bucket}" ]; then
      uv run python scripts/sync_brainset_s3.py upload-log --local-path "$LOG_PATH" --key {log_key}{sync_args} || true
    fi
  }}
  echo "=== syncing environment ==="
  {dependency_sync_command}
  upload_log
{verification_block.rstrip()}
  upload_log
{cell_type_priors_block.rstrip()}
  upload_log
  if [ ! -f {manifest_path} ]; then
    uv run python scripts/select_ibl_manifest.py --target {build_recordings} --out {manifest_path}
  fi
  if [ -n "{config.s3_bucket}" ]; then
    echo "=== downloading cached BrainSet data ==="
    uv run python scripts/sync_brainset_s3.py download --manifest {manifest_path}{sync_args} || true
    upload_log
  fi
  echo "=== building BrainSet data ==="
  mkdir -p {output_root}
  uv run python scripts/build_ibl_brainset_batch.py --manifest {manifest_path} --report {output_root}/build_report.md{build_extra}
  upload_log
  if [ -n "{config.s3_bucket}" ]; then
    echo "=== uploading built BrainSet data ==="
    uv run python scripts/sync_brainset_s3.py upload --manifest {manifest_path}{sync_args}
    upload_log
    echo "=== verifying BrainSet cache upload ==="
    uv run python scripts/sync_brainset_s3.py verify-local --manifest {manifest_path}{sync_args} --report {output_root}/cache_audit.md
    upload_log
  fi
  uv run python scripts/write_dataset_manifest.py
  upload_log
{sweep_block.rstrip()}
  upload_log
RUNSCRIPT
timeout {run_timeout} bash /tmp/run_phase3_5_body.sh
"""


def build_pod_body(name: str, config: ClonePilotConfig, runpod_key: str, github_key: str) -> dict[str, Any]:
    env = {
        "RUNPOD_API_KEY": runpod_key,
        "GITHUB_TOKEN": github_key,
    }
    if config.s3_bucket:
        s3_env = load_dotenv(REPO_ROOT / ".env")
        access_key = (
            os.environ.get("BRAINSET_S3_ACCESS_KEY")
            or os.environ.get("RUNPOD_S3_ACCESS_KEY")
            or s3_env.get("BRAINSET_S3_ACCESS_KEY")
            or s3_env.get("RUNPOD_S3_ACCESS_KEY")
            or ""
        )
        secret_key = (
            os.environ.get("BRAINSET_S3_SECRET_KEY")
            or os.environ.get("RUNPOD_S3_SECRET_KEY")
            or s3_env.get("BRAINSET_S3_SECRET_KEY")
            or s3_env.get("RUNPOD_S3_SECRET_KEY")
            or ""
        )
        env["BRAINSET_S3_ACCESS_KEY"] = access_key
        env["BRAINSET_S3_SECRET_KEY"] = secret_key
    gpu_type_ids = [gpu.strip() for gpu in config.gpu_type.split(",") if gpu.strip()]
    body = {
        "name": name,
        "imageName": config.image_name,
        "cloudType": "SECURE",
        "computeType": "GPU",
        "gpuTypeIds": gpu_type_ids,
        "gpuTypePriority": "availability",
        "gpuCount": 1,
        "dataCenterPriority": "availability" if config.datacenter.upper() == "ANY" else "custom",
        "containerDiskInGb": config.container_disk_gb,
        "volumeInGb": config.volume_gb,
        "volumeMountPath": "/workspace",
        "ports": [],
        "interruptible": False,
        "env": env,
        "dockerStartCmd": ["bash", "-lc", build_start_script(config)],
    }
    if config.datacenter.upper() != "ANY":
        body["dataCenterIds"] = [config.datacenter]
    return body


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
    p.add_argument("--datacenter", default="US-MO-1",
                   help="RunPod data center ID, or ANY to let RunPod pick by availability.")
    p.add_argument("--gpu-type", default="NVIDIA A100 80GB PCIe",
                   help="GPU type ID, or a comma-separated priority list of type IDs.")
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
    p.add_argument("--sweep-script", default="scripts/run_phase2_cloud_a100.sh")
    p.add_argument("--output-root", default="runs/phase2_cloud_a100")
    p.add_argument("--result-doc", default="docs/cloud_phase3_5_results.md")
    p.add_argument("--name-prefix", default="anfm-a100-clone-pilot")
    p.add_argument("--skip-verification", action="store_true",
                   help="Skip pytest and the IBL smoke test on the pod after local verification.")
    p.add_argument("--build-extra-args", default="",
                   help="Additional arguments passed to build_ibl_brainset_batch.py.")
    p.add_argument("--s3-bucket", default="",
                   help="Optional S3 bucket for persistent BrainSet HDF5 cache.")
    p.add_argument("--s3-prefix", default="brainsets/ibl_bwm")
    p.add_argument("--s3-endpoint-url", default="")
    p.add_argument("--s3-datacenter", default="")
    p.add_argument("--skip-cell-type-priors", action="store_true",
                   help="Skip ABC atlas cell-type prior construction on the pod.")
    p.add_argument("--skip-sweep", action="store_true",
                   help="Only build/sync BrainSet data and reports; do not run the sweep script.")
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
        sweep_script=args.sweep_script,
        output_root=args.output_root,
        result_doc=args.result_doc,
        skip_verification=args.skip_verification,
        build_extra_args=args.build_extra_args,
        s3_bucket=args.s3_bucket,
        s3_prefix=args.s3_prefix,
        s3_endpoint_url=args.s3_endpoint_url,
        s3_datacenter=args.s3_datacenter or (args.datacenter if args.s3_bucket else ""),
        skip_cell_type_priors=args.skip_cell_type_priors,
        skip_sweep=args.skip_sweep,
    )
    env = load_dotenv(REPO_ROOT / ".env")
    runpod_key = require_env(env, "RUNPOD_API_KEY")
    if config.s3_bucket:
        if not (
            os.environ.get("BRAINSET_S3_ACCESS_KEY")
            or os.environ.get("RUNPOD_S3_ACCESS_KEY")
            or env.get("BRAINSET_S3_ACCESS_KEY")
            or env.get("RUNPOD_S3_ACCESS_KEY")
        ):
            raise SystemExit("Missing S3 access key for --s3-bucket.")
        if not (
            os.environ.get("BRAINSET_S3_SECRET_KEY")
            or os.environ.get("RUNPOD_S3_SECRET_KEY")
            or env.get("BRAINSET_S3_SECRET_KEY")
            or env.get("RUNPOD_S3_SECRET_KEY")
        ):
            raise SystemExit("Missing S3 secret key for --s3-bucket.")
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
