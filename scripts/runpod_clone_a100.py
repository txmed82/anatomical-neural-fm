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
    from scripts.runpod_first_a100 import REPO_ROOT, S3_ENDPOINTS, RunpodClient, load_dotenv, require_env
except ModuleNotFoundError:
    from runpod_first_a100 import REPO_ROOT, S3_ENDPOINTS, RunpodClient, load_dotenv, require_env


@dataclass(frozen=True)
class ClonePilotConfig:
    branch: str
    repo_url: str
    datacenter: str
    compute_type: str
    cpu_flavor: str
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
    setup_mode: str = "project"
    startup_smoke_only: bool = False


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
    bootstrap_log_block = ""
    if config.s3_bucket:
        sync_args = f" --bucket {shlex.quote(config.s3_bucket)} --prefix {shlex.quote(config.s3_prefix)}"
        if config.s3_endpoint_url:
            sync_args += f" --endpoint-url {shlex.quote(config.s3_endpoint_url)}"
        if config.s3_datacenter:
            sync_args += f" --datacenter {shlex.quote(config.s3_datacenter)}"
        endpoint_url = config.s3_endpoint_url
        if not endpoint_url and config.s3_datacenter:
            endpoint_url = S3_ENDPOINTS.get(config.s3_datacenter, "")
        bootstrap_key = f"{config.s3_prefix.strip('/')}/logs/bootstrap_{config.result_doc.replace('/', '_').removesuffix('.md')}.log"
        bootstrap_log_block = f"""
bootstrap_upload_log() {{
  if [ ! -s "$LOG_PATH" ]; then
    return 0
  fi
  python3 - <<'PY' || true
import os
import subprocess
import sys

try:
    import boto3
except Exception:
    subprocess.run([sys.executable, "-m", "pip", "install", "--user", "boto3"], check=False)
    import boto3

client = boto3.client(
    "s3",
    aws_access_key_id=os.environ.get("BRAINSET_S3_ACCESS_KEY"),
    aws_secret_access_key=os.environ.get("BRAINSET_S3_SECRET_KEY"),
    endpoint_url={endpoint_url!r} or None,
    region_name={config.s3_datacenter.lower()!r} or "auto",
)
client.upload_file(
    os.environ["LOG_PATH"],
    {config.s3_bucket!r},
    {bootstrap_key!r},
)
PY
}}
"""
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
    if config.setup_mode == "minimal-data":
        system_setup_command = (
            "if command -v git >/dev/null 2>&1 && command -v curl >/dev/null 2>&1 && command -v python3 >/dev/null 2>&1; then\n"
            "  echo \"minimal data-build system tools already installed\"\n"
            "else\n"
            "  apt-get update\n"
            "  apt-get install -y --no-install-recommends git curl ca-certificates python3-pip\n"
            "fi"
        )
        dependency_sync_command = (
            "if python3 - <<'PY'\n"
            "import importlib.util\n"
            "missing = [m for m in ['boto3', 'h5py', 'numpy', 'one', 'iblatlas', 'temporaldata'] if importlib.util.find_spec(m) is None]\n"
            "raise SystemExit(1 if missing else 0)\n"
            "PY\n"
            "  then\n"
            "    echo \"minimal data-build dependencies already installed\"\n"
            "  else\n"
            "    python3 -m pip install --user --upgrade pip\n"
            "    python3 -m pip install --user boto3 h5py numpy one-api iblatlas temporaldata\n"
            "  fi"
        )
        python_runner = "python3"
        dataset_manifest_block = '  echo "=== skipping dataset manifest (minimal-data setup) ==="\n'
    else:
        system_setup_command = (
            "apt-get update\n"
            "apt-get install -y --no-install-recommends git curl ca-certificates python3-pip"
        )
        dependency_sync_command = "uv sync --no-dev" if config.skip_verification else "uv sync --dev"
        python_runner = "uv run python"
        dataset_manifest_block = "  uv run python scripts/write_dataset_manifest.py\n"
    cell_type_priors_block = (
        '  echo "=== skipping cell-type priors ==="\n'
        if config.skip_cell_type_priors
        else "  uv run python scripts/build_cell_type_priors.py\n"
    )
    startup_smoke_block = (
        '  echo "=== startup smoke complete ==="\n'
        "  upload_log\n"
        "  exit 0"
        if config.startup_smoke_only
        else ""
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
            f"  export MANIFEST={manifest_path}\n"
            f"  export OUT_ROOT={output_root}\n"
            f"  bash {sweep_script}\n"
        )
    )
    return f"""set -uo pipefail
LOG_PATH=/tmp/runpod_phase3_5.log
REPO_DIR=/workspace/{repo_dir_q}
export LOG_PATH
touch "$LOG_PATH"
exec > >(tee -a "$LOG_PATH") 2>&1
{bootstrap_log_block}

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
- setup mode: {config.setup_mode}
- skip cell-type priors: {config.skip_cell_type_priors}
- skip sweep: {config.skip_sweep}
- startup smoke only: {config.startup_smoke_only}
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
    elif [ -f {output_root}/within_summary.md ] || [ -f {output_root}/cross_summary.md ]; then
      cat >> {result_doc} <<EOF
## Within-Animal Summary

EOF
      cat {output_root}/within_summary.md >> {result_doc} 2>/dev/null || true
      cat >> {result_doc} <<EOF

## Cross-Animal Summary

EOF
      cat {output_root}/cross_summary.md >> {result_doc} 2>/dev/null || true
    else
      cat >> {result_doc} <<EOF
## Missing Sweep Summary

No \`{config.output_root}/summary.md\`, \`within_summary.md\`, or
\`cross_summary.md\` file was present when cleanup pushed artifacts. Treat this
cloud result as incomplete/non-evidence even if the pod exit status is 0.

EOF
    fi

    git add {result_doc} docs/cloud_phase3_5_runpod.log 2>/dev/null || true
    git add manifests/ibl_bwm.local.json 2>/dev/null || true
    git commit -m "Add cloud phase 3-5 pilot results" || true
    git push origin HEAD:{branch_raw} || true
  fi
}}

cleanup() {{
  status="$?"
  if [ -n "${{GUARD_PID:-}}" ]; then
    kill "$GUARD_PID" >/dev/null 2>&1 || true
  fi
  push_artifacts "$status" || true
  if declare -f bootstrap_upload_log >/dev/null 2>&1; then
    bootstrap_upload_log || true
  fi
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

guard_timeout() {{
  sleep {run_timeout}
  echo "=== max runtime seconds exceeded; terminating pod ===" >> "$LOG_PATH" || true
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
guard_timeout &
GUARD_PID="$!"

set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
{system_setup_command}

cd /workspace
rm -rf {repo_dir_q}
git clone --branch {branch} --single-branch "{clone_url}"
cd {repo_dir_q}
git config user.name "RunPod Pilot"
git config user.email "runpod-pilot@example.invalid"

export PATH="$HOME/.local/bin:$PATH"
if [ "{config.setup_mode}" != "minimal-data" ] && ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh || python3 -m pip install --user uv
fi
if command -v uv >/dev/null 2>&1; then
  uv --version
else
  echo "uv not installed; using python3 minimal-data setup"
fi
export UV_LINK_MODE=copy
export WANDB_MODE=offline

cat > /tmp/run_phase3_5_body.sh <<'RUNSCRIPT'
  set -euo pipefail
  upload_log() {{
    if [ -n "{config.s3_bucket}" ]; then
      {python_runner} scripts/sync_brainset_s3.py upload-log --local-path "$LOG_PATH" --key {log_key}{sync_args} || true
    fi
  }}
  echo "=== syncing environment ==="
  {dependency_sync_command}
  upload_log
{startup_smoke_block}
{verification_block.rstrip()}
  upload_log
{cell_type_priors_block.rstrip()}
  upload_log
  if [ ! -f {manifest_path} ]; then
    {python_runner} scripts/select_ibl_manifest.py --target {build_recordings} --out {manifest_path}
  fi
  if [ -n "{config.s3_bucket}" ]; then
    echo "=== downloading cached BrainSet data ==="
    {python_runner} scripts/sync_brainset_s3.py download --manifest {manifest_path}{sync_args} || true
    upload_log
  fi
  echo "=== building BrainSet data ==="
  mkdir -p {output_root}
  {python_runner} scripts/build_ibl_brainset_batch.py --manifest {manifest_path} --report {output_root}/build_report.md{build_extra}
  upload_log
  if [ -n "{config.s3_bucket}" ]; then
    echo "=== uploading built BrainSet data ==="
    {python_runner} scripts/sync_brainset_s3.py upload --manifest {manifest_path}{sync_args} --skip-existing
    upload_log
    echo "=== verifying BrainSet cache upload ==="
    {python_runner} scripts/sync_brainset_s3.py verify-local --manifest {manifest_path}{sync_args} --report {output_root}/cache_audit.md
    upload_log
  fi
{dataset_manifest_block.rstrip()}
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
    body = {
        "name": name,
        "imageName": config.image_name,
        "cloudType": "SECURE",
        "computeType": config.compute_type,
        "dataCenterPriority": "availability" if config.datacenter.upper() == "ANY" else "custom",
        "containerDiskInGb": config.container_disk_gb,
        "volumeInGb": config.volume_gb,
        "volumeMountPath": "/workspace",
        "ports": [],
        "interruptible": False,
        "env": env,
        "dockerEntrypoint": ["bash", "-lc"],
        "dockerStartCmd": [build_start_script(config)],
    }
    if config.compute_type == "CPU":
        cpu_flavor_ids = [flavor.strip() for flavor in config.cpu_flavor.split(",") if flavor.strip()]
        body["cpuFlavorIds"] = cpu_flavor_ids
        body["cpuFlavorPriority"] = "availability"
    else:
        gpu_type_ids = [gpu.strip() for gpu in config.gpu_type.split(",") if gpu.strip()]
        body["gpuTypeIds"] = gpu_type_ids
        body["gpuTypePriority"] = "availability"
        body["gpuCount"] = 1
    if config.datacenter.upper() != "ANY":
        body["dataCenterIds"] = [config.datacenter]
    return body


def summarize_pod(pod: dict[str, Any]) -> dict[str, Any]:
    machine = pod.get("machine") or {}
    return {
        "id": pod.get("id"),
        "name": pod.get("name"),
        "desiredStatus": pod.get("desiredStatus"),
        "costPerHr": pod.get("costPerHr"),
        "machineId": pod.get("machineId"),
        "cpuFlavorId": pod.get("cpuFlavorId"),
        "publicIp": pod.get("publicIp"),
        "volumeInGb": pod.get("volumeInGb"),
        "machineReady": bool(machine),
        "lastStatusChange": pod.get("lastStatusChange"),
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--branch", default=current_branch())
    p.add_argument("--repo-url", default="https://github.com/txmed82/anatomical-neural-fm.git")
    p.add_argument("--datacenter", default="US-MO-1",
                   help="RunPod data center ID, or ANY to let RunPod pick by availability.")
    p.add_argument("--compute-type", choices=["GPU", "CPU"], default="GPU")
    p.add_argument("--cpu-flavor", default="cpu3c,cpu3g,cpu3m",
                   help="CPU flavor ID, or a comma-separated priority list of IDs.")
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
    p.add_argument("--setup-mode", choices=["project", "minimal-data"], default="project",
                   help="Dependency setup strategy. minimal-data avoids torch/project sync for cache builds.")
    p.add_argument("--startup-smoke-only", action="store_true",
                   help="Stop after dependency setup and first S3 log upload.")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--poll", action="store_true")
    p.add_argument("--max-provision-seconds", type=int, default=600,
                   help="When polling, terminate if the pod remains rented but unprovisioned this long.")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    config = ClonePilotConfig(
        branch=args.branch,
        repo_url=args.repo_url,
        datacenter=args.datacenter,
        compute_type=args.compute_type,
        cpu_flavor=args.cpu_flavor,
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
        setup_mode=args.setup_mode,
        startup_smoke_only=args.startup_smoke_only,
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
    print(f"Creating {config.compute_type} clone pilot pod on {config.datacenter}", flush=True)
    pod = client.create_pod(body)
    print(json.dumps(summarize_pod(pod), indent=2), flush=True)

    if args.poll:
        pod_id = pod["id"]
        print("Polling pod status; the pod has a self-termination trap.", flush=True)
        provision_deadline = time.time() + args.max_provision_seconds
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
            machine = current.get("machine") or {}
            public_ip = current.get("publicIp")
            if (
                args.max_provision_seconds > 0
                and time.time() > provision_deadline
                and not machine
                and not public_ip
            ):
                print(
                    f"Pod stayed unprovisioned for {args.max_provision_seconds}s; terminating.",
                    flush=True,
                )
                client.terminate_pod(pod_id)
                break
    return 0


if __name__ == "__main__":
    sys.exit(main())
