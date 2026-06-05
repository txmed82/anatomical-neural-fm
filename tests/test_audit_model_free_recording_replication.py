import pytest

from scripts.audit_model_free_recording_replication import (
    RecordingReplicationRow,
    build_replication_rows,
    summarize,
    summarize_group,
)
from scripts.audit_model_free_recording_support import RecordingObservation


def obs(
    report: str,
    recording: str = "rec",
    subject: str = "S1",
    *,
    target0: float,
    target1: float,
) -> RecordingObservation:
    return RecordingObservation(
        report=report,
        context=subject,
        target_subject=subject,
        recording=recording,
        target0=target0,
        target1=target1,
        improved_fraction=(target0 + target1) / 2,
        mean_true_class_delta=target0 - target1,
        n_trials=20,
    )


def test_summarize_group_counts_bidirectional_observations() -> None:
    summary = summarize_group(
        [
            obs("a", target0=0.60, target1=0.56),
            obs("b", target0=0.70, target1=0.30),
        ],
        min_target_improvement=0.55,
    )

    assert summary["n_observations"] == 2
    assert summary["n_bidirectional_observations"] == 1
    assert summary["bidirectional_fraction"] == 0.5
    assert summary["mean_target0"] == pytest.approx(0.65)
    assert summary["mean_target1"] == pytest.approx(0.43)


def test_build_replication_rows_requires_discovery_and_validation_support() -> None:
    rows = build_replication_rows(
        [
            obs("discover", target0=0.60, target1=0.60),
            obs("discover", target0=0.62, target1=0.62),
            obs("validate", target0=0.61, target1=0.61),
            obs("validate", target0=0.56, target1=0.70),
            obs("discover", recording="one-sided", target0=0.90, target1=0.20),
            obs("validate", recording="one-sided", target0=0.90, target1=0.20),
        ],
        discovery_reports={"discover"},
        validation_reports={"validate"},
        min_target_improvement=0.55,
        min_discovery_bidirectional_fraction=0.5,
        min_validation_bidirectional_fraction=0.5,
        min_discovery_observations=2,
        min_validation_observations=2,
    )

    by_recording = {row.recording: row for row in rows}
    assert by_recording["rec"].selected
    assert by_recording["rec"].replicated
    assert not by_recording["one-sided"].selected
    assert not by_recording["one-sided"].replicated


def test_summarize_reports_selected_and_replicated_recordings() -> None:
    rows = [
        RecordingReplicationRow(
            recording="r1",
            target_subject="S1",
            discovery_observations=2,
            discovery_bidirectional_observations=2,
            discovery_bidirectional_fraction=1.0,
            discovery_mean_target0=0.6,
            discovery_mean_target1=0.6,
            validation_observations=2,
            validation_bidirectional_observations=1,
            validation_bidirectional_fraction=0.5,
            validation_mean_target0=0.6,
            validation_mean_target1=0.6,
            selected=True,
            replicated=True,
        )
    ]

    summary = summarize(rows)

    assert summary["n_recording_subject_rows"] == 1
    assert summary["n_selected_by_discovery_rule"] == 1
    assert summary["n_replicated_in_validation"] == 1
    assert summary["decision"] == "recording_rule_replicates"
