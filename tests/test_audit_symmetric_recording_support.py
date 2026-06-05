from scripts.audit_symmetric_recording_support import summarize, summarize_gate_row


def test_summarize_gate_row_uses_min_target_per_recording() -> None:
    row = {
        "holdout": "S1",
        "summary": {
            "delta_centered_auc": 0.02,
            "paired_true_vs_shuffle": {
                "target0_improved_fraction": 0.6,
                "target1_improved_fraction": 0.6,
            },
        },
        "recording_target_rows": [
            {"recording": "a", "target0_improved": 0.60, "target1_improved": 0.70},
            {"recording": "b", "target0_improved": 0.90, "target1_improved": 0.20},
        ],
    }

    result = summarize_gate_row(
        "report",
        row,
        min_target_improvement=0.55,
        min_bidirectional_recording_fraction=0.75,
    )

    assert result is not None
    assert result.n_bidirectional_recordings == 1
    assert result.mean_symmetric_support == 0.4
    assert result.n_target0_only == 1
    assert result.decision == "not_symmetric_recording_candidate"


def test_summarize_ranks_bidirectional_rows_first() -> None:
    candidate = summarize_gate_row(
        "report",
        {
            "holdout": "A",
            "summary": {"paired_true_vs_shuffle": {"target0_improved_fraction": 0.7, "target1_improved_fraction": 0.7}},
            "recording_target_rows": [
                {"recording": "a", "target0_improved": 0.60, "target1_improved": 0.60},
                {"recording": "b", "target0_improved": 0.70, "target1_improved": 0.70},
            ],
        },
        min_target_improvement=0.55,
        min_bidirectional_recording_fraction=1.0,
    )
    one_sided = summarize_gate_row(
        "report",
        {
            "holdout": "B",
            "recording_target_rows": [
                {"recording": "c", "target0_improved": 1.00, "target1_improved": 0.00},
                {"recording": "d", "target0_improved": 1.00, "target1_improved": 0.00},
            ],
        },
        min_target_improvement=0.55,
        min_bidirectional_recording_fraction=1.0,
    )

    summary = summarize([one_sided, candidate])

    assert summary["n_candidates"] == 1
    assert summary["top_rows"][0]["context"] == "A"
    assert summary["decision"] == "symmetric_recording_candidate_found"
