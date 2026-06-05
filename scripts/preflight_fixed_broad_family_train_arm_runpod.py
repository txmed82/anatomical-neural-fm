"""Preflight the fixed broad-family train-arm RunPod panel without launching."""
from __future__ import annotations

import sys
from pathlib import Path

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
    from preflight_two_holdout_runpod import (
        PreflightConfig,
        active_pods,
        build_launch_command,
        estimate_cost,
        git_branch_status,
        shell_join,
    )
    from runpod_first_a100 import REPO_ROOT, RunpodClient, load_dotenv, require_env


def fixed_broad_family_train_arm_config() -> PreflightConfig:
    return PreflightConfig(
        max_runtime_seconds=1800,
        max_provision_seconds=300,
        max_dollars=8.0,
        assumed_cost_per_hr=0.39,
        datacenter="ANY",
        gpu_type="NVIDIA L4",
        s3_bucket="rppfvo6ifn",
        s3_datacenter="US-IL-1",
        name_prefix="anfm-fixed-broad-family",
        manifest_path="manifests/ibl_bwm_local_cached_external_support80_projected_hdf5.json",
        sweep_script="scripts/run_fixed_broad_family_train_arm_panel.sh",
        output_root="runs/fixed_broad_family_train_arm_panel_runpod",
        result_doc="docs/fixed_broad_family_train_arm_runpod_results.md",
        seeds="0",
        max_steps=1000,
        eval_batches=1,
        target_mode="post_error_response_extreme_25_75_le_1",
        container_disk_gb=80,
        sweep_env=(
            "MANIFEST_PATH=manifests/ibl_bwm_local_cached_external_support80_projected_hdf5.json",
            "SEEDS=0",
            "DEVICE=cpu",
            "MAX_STEPS=1000",
            "BEST_METRIC=full_eval_centered_auc",
        ),
    )


def print_preflight(config: PreflightConfig, *, repo_root: Path = REPO_ROOT) -> int:
    branch, git_ready = git_branch_status()
    env = load_dotenv(repo_root / ".env")
    client = RunpodClient(require_env(env, "RUNPOD_API_KEY"))
    pods = active_pods(client)
    cost = estimate_cost(
        config.max_runtime_seconds,
        config.assumed_cost_per_hr,
        config.max_provision_seconds,
    )
    command = build_launch_command(config)

    print("# Fixed broad-family train-arm RunPod preflight")
    print(f"branch: {branch}")
    print(f"git_ready: {git_ready}")
    print(f"active_pods: {len(pods)}")
    for pod in pods:
        print(f"- {pod.get('id')} {pod.get('name')} cost={pod.get('costPerHr')} status={pod.get('desiredStatus') or pod.get('status')}")
    print(f"estimated_max_cost: ${cost:.2f}")
    print(f"max_dollars: ${config.max_dollars:.2f}")
    print(f"gpu_type: {config.gpu_type}")
    print(f"sweep_script: {config.sweep_script}")
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


def main() -> int:
    return print_preflight(fixed_broad_family_train_arm_config())


if __name__ == "__main__":
    raise SystemExit(main())
