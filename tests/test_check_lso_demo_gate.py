from __future__ import annotations

import json

from scripts.check_lso_demo_gate import evaluate_gate


def write_predictions(root, holdout: str, arm: str, seed: int, rows: list[dict]) -> None:
    run_dir = root / f"holdout_{holdout}" / f"cloud_choice_{arm}_seed{seed}"
    run_dir.mkdir(parents=True)
    (run_dir / "eval_predictions.jsonl").write_text("\n".join(json.dumps(row) for row in rows) + "\n")


def test_evaluate_gate_requires_true_to_beat_shared_shuffle_and_paired_threshold(tmp_path) -> None:
    rows_shared = [
        {"recording_id": "rec", "t0": 0.0, "target": 0, "prob": 0.45},
        {"recording_id": "rec", "t0": 1.0, "target": 0, "prob": 0.50},
        {"recording_id": "rec", "t0": 2.0, "target": 0, "prob": 0.55},
        {"recording_id": "rec", "t0": 3.0, "target": 1, "prob": 0.46},
        {"recording_id": "rec", "t0": 4.0, "target": 1, "prob": 0.51},
        {"recording_id": "rec", "t0": 5.0, "target": 1, "prob": 0.56},
    ]
    rows_shuffle = [
        {"recording_id": "rec", "t0": 0.0, "target": 0, "prob": 0.40},
        {"recording_id": "rec", "t0": 1.0, "target": 0, "prob": 0.50},
        {"recording_id": "rec", "t0": 2.0, "target": 0, "prob": 0.60},
        {"recording_id": "rec", "t0": 3.0, "target": 1, "prob": 0.50},
        {"recording_id": "rec", "t0": 4.0, "target": 1, "prob": 0.60},
        {"recording_id": "rec", "t0": 5.0, "target": 1, "prob": 0.70},
    ]
    rows_true = [
        {"recording_id": "rec", "t0": 0.0, "target": 0, "prob": 0.10},
        {"recording_id": "rec", "t0": 1.0, "target": 0, "prob": 0.20},
        {"recording_id": "rec", "t0": 2.0, "target": 0, "prob": 0.30},
        {"recording_id": "rec", "t0": 3.0, "target": 1, "prob": 0.70},
        {"recording_id": "rec", "t0": 4.0, "target": 1, "prob": 0.80},
        {"recording_id": "rec", "t0": 5.0, "target": 1, "prob": 0.90},
    ]
    write_predictions(tmp_path, "mouse_a", "shared_baseline", 0, rows_shared)
    write_predictions(tmp_path, "mouse_a", "region_shuffle", 0, rows_shuffle)
    write_predictions(tmp_path, "mouse_a", "region_only", 0, rows_true)

    result = evaluate_gate(tmp_path, "mouse_a")

    assert result["pass"] is True
    assert result["n_passing_seeds"] == 1
    checks = result["seed_results"][0]["checks"]
    assert all(checks.values())


def test_evaluate_gate_fails_when_paired_true_vs_shuffle_is_too_weak(tmp_path) -> None:
    rows_shared = [
        {"recording_id": "rec", "t0": 0.0, "target": 0, "prob": 0.45},
        {"recording_id": "rec", "t0": 1.0, "target": 1, "prob": 0.55},
    ]
    rows_shuffle = [
        {"recording_id": "rec", "t0": 0.0, "target": 0, "prob": 0.30},
        {"recording_id": "rec", "t0": 1.0, "target": 1, "prob": 0.70},
    ]
    rows_true = [
        {"recording_id": "rec", "t0": 0.0, "target": 0, "prob": 0.29},
        {"recording_id": "rec", "t0": 1.0, "target": 1, "prob": 0.69},
    ]
    write_predictions(tmp_path, "mouse_a", "shared_baseline", 0, rows_shared)
    write_predictions(tmp_path, "mouse_a", "region_shuffle", 0, rows_shuffle)
    write_predictions(tmp_path, "mouse_a", "region_only", 0, rows_true)

    result = evaluate_gate(tmp_path, "mouse_a")

    assert result["pass"] is False
    assert result["seed_results"][0]["checks"]["paired_true_beats_shuffle_threshold"] is False
