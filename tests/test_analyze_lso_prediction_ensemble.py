from __future__ import annotations

import json

from scripts.analyze_lso_prediction_ensemble import analyze


def write_predictions(root, holdout: str, arm: str, seed: int, rows: list[dict]) -> None:
    run_dir = root / f"holdout_{holdout}" / f"cloud_choice_{arm}_seed{seed}"
    run_dir.mkdir(parents=True)
    (run_dir / "eval_predictions.jsonl").write_text("\n".join(json.dumps(row) for row in rows) + "\n")


def test_analyze_reports_seed_ensemble_and_recording_paired_metrics(tmp_path) -> None:
    shared = [
        {"recording_id": "rec_a", "t0": 0.0, "target": 0, "prob": 0.45},
        {"recording_id": "rec_a", "t0": 1.0, "target": 1, "prob": 0.55},
        {"recording_id": "rec_b", "t0": 0.0, "target": 0, "prob": 0.45},
        {"recording_id": "rec_b", "t0": 1.0, "target": 1, "prob": 0.55},
    ]
    shuffle = [
        {"recording_id": "rec_a", "t0": 0.0, "target": 0, "prob": 0.40},
        {"recording_id": "rec_a", "t0": 1.0, "target": 1, "prob": 0.60},
        {"recording_id": "rec_b", "t0": 0.0, "target": 0, "prob": 0.35},
        {"recording_id": "rec_b", "t0": 1.0, "target": 1, "prob": 0.65},
    ]
    region_seed0 = [
        {"recording_id": "rec_a", "t0": 0.0, "target": 0, "prob": 0.30},
        {"recording_id": "rec_a", "t0": 1.0, "target": 1, "prob": 0.70},
        {"recording_id": "rec_b", "t0": 0.0, "target": 0, "prob": 0.50},
        {"recording_id": "rec_b", "t0": 1.0, "target": 1, "prob": 0.50},
    ]
    region_seed1 = [
        {"recording_id": "rec_a", "t0": 0.0, "target": 0, "prob": 0.20},
        {"recording_id": "rec_a", "t0": 1.0, "target": 1, "prob": 0.80},
        {"recording_id": "rec_b", "t0": 0.0, "target": 0, "prob": 0.45},
        {"recording_id": "rec_b", "t0": 1.0, "target": 1, "prob": 0.55},
    ]
    for seed in (0, 1):
        write_predictions(tmp_path, "mouse_a", "shared_baseline", seed, shared)
        write_predictions(tmp_path, "mouse_a", "region_shuffle", seed, shuffle)
    write_predictions(tmp_path, "mouse_a", "region_only", 0, region_seed0)
    write_predictions(tmp_path, "mouse_a", "region_only", 1, region_seed1)

    result = analyze(tmp_path, "mouse_a")

    assert result["seeds"] == [0, 1]
    assert result["ensemble_metrics"]["region_only"]["n"] == 4
    assert result["ensemble_metrics"]["region_only"]["recording_auc"]["rec_a"]["auc"] == 1.0
    paired = result["ensemble_paired"]["region_only_vs_shuffle"]
    assert paired["n"] == 4
    assert paired["recordings"]["rec_a"]["improved_fraction"] == 1.0
    assert paired["recordings"]["rec_b"]["improved_fraction"] == 0.0
