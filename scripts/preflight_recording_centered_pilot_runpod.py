"""Preflight the next bounded recording-centered anatomy pilot.

This does not launch a pod. It prints the exact RunPod command for a one-seed
CSH_ZAD_019 pilot whose checkpoint selection and official gate are centered on
within-recording evidence rather than raw full-trial AUC.
"""
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


def recording_centered_pilot_config() -> PreflightConfig:
    return PreflightConfig(
        max_runtime_seconds=3600,
        max_provision_seconds=300,
        max_dollars=8.0,
        assumed_cost_per_hr=0.39,
        datacenter="ANY",
        gpu_type="NVIDIA L4",
        s3_bucket="rppfvo6ifn",
        s3_datacenter="US-IL-1",
        name_prefix="anfm-csh-reccentered-gate",
        output_root="runs/lso_csh_recording_centered_gate_pilot",
        result_doc="docs/lso_csh_recording_centered_gate_pilot_results.md",
        seeds="0",
        max_steps=300,
        eval_batches=20,
        target_mode="stimulus_side",
        sweep_env=(
            "SUBJECTS=CSH_ZAD_019",
            "SEEDS=0",
            "REGION_SHUFFLE_CONTROL=within_recording_shuffle",
            "BEST_METRIC=full_eval_centered_auc",
            "FULL_EVAL_ON_BEST=1",
            "SAVE_DIAGNOSTICS=1",
        ),
    )


def post_run_output_paths(config: PreflightConfig) -> dict[str, str]:
    doc_path = Path(config.result_doc)
    stem = doc_path.stem
    if stem.endswith("_results"):
        stem = stem.removesuffix("_results")
    return {
        "gate_json": str(doc_path.with_name(f"{stem}_anatomy_specific_gate.json")),
        "failure_json": str(doc_path.with_name(f"{stem}_failure_modes.json")),
        "failure_md": str(doc_path.with_name(f"{stem}_failure_modes.md")),
        "mechanism_json": str(doc_path.with_name(f"{stem}_mechanism.json")),
        "mechanism_md": str(doc_path.with_name(f"{stem}_mechanism.md")),
    }


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
    post_run_paths = post_run_output_paths(config)

    print(f"# {config.name_prefix} RunPod preflight")
    print(f"branch: {branch}")
    print(f"git_ready: {git_ready}")
    print(f"active_pods: {len(pods)}")
    for pod in pods:
        print(f"- {pod.get('id')} {pod.get('name')} cost={pod.get('costPerHr')} status={pod.get('desiredStatus') or pod.get('status')}")
    print(f"estimated_max_cost: ${cost:.2f}")
    print(f"max_dollars: ${config.max_dollars:.2f}")
    print(f"gpu_type: {config.gpu_type}")
    print(f"seeds: {config.seeds}")
    print("best_metric: full_eval_centered_auc")
    print("negative_control: within_recording_shuffle")
    print(f"output_root: {config.output_root}")
    print(f"result_doc: {config.result_doc}")
    print(f"sweep_env: {', '.join(config.sweep_env)}")
    print("")
    print("Launch command:")
    print(shell_join(command))
    print("")
    print("Required post-run gate:")
    print(
        "uv run python scripts/analyze_anatomy_specific_permutation.py "
        f"{config.output_root} --holdout CSH_ZAD_019 "
        f"--out {post_run_paths['gate_json']}"
    )
    print("")
    print("Required post-run failure-mode audit:")
    print(
        "uv run python scripts/audit_prediction_failure_modes.py "
        f"{config.output_root} --holdout CSH_ZAD_019 "
        f"--out {post_run_paths['failure_json']} "
        f"--md-out {post_run_paths['failure_md']}"
    )
    print("")
    print("Required post-run mechanism audit:")
    print(
        "uv run python scripts/audit_csh_mechanism.py "
        f"--root {config.output_root} --holdout CSH_ZAD_019 "
        f"--out-json {post_run_paths['mechanism_json']} "
        f"--out-md {post_run_paths['mechanism_md']}"
    )

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
    return print_preflight(recording_centered_pilot_config())


if __name__ == "__main__":
    raise SystemExit(main())
