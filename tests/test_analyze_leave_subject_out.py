from __future__ import annotations

import json

from scripts.analyze_leave_subject_out import (
    PAIRED_TRUE_VS_SHUFFLE_GATE,
    collect,
    collect_full,
    collect_recording_centered,
    collect_true_vs_shuffle_gate,
    paired_true_improvement,
    recording_centered_auc,
)


def write_run(root, holdout: str, arm: str, seed: int, auc: float) -> None:
    run_dir = root / f"holdout_{holdout}" / f"cloud_choice_{arm}_seed{seed}"
    run_dir.mkdir(parents=True)
    rows = [
        {"event": "eval", "step": 150, "eval_loss": 0.7, "eval_auc": auc},
        {"event": "done"},
    ]
    (run_dir / "log.jsonl").write_text("\n".join(json.dumps(row) for row in rows) + "\n")


def test_collect_groups_auc_by_holdout_arm_and_seed(tmp_path) -> None:
    write_run(tmp_path, "mouse_a", "shared_baseline", 0, 0.50)
    write_run(tmp_path, "mouse_a", "region_only", 0, 0.56)
    write_run(tmp_path, "mouse_b", "shared_baseline", 1, 0.51)
    write_run(tmp_path, "mouse_b", "region_only", 1, 0.49)

    runs = collect(tmp_path)

    assert runs["mouse_a"]["shared_baseline"][0] == 0.50
    assert runs["mouse_a"]["region_only"][0] == 0.56
    assert runs["mouse_b"]["shared_baseline"][1] == 0.51
    assert runs["mouse_b"]["region_only"][1] == 0.49


def test_collect_full_prefers_full_eval_log_metric(tmp_path) -> None:
    run_dir = tmp_path / "holdout_mouse_a" / "cloud_choice_region_only_seed0"
    run_dir.mkdir(parents=True)
    rows = [
        {"event": "full_eval", "step": 150, "full_eval_auc": 0.61},
        {"event": "full_eval", "step": 300, "full_eval_auc": 0.63},
    ]
    (run_dir / "log.jsonl").write_text("\n".join(json.dumps(row) for row in rows) + "\n")

    runs = collect_full(tmp_path)

    assert runs["mouse_a"]["region_only"][0] == 0.63


def test_collect_full_falls_back_to_eval_predictions(tmp_path) -> None:
    run_dir = tmp_path / "holdout_mouse_a" / "cloud_choice_region_only_seed2"
    run_dir.mkdir(parents=True)
    rows = [
        {"target": 0, "prob": 0.1},
        {"target": 0, "prob": 0.2},
        {"target": 1, "prob": 0.8},
        {"target": 1, "prob": 0.9},
    ]
    (run_dir / "eval_predictions.jsonl").write_text("\n".join(json.dumps(row) for row in rows) + "\n")

    runs = collect_full(tmp_path)

    assert runs["mouse_a"]["region_only"][2] == 1.0


def test_recording_centered_auc_removes_recording_offsets() -> None:
    rows = [
        {"recording_id": "a", "target": 0, "prob": 0.89},
        {"recording_id": "a", "target": 1, "prob": 0.91},
        {"recording_id": "b", "target": 0, "prob": 0.09},
        {"recording_id": "b", "target": 1, "prob": 0.11},
    ]

    assert recording_centered_auc(rows) == 1.0


def test_paired_true_improvement_counts_target_direction() -> None:
    baseline = [
        {"recording_id": "rec", "t0": 0.0, "target": 0, "prob": 0.4},
        {"recording_id": "rec", "t0": 1.0, "target": 1, "prob": 0.6},
    ]
    candidate = [
        {"recording_id": "rec", "t0": 0.0, "target": 0, "prob": 0.3},
        {"recording_id": "rec", "t0": 1.0, "target": 1, "prob": 0.55},
    ]

    assert paired_true_improvement(candidate, baseline) == (2, 0.5)


def write_predictions(root, holdout: str, arm: str, seed: int, rows: list[dict]) -> None:
    run_dir = root / f"holdout_{holdout}" / f"cloud_choice_{arm}_seed{seed}"
    run_dir.mkdir(parents=True)
    (run_dir / "eval_predictions.jsonl").write_text("\n".join(json.dumps(row) for row in rows) + "\n")


def test_collect_recording_centered_groups_by_holdout_arm_seed(tmp_path) -> None:
    write_predictions(
        tmp_path,
        "mouse_a",
        "region_only",
        0,
        [
            {"recording_id": "a", "t0": 0.0, "target": 0, "prob": 0.89},
            {"recording_id": "a", "t0": 1.0, "target": 1, "prob": 0.91},
            {"recording_id": "b", "t0": 2.0, "target": 0, "prob": 0.09},
            {"recording_id": "b", "t0": 3.0, "target": 1, "prob": 0.11},
        ],
    )

    runs = collect_recording_centered(tmp_path)

    assert runs["mouse_a"]["region_only"][0] == 1.0


def test_collect_true_vs_shuffle_gate_uses_region_only_against_shuffle(tmp_path) -> None:
    rows_shuffle = [
        {"recording_id": "rec", "t0": 0.0, "target": 0, "prob": 0.4},
        {"recording_id": "rec", "t0": 1.0, "target": 1, "prob": 0.6},
    ]
    rows_true = [
        {"recording_id": "rec", "t0": 0.0, "target": 0, "prob": 0.3},
        {"recording_id": "rec", "t0": 1.0, "target": 1, "prob": 0.7},
    ]
    write_predictions(tmp_path, "mouse_a", "region_shuffle", 1, rows_shuffle)
    write_predictions(tmp_path, "mouse_a", "region_only", 1, rows_true)

    gates = collect_true_vs_shuffle_gate(tmp_path)

    assert gates["mouse_a"][1] == (2, 1.0)
    assert PAIRED_TRUE_VS_SHUFFLE_GATE == 0.55
