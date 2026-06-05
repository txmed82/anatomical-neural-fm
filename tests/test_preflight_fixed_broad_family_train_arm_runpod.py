from scripts.preflight_fixed_broad_family_train_arm_runpod import fixed_broad_family_train_arm_config
from scripts.preflight_two_holdout_runpod import estimate_cost


def test_fixed_broad_family_preflight_uses_bounded_low_cost_panel() -> None:
    config = fixed_broad_family_train_arm_config()

    assert config.sweep_script == "scripts/run_fixed_broad_family_train_arm_panel.sh"
    assert config.gpu_type == "NVIDIA L4"
    assert config.max_dollars == 8.0
    assert estimate_cost(config.max_runtime_seconds, config.assumed_cost_per_hr, config.max_provision_seconds) <= 8.0
    assert "DEVICE=cpu" in config.sweep_env
    assert "BEST_METRIC=full_eval_centered_auc" in config.sweep_env
