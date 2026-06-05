from scripts.audit_extreme_quantile_seed_sensitivity import summarize_case


def test_summarize_case_requires_all_candidate_seeds(monkeypatch) -> None:
    rows = {
        0: {"decision": "candidate", "centered_delta_vs_shuffle": 0.001},
        1: {"decision": "candidate", "centered_delta_vs_shuffle": 0.001},
        2: {"decision": "reject: shuffle", "centered_delta_vs_shuffle": -0.001},
    }

    def fake_load_case_row(_case: dict, seed: int) -> dict:
        return {
            "centered_delta_vs_total": 0.001,
            "target0_improved_vs_shuffle": 0.60,
            "target1_improved_vs_shuffle": 0.61,
            "n_bidirectional_recordings": 4,
        } | rows[seed]

    monkeypatch.setattr("scripts.audit_extreme_quantile_seed_sensitivity.load_case_row", fake_load_case_row)

    summary = summarize_case(
        {"target_mode": "target", "family": "family", "holdout": "subject"},
        [0, 1, 2],
        min_positive_seed_fraction=0.5,
    )

    assert summary["n_positive_shuffle_delta_seeds"] == 2
    assert summary["n_candidate_seeds"] == 2
    assert not summary["robust_shuffle_seed_candidate"]


def test_summarize_case_accepts_consistent_candidate_seeds(monkeypatch) -> None:
    def fake_load_case_row(_case: dict, _seed: int) -> dict:
        return {
            "decision": "candidate",
            "centered_delta_vs_shuffle": 0.001,
            "centered_delta_vs_total": 0.001,
            "target0_improved_vs_shuffle": 0.60,
            "target1_improved_vs_shuffle": 0.61,
            "n_bidirectional_recordings": 4,
        }

    monkeypatch.setattr("scripts.audit_extreme_quantile_seed_sensitivity.load_case_row", fake_load_case_row)

    summary = summarize_case(
        {"target_mode": "target", "family": "family", "holdout": "subject"},
        [0, 1, 2],
        min_positive_seed_fraction=0.8,
    )

    assert summary["n_candidate_seeds"] == 3
    assert summary["robust_shuffle_seed_candidate"]
