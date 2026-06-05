from scripts.audit_model_free_source_target_pairs import pair_decision_counts, rids_for_subject, summarize_pairs


def test_rids_for_subject_sorts_matching_recordings() -> None:
    subject_by_rid = {"b": "mouse2", "a": "mouse1", "c": "mouse1"}

    assert rids_for_subject(subject_by_rid, "mouse1") == ["a", "c"]


def test_summarize_pairs_tracks_candidates_and_positive_deltas() -> None:
    rows = [
        {
            "source_subject": "A",
            "target_subject": "B",
            "recording_bidirectional_decision": "candidate",
            "summary": {"delta_centered_auc": 0.02},
            "recording_bidirectional": {"bidirectional_recording_fraction": 0.75},
        },
        {
            "source_subject": "C",
            "target_subject": "B",
            "recording_bidirectional_decision": "reject: global target1",
            "summary": {"delta_centered_auc": 0.03},
            "recording_bidirectional": {"bidirectional_recording_fraction": 0.25},
        },
        {
            "source_subject": "A",
            "target_subject": "C",
            "recording_bidirectional_decision": "reject: centered delta",
            "summary": {"delta_centered_auc": -0.01},
            "recording_bidirectional": {"bidirectional_recording_fraction": 0.0},
        },
    ]

    summary = summarize_pairs(rows)

    assert summary["n_pairs"] == 3
    assert summary["n_candidates"] == 1
    assert summary["candidate_pairs"] == [{"source": "A", "target": "B"}]
    assert summary["n_positive_delta_pairs"] == 2
    assert summary["mean_bidirectional_recording_fraction"] == (0.75 + 0.25 + 0.0) / 3
    assert summary["decision"] == "source_target_pair_candidate"


def test_pair_decision_counts_sorts_decision_names() -> None:
    rows = [
        {"recording_bidirectional_decision": "reject: b"},
        {"recording_bidirectional_decision": "reject: a"},
        {"recording_bidirectional_decision": "reject: b"},
    ]

    assert pair_decision_counts(rows) == {"reject: a": 1, "reject: b": 2}
