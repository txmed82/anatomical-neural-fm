from scripts.preflight_pairwise_rank_centered_bce_pilot_runpod import (
    pairwise_rank_centered_bce_pilot_config,
)
from scripts.preflight_recording_centered_pilot_runpod import post_run_output_paths
from scripts.preflight_two_holdout_runpod import build_launch_command, shell_join


def test_pairwise_rank_centered_bce_pilot_config_sets_objective_controls() -> None:
    config = pairwise_rank_centered_bce_pilot_config()
    joined = shell_join(build_launch_command(config))

    assert config.gpu_type == "NVIDIA L4"
    assert config.seeds == "0"
    assert config.max_dollars == 8.0
    assert "--output-root runs/lso_csh_pairwise_rank_centered_bce_pilot" in joined
    assert "--result-doc docs/lso_csh_pairwise_rank_centered_bce_pilot_results.md" in joined
    assert "--sweep-env BATCH_SAMPLING=recording_target_balanced" in joined
    assert "--sweep-env LOSS_MODE=recording_pairwise_rank_centered_bce" in joined
    assert "--sweep-env REGION_SHUFFLE_CONTROL=within_recording_shuffle" in joined
    assert "--sweep-env BEST_METRIC=full_eval_centered_auc" in joined


def test_pairwise_rank_centered_bce_preflight_uses_matching_post_run_paths() -> None:
    paths = post_run_output_paths(pairwise_rank_centered_bce_pilot_config())

    assert paths == {
        "gate_json": "docs/lso_csh_pairwise_rank_centered_bce_pilot_anatomy_specific_gate.json",
        "failure_json": "docs/lso_csh_pairwise_rank_centered_bce_pilot_failure_modes.json",
        "failure_md": "docs/lso_csh_pairwise_rank_centered_bce_pilot_failure_modes.md",
        "mechanism_json": "docs/lso_csh_pairwise_rank_centered_bce_pilot_mechanism.json",
        "mechanism_md": "docs/lso_csh_pairwise_rank_centered_bce_pilot_mechanism.md",
    }
