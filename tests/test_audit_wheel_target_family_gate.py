from types import SimpleNamespace

import numpy as np

from scripts.audit_wheel_target_family_gate import (
    build_wheel_trial_samples,
    per_recording_wheel_labels,
)


def fake_recording(*, stim_on_times, wheel_t=None, wheel_position=None, choice=None, domain_end=10.0) -> SimpleNamespace:
    trials = {"stim_on_times": np.asarray(stim_on_times)}
    if choice is not None:
        trials["choice"] = np.asarray(choice)
    rec = SimpleNamespace(
        trials=SimpleNamespace(**trials),
        domain=SimpleNamespace(end=np.asarray([domain_end])),
    )
    if wheel_t is not None and wheel_position is not None:
        rec.wheel = SimpleNamespace(
            timestamps=np.asarray(wheel_t),
            position=np.asarray(wheel_position),
        )
    return rec


def test_missing_wheel_returns_nan_labels() -> None:
    rec = fake_recording(stim_on_times=[0.0, 1.0, 2.0])

    labels = per_recording_wheel_labels(rec, "wheel_active")

    assert np.isnan(labels).all()


def test_wheel_active_labels_split_by_recording_median() -> None:
    rec = fake_recording(
        stim_on_times=[0.0, 2.0, 4.0],
        wheel_t=[0.0, 0.5, 1.0, 2.0, 2.5, 3.0, 4.0, 4.5, 5.0],
        wheel_position=[0.0, 0.0, 0.0, 0.0, 0.5, 1.0, 0.0, 1.5, 3.0],
    )

    labels = per_recording_wheel_labels(rec, "wheel_active")

    assert labels[0] == 0.0
    assert np.isnan(labels[1])
    assert labels[2] == 1.0


def test_wheel_displacement_labels_split_by_recording_median() -> None:
    rec = fake_recording(
        stim_on_times=[0.0, 2.0, 4.0],
        wheel_t=[0.0, 0.5, 1.0, 2.0, 2.5, 3.0, 4.0, 4.5, 5.0],
        wheel_position=[0.0, 0.1, 0.1, 0.0, 0.5, 1.0, 0.0, -1.5, -3.0],
    )

    labels = per_recording_wheel_labels(rec, "wheel_displacement")

    assert labels[0] == 0.0
    assert np.isnan(labels[1])
    assert labels[2] == 1.0


def test_choice_aligned_wheel_uses_signed_displacement_and_choice() -> None:
    rec = fake_recording(
        stim_on_times=[0.0, 2.0, 4.0],
        wheel_t=[0.0, 0.5, 1.0, 2.0, 2.5, 3.0, 4.0, 4.5, 5.0],
        wheel_position=[0.0, 0.5, 1.0, 0.0, 0.5, 1.0, 0.0, -0.5, -1.0],
        choice=[1.0, -1.0, 1.0],
    )

    labels = per_recording_wheel_labels(rec, "choice_aligned_wheel")

    assert labels.tolist() == [1.0, 0.0, 0.0]


def test_build_wheel_trial_samples_drops_nan_and_overrun_windows() -> None:
    recs = {
        "r1": fake_recording(
            stim_on_times=[0.0, 2.0, 9.5],
            wheel_t=[0.0, 0.5, 1.0, 2.0, 2.5, 3.0, 9.5, 9.7, 9.9],
            wheel_position=[0.0, 0.0, 0.0, 0.0, 0.5, 1.0, 0.0, 1.0, 2.0],
            choice=[0.0, 1.0, 1.0],
            domain_end=10.0,
        )
    }

    rows = build_wheel_trial_samples(recs, ["r1"], window_len=1.0, target_name="choice_aligned_wheel")

    assert rows == [("r1", 2.0, 1.0)]
