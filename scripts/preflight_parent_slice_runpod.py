"""Preflight the fixed parent-region slice RunPod attempt without launching."""
from __future__ import annotations

import argparse
import sys

try:
    from scripts.preflight_two_holdout_runpod import (
        PreflightConfig,
        active_pods,
        build_launch_command,
        estimate_cost,
        git_branch_status,
        shell_join,
    )
    from scripts.runpod_first_a100 import REPO_ROOT, RunpodClient, load_dotenv, require_env
except ModuleNotFoundError:
    from preflight_two_holdout_runpod import (  # type: ignore
        PreflightConfig,
        active_pods,
        build_launch_command,
        estimate_cost,
        git_branch_status,
        shell_join,
    )
    from runpod_first_a100 import REPO_ROOT, RunpodClient, load_dotenv, require_env  # type: ignore


SLICE_PARENTS = "PRT,CA,VP,MOp,DG,mfbc"


def slice_config(args: argparse.Namespace) -> PreflightConfig:
    return PreflightConfig(
        max_runtime_seconds=args.max_runtime_seconds,
        max_provision_seconds=args.max_provision_seconds,
        max_dollars=args.max_dollars,
        assumed_cost_per_hr=args.assumed_cost_per_hr,
        datacenter=args.datacenter,
        gpu_type=args.gpu_type,
        s3_bucket=args.s3_bucket,
        s3_datacenter=args.s3_datacenter,
        name_prefix=args.name_prefix,
        output_root=args.output_root,
        result_doc=args.result_doc,
        sweep_env=(
            f"SUBJECTS={args.subject}",
            "REGION_FILTER=include_regions",
            "REGION_GRANULARITY=parent",
            f"REGION_INCLUDE={args.region_include}",
        ),
    )


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
    parser.add_argument("--subject", default="NYU-12")
    parser.add_argument("--region-include", default=SLICE_PARENTS)
    parser.add_argument("--name-prefix", default="anfm-nyu12-parent-slice")
    parser.add_argument("--output-root", default="runs/lso_nyu12_parent_slice")
    parser.add_argument("--result-doc", default="docs/lso_nyu12_parent_slice_results.md")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = slice_config(args)
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

    print("# Parent-slice RunPod preflight")
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
    print(f"subject: {args.subject}")
    print(f"region_include: {args.region_include}")
    print(f"output_root: {config.output_root}")
    print(f"result_doc: {config.result_doc}")
    print(f"sweep_env: {', '.join(config.sweep_env)}")
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
