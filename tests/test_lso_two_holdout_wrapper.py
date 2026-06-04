from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


def test_two_holdout_wrapper_writes_incremental_summary() -> None:
    script = (REPO_ROOT / "scripts/run_lso_two_holdout_shared_parent_shuffle_a100.sh").read_text()

    assert "write_incremental_summary()" in script
    assert 'tmp_summary="$OUT_ROOT/summary.md.tmp"' in script
    assert 'mv "$tmp_summary" "$OUT_ROOT/summary.md"' in script
    assert "uv run python scripts/analyze_leave_subject_out.py \"$OUT_ROOT\"" in script
    assert script.count("write_incremental_summary") >= 4
