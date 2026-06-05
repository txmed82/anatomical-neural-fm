from __future__ import annotations

import json

from scripts.analyze_leave_subject_out import collect, collect_full


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
