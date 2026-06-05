import json
from pathlib import Path

import pytest

from scripts.audit_pairwise_rank_mismatch import audit, summarize_pairs


def write_predictions(root: Path, holdout: str, arm: str, seed: int, rows: list[dict]) -> None:
    run_dir = root / f"holdout_{holdout}" / f"cloud_choice_{arm}_seed{seed}"
    run_dir.mkdir(parents=True)
    (run_dir / "eval_predictions.jsonl").write_text(
        "\n".join(json.dumps(row) for row in rows) + "\n"
    )


def test_summarize_pairs_detects_downward_shift_not_ranking_gain() -> None:
    true_rows = [
        {"recording_id": "r0", "t0": 0.0, "target": 0, "prob": 0.2},
        {"recording_id": "r0", "t0": 1.0, "target": 0, "prob": 0.2},
        {"recording_id": "r0", "t0": 2.0, "target": 1, "prob": 0.2},
    ]
    shuffle_rows = [
        {"recording_id": "r0", "t0": 0.0, "target": 0, "prob": 0.5},
        {"recording_id": "r0", "t0": 1.0, "target": 0, "prob": 0.5},
        {"recording_id": "r0", "t0": 2.0, "target": 1, "prob": 0.5},
    ]

    result = summarize_pairs(true_rows, shuffle_rows)

    assert result["paired_true_class_improved_fraction"] == pytest.approx(2 / 3)
    assert result["target0_true_class_improved_fraction"] == pytest.approx(1.0)
    assert result["target1_true_class_improved_fraction"] == pytest.approx(0.0)
    assert result["recordings"]["r0"]["classification"] == "downward_probability_shift"


def test_audit_reads_prediction_artifacts(tmp_path: Path) -> None:
    root = tmp_path / "runs"
    holdout = "heldout"
    true_rows = [
        {"recording_id": "r0", "t0": 0.0, "target": 0, "prob": 0.2},
        {"recording_id": "r0", "t0": 1.0, "target": 1, "prob": 0.8},
    ]
    shuffle_rows = [
        {"recording_id": "r0", "t0": 0.0, "target": 0, "prob": 0.4},
        {"recording_id": "r0", "t0": 1.0, "target": 1, "prob": 0.6},
    ]
    write_predictions(root, holdout, "region_only", 0, true_rows)
    write_predictions(root, holdout, "region_shuffle", 0, shuffle_rows)

    result = audit(root, holdout, 0)

    assert result["summary"]["true_minus_shuffle_auc"] == pytest.approx(0.0)
    assert result["summary"]["paired_true_class_improved_fraction"] == pytest.approx(1.0)
