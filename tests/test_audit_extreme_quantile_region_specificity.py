from scripts.audit_extreme_quantile_region_specificity import summarize_rows


def row(region: str, decision: str, delta: float, bidir: int) -> dict:
    return {
        "target_mode": "response_latency_extreme",
        "region": region,
        "holdout": "NR_0019",
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


def test_summarize_rows_reports_region_candidates_first() -> None:
    summary = summarize_rows([
        row("VISp", "reject: shuffle", 0.02, 4),
        row("MOp", "candidate", 0.01, 3),
    ])

    assert summary["n_regions"] == 2
    assert summary["n_candidates"] == 1
    assert summary["decision"] == "extreme_quantile_region_candidate"
    assert summary["top_rows"][0]["region"] == "MOp"


def test_summarize_rows_rejects_without_candidates() -> None:
    summary = summarize_rows([row("VISp", "reject: shuffle", -0.01, 4)])

    assert summary["n_candidates"] == 0
    assert summary["decision"] == "no_extreme_quantile_region_candidate"
