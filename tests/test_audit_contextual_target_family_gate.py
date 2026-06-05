from types import SimpleNamespace

import numpy as np

from scripts.audit_contextual_target_family_gate import (
    _block_slices,
    build_contextual_trial_samples,
    per_recording_contextual_labels,
    screen_precomputed,
)


def fake_recording(**trial_fields) -> SimpleNamespace:
    return SimpleNamespace(
        trials=SimpleNamespace(**trial_fields),
        domain=SimpleNamespace(end=np.asarray([100.0])),
    )


def test_block_slices_break_on_probability_changes() -> None:
    values = np.asarray([0.5, 0.5, 0.2, 0.2, np.nan, 0.8, 0.8])

    assert _block_slices(values) == [(0, 2), (2, 4), (5, 7)]


def test_post_error_uses_previous_trial_feedback() -> None:
    rec = fake_recording(
        stim_on_times=np.arange(5, dtype=np.float64),
        feedback_type=np.asarray([1, -1, 1, -1, -1], dtype=np.float64),
    )

    labels = per_recording_contextual_labels(rec, "post_error")

    assert np.isnan(labels[0])
    assert labels[1:].tolist() == [0.0, 1.0, 0.0, 1.0]


def test_prior_block_switch_labels_early_post_switch_vs_stable() -> None:
    prob = np.asarray([0.5] * 45 + [0.2] * 45, dtype=np.float64)
    rec = fake_recording(stim_on_times=np.arange(len(prob), dtype=np.float64), probability_left=prob)

    labels = per_recording_contextual_labels(rec, "prior_block_switch")

    assert np.all(labels[:45] != labels[:45])
    assert labels[45:55].tolist() == [1.0] * 10
    assert np.all(labels[55:75] != labels[55:75])
    assert labels[75:90].tolist() == [0.0] * 15


def test_prior_block_late_labels_first_and_last_block_edges() -> None:
    prob = np.asarray([0.5] * 42, dtype=np.float64)
    rec = fake_recording(stim_on_times=np.arange(len(prob), dtype=np.float64), probability_left=prob)

    labels = per_recording_contextual_labels(rec, "prior_block_late")

    assert labels[:12].tolist() == [0.0] * 12
    assert np.all(labels[12:30] != labels[12:30])
    assert labels[30:].tolist() == [1.0] * 12


def test_build_contextual_trial_samples_drops_overrun_windows() -> None:
    recs = {
        "r1": SimpleNamespace(
            trials=SimpleNamespace(
                stim_on_times=np.asarray([0.0, 1.0, 99.5]),
                feedback_type=np.asarray([1.0, -1.0, 1.0]),
            ),
            domain=SimpleNamespace(end=np.asarray([100.0])),
        )
    }

    rows = build_contextual_trial_samples(recs, ["r1"], window_len=1.0, target_name="post_error")

    assert rows == [("r1", 1.0, 0.0)]


def test_screen_precomputed_skips_one_class_contextual_holdouts() -> None:
    payload = {
        "target_mode": "post_error",
        "family_names": ["thalamic"],
        "family_true": np.zeros((4, 1), dtype=np.float32),
        "family_shuffle": np.zeros((4, 1), dtype=np.float32),
        "total": np.zeros((4, 1), dtype=np.float32),
        "y": np.asarray([0, 1, 1, 1]),
        "recording_ids": ["r1", "r1", "r2", "r2"],
        "subject_ids": ["s1", "s1", "s2", "s2"],
    }

    rows = screen_precomputed(
        payload,
        holdouts=["s2"],
        l2=10.0,
        min_centered_delta=0.0,
        min_total_delta=0.0,
        min_target_improvement=0.55,
        min_bidirectional_recording_fraction=0.75,
    )

    assert rows == []
