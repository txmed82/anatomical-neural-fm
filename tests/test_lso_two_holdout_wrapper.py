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


def test_csh_wrapper_can_enable_diagnostic_exports() -> None:
    script = (REPO_ROOT / "scripts/run_lso_csh_zad_019_shared_parent_shuffle_a100.sh").read_text()

    assert 'SAVE_DIAGNOSTICS="${SAVE_DIAGNOSTICS:-0}"' in script
    assert "--save-eval-predictions --save-region-embeddings" in script
    assert "--eval-prediction-max-trials" in script
    assert 'FULL_EVAL_ON_BEST="${FULL_EVAL_ON_BEST:-0}"' in script
    assert "--full-eval-on-best" in script
    assert 'BEST_METRIC="${BEST_METRIC:-eval_loss}"' in script
    assert "--best-metric" in script
