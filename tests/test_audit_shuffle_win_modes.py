from __future__ import annotations

import json

from scripts.audit_shuffle_win_modes import (
    centered_target_separation,
    mean_target_separation,
    run_summary,
)


def write_predictions(root, holdout: str, arm: str, seed: int, rows: list[dict]) -> None:
    run_dir = root / f"holdout_{holdout}" / f"cloud_choice_{arm}_seed{seed}"
    run_dir.mkdir(parents=True)
    (run_dir / "eval_predictions.jsonl").write_text(
        "\n".join(json.dumps(row) for row in rows) + "\n"
    )


def test_centered_target_separation_removes_recording_offsets() -> None:
    rows = [
        {"recording_id": "a", "target": 0, "prob": 0.89},
        {"recording_id": "a", "target": 1, "prob": 0.91},
        {"recording_id": "b", "target": 0, "prob": 0.89},
        {"recording_id": "b", "target": 1, "prob": 0.11},
    ]

    assert mean_target_separation(rows) == -0.38
    assert centered_target_separation(rows) == -0.38


def test_run_summary_flags_shuffle_centered_separation_win(tmp_path) -> None:
    shared = [
        {"recording_id": "rec", "t0": 0.0, "target": 0, "prob": 0.45},
        {"recording_id": "rec", "t0": 1.0, "target": 0, "prob": 0.46},
        {"recording_id": "rec", "t0": 2.0, "target": 1, "prob": 0.55},
        {"recording_id": "rec", "t0": 3.0, "target": 1, "prob": 0.56},
    ]
    true_region = [
        {"recording_id": "rec", "t0": 0.0, "target": 0, "prob": 0.44},
        {"recording_id": "rec", "t0": 1.0, "target": 0, "prob": 0.57},
        {"recording_id": "rec", "t0": 2.0, "target": 1, "prob": 0.53},
        {"recording_id": "rec", "t0": 3.0, "target": 1, "prob": 0.56},
    ]
    shuffle = [
        {"recording_id": "rec", "t0": 0.0, "target": 0, "prob": 0.20},
        {"recording_id": "rec", "t0": 1.0, "target": 0, "prob": 0.30},
        {"recording_id": "rec", "t0": 2.0, "target": 1, "prob": 0.70},
        {"recording_id": "rec", "t0": 3.0, "target": 1, "prob": 0.80},
    ]
    write_predictions(tmp_path, "mouse_a", "shared_baseline", 0, shared)
    write_predictions(tmp_path, "mouse_a", "region_only", 0, true_region)
    write_predictions(tmp_path, "mouse_a", "region_shuffle", 0, shuffle)

    result = run_summary(tmp_path, "mouse_a", "fixture")

    assert result["interpretation"]["diagnosis"] == (
        "shuffle_labels_create_stronger_within_recording_target_separation"
    )
    assert result["ensemble"]["deltas"]["true_minus_shuffle_centered_target_separation"] < 0
    assert result["ensemble"]["recordings"]["rec"]["true_minus_shuffle_centered_sep"] < 0
