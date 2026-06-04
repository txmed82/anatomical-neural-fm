from __future__ import annotations

import json

from scripts.analyze_sweep import load_run


def test_load_run_selects_highest_auc_not_lowest_loss(tmp_path) -> None:
    run_dir = tmp_path / "cloud_choice_pure_anatomy_seed0"
    run_dir.mkdir()
    rows = [
        {"event": "eval", "step": 150, "eval_loss": 0.5, "eval_auc": 0.51},
        {"event": "eval", "step": 300, "eval_loss": 0.7, "eval_auc": 0.63},
        {"event": "done"},
    ]
    (run_dir / "log.jsonl").write_text("\n".join(json.dumps(row) for row in rows) + "\n")

    out = load_run(run_dir)

    assert out is not None
    assert out["best"]["step"] == 300
    assert out["best_loss"]["step"] == 150
