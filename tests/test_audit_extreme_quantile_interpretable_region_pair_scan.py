import json

from scripts.audit_extreme_quantile_interpretable_region_pair_scan import (
    pair_label,
    region_pairs,
    select_regions_from_source,
    summarize_rows,
)


def source_row(region: str, decision: str, delta: float, bidir: int) -> dict:
    return {
        "target_mode": "response_latency_extreme",
        "region": region,
        "holdout": "CSH_ZAD_019",
        "decision": decision,
        "centered_delta_vs_shuffle": delta,
        "centered_delta_vs_total": 0.01,
        "target0_improved_vs_shuffle": 0.60,
        "target1_improved_vs_shuffle": 0.61,
        "n_bidirectional_recordings": bidir,
        "n_recordings": 4,
        "bidirectional_recording_fraction": bidir / 4,
        "eval_nonzero_fraction": 0.5,
    }


def pair_row(pair: str, decision: str, delta: float, bidir: int) -> dict:
    return {
        "target_mode": "response_latency_extreme",
        "region_pair": pair,
        "regions": pair.split("+"),
        "holdout": "CSH_ZAD_019",
        "decision": decision,
        "centered_delta_vs_shuffle": delta,
        "centered_delta_vs_total": 0.01,
        "target0_improved_vs_shuffle": 0.60,
        "target1_improved_vs_shuffle": 0.61,
        "n_bidirectional_recordings": bidir,
        "n_recordings": 4,
        "bidirectional_recording_fraction": bidir / 4,
        "eval_nonzero_fraction": 0.5,
    }


def test_region_pairs_are_unique_unordered_pairs() -> None:
    assert pair_label("VISp", "MOp") == "VISp+MOp"
    assert region_pairs(["VISp", "MOp", "CA"]) == [
        ("VISp", "MOp"),
        ("VISp", "CA"),
        ("MOp", "CA"),
    ]


def test_select_regions_from_source_ranks_and_excludes_meta_labels(tmp_path) -> None:
    source = tmp_path / "source.json"
    source.write_text(json.dumps({
        "rows": [
            source_row("root", "candidate", 1.0, 4),
            source_row("VISp", "reject: target0", 0.2, 3),
            source_row("MOp", "reject: shuffle", 0.3, 2),
            source_row("CA", "reject: shuffle", 0.1, 4),
        ]
    }))

    assert select_regions_from_source(source, top_n_regions=2) == ["CA", "VISp"]


def test_summarize_rows_reports_pair_candidates_without_training_trigger() -> None:
    summary = summarize_rows([
        pair_row("VISp+MOp", "reject: target0", 0.2, 4),
        pair_row("VISp+CA", "candidate", 0.1, 3),
    ])

    assert summary["n_region_pairs"] == 2
    assert summary["n_candidates"] == 1
    assert summary["decision"] == "extreme_quantile_interpretable_region_pair_candidate"
    assert not summary["gpu_training_ready"]
    assert summary["top_rows"][0]["region_pair"] == "VISp+CA"
