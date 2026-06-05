from scripts.audit_neutral_prior_low_contrast_choice_family_gate import (
    build_neutral_prior_low_contrast_choice_trial_samples,
    per_recording_neutral_prior_low_contrast_choice_labels,
    summarize,
    target_name_for_threshold,
)
from tests.test_audit_low_contrast_choice_family_gate import fake_recording, row

import numpy as np


def test_neutral_prior_low_contrast_choice_labels_require_neutral_prior() -> None:
    rec = fake_recording(
        stim_on_times=np.asarray([0.0, 1.0, 2.0, 3.0, 4.0]),
        contrast_left=np.asarray([0.0, 0.0625, 0.0, 0.0, 0.5]),
        contrast_right=np.asarray([0.0, 0.0, 0.0, 0.0, 0.0]),
        choice=np.asarray([-1.0, 1.0, -1.0, 1.0, 1.0]),
        probability_left=np.asarray([0.5, 0.5, 0.8, 0.2, 0.5]),
    )

    labels = per_recording_neutral_prior_low_contrast_choice_labels(rec, max_contrast=0.0625)

    assert labels[0] == 0.0
    assert labels[1] == 1.0
    assert np.isnan(labels[2])
    assert np.isnan(labels[3])
    assert np.isnan(labels[4])


def test_build_neutral_prior_low_contrast_choice_trial_samples_drops_invalid_windows() -> None:
    recs = {
        "r1": fake_recording(
            stim_on_times=np.asarray([0.0, 8.5, 9.5]),
            contrast_left=np.asarray([0.0, 0.0, 0.0]),
            contrast_right=np.asarray([0.0, 0.0, 0.0]),
            choice=np.asarray([-1.0, 1.0, -1.0]),
            probability_left=np.asarray([0.5, 0.5, 0.5]),
        )
    }

    rows = build_neutral_prior_low_contrast_choice_trial_samples(
        recs,
        ["r1"],
        window_len=1.0,
        max_contrast=0.0625,
    )

    assert rows == [("r1", 0.0, 0.0), ("r1", 8.5, 1.0)]


def test_target_name_for_threshold_is_stable() -> None:
    assert target_name_for_threshold(0.0625) == "neutral_prior_low_contrast_choice_le_0.0625"
    assert target_name_for_threshold(0.25) == "neutral_prior_low_contrast_choice_le_0.25"


def test_summarize_neutral_prior_low_contrast_candidate_keeps_gpu_trigger_false() -> None:
    summary = summarize(
        [row("candidate")],
        {
            "neutral_prior_low_contrast_choice_le_0.0625": {
                "n_trials": 100,
                "eligible_recordings": 4,
                "n_recordings": 4,
            }
        },
    )

    assert summary["n_candidates"] == 1
    assert summary["decision"] == "neutral_prior_low_contrast_choice_family_candidate"
    assert not summary["gpu_training_ready"]
