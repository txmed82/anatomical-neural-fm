import numpy as np

from scripts.audit_model_free_region_signal import (
    centered_auc,
    evaluate_feature_set,
    paired_improvement,
    recording_region_unit_fractions,
    summarize_results,
    transform_region_features,
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


def test_transform_region_features_can_use_trial_fractions() -> None:
    features = np.asarray([
        [2.0, 2.0, 0.0],
        [0.0, 0.0, 0.0],
        [1.0, 3.0, 4.0],
    ], dtype=np.float32)

    fractions = transform_region_features(features, "fractions")

    assert np.allclose(fractions[0], [0.5, 0.5, 0.0])
    assert np.allclose(fractions[1], [0.0, 0.0, 0.0])
    assert np.allclose(fractions[2], [0.125, 0.375, 0.5])
    assert transform_region_features(features, "counts") is features


def test_recording_region_unit_fractions_uses_recording_labels() -> None:
    class Units:
        region_acronym = np.asarray(["A", "A", "B", "C"])

    class Rec:
        units = Units()

    fractions = recording_region_unit_fractions(
        {"rec": Rec()},
        ["rec"],
        regions=["A", "B", "C"],
        region_granularity="fine",
        region_control="none",
        seed=0,
    )

    assert np.allclose(fractions["rec"], [0.5, 0.25, 0.25])


def test_transform_region_features_can_center_within_recording() -> None:
    features = np.asarray([
        [1.0, 3.0],
        [3.0, 7.0],
        [10.0, 2.0],
    ], dtype=np.float32)

    centered = transform_region_features(
        features,
        "recording_centered",
        recording_ids=["a", "a", "b"],
    )

    assert np.allclose(centered[0], [-1.0, -2.0])
    assert np.allclose(centered[1], [1.0, 2.0])
    assert np.allclose(centered[2], [0.0, 0.0])


def test_transform_region_features_can_zscore_within_recording() -> None:
    features = np.asarray([
        [1.0, 3.0],
        [3.0, 7.0],
        [10.0, 2.0],
    ], dtype=np.float32)

    zscored = transform_region_features(
        features,
        "recording_zscore",
        recording_ids=["a", "a", "b"],
    )

    assert np.allclose(zscored[0], [-1.0, -1.0])
    assert np.allclose(zscored[1], [1.0, 1.0])
    assert np.allclose(zscored[2], [0.0, 0.0])


def test_transform_region_features_can_residualize_unit_distribution() -> None:
    features = np.asarray([
        [8.0, 2.0],
        [0.0, 0.0],
        [4.0, 6.0],
    ], dtype=np.float32)
    unit_fractions = {
        "a": np.asarray([0.75, 0.25], dtype=np.float32),
        "b": np.asarray([0.25, 0.75], dtype=np.float32),
    }

    residuals = transform_region_features(
        features,
        "unit_residuals",
        recording_ids=["a", "a", "b"],
        unit_region_fractions=unit_fractions,
    )

    assert np.allclose(residuals[0], [0.5, -0.5])
    assert np.allclose(residuals[1], [0.0, 0.0])
    assert np.allclose(residuals[2], [1.5, -1.5])


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
