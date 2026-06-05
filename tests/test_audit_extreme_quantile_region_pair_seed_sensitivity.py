from scripts.audit_extreme_quantile_region_pair_seed_sensitivity import summarize_case


def test_region_pair_seed_summary_rejects_seed_fragile_pair(monkeypatch) -> None:
    rows = {
        0: {"decision": "candidate", "centered_delta_vs_shuffle": 0.10, "n_bidirectional_recordings": 3},
        1: {"decision": "reject: target0", "centered_delta_vs_shuffle": 0.08, "n_bidirectional_recordings": 2},
    }

    def fake_load_case_row(_case: dict, seed: int) -> dict:
        return {
            "centered_delta_vs_total": 0.01,
            "target0_improved_vs_shuffle": 0.55,
            "target1_improved_vs_shuffle": 0.56,
            "n_recordings": 4,
        } | rows[seed]

    monkeypatch.setattr(
        "scripts.audit_extreme_quantile_region_pair_seed_sensitivity.load_case_row",
        fake_load_case_row,
    )

    summary = summarize_case(
        {"target_mode": "response_latency_extreme", "region_pair": "PRT+VP", "holdout": "CSH_ZAD_019"},
        [0, 1],
        min_positive_seed_fraction=1.0,
    )

    assert summary["n_positive_shuffle_delta_seeds"] == 2
    assert summary["n_candidate_seeds"] == 1
    assert not summary["robust_region_pair_seed_candidate"]


def test_region_pair_seed_summary_accepts_all_candidate_seeds(monkeypatch) -> None:
    def fake_load_case_row(_case: dict, _seed: int) -> dict:
        return {
            "decision": "candidate",
            "centered_delta_vs_shuffle": 0.10,
            "centered_delta_vs_total": 0.01,
            "target0_improved_vs_shuffle": 0.60,
            "target1_improved_vs_shuffle": 0.61,
            "n_bidirectional_recordings": 3,
            "n_recordings": 4,
        }

    monkeypatch.setattr(
        "scripts.audit_extreme_quantile_region_pair_seed_sensitivity.load_case_row",
        fake_load_case_row,
    )

    summary = summarize_case(
        {"target_mode": "response_latency_extreme", "region_pair": "PRT+VP", "holdout": "CSH_ZAD_019"},
        [0, 1],
        min_positive_seed_fraction=1.0,
    )

    assert summary["n_candidate_seeds"] == 2
    assert summary["robust_region_pair_seed_candidate"]
