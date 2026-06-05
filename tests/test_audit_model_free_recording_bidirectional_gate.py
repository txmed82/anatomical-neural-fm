from scripts.audit_model_free_recording_bidirectional_gate import (
    gate_decision,
    recording_bidirectional_summary,
    summarize_panel,
)


def test_recording_bidirectional_summary_requires_both_targets() -> None:
    rows = [
        {"recording": "a", "target0_improved": 0.60, "target1_improved": 0.61},
        {"recording": "b", "target0_improved": 0.80, "target1_improved": 0.20},
        {"recording": "c", "target0_improved": float("nan"), "target1_improved": 0.90},
    ]

    summary = recording_bidirectional_summary(rows, min_target_improvement=0.55)

    assert summary["n_evaluable_recordings"] == 2
    assert summary["n_bidirectional_recordings"] == 1
    assert summary["bidirectional_recording_fraction"] == 0.5
    assert summary["bidirectional_recordings"] == ["a"]


def test_gate_decision_rejects_split_recording_target_support() -> None:
    holdout = {
        "summary": {
            "delta_centered_auc": 0.04,
            "paired_true_vs_shuffle": {
                "target0_improved_fraction": 0.70,
                "target1_improved_fraction": 0.72,
            },
        },
    }
    bidirectional = {
        "bidirectional_recording_fraction": 0.5,
    }

    decision = gate_decision(
        holdout,
        bidirectional,
        min_centered_delta=0.01,
        min_target_improvement=0.55,
        min_bidirectional_recording_fraction=0.75,
    )

    assert decision == "reject: recording bidirectionality"


def test_summarize_panel_counts_candidates() -> None:
    rows = [
        {
            "holdout": "A",
            "recording_bidirectional_decision": "candidate",
            "summary": {"delta_centered_auc": 0.02},
            "recording_bidirectional": {"bidirectional_recording_fraction": 0.8},
        },
        {
            "holdout": "B",
            "recording_bidirectional_decision": "reject: global target1",
            "summary": {"delta_centered_auc": -0.01},
            "recording_bidirectional": {"bidirectional_recording_fraction": 0.0},
        },
    ]

    summary = summarize_panel(rows)

    assert summary["n_holdouts"] == 2
    assert summary["n_candidates"] == 1
    assert summary["candidate_holdouts"] == ["A"]
    assert summary["n_positive_delta_holdouts"] == 1
    assert summary["decision"] == "recording_bidirectional_panel_candidate"
