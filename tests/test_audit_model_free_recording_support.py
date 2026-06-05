from scripts.audit_model_free_recording_support import (
    RecordingObservation,
    context_for_row,
    is_bidirectional,
    summarize_recordings,
    summarize_subjects,
)


def obs(
    recording: str,
    *,
    target_subject: str = "S1",
    target0: float,
    target1: float,
) -> RecordingObservation:
    return RecordingObservation(
        report="report",
        context=f"source -> {target_subject}",
        target_subject=target_subject,
        recording=recording,
        target0=target0,
        target1=target1,
        improved_fraction=(target0 + target1) / 2,
        mean_true_class_delta=target0 - target1,
        n_trials=10,
    )


def test_context_for_row_handles_holdout_and_source_target_rows() -> None:
    assert context_for_row({"holdout": "KS014"}) == ("KS014", "KS014")
    assert context_for_row({"source_subject": "A", "target_subject": "B"}) == ("A -> B", "B")


def test_is_bidirectional_requires_both_target_classes() -> None:
    assert is_bidirectional(obs("r1", target0=0.60, target1=0.55), min_target_improvement=0.55)
    assert not is_bidirectional(obs("r1", target0=0.60, target1=0.54), min_target_improvement=0.55)


def test_summarize_recordings_aggregates_and_sorts_by_bidirectional_support() -> None:
    rows = summarize_recordings(
        [
            obs("rec-low", target_subject="S1", target0=0.80, target1=0.40),
            obs("rec-high", target_subject="S1", target0=0.60, target1=0.60),
            obs("rec-high", target_subject="S2", target0=0.70, target1=0.56),
        ],
        min_target_improvement=0.55,
    )

    assert rows[0]["recording"] == "rec-high"
    assert rows[0]["target_subjects"] == ["S1", "S2"]
    assert rows[0]["n_observations"] == 2
    assert rows[0]["n_bidirectional_observations"] == 2
    assert rows[0]["bidirectional_observation_fraction"] == 1.0
    assert rows[1]["recording"] == "rec-low"
    assert rows[1]["n_bidirectional_observations"] == 0


def test_summarize_subjects_counts_recordings_with_any_support() -> None:
    recording_rows = [
        {
            "recording": "r1",
            "target_subjects": ["S1", "S2"],
            "n_bidirectional_observations": 2,
        },
        {
            "recording": "r2",
            "target_subjects": ["S1"],
            "n_bidirectional_observations": 0,
        },
    ]

    subjects = summarize_subjects(recording_rows)
    by_subject = {row["subject"]: row for row in subjects}

    assert by_subject["S2"] == {
        "subject": "S2",
        "n_recordings": 1,
        "recordings_with_bidirectional_support": 1,
        "total_bidirectional_observations": 2,
        "max_bidirectional_observations": 2,
    }
    assert by_subject["S1"]["n_recordings"] == 2
    assert by_subject["S1"]["recordings_with_bidirectional_support"] == 1
