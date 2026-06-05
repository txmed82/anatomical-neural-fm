import json
from pathlib import Path

from scripts.summarize_experiment_state import (
    read_slice_result,
    read_strict_gate,
    render_markdown,
    slice_outcome,
    strict_gate_outcome,
    summarize,
)


def test_strict_gate_outcome_lists_failed_checks(tmp_path: Path) -> None:
    path = tmp_path / "gate.json"
    path.write_text(json.dumps({
        "holdout": "mouse",
        "pass": False,
        "metrics": {
            "centered_auc_delta_vs_shuffle": 0.001,
            "paired_true_vs_shuffle": 0.44,
            "paired_specificity_gap": -0.10,
            "recording_sign_flip": {"one_sided_p": 0.25},
        },
    }))

    row = read_strict_gate("pilot", path)

    assert row is not None
    assert row.holdout == "mouse"
    assert strict_gate_outcome(row) == "fail: small centered delta, paired gate, specificity, sign-flip"


def test_slice_result_parses_true_minus_shuffle(tmp_path: Path) -> None:
    path = tmp_path / "results.md"
    path.write_text("\n".join([
        "| holdout | arm | n_seeds | mean_AUC | mean_delta_vs_shared | seed_deltas |",
        "|---|---|---:|---:|---:|---|",
        "| NYU-12 | region_only | 3 | 0.513 | +0.013 | +0.067, +0.021, -0.048 |",
        "| NYU-12 | region_shuffle | 3 | 0.520 | +0.020 | +0.038, +0.015, +0.007 |",
    ]))

    row = read_slice_result("slice", path, "NYU-12")

    assert row is not None
    assert row.true_delta == 0.013
    assert row.shuffle_delta == 0.020
    assert row.true_positive == "2/3"
    assert row.shuffle_positive == "3/3"
    assert slice_outcome(row) == "shuffle >= true"


def test_render_markdown_keeps_no_paid_broadening_decision(tmp_path: Path) -> None:
    gate_path = tmp_path / "gate.json"
    gate_path.write_text(json.dumps({
        "holdout": "mouse",
        "pass": False,
        "metrics": {"paired_true_vs_shuffle": 0.44},
    }))
    gate = read_strict_gate("pilot", gate_path)
    summary = summarize([gate], [])
    markdown = render_markdown([gate], [])

    assert summary["decision"] == "no_paid_broadening_without_new_mechanism"
    assert "Current Anatomy-Transfer Experiment State" in markdown
    assert "No current strict-gate artifact supports paid broadening" in markdown
