from pathlib import Path

from scripts.run_local_objective_probe import ProbeConfig, train_command


def test_local_probe_train_command_sets_cpu_tiny_diagnostic_run(tmp_path: Path) -> None:
    config = ProbeConfig(root=tmp_path / "probe", max_steps=3)
    command = train_command(config, "region_only")
    joined = " ".join(command)

    assert "--device cpu" in joined
    assert "--loss-mode recording_local_auc_surrogate" in joined
    assert "--batch-sampling recording_target_balanced" in joined
    assert "--best-metric full_eval_centered_auc" in joined
    assert "--full-eval-on-best" in command
    assert "--save-eval-predictions" in command
    assert "--eval-every 3" in joined


def test_local_probe_shuffle_arm_uses_within_recording_control(tmp_path: Path) -> None:
    config = ProbeConfig(root=tmp_path / "probe")
    command = train_command(config, "region_shuffle")
    joined = " ".join(command)

    assert "--arm region_only" in joined
    assert "--region-label-control within_recording_shuffle" in joined
