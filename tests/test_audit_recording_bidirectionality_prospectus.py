from scripts.audit_recording_bidirectionality_prospectus import (
    RecordingObservation,
    is_bidirectional,
    prospect_recordings,
    summarize_recordings,
)


def obs(
    recording: str,
    *,
    source: str = "source-a",
    target_mode: str = "choice",
    family: str = "broad",
    target0: float,
    target1: float,
) -> RecordingObservation:
    return RecordingObservation(
        source=source,
        target_mode=target_mode,
        family=family,
        feature_mode="recording_centered",
        holdout="S1",
        recording=recording,
        target0=target0,
        target1=target1,
        improved_fraction=(target0 + target1) / 2,
        mean_true_class_delta=target0 - target1,
        n_trials=10,
        row_decision="reject",
        row_centered_delta_vs_shuffle=0.01,
        row_centered_delta_vs_total=0.02,
        row_bidirectional_fraction=0.5,
    )


def test_is_bidirectional_requires_both_targets() -> None:
    assert is_bidirectional(obs("r1", target0=0.55, target1=0.56), min_target_improvement=0.55)
    assert not is_bidirectional(obs("r1", target0=0.54, target1=0.90), min_target_improvement=0.55)


def test_summarize_recordings_tracks_cross_source_and_target_support() -> None:
    rows = summarize_recordings(
        [
            obs("stable", source="a", target_mode="choice", family="depth", target0=0.60, target1=0.61),
            obs("stable", source="b", target_mode="feedback", family="depth", target0=0.62, target1=0.58),
            obs("weak", source="a", target_mode="choice", family="depth", target0=0.80, target1=0.40),
        ],
        min_target_improvement=0.55,
    )

    assert rows[0]["recording"] == "stable"
    assert rows[0]["n_bidirectional_observations"] == 2
    assert rows[0]["n_bidirectional_sources"] == 2
    assert rows[0]["n_bidirectional_target_modes"] == 2
    assert rows[1]["recording"] == "weak"
    assert rows[1]["n_bidirectional_observations"] == 0


def test_prospect_recordings_requires_repeated_cross_source_support() -> None:
    recording_rows = summarize_recordings(
        [
            obs("lead", source="a", target_mode="choice", family="depth", target0=0.60, target1=0.61),
            obs("lead", source="b", target_mode="feedback", family="depth", target0=0.62, target1=0.58),
            obs("lead", source="b", target_mode="feedback", family="waveform", target0=0.57, target1=0.59),
            obs("posthoc", source="a", target_mode="choice", family="depth", target0=0.60, target1=0.61),
            obs("posthoc", source="a", target_mode="choice", family="waveform", target0=0.62, target1=0.58),
            obs("posthoc", source="a", target_mode="choice", family="wheel", target0=0.57, target1=0.59),
        ],
        min_target_improvement=0.55,
    )

    leads = prospect_recordings(
        recording_rows,
        min_bidirectional_observations=3,
        min_bidirectional_target_modes=2,
        min_bidirectional_sources=2,
    )

    assert [row["recording"] for row in leads] == ["lead"]
