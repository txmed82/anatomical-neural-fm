from types import SimpleNamespace

import numpy as np

from scripts.audit_composite_behavior_target_family_gate import (
    build_composite_trial_samples,
    per_recording_composite_labels,
    summarize,
)
from tests.test_audit_low_contrast_choice_family_gate import row


def fake_recording(**trial_fields) -> SimpleNamespace:
    return SimpleNamespace(
        trials=SimpleNamespace(**trial_fields),
        domain=SimpleNamespace(end=np.asarray([10.0])),
    )


def test_low_contrast_fast_response_uses_filtered_recording_median() -> None:
    rec = fake_recording(
        stim_on_times=np.asarray([0.0, 1.0, 2.0, 3.0]),
        response_times=np.asarray([0.2, 1.5, 2.8, 5.0]),
        contrast_left=np.asarray([0.0, 0.0, 0.25, 0.5]),
        contrast_right=np.asarray([0.0, 0.0, 0.0, 0.0]),
    )

    labels = per_recording_composite_labels(rec, "low_contrast_fast_response_le_0.25")

    assert labels[0] == 1.0
    assert np.isnan(labels[1])
    assert labels[2] == 0.0
    assert np.isnan(labels[3])


def test_post_error_low_contrast_choice_labels_previous_errors_only() -> None:
    rec = fake_recording(
        stim_on_times=np.asarray([0.0, 1.0, 2.0, 3.0]),
        feedback_type=np.asarray([1.0, -1.0, 1.0, -1.0]),
        choice=np.asarray([-1.0, 1.0, -1.0, 1.0]),
        contrast_left=np.asarray([0.0, 0.0, 0.25, 0.5]),
        contrast_right=np.asarray([0.0, 0.0, 0.0, 0.0]),
    )

    labels = per_recording_composite_labels(rec, "post_error_low_contrast_choice_le_0.25")

    assert np.isnan(labels[0])
    assert np.isnan(labels[1])
    assert labels[2] == 0.0
    assert np.isnan(labels[3])


def test_prior_switch_choice_uses_first_trials_after_new_long_block() -> None:
    probability_left = np.asarray([0.5] * 45 + [0.2] * 45, dtype=np.float64)
    choice = np.asarray([-1.0, 1.0] * 45, dtype=np.float64)
    rec = fake_recording(
        stim_on_times=np.arange(len(probability_left), dtype=np.float64),
        probability_left=probability_left,
        choice=choice,
        contrast_left=np.zeros(len(probability_left), dtype=np.float64),
        contrast_right=np.zeros(len(probability_left), dtype=np.float64),
    )

    labels = per_recording_composite_labels(rec, "prior_switch_choice_le_1")

    assert np.all(labels[:45] != labels[:45])
    assert labels[45:55].tolist() == choice[45:55].clip(min=0.0).tolist()
    assert np.all(labels[55:] != labels[55:])


def test_build_composite_trial_samples_drops_invalid_windows() -> None:
    recs = {
        "r1": fake_recording(
            stim_on_times=np.asarray([0.0, 8.5, 9.5]),
            response_times=np.asarray([0.2, 9.5, 9.8]),
            contrast_left=np.asarray([0.0, 0.0, 0.0]),
            contrast_right=np.asarray([0.0, 0.0, 0.0]),
        )
    }

    rows = build_composite_trial_samples(
        recs,
        ["r1"],
        window_len=1.0,
        target_name="low_contrast_fast_response_le_0.25",
    )

    assert rows == [("r1", 0.0, 1.0), ("r1", 8.5, 0.0)]


def test_summarize_composite_candidate_keeps_gpu_trigger_false() -> None:
    summary = summarize(
        [row("candidate")],
        {"low_contrast_fast_response_le_0.25": {"n_trials": 100, "eligible_recordings": 4, "n_recordings": 4}},
    )

    assert summary["n_candidates"] == 1
    assert summary["decision"] == "composite_behavior_target_family_candidate"
    assert not summary["gpu_training_ready"]
