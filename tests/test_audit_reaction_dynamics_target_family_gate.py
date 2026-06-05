from types import SimpleNamespace

import numpy as np

from scripts.audit_reaction_dynamics_target_family_gate import (
    build_reaction_trial_samples,
    per_recording_reaction_labels,
)


def fake_recording(*, stim_on_times, wheel_t=None, wheel_position=None, domain_end=10.0) -> SimpleNamespace:
    rec = SimpleNamespace(
        trials=SimpleNamespace(stim_on_times=np.asarray(stim_on_times)),
        domain=SimpleNamespace(end=np.asarray([domain_end])),
    )
    if wheel_t is not None and wheel_position is not None:
        rec.wheel = SimpleNamespace(
            timestamps=np.asarray(wheel_t),
            position=np.asarray(wheel_position),
        )
    return rec


def test_missing_wheel_returns_nan_reaction_labels() -> None:
    rec = fake_recording(stim_on_times=[1.0, 2.0, 3.0])

    labels = per_recording_reaction_labels(rec, "wheel_reaction_latency")

    assert np.isnan(labels).all()


def test_pre_stim_quiescence_inverts_pre_stim_activity_split() -> None:
    rec = fake_recording(
        stim_on_times=[1.0, 3.0, 5.0],
        wheel_t=[0.0, 0.5, 1.0, 2.5, 3.0, 4.5, 5.0],
        wheel_position=[0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 3.0],
    )

    labels = per_recording_reaction_labels(rec, "pre_stim_quiescence", pre_window_len=0.5)

    assert labels[0] == 1.0
    assert np.isnan(labels[1])
    assert labels[2] == 0.0


def test_post_stim_speedup_splits_post_minus_pre_velocity() -> None:
    rec = fake_recording(
        stim_on_times=[1.0, 3.0, 5.0],
        wheel_t=[0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0],
        wheel_position=[0.0, 0.0, 0.5, 1.0, 2.0, 2.0, 2.0, 2.1, 2.2, 2.2, 3.2, 4.2],
    )

    labels = per_recording_reaction_labels(rec, "post_stim_speedup", window_len=1.0, pre_window_len=0.5)

    assert np.isnan(labels[0])
    assert labels[1] == 0.0
    assert labels[2] == 1.0


def test_wheel_reaction_latency_labels_fast_movements_high() -> None:
    rec = fake_recording(
        stim_on_times=[1.0, 3.0, 5.0],
        wheel_t=[1.0, 1.1, 1.2, 3.0, 3.8, 3.9, 5.0, 5.4, 5.5],
        wheel_position=[0.0, 1.0, 2.0, 0.0, 0.1, 1.1, 0.0, 0.1, 1.1],
    )

    labels = per_recording_reaction_labels(rec, "wheel_reaction_latency", window_len=1.0)

    assert labels[0] == 1.0
    assert labels[1] == 0.0
    assert np.isnan(labels[2])


def test_build_reaction_trial_samples_drops_nan_and_overrun_windows() -> None:
    recs = {
        "r1": fake_recording(
            stim_on_times=[1.0, 3.0, 9.5],
            wheel_t=[1.0, 1.1, 1.2, 3.0, 3.8, 3.9, 9.5, 9.7, 9.9],
            wheel_position=[0.0, 1.0, 2.0, 0.0, 0.1, 1.1, 0.0, 1.0, 2.0],
            domain_end=10.0,
        )
    }

    rows = build_reaction_trial_samples(
        recs,
        ["r1"],
        window_len=1.0,
        pre_window_len=0.5,
        target_name="wheel_reaction_latency",
    )

    assert rows == [("r1", 1.0, 1.0), ("r1", 3.0, 0.0)]
