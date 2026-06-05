import numpy as np

from scripts.audit_model_free_region_signal import (
    centered_auc,
    evaluate_feature_set,
    paired_improvement,
    summarize_results,
)


def test_ridge_feature_set_separates_simple_signal() -> None:
    train_x = np.asarray([[0.0], [0.1], [1.0], [1.1]], dtype=np.float32)
    train_y = np.asarray([0, 0, 1, 1], dtype=np.int64)
    eval_x = np.asarray([[0.0], [0.2], [1.0], [1.2]], dtype=np.float32)
    eval_y = np.asarray([0, 0, 1, 1], dtype=np.int64)

    result = evaluate_feature_set(
        name="simple",
        train_x=train_x,
        train_y=train_y,
        eval_x=eval_x,
        eval_y=eval_y,
        eval_recording_ids=["a", "a", "b", "b"],
        l2=0.1,
    )

    assert result["eval_auc"] == 1.0


def test_centered_auc_removes_recording_offsets() -> None:
    scores = np.asarray([0.1, 0.2, 10.2, 10.1], dtype=np.float64)
    labels = np.asarray([0, 1, 0, 1], dtype=np.int64)
    recording_ids = ["a", "a", "b", "b"]

    assert centered_auc(scores, labels, recording_ids) == 0.5


def test_summary_decision_tracks_bidirectional_failure() -> None:
    eval_y = np.asarray([0, 0, 1, 1], dtype=np.int64)
    recording_ids = ["a", "a", "b", "b"]
    results = {
        "total_spikes": {
            "train_auc": 0.5,
            "eval_auc": 0.5,
            "eval_centered_auc": 0.5,
            "eval_scores": np.asarray([0.0, 0.0, 0.0, 0.0]),
            "per_recording_auc": {"a": 0.5, "b": 0.5},
        },
        "region_true": {
            "train_auc": 0.6,
            "eval_auc": 0.6,
            "eval_centered_auc": 0.5,
            "eval_scores": np.asarray([-1.0, -1.0, -1.0, -1.0]),
            "per_recording_auc": {"a": 0.5, "b": 0.5},
        },
        "region_shuffle": {
            "train_auc": 0.5,
            "eval_auc": 0.5,
            "eval_centered_auc": 0.5,
            "eval_scores": np.asarray([0.0, 0.0, 0.0, 0.0]),
            "per_recording_auc": {"a": 0.5, "b": 0.5},
        },
    }

    summary = summarize_results(results, eval_y, recording_ids)
    paired = paired_improvement(results["region_true"]["eval_scores"], results["region_shuffle"]["eval_scores"], eval_y)

    assert paired["target0_improved_fraction"] == 1.0
    assert paired["target1_improved_fraction"] == 0.0
    assert summary["recordings_positive_true_minus_shuffle"] == 0
