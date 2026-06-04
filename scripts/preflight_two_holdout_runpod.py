"""Preflight the next two-holdout RunPod broadening attempt without launching."""
from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    from scripts.runpod_first_a100 import REPO_ROOT, RunpodClient, load_dotenv, require_env
except ModuleNotFoundError:
    from runpod_first_a100 import REPO_ROOT, RunpodClient, load_dotenv, require_env


@dataclass(frozen=True)
class PreflightConfig:
    max_runtime_seconds: int = 5400
    max_dollars: float = 10.0
    assumed_cost_per_hr: float = 1.50
    datacenter: str = "ANY"
    s3_bucket: str = "rppfvo6ifn"
    s3_datacenter: str = "US-IL-1"
    name_prefix: str = "anfm-two-parent-compact"


def estimate_cost(max_runtime_seconds: int, assumed_cost_per_hr: float) -> float:
    return (max_runtime_seconds / 3600.0) * assumed_cost_per_hr


def build_launch_command(config: PreflightConfig) -> list[str]:
    return [
        "uv", "run", "python", "scripts/runpod_clone_a100.py",
        "--poll",
        "--datacenter", config.datacenter,
        "--container-disk-gb", "80",
        "--max-runtime-seconds", str(config.max_runtime_seconds),
        "--max-provision-seconds", str(config.max_runtime_seconds + 1800),
        "--skip-verification",
        "--skip-cell-type-priors",
        "--build-recordings", "0",
        "--max-steps", "300",
        "--eval-batches", "20",
        "--target-mode", "stimulus_side",
        "--manifest-path", "manifests/ibl_bwm_region_matched_support80_best6.json",
        "--seeds", "0 1 2",
        "--sweep-script", "scripts/run_lso_two_holdout_shared_parent_shuffle_a100.sh",
        "--output-root", "runs/lso_two_holdout_shared_parent_shuffle",
        "--result-doc", "docs/lso_two_holdout_shared_parent_shuffle_results.md",
        "--s3-bucket", config.s3_bucket,
        "--s3-prefix", "brainsets/ibl_bwm",
        "--s3-datacenter", config.s3_datacenter,
        "--name-prefix", config.name_prefix,
    ]


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
    parser.add_argument("--assumed-cost-per-hr", type=float, default=1.50)
    parser.add_argument("--datacenter", default="ANY")
    parser.add_argument("--s3-bucket", default="rppfvo6ifn")
    parser.add_argument("--s3-datacenter", default="US-IL-1")
    parser.add_argument("--name-prefix", default="anfm-two-parent-compact")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = PreflightConfig(
        max_runtime_seconds=args.max_runtime_seconds,
        max_dollars=args.max_dollars,
        assumed_cost_per_hr=args.assumed_cost_per_hr,
        datacenter=args.datacenter,
        s3_bucket=args.s3_bucket,
        s3_datacenter=args.s3_datacenter,
        name_prefix=args.name_prefix,
    )

    branch, git_ready = git_branch_status()
    env = load_dotenv(REPO_ROOT / ".env")
    client = RunpodClient(require_env(env, "RUNPOD_API_KEY"))
    pods = active_pods(client)
    cost = estimate_cost(config.max_runtime_seconds, config.assumed_cost_per_hr)
    command = build_launch_command(config)

    print("# Two-holdout RunPod preflight")
    print(f"branch: {branch}")
    print(f"git_ready: {git_ready}")
    print(f"active_pods: {len(pods)}")
    for pod in pods:
        print(f"- {pod.get('id')} {pod.get('name')} cost={pod.get('costPerHr')} status={pod.get('desiredStatus') or pod.get('status')}")
    print(f"estimated_max_cost: ${cost:.2f}")
    print(f"max_dollars: ${config.max_dollars:.2f}")
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
