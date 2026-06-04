from scripts.preflight_two_holdout_runpod import (
    PreflightConfig,
    build_launch_command,
    estimate_cost,
    shell_join,
)


def test_estimate_cost_uses_runtime_hours() -> None:
    assert estimate_cost(5400, 1.50) == 2.25


def test_build_launch_command_targets_two_holdout_sweep() -> None:
    command = build_launch_command(PreflightConfig(max_runtime_seconds=5400, max_dollars=10.0))
    joined = shell_join(command)

    assert "--poll" in command
    assert "--max-runtime-seconds 5400" in joined
    assert "--max-provision-seconds 7200" in joined
    assert "--max-steps 300" in joined
    assert "--eval-batches 20" in joined
    assert "--target-mode stimulus_side" in joined
    assert "--manifest-path manifests/ibl_bwm_region_matched_support80_best6.json" in joined
    assert "--sweep-script scripts/run_lso_two_holdout_shared_parent_shuffle_a100.sh" in joined
    assert "--result-doc docs/lso_two_holdout_shared_parent_shuffle_results.md" in joined
    assert "--s3-bucket rppfvo6ifn" in joined
    assert "--name-prefix anfm-two-parent-compact" in joined
