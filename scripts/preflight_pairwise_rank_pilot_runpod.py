"""Preflight the bounded recording-pairwise-rank anatomy pilot.

This does not launch a pod. It prints the exact command for testing whether a
recording-local ranking objective can make true anatomical labels beat the
within-recording shuffled control on the strict paired gate.
"""
from __future__ import annotations

try:
    from scripts.preflight_recording_centered_pilot_runpod import print_preflight
    from scripts.preflight_two_holdout_runpod import PreflightConfig
except ModuleNotFoundError:
    from preflight_recording_centered_pilot_runpod import print_preflight
    from preflight_two_holdout_runpod import PreflightConfig


def pairwise_rank_pilot_config() -> PreflightConfig:
    return PreflightConfig(
        max_runtime_seconds=3600,
        max_provision_seconds=300,
        max_dollars=8.0,
        assumed_cost_per_hr=0.39,
        datacenter="ANY",
        gpu_type="NVIDIA L4",
        s3_bucket="rppfvo6ifn",
        s3_datacenter="US-IL-1",
        name_prefix="anfm-csh-pairwise-rank",
        output_root="runs/lso_csh_pairwise_rank_pilot",
        result_doc="docs/lso_csh_pairwise_rank_pilot_results.md",
        seeds="0",
        max_steps=300,
        eval_batches=20,
        target_mode="stimulus_side",
        sweep_env=(
            "SUBJECTS=CSH_ZAD_019",
            "SEEDS=0",
            "BATCH_SAMPLING=recording_target_balanced",
            "LOSS_MODE=recording_pairwise_rank",
            "REGION_SHUFFLE_CONTROL=within_recording_shuffle",
            "BEST_METRIC=full_eval_centered_auc",
            "FULL_EVAL_ON_BEST=1",
            "SAVE_DIAGNOSTICS=1",
        ),
    )


def main() -> int:
    return print_preflight(pairwise_rank_pilot_config())


if __name__ == "__main__":
    raise SystemExit(main())
