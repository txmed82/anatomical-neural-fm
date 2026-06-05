from scripts.preflight_recording_centered_pilot_runpod import recording_centered_pilot_config
from scripts.preflight_two_holdout_runpod import build_launch_command, estimate_cost, shell_join


def test_recording_centered_pilot_config_is_one_seed_l4_with_centered_gate() -> None:
    config = recording_centered_pilot_config()
    command = build_launch_command(config)
    joined = shell_join(command)

    assert config.gpu_type == "NVIDIA L4"
    assert config.seeds == "0"
    assert config.max_dollars == 8.0
    assert estimate_cost(
        config.max_runtime_seconds,
        config.assumed_cost_per_hr,
        config.max_provision_seconds,
    ) == 0.39
    assert "--seeds 0" in joined
    assert "--max-runtime-seconds 3600" in joined
    assert "--max-provision-seconds 300" in joined
    assert "--sweep-env SUBJECTS=CSH_ZAD_019" in joined
    assert "--sweep-env SEEDS=0" in joined
    assert "--sweep-env REGION_SHUFFLE_CONTROL=within_recording_shuffle" in joined
    assert "--sweep-env BEST_METRIC=full_eval_centered_auc" in joined
    assert "--sweep-env FULL_EVAL_ON_BEST=1" in joined
    assert "--sweep-env SAVE_DIAGNOSTICS=1" in joined
    assert "lso_csh_recording_centered_gate_pilot" in joined
