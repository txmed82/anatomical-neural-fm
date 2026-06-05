from scripts.audit_manifest_target_anatomy_feasibility import (
    RecordingTargetBalance,
    summarize_target_rows,
    trial_balance,
)


def test_trial_balance_marks_recordings_with_both_classes_eligible() -> None:
    rows = trial_balance(
        [
            ("r1", 0.0, 0.0),
            ("r1", 1.0, 0.0),
            ("r1", 2.0, 1.0),
            ("r1", 3.0, 1.0),
            ("r2", 0.0, 1.0),
        ],
        subject_by_rid={"r1": "S1", "r2": "S1"},
        min_class_trials=2,
    )

    by_recording = {row.recording: row for row in rows}
    assert by_recording["r1"].eligible
    assert by_recording["r1"].balance_fraction == 0.5
    assert not by_recording["r2"].eligible


def test_summarize_target_rows_requires_subject_recording_floor() -> None:
    rows = [
        RecordingTargetBalance("r1", "S1", 100, 50, 50, 50, 0.5, 0.5, True),
        RecordingTargetBalance("r2", "S1", 80, 40, 40, 40, 0.5, 0.5, True),
        RecordingTargetBalance("r3", "S2", 80, 70, 10, 10, 0.125, 0.125, False),
    ]

    summary = summarize_target_rows(rows, min_recordings_per_subject=2)

    assert summary["eligible_recordings"] == 2
    assert summary["subjects_passing_recording_floor"] == 1
    assert not summary["all_subjects_pass_recording_floor"]
    assert summary["subject_rows"][0]["subject"] == "S1"
    assert summary["subject_rows"][0]["passes_recording_floor"]
