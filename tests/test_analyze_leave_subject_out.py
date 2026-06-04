from __future__ import annotations

import json

from scripts.analyze_leave_subject_out import collect


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
