from scripts.audit_symmetric_threshold_sensitivity import summarize


def test_summarize_reports_strict_and_candidate_settings() -> None:
    rows = [
        {
            "min_target_improvement": 0.55,
            "min_bidirectional_recording_fraction": 0.75,
            "n_candidates": 0,
            "max_bidirectional_recordings": 2,
        },
        {
            "min_target_improvement": 0.50,
            "min_bidirectional_recording_fraction": 0.25,
            "n_candidates": 3,
            "max_bidirectional_recordings": 4,
        },
    ]

    summary = summarize(rows)

    assert summary["strict_candidates"] == 0
    assert summary["strict_max_bidirectional_recordings"] == 2
    assert summary["n_settings_with_candidates"] == 1
    assert summary["highest_target_candidate_setting"]["min_target_improvement"] == 0.50
    assert summary["strongest_default_target_candidate_setting"] is None
    assert summary["decision"] == "threshold_relaxation_needed_for_candidates"
