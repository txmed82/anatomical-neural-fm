from scripts.audit_shared_family_target_control_gate import family_gate_decision, summarize_rows


def base_row(**overrides) -> dict:
    row = {
        "target_mode": "stimulus_side",
        "family": "thalamic",
        "holdout": "S1",
        "centered_delta_vs_shuffle": 0.02,
        "centered_delta_vs_total": 0.01,
        "target0_improved_vs_shuffle": 0.60,
        "target1_improved_vs_shuffle": 0.61,
        "bidirectional_recording_fraction": 0.75,
        "n_bidirectional_recordings": 3,
    }
    row.update(overrides)
    return row


def test_family_gate_decision_requires_total_and_bidirectional_gates() -> None:
    assert family_gate_decision(
        base_row(),
        min_centered_delta=0.01,
        min_total_delta=0.0,
        min_target_improvement=0.55,
        min_bidirectional_recording_fraction=0.75,
    ) == "candidate"
    assert family_gate_decision(
        base_row(centered_delta_vs_total=-0.01),
        min_centered_delta=0.01,
        min_total_delta=0.0,
        min_target_improvement=0.55,
        min_bidirectional_recording_fraction=0.75,
    ) == "reject: total baseline"
    assert family_gate_decision(
        base_row(bidirectional_recording_fraction=0.50),
        min_centered_delta=0.01,
        min_total_delta=0.0,
        min_target_improvement=0.55,
        min_bidirectional_recording_fraction=0.75,
    ) == "reject: recording bidirectionality"


def test_summarize_rows_counts_targets_and_families() -> None:
    rows = [
        base_row(decision="candidate", n_recordings=4),
        base_row(
            target_mode="choice",
            family="fiber_tracts",
            decision="reject: target1",
            centered_delta_vs_shuffle=0.03,
            target1_improved_vs_shuffle=0.40,
            n_recordings=4,
        ),
    ]

    summary = summarize_rows(rows)

    assert summary["n_rows"] == 2
    assert summary["n_candidates"] == 1
    assert summary["n_positive_centered_delta"] == 2
    assert summary["by_target"]["stimulus_side"]["n_candidates"] == 1
    assert summary["by_family"]["fiber_tracts"]["n_positive_centered_delta"] == 1
    assert summary["decision"] == "shared_family_target_candidate"
