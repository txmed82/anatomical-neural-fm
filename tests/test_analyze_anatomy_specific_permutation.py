from __future__ import annotations

import json

from scripts.analyze_anatomy_specific_permutation import (
    anatomy_specific_gate,
    sign_flip_p_value,
)


def write_predictions(root, holdout: str, arm: str, seed: int, rows: list[dict]) -> None:
    run_dir = root / f"holdout_{holdout}" / f"cloud_choice_{arm}_seed{seed}"
    run_dir.mkdir(parents=True)
    (run_dir / "eval_predictions.jsonl").write_text("\n".join(json.dumps(row) for row in rows) + "\n")


def test_sign_flip_p_value_uses_recording_level_deltas() -> None:
    result = sign_flip_p_value({"a": 0.2, "b": 0.1})

    assert result["observed_mean_delta"] == 0.15000000000000002
    assert result["n_recordings"] == 2
    assert result["one_sided_p"] == 0.25


def test_anatomy_specific_gate_requires_specificity_and_recording_support(tmp_path) -> None:
    shared = [
        {"recording_id": "rec_a", "t0": 0.0, "target": 0, "prob": 0.45},
        {"recording_id": "rec_a", "t0": 1.0, "target": 0, "prob": 0.50},
        {"recording_id": "rec_a", "t0": 2.0, "target": 1, "prob": 0.50},
        {"recording_id": "rec_a", "t0": 3.0, "target": 1, "prob": 0.55},
        {"recording_id": "rec_b", "t0": 0.0, "target": 0, "prob": 0.45},
        {"recording_id": "rec_b", "t0": 1.0, "target": 0, "prob": 0.50},
        {"recording_id": "rec_b", "t0": 2.0, "target": 1, "prob": 0.50},
        {"recording_id": "rec_b", "t0": 3.0, "target": 1, "prob": 0.55},
    ]
    shuffle = [
        {"recording_id": "rec_a", "t0": 0.0, "target": 0, "prob": 0.40},
        {"recording_id": "rec_a", "t0": 1.0, "target": 0, "prob": 0.70},
        {"recording_id": "rec_a", "t0": 2.0, "target": 1, "prob": 0.30},
        {"recording_id": "rec_a", "t0": 3.0, "target": 1, "prob": 0.80},
        {"recording_id": "rec_b", "t0": 0.0, "target": 0, "prob": 0.40},
        {"recording_id": "rec_b", "t0": 1.0, "target": 0, "prob": 0.70},
        {"recording_id": "rec_b", "t0": 2.0, "target": 1, "prob": 0.30},
        {"recording_id": "rec_b", "t0": 3.0, "target": 1, "prob": 0.80},
    ]
    region = [
        {"recording_id": "rec_a", "t0": 0.0, "target": 0, "prob": 0.20},
        {"recording_id": "rec_a", "t0": 1.0, "target": 0, "prob": 0.30},
        {"recording_id": "rec_a", "t0": 2.0, "target": 1, "prob": 0.70},
        {"recording_id": "rec_a", "t0": 3.0, "target": 1, "prob": 0.80},
        {"recording_id": "rec_b", "t0": 0.0, "target": 0, "prob": 0.20},
        {"recording_id": "rec_b", "t0": 1.0, "target": 0, "prob": 0.30},
        {"recording_id": "rec_b", "t0": 2.0, "target": 1, "prob": 0.70},
        {"recording_id": "rec_b", "t0": 3.0, "target": 1, "prob": 0.80},
    ]
    write_predictions(tmp_path, "mouse_a", "shared_baseline", 0, shared)
    write_predictions(tmp_path, "mouse_a", "region_shuffle", 0, shuffle)
    write_predictions(tmp_path, "mouse_a", "region_only", 0, region)

    result = anatomy_specific_gate(
        tmp_path,
        "mouse_a",
        alpha=0.25,
        min_recording_support_fraction=1.0,
        min_centered_delta=0.0,
        min_specificity_gap=-1.0,
    )

    assert result["checks"]["recording_support"] is True
    assert result["checks"]["recording_permutation"] is True
    assert result["pass"] is True
