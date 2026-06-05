import numpy as np

from scripts.scan_model_free_region_candidates import candidate_outcome, region_sort_key, scan_candidates


def test_candidate_outcome_requires_total_baseline_and_bidirectional_support() -> None:
    row = {
        "eval_nonzero_fraction": 0.5,
        "centered_delta_vs_shuffle": 0.02,
        "centered_delta_vs_total": -0.01,
        "target0_improved_vs_shuffle": 0.60,
        "target1_improved_vs_shuffle": 0.60,
        "positive_recordings_vs_shuffle": 4,
    }

    assert candidate_outcome(row, min_centered_delta=0.01, min_target_improvement=0.55) == "reject: total baseline"

    row["centered_delta_vs_total"] = 0.02
    assert candidate_outcome(row, min_centered_delta=0.01, min_target_improvement=0.55) == "candidate"


def test_scan_candidates_ranks_clear_single_region_signal() -> None:
    train_y = np.asarray([0, 1, 0, 1, 0, 1, 0, 1], dtype=np.int64)
    eval_y = train_y.copy()
    train_true_x = np.asarray([
        [0.0, 0.0],
        [1.0, 0.0],
        [0.1, 1.0],
        [1.1, 1.0],
        [0.0, 0.0],
        [1.0, 0.0],
        [0.1, 1.0],
        [1.1, 1.0],
    ], dtype=np.float32)
    eval_true_x = train_true_x.copy()
    train_shuffle_x = np.asarray([
        [0.5, 0.0],
        [0.5, 0.0],
        [0.5, 1.0],
        [0.5, 1.0],
        [0.5, 0.0],
        [0.5, 0.0],
        [0.5, 1.0],
        [0.5, 1.0],
    ], dtype=np.float32)
    eval_shuffle_x = train_shuffle_x.copy()

    rows = scan_candidates(
        regions=["signal", "nuisance"],
        train_true_x=train_true_x,
        train_shuffle_x=train_shuffle_x,
        train_y=train_y,
        eval_true_x=eval_true_x,
        eval_shuffle_x=eval_shuffle_x,
        eval_y=eval_y,
        eval_recording_ids=["a", "a", "b", "b", "c", "c", "d", "d"],
        l2=0.1,
        min_centered_delta=0.01,
        min_target_improvement=0.55,
    )

    assert rows[0]["region"] == "signal"
    assert rows[0]["centered_delta_vs_shuffle"] > rows[1]["centered_delta_vs_shuffle"]


def test_region_sort_key_prefers_evaluable_regions_over_absent_artifacts() -> None:
    absent = {
        "outcome": "reject: absent in eval",
        "eval_nonzero_fraction": 0.0,
        "centered_delta_vs_shuffle": 0.5,
        "centered_delta_vs_total": 0.5,
        "positive_recordings_vs_shuffle": 0,
    }
    evaluable = {
        "outcome": "reject: target0",
        "eval_nonzero_fraction": 0.2,
        "centered_delta_vs_shuffle": 0.1,
        "centered_delta_vs_total": 0.1,
        "positive_recordings_vs_shuffle": 1,
    }

    assert region_sort_key(evaluable) > region_sort_key(absent)
