"""Preflight the next two-holdout RunPod broadening attempt without launching."""
from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from dataclasses import dataclass

try:
    from scripts.runpod_first_a100 import REPO_ROOT, RunpodClient, load_dotenv, require_env
except ModuleNotFoundError:
    from runpod_first_a100 import REPO_ROOT, RunpodClient, load_dotenv, require_env


@dataclass(frozen=True)
class PreflightConfig:
    max_runtime_seconds: int = 5400
    max_provision_seconds: int = 7200
    max_dollars: float = 10.0
    assumed_cost_per_hr: float = 3.00
    datacenter: str = "ANY"
    gpu_type: str = "NVIDIA A100 80GB PCIe,NVIDIA A100-SXM4-80GB"
    s3_bucket: str = "rppfvo6ifn"
    s3_datacenter: str = "US-IL-1"
    name_prefix: str = "anfm-nr0019-parent-compact"
    manifest_path: str = "manifests/ibl_bwm_region_matched_support80_best6.json"
    sweep_script: str = "scripts/run_lso_two_holdout_shared_parent_shuffle_a100.sh"
    output_root: str = "runs/lso_nr0019_shared_parent_shuffle"
    result_doc: str = "docs/lso_nr0019_shared_parent_shuffle_results.md"
    seeds: str = "0 1 2"
    max_steps: int = 300
    eval_batches: int = 20
    target_mode: str = "stimulus_side"
    container_disk_gb: int = 80
    dependency_diagnostic: bool = False
    sweep_env: tuple[str, ...] = ("SUBJECTS=NR_0019",)


def estimate_cost(
    max_runtime_seconds: int,
    assumed_cost_per_hr: float,
    max_provision_seconds: int | None = None,
) -> float:
    billable_guard_seconds = max(max_runtime_seconds, max_provision_seconds or 0)
    return (billable_guard_seconds / 3600.0) * assumed_cost_per_hr


def build_launch_command(config: PreflightConfig) -> list[str]:
    output_root = config.output_root
    result_doc = config.result_doc
    name_prefix = config.name_prefix
    if config.dependency_diagnostic:
        output_root = "runs/runpod_dependency_diagnostic"
        result_doc = "docs/runpod_dependency_diagnostic.md"
        name_prefix = "anfm-depdiag"
    command = [
        "uv", "run", "python", "scripts/runpod_clone_a100.py",
        "--poll",
        "--datacenter", config.datacenter,
        "--gpu-type", config.gpu_type,
        "--container-disk-gb", str(config.container_disk_gb),
        "--max-runtime-seconds", str(config.max_runtime_seconds),
        "--max-provision-seconds", str(config.max_provision_seconds),
        "--skip-verification",
        "--skip-cell-type-priors",
        "--build-recordings", "0",
        "--max-steps", str(config.max_steps),
        "--eval-batches", str(config.eval_batches),
        "--target-mode", config.target_mode,
        "--manifest-path", config.manifest_path,
        "--seeds", config.seeds,
        "--sweep-script", config.sweep_script,
        "--output-root", output_root,
        "--result-doc", result_doc,
        "--s3-bucket", config.s3_bucket,
        "--s3-prefix", "brainsets/ibl_bwm",
        "--s3-datacenter", config.s3_datacenter,
        "--name-prefix", name_prefix,
    ]
    for item in config.sweep_env:
        command.extend(["--sweep-env", item])
    if config.dependency_diagnostic:
        command.append("--dependency-diagnostic")
    return command


def shell_join(argv: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in argv)


def git_branch_status() -> tuple[str, bool]:
    branch = subprocess.check_output(["git", "branch", "--show-current"], text=True).strip()
    status = subprocess.check_output(["git", "status", "--short", "--branch"], text=True).strip()
    synced = "[ahead" not in status and "[behind" not in status and "[gone" not in status
    dirty = any(line and not line.startswith("## ") for line in status.splitlines())
    return branch, synced and not dirty


def active_pods(client: RunpodClient) -> list[dict]:
    pods = client.request("GET", "/pods")
    if isinstance(pods, dict):
        items = pods.get("pods") or pods.get("items") or pods.get("data") or []
    elif isinstance(pods, list):
        items = pods
    else:
        items = []
    return list(items)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-dollars", type=float, default=10.0)
    parser.add_argument("--max-runtime-seconds", type=int, default=5400)
    parser.add_argument("--max-provision-seconds", type=int, default=7200)
    parser.add_argument("--assumed-cost-per-hr", type=float, default=3.00)
    parser.add_argument("--datacenter", default="ANY")
    parser.add_argument("--gpu-type", default="NVIDIA A100 80GB PCIe,NVIDIA A100-SXM4-80GB")
    parser.add_argument("--s3-bucket", default="rppfvo6ifn")
    parser.add_argument("--s3-datacenter", default="US-IL-1")
    parser.add_argument("--name-prefix", default="anfm-nr0019-parent-compact")
    parser.add_argument("--manifest-path", default="manifests/ibl_bwm_region_matched_support80_best6.json")
    parser.add_argument("--sweep-script", default="scripts/run_lso_two_holdout_shared_parent_shuffle_a100.sh")
    parser.add_argument("--output-root", default="runs/lso_nr0019_shared_parent_shuffle")
    parser.add_argument("--result-doc", default="docs/lso_nr0019_shared_parent_shuffle_results.md")
    parser.add_argument("--seeds", default="0 1 2")
    parser.add_argument("--max-steps", type=int, default=300)
    parser.add_argument("--eval-batches", type=int, default=20)
    parser.add_argument("--target-mode", default="stimulus_side")
    parser.add_argument("--container-disk-gb", type=int, default=80)
    parser.add_argument("--sweep-env", action="append", default=None)
    parser.add_argument("--dependency-diagnostic", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = PreflightConfig(
        max_runtime_seconds=args.max_runtime_seconds,
        max_provision_seconds=args.max_provision_seconds,
        max_dollars=args.max_dollars,
        assumed_cost_per_hr=args.assumed_cost_per_hr,
        datacenter=args.datacenter,
        gpu_type=args.gpu_type,
        s3_bucket=args.s3_bucket,
        s3_datacenter=args.s3_datacenter,
        name_prefix=args.name_prefix,
        manifest_path=args.manifest_path,
        sweep_script=args.sweep_script,
        output_root=args.output_root,
        result_doc=args.result_doc,
        seeds=args.seeds,
        max_steps=args.max_steps,
        eval_batches=args.eval_batches,
        target_mode=args.target_mode,
        container_disk_gb=args.container_disk_gb,
        dependency_diagnostic=args.dependency_diagnostic,
        sweep_env=tuple(args.sweep_env or ["SUBJECTS=NR_0019"]),
    )

    branch, git_ready = git_branch_status()
    env = load_dotenv(REPO_ROOT / ".env")
    client = RunpodClient(require_env(env, "RUNPOD_API_KEY"))
    pods = active_pods(client)
    cost = estimate_cost(
        config.max_runtime_seconds,
        config.assumed_cost_per_hr,
        config.max_provision_seconds,
    )
    command = build_launch_command(config)

    print("# Two-holdout RunPod preflight")
    print(f"branch: {branch}")
    print(f"git_ready: {git_ready}")
    print(f"active_pods: {len(pods)}")
    for pod in pods:
        print(f"- {pod.get('id')} {pod.get('name')} cost={pod.get('costPerHr')} status={pod.get('desiredStatus') or pod.get('status')}")
    print(f"estimated_max_cost: ${cost:.2f}")
    print(f"max_dollars: ${config.max_dollars:.2f}")
    print(f"max_runtime_seconds: {config.max_runtime_seconds}")
    print(f"max_provision_seconds: {config.max_provision_seconds}")
    print(f"gpu_type: {config.gpu_type}")
    print(f"manifest_path: {config.manifest_path}")
    print(f"sweep_script: {config.sweep_script}")
    print(f"output_root: {config.output_root}")
    print(f"result_doc: {config.result_doc}")
    print(f"seeds: {config.seeds}")
    print(f"max_steps: {config.max_steps}")
    print(f"eval_batches: {config.eval_batches}")
    print(f"target_mode: {config.target_mode}")
    print(f"sweep_env: {', '.join(config.sweep_env) or '<none>'}")
    print(f"dependency_diagnostic: {config.dependency_diagnostic}")
    print("")
    print("Launch command:")
    print(shell_join(command))

    if not git_ready:
        print("preflight failed: git branch is dirty, ahead, or behind", file=sys.stderr)
        return 2
    if pods:
        print("preflight failed: active RunPod pods exist", file=sys.stderr)
        return 3
    if cost > config.max_dollars:
        print("preflight failed: estimated max cost exceeds cap", file=sys.stderr)
        return 4
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
