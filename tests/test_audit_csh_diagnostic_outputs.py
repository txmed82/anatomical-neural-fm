from pathlib import Path

import pytest

from scripts.audit_csh_diagnostic_outputs import (
    cosine,
    parse_run_path,
    prediction_metrics,
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
