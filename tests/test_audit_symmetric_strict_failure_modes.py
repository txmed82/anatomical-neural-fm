from scripts.audit_symmetric_recording_support import summarize_gate_row
from scripts.audit_symmetric_strict_failure_modes import (
    blocker_labels,
    rank_scored_rows,
    required_bidirectional_recordings,
    score_row,
)


def test_required_bidirectional_recordings_rounds_up() -> None:
    assert required_bidirectional_recordings(4, 0.75) == 3
    assert required_bidirectional_recordings(3, 0.75) == 3
    assert required_bidirectional_recordings(0, 0.75) == 0


def test_score_row_reports_recording_and_global_blockers() -> None:
    row = summarize_gate_row(
        "report",
        {
            "holdout": "A",
            "summary": {
                "paired_true_vs_shuffle": {
                    "target0_improved_fraction": 0.54,
                    "target1_improved_fraction": 0.61,
                },
            },
            "recording_target_rows": [
                {"recording": "a", "target0_improved": 0.60, "target1_improved": 0.60},
                {"recording": "b", "target0_improved": 0.60, "target1_improved": 0.60},
                {"recording": "c", "target0_improved": 0.80, "target1_improved": 0.10},
                {"recording": "d", "target0_improved": 0.10, "target1_improved": 0.80},
            ],
        },
        min_target_improvement=0.55,
        min_bidirectional_recording_fraction=0.75,
    )

    assert row is not None
    assert blocker_labels(row, target_threshold=0.55, bidirectional_fraction=0.75) == [
        "recording_bidirectionality",
        "global_target0",
    ]
    scored = score_row(row, target_threshold=0.55, bidirectional_fraction=0.75)
    assert scored["required_bidirectional_recordings"] == 3
    assert scored["missing_bidirectional_recordings"] == 1
    assert scored["target0_margin"] == -0.010000000000000009
    assert not scored["strict_pass"]


def test_rank_scored_rows_prefers_one_short_global_clear() -> None:
    global_clear = {
        "strict_pass": False,
        "missing_bidirectional_recordings": 1,
        "min_global_target_margin": 0.01,
        "n_bidirectional_recordings": 2,
        "mean_symmetric_support": 0.5,
        "mean_target_imbalance": 0.05,
    }
    global_fail = {
        "strict_pass": False,
        "missing_bidirectional_recordings": 1,
        "min_global_target_margin": -0.04,
        "n_bidirectional_recordings": 2,
        "mean_symmetric_support": 0.6,
        "mean_target_imbalance": 0.02,
    }

    assert rank_scored_rows([global_fail, global_clear])[0] is global_clear
