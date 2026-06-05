from scripts.audit_extreme_quantile_interpretable_region_filter import (
    is_interpretable_region,
    summarize_rows,
)


def row(region: str, decision: str) -> dict:
    return {
        "target_mode": "response_latency_extreme",
        "region": region,
        "holdout": "CSH_ZAD_019",
        "decision": decision,
        "centered_delta_vs_shuffle": 0.10,
        "centered_delta_vs_total": 0.01,
        "target0_improved_vs_shuffle": 0.60,
        "target1_improved_vs_shuffle": 0.61,
        "n_bidirectional_recordings": 3,
        "n_recordings": 4,
        "bidirectional_recording_fraction": 0.75,
        "eval_nonzero_fraction": 0.5,
    }


def test_interpretable_region_filter_excludes_only_meta_labels() -> None:
    assert not is_interpretable_region("root")
    assert not is_interpretable_region("void")
    assert is_interpretable_region("MOp")
    assert is_interpretable_region("fiber tracts")


def test_summarize_rows_moves_root_candidate_to_excluded_candidates() -> None:
    summary = summarize_rows(
        [row("root", "candidate"), row("MOp", "reject: target0")],
        excluded_regions={"root", "void"},
    )

    assert summary["n_candidates"] == 0
    assert summary["n_excluded_candidates"] == 1
    assert summary["excluded_candidate_rows"] == [
        {"target_mode": "response_latency_extreme", "region": "root", "holdout": "CSH_ZAD_019"}
    ]
    assert summary["decision"] == "no_extreme_quantile_interpretable_region_candidate"
