from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


def test_fixed_broad_family_wrapper_runs_true_and_shuffle_controls() -> None:
    script = (REPO_ROOT / "scripts/run_fixed_broad_family_train_arm_panel.sh").read_text()

    assert "--arm fixed_broad_family_count" in script
    assert "--fixed-family broad_named_anatomy" in script
    assert '"post_error_response_extreme_25_75_le_1"' in script
    assert '"post_error_response_extreme_33_67_le_1"' in script
    assert '"none"' in script
    assert '"within_recording_shuffle"' in script


def test_fixed_broad_family_wrapper_writes_panel_summary() -> None:
    script = (REPO_ROOT / "scripts/run_fixed_broad_family_train_arm_panel.sh").read_text()

    assert "scripts/summarize_fixed_broad_family_train_arm_panel.py" in script
    assert '--out-json "$OUT_ROOT/summary.json"' in script
    assert '--out-md "$OUT_ROOT/summary.md"' in script
