import json
from pathlib import Path

from scripts.summarize_experiment_state import (
    local_probe_outcome,
    read_cache_audit,
    read_slice_result,
    read_local_probe_result,
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


def test_local_probe_matrix_rejects_failed_target_class(tmp_path: Path) -> None:
    gate_path = tmp_path / "gate.json"
    mismatch_path = tmp_path / "mismatch.json"
    gate_path.write_text(json.dumps({
        "pass": False,
        "metrics": {
            "centered_auc_delta_vs_shuffle": -0.005,
            "paired_true_vs_shuffle": 0.494,
            "paired_specificity_gap": 0.010,
            "target0_true_class_improved": 0.556,
            "target1_true_class_improved": 0.419,
            "recordings_positive": 2,
            "n_recordings": 4,
        },
    }))
    mismatch_path.write_text(json.dumps({
        "decision": "paired_metric_not_recording_rank_stable",
        "summary": {"true_minus_shuffle_auc": -0.009},
    }))

    row = read_local_probe_result("probe", gate_path, mismatch_path)
    markdown = render_markdown([], [], local_probes=[row])

    assert row is not None
    assert local_probe_outcome(row) == "reject: centered AUC, target1, recording support, mismatch"
    assert "Local Probe Matrix" in markdown
    assert "paired_metric_not_recording_rank_stable" in markdown


def test_read_cache_audit_parses_missing_without_present(tmp_path: Path) -> None:
    path = tmp_path / "cache.md"
    path.write_text("\n".join([
        "# BrainSet S3 Cache Audit",
        "",
        "Present: 1/3 (33.3%)",
        "",
        "## Missing",
        "",
        "| filename |",
        "|---|",
        "| `missing-a.h5` |",
        "| `missing-b.h5` |",
        "",
        "## Shard Build Plan",
        "",
        "| shard | recordings | present | missing | build command |",
        "|---:|---:|---:|---:|---|",
        "| 0 | 2 | 1 | 1 | `build 0` |",
        "",
        "## Present",
        "",
        "| filename |",
        "|---|",
        "| `present.h5` |",
    ]))

    audit = read_cache_audit(path)

    assert audit is not None
    assert audit["present"] == 1
    assert audit["total"] == 3
    assert audit["missing_count"] == 2
    assert audit["missing_files"] == ["missing-a.h5", "missing-b.h5"]
    assert audit["shards_with_missing"] == [{"shard": 0, "recordings": 2, "present": 1, "missing": 1}]
