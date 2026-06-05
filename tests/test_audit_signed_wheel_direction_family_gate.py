import numpy as np

from scripts.audit_signed_wheel_direction_family_gate import (
    TARGET_NAME,
    build_signed_wheel_direction_trial_samples,
    per_recording_signed_wheel_direction_labels,
    summarize,
)
from tests.test_audit_low_contrast_choice_family_gate import row
from tests.test_audit_wheel_target_family_gate import fake_recording


def test_signed_wheel_direction_labels_displacement_sign() -> None:
    rec = fake_recording(
        stim_on_times=[0.0, 2.0, 4.0],
        wheel_t=[0.0, 0.5, 1.0, 2.0, 2.5, 3.0, 4.0, 4.5, 5.0],
        wheel_position=[0.0, 0.5, 1.0, 0.0, -0.5, -1.0, 0.0, 0.0, 0.0],
    )

    labels = per_recording_signed_wheel_direction_labels(rec, window_len=1.0)

    assert labels[0] == 1.0
    assert labels[1] == 0.0
    assert np.isnan(labels[2])


def test_build_signed_wheel_direction_trial_samples_drops_nan_and_overrun_windows() -> None:
    recs = {
        "r1": fake_recording(
            stim_on_times=[0.0, 2.0, 9.5],
            wheel_t=[0.0, 0.5, 1.0, 2.0, 2.5, 3.0, 9.5, 9.7, 9.9],
            wheel_position=[0.0, 0.0, 0.0, 0.0, -0.5, -1.0, 0.0, 1.0, 2.0],
            domain_end=10.0,
        )
    }

    rows = build_signed_wheel_direction_trial_samples(
        recs,
        ["r1"],
        window_len=1.0,
        target_name=TARGET_NAME,
    )

    assert rows == [("r1", 2.0, 0.0)]


def test_summarize_signed_wheel_direction_candidate_keeps_gpu_trigger_false() -> None:
    summary = summarize(
        [row("candidate")],
        {TARGET_NAME: {"n_trials": 100, "eligible_recordings": 4, "n_recordings": 4}},
    )

    assert summary["n_candidates"] == 1
    assert summary["decision"] == "signed_wheel_direction_family_candidate"
    assert not summary["gpu_training_ready"]
