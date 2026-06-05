from types import SimpleNamespace

import numpy as np

from scripts.audit_correct_low_contrast_choice_family_gate import (
    build_correct_low_contrast_choice_trial_samples,
    per_recording_correct_low_contrast_choice_labels,
    summarize,
    target_name_for_threshold,
)


def fake_recording(**trial_fields) -> SimpleNamespace:
    return SimpleNamespace(
        trials=SimpleNamespace(**trial_fields),
        domain=SimpleNamespace(end=np.asarray([10.0])),
    )


def test_correct_low_contrast_choice_labels_drop_errors_and_high_contrast() -> None:
    rec = fake_recording(
        stim_on_times=np.asarray([0.0, 1.0, 2.0, 3.0]),
        contrast_left=np.asarray([0.0, 0.0625, 0.125, 0.0]),
        contrast_right=np.asarray([0.0, 0.0, 0.0, 0.0]),
        choice=np.asarray([-1.0, 1.0, -1.0, 1.0]),
        feedback_type=np.asarray([1.0, -1.0, 1.0, 1.0]),
    )

    labels = per_recording_correct_low_contrast_choice_labels(rec, max_contrast=0.0625)

    assert labels[0] == 0.0
    assert np.isnan(labels[1])
    assert np.isnan(labels[2])
    assert labels[3] == 1.0


def test_build_correct_low_contrast_choice_trial_samples_drops_overrun_windows() -> None:
    recs = {
        "r1": fake_recording(
            stim_on_times=np.asarray([0.0, 8.5, 9.5]),
            contrast_left=np.asarray([0.0, 0.0, 0.0]),
            contrast_right=np.asarray([0.0, 0.0, 0.0]),
            choice=np.asarray([-1.0, 1.0, -1.0]),
            feedback_type=np.asarray([1.0, 1.0, 1.0]),
        )
    }

    rows = build_correct_low_contrast_choice_trial_samples(
        recs,
        ["r1"],
        window_len=1.0,
        max_contrast=0.0625,
    )

    assert rows == [("r1", 0.0, 0.0), ("r1", 8.5, 1.0)]


def test_target_name_for_threshold_is_correct_low_contrast_specific() -> None:
    assert target_name_for_threshold(0.125) == "correct_low_contrast_choice_le_0.125"


def test_summarize_correct_low_contrast_candidate_keeps_gpu_trigger_false() -> None:
    row = {
        "target_mode": "correct_low_contrast_choice_le_0.125",
        "family": "fiber_tracts",
        "holdout": "CSH_ZAD_019",
        "decision": "candidate",
        "centered_delta_vs_shuffle": 0.01,
        "centered_delta_vs_total": 0.02,
        "target0_improved_vs_shuffle": 0.60,
        "target1_improved_vs_shuffle": 0.61,
        "n_bidirectional_recordings": 3,
        "n_recordings": 4,
        "bidirectional_recording_fraction": 0.75,
    }

    summary = summarize(
        [row],
        {
            "correct_low_contrast_choice_le_0.125": {
                "n_trials": 100,
                "eligible_recordings": 4,
                "n_recordings": 4,
            }
        },
    )

    assert summary["n_candidates"] == 1
    assert summary["decision"] == "correct_low_contrast_choice_family_candidate"
    assert not summary["gpu_training_ready"]
