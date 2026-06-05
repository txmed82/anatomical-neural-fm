from pathlib import Path

import pytest

from scripts.audit_csh_diagnostic_outputs import (
    PAIRED_TRUE_VS_SHUFFLE_GATE,
    cosine,
    paired_delta_metrics,
    parse_run_path,
    prediction_metrics,
    recording_centered_auc,
    trial_key,
)


def test_parse_run_path_reads_arm_and_seed() -> None:
    path = Path("runs/root/holdout_CSH/cloud_choice_region_shuffle_seed12/eval_predictions.jsonl")

    assert parse_run_path(path) == ("region_shuffle", 12)


def test_prediction_metrics_computes_auc_accuracy_and_prob_means() -> None:
    rows = [
        {"target": 0, "prob": 0.1},
        {"target": 0, "prob": 0.4},
        {"target": 1, "prob": 0.8},
        {"target": 1, "prob": 0.9},
    ]

    metrics = prediction_metrics(rows)

    assert metrics.n == 4
    assert metrics.auc == pytest.approx(1.0)
    assert metrics.acc == pytest.approx(1.0)
    assert metrics.mean_prob_target0 == pytest.approx(0.25)
    assert metrics.mean_prob_target1 == pytest.approx(0.85)


def test_cosine_handles_orthogonal_vectors() -> None:
    assert cosine([1.0, 0.0], [0.0, 2.0]) == pytest.approx(0.0)


def test_trial_key_uses_recording_time_and_target() -> None:
    row = {"recording_id": "rec", "t0": 12.5, "target": 1, "prob": 0.8}

    assert trial_key(row) == ("rec", 12.5, 1)


def test_paired_delta_metrics_tracks_probability_and_true_class_improvement() -> None:
    baseline = [
        {"recording_id": "rec", "t0": 0.0, "target": 0, "prob": 0.4},
        {"recording_id": "rec", "t0": 1.0, "target": 1, "prob": 0.6},
        {"recording_id": "rec", "t0": 2.0, "target": 1, "prob": 0.7},
    ]
    candidate = [
        {"recording_id": "rec", "t0": 0.0, "target": 0, "prob": 0.3},
        {"recording_id": "rec", "t0": 1.0, "target": 1, "prob": 0.65},
        {"recording_id": "rec", "t0": 2.0, "target": 1, "prob": 0.6},
        {"recording_id": "rec", "t0": 3.0, "target": 1, "prob": 0.9},
    ]

    metrics = paired_delta_metrics(candidate, baseline)

    assert metrics.n == 3
    assert metrics.mean_delta == pytest.approx((-0.1 + 0.05 - 0.1) / 3)
    assert metrics.mean_abs_delta == pytest.approx((0.1 + 0.05 + 0.1) / 3)
    assert metrics.mean_delta_target0 == pytest.approx(-0.1)
    assert metrics.mean_delta_target1 == pytest.approx(-0.025)
    assert metrics.frac_true_probability_improved == pytest.approx(2 / 3)


def test_recording_centered_auc_removes_recording_offsets() -> None:
    rows = [
        {"recording_id": "a", "target": 0, "prob": 0.89},
        {"recording_id": "a", "target": 1, "prob": 0.91},
        {"recording_id": "b", "target": 0, "prob": 0.09},
        {"recording_id": "b", "target": 1, "prob": 0.11},
    ]

    raw = prediction_metrics(rows)
    centered = recording_centered_auc(rows)

    assert raw.auc == pytest.approx(0.75)
    assert centered.n == 4
    assert centered.auc == pytest.approx(1.0)


def test_paired_true_vs_shuffle_demo_gate_requires_margin() -> None:
    assert PAIRED_TRUE_VS_SHUFFLE_GATE == pytest.approx(0.55)
