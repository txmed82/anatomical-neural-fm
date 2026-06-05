from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


def test_two_holdout_wrapper_writes_incremental_summary() -> None:
    script = (REPO_ROOT / "scripts/run_lso_two_holdout_shared_parent_shuffle_a100.sh").read_text()

    assert "write_incremental_summary()" in script
    assert 'tmp_summary="$OUT_ROOT/summary.md.tmp"' in script
    assert 'mv "$tmp_summary" "$OUT_ROOT/summary.md"' in script
    assert "uv run python scripts/analyze_leave_subject_out.py \"$OUT_ROOT\"" in script
    assert script.count("write_incremental_summary") >= 4


def test_two_holdout_wrapper_can_pass_region_include_list() -> None:
    script = (REPO_ROOT / "scripts/run_lso_two_holdout_shared_parent_shuffle_a100.sh").read_text()

    assert 'REGION_INCLUDE="${REGION_INCLUDE:-}"' in script
    assert 'COMMON_ARGS+=(--region-include "$REGION_INCLUDE")' in script
    assert 'region_include: ${REGION_INCLUDE:-<none>}' in script


def test_two_holdout_wrapper_can_enable_diagnostic_exports() -> None:
    script = (REPO_ROOT / "scripts/run_lso_two_holdout_shared_parent_shuffle_a100.sh").read_text()

    assert 'SAVE_DIAGNOSTICS="${SAVE_DIAGNOSTICS:-0}"' in script
    assert "--save-eval-predictions --save-region-embeddings" in script
    assert "--eval-prediction-max-trials" in script
    assert 'FULL_EVAL_ON_BEST="${FULL_EVAL_ON_BEST:-0}"' in script
    assert "--full-eval-on-best" in script
    assert 'BEST_METRIC="${BEST_METRIC:-eval_loss}"' in script
    assert "--best-metric" in script


def test_two_holdout_wrapper_can_set_batch_sampling_mode() -> None:
    script = (REPO_ROOT / "scripts/run_lso_two_holdout_shared_parent_shuffle_a100.sh").read_text()

    assert 'BATCH_SAMPLING="${BATCH_SAMPLING:-uniform}"' in script
    assert '--batch-sampling "$BATCH_SAMPLING"' in script
    assert 'batch_sampling: $BATCH_SAMPLING' in script


def test_two_holdout_wrapper_can_set_loss_mode() -> None:
    script = (REPO_ROOT / "scripts/run_lso_two_holdout_shared_parent_shuffle_a100.sh").read_text()

    assert 'LOSS_MODE="${LOSS_MODE:-bce}"' in script
    assert '--loss-mode "$LOSS_MODE"' in script
    assert 'loss_mode: $LOSS_MODE' in script


def test_two_holdout_wrapper_can_set_region_shuffle_control() -> None:
    script = (REPO_ROOT / "scripts/run_lso_two_holdout_shared_parent_shuffle_a100.sh").read_text()

    assert 'REGION_SHUFFLE_CONTROL="${REGION_SHUFFLE_CONTROL:-shuffle}"' in script
    assert '--region-label-control "$REGION_SHUFFLE_CONTROL"' in script
    assert 'region_shuffle_control: $REGION_SHUFFLE_CONTROL' in script


def test_two_holdout_wrapper_can_resume_prediction_only_arms() -> None:
    script = (REPO_ROOT / "scripts/run_lso_two_holdout_shared_parent_shuffle_a100.sh").read_text()

    assert "arm_complete()" in script
    assert '[ "$SAVE_DIAGNOSTICS" = "1" ] && [ -f "$out/eval_predictions.jsonl" ]' in script
    assert 'if arm_complete "$out"; then' in script


def test_csh_wrapper_can_enable_diagnostic_exports() -> None:
    script = (REPO_ROOT / "scripts/run_lso_csh_zad_019_shared_parent_shuffle_a100.sh").read_text()

    assert 'SAVE_DIAGNOSTICS="${SAVE_DIAGNOSTICS:-0}"' in script
    assert "--save-eval-predictions --save-region-embeddings" in script
    assert "--eval-prediction-max-trials" in script
    assert 'FULL_EVAL_ON_BEST="${FULL_EVAL_ON_BEST:-0}"' in script
    assert "--full-eval-on-best" in script
    assert 'BEST_METRIC="${BEST_METRIC:-eval_loss}"' in script
    assert "--best-metric" in script


def test_csh_wrapper_can_set_batch_sampling_mode() -> None:
    script = (REPO_ROOT / "scripts/run_lso_csh_zad_019_shared_parent_shuffle_a100.sh").read_text()

    assert 'BATCH_SAMPLING="${BATCH_SAMPLING:-uniform}"' in script
    assert '--batch-sampling "$BATCH_SAMPLING"' in script
    assert 'batch_sampling: $BATCH_SAMPLING' in script


def test_csh_wrapper_can_set_loss_mode() -> None:
    script = (REPO_ROOT / "scripts/run_lso_csh_zad_019_shared_parent_shuffle_a100.sh").read_text()

    assert 'LOSS_MODE="${LOSS_MODE:-bce}"' in script
    assert '--loss-mode "$LOSS_MODE"' in script
    assert 'loss_mode: $LOSS_MODE' in script


def test_csh_wrapper_can_set_region_shuffle_control() -> None:
    script = (REPO_ROOT / "scripts/run_lso_csh_zad_019_shared_parent_shuffle_a100.sh").read_text()

    assert 'REGION_SHUFFLE_CONTROL="${REGION_SHUFFLE_CONTROL:-shuffle}"' in script
    assert '--region-label-control "$REGION_SHUFFLE_CONTROL"' in script
    assert 'region_shuffle_control: $REGION_SHUFFLE_CONTROL' in script


def test_csh_wrapper_can_resume_prediction_only_arms() -> None:
    script = (REPO_ROOT / "scripts/run_lso_csh_zad_019_shared_parent_shuffle_a100.sh").read_text()

    assert "arm_complete()" in script
    assert '[ "$SAVE_DIAGNOSTICS" = "1" ] && [ -f "$out/eval_predictions.jsonl" ]' in script
    assert 'if arm_complete "$out"; then' in script
