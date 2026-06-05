from types import SimpleNamespace

import numpy as np

from scripts.audit_derived_target_family_gate import (
    build_derived_trial_samples,
    per_recording_derived_labels,
    screen_precomputed,
    target_balance,
)


def fake_recording(**trial_fields) -> SimpleNamespace:
    return SimpleNamespace(
        trials=SimpleNamespace(**trial_fields),
        domain=SimpleNamespace(end=np.asarray([10.0])),
    )


def test_contrast_strength_labels_split_by_recording_median() -> None:
    rec = fake_recording(
        stim_on_times=np.asarray([0.0, 1.0, 2.0, 3.0, 4.0]),
        contrast_left=np.asarray([0.0, 0.1, 0.5, 0.9, np.nan]),
        contrast_right=np.asarray([0.0, 0.0, 0.0, 0.0, 0.0]),
    )

    labels = per_recording_derived_labels(rec, "contrast_strength")

    assert np.isnan(labels[0])
    assert labels[1] == 0.0
    assert np.isnan(labels[2])
    assert labels[3] == 1.0
    assert np.isnan(labels[4])


def test_response_latency_labels_fast_trials_as_one() -> None:
    rec = fake_recording(
        stim_on_times=np.asarray([0.0, 1.0, 2.0, 3.0]),
        response_times=np.asarray([0.2, 1.8, 2.5, np.nan]),
    )

    labels = per_recording_derived_labels(rec, "response_latency")

    assert labels[0] == 1.0
    assert labels[1] == 0.0
    assert np.isnan(labels[2])
    assert np.isnan(labels[3])


def test_prior_engaged_labels_biased_blocks() -> None:
    rec = fake_recording(
        stim_on_times=np.asarray([0.0, 1.0, 2.0]),
        probability_left=np.asarray([0.5, 0.2, 0.8]),
    )

    assert per_recording_derived_labels(rec, "prior_engaged").tolist() == [0.0, 1.0, 1.0]


def test_build_derived_trial_samples_drops_nan_and_overrun_windows() -> None:
    recs = {
        "r1": fake_recording(
            stim_on_times=np.asarray([0.0, 8.5, 9.5]),
            probability_left=np.asarray([0.5, 0.2, 0.8]),
        )
    }

    rows = build_derived_trial_samples(recs, ["r1"], window_len=1.0, target_name="prior_engaged")

    assert rows == [("r1", 0.0, 0.0), ("r1", 8.5, 1.0)]


def test_target_balance_counts_eligible_recordings_and_subjects() -> None:
    rows = [
        ("r1", 0.0, 0.0),
        ("r1", 1.0, 1.0),
        ("r1", 2.0, 1.0),
        ("r2", 0.0, 1.0),
    ]

    balance = target_balance(rows, {"r1": "s1", "r2": "s2"}, min_class_trials=1)

    assert balance["n_recordings"] == 2
    assert balance["eligible_recordings"] == 1
    assert balance["subject_rows"][0]["eligible_recordings"] == 1
    assert balance["subject_rows"][1]["eligible_recordings"] == 0


def test_screen_precomputed_skips_one_class_holdouts() -> None:
    payload = {
        "target_mode": "prior_engaged",
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
