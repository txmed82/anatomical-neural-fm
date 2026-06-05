from __future__ import annotations

import json

from scripts.summarize_anatomy_transfer_evidence import (
    evidence_for_paths,
    render_markdown,
    summarize,
)


def write_json(path, data: dict) -> None:
    path.write_text(json.dumps(data))


def test_summary_flags_failed_or_nonspecific_holdouts(tmp_path) -> None:
    gate = tmp_path / "gate.json"
    ensemble = tmp_path / "ensemble.json"
    write_json(
        gate,
        {
            "holdout": "mouse_a",
            "pass": False,
            "n_passing_seeds": 1,
            "n_seeds": 3,
        },
    )
    write_json(
        ensemble,
        {
            "ensemble_metrics": {
                "region_only": {
                    "centered_auc": 0.52,
                    "full_auc": 0.51,
                    "recording_auc": {"rec1": {"auc": 0.6}, "rec2": {"auc": 0.4}},
                },
                "region_shuffle": {
                    "centered_auc": 0.50,
                    "full_auc": 0.50,
                    "recording_auc": {"rec1": {"auc": 0.5}, "rec2": {"auc": 0.5}},
                },
            },
            "ensemble_paired": {
                "region_only_vs_shuffle": {"improved_fraction": 0.53},
                "shuffle_vs_shared": {"improved_fraction": 0.55},
            },
        },
    )

    row = evidence_for_paths(gate, ensemble)
    summary = summarize([row])

    assert row.paired_specificity_gap == -0.020000000000000018
    assert row.recordings_true_beats_shuffle == 1
    assert summary["decision"] == "redesign_before_more_spend"
    assert "mouse_a" in render_markdown(summary)


def test_summary_allows_replicated_specific_gate_pass(tmp_path) -> None:
    gate = tmp_path / "gate.json"
    ensemble = tmp_path / "ensemble.json"
    write_json(gate, {"holdout": "mouse_a", "pass": True, "n_passing_seeds": 3, "n_seeds": 3})
    write_json(
        ensemble,
        {
            "ensemble_metrics": {
                "region_only": {
                    "centered_auc": 0.56,
                    "full_auc": 0.55,
                    "recording_auc": {"rec1": {"auc": 0.6}, "rec2": {"auc": 0.6}},
                },
                "region_shuffle": {
                    "centered_auc": 0.50,
                    "full_auc": 0.50,
                    "recording_auc": {"rec1": {"auc": 0.5}, "rec2": {"auc": 0.5}},
                },
            },
            "ensemble_paired": {
                "region_only_vs_shuffle": {"improved_fraction": 0.58},
                "shuffle_vs_shared": {"improved_fraction": 0.51},
            },
        },
    )

    summary = summarize([evidence_for_paths(gate, ensemble)])

    assert summary["decision"] == "demo_ready"
