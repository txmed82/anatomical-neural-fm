from scripts.audit_extreme_quantile_cutoff_sensitivity import summarize_cutoff


def test_cutoff_summary_rejects_partial_seed_support(monkeypatch) -> None:
    rows = [
        {"decision": "candidate", "centered_delta_vs_shuffle": 0.001},
        {"decision": "reject: shuffle", "centered_delta_vs_shuffle": -0.001},
    ]

    def fake_load_case_row(_path: str) -> dict:
        row = rows.pop(0)
        return {
            "centered_delta_vs_total": 0.001,
            "target0_improved_vs_shuffle": 0.60,
            "target1_improved_vs_shuffle": 0.61,
            "n_bidirectional_recordings": 4,
        } | row

    monkeypatch.setattr("scripts.audit_extreme_quantile_cutoff_sensitivity.load_case_row", fake_load_case_row)

    summary = summarize_cutoff(
        {"label": "x", "low_quantile": 0.2, "high_quantile": 0.8, "paths": ["a", "b"]},
        min_positive_seed_fraction=0.5,
    )

    assert summary["n_candidate_seeds"] == 1
    assert not summary["robust_cutoff_candidate"]


def test_cutoff_summary_accepts_all_candidate_seeds(monkeypatch) -> None:
    def fake_load_case_row(_path: str) -> dict:
        return {
            "decision": "candidate",
            "centered_delta_vs_shuffle": 0.001,
            "centered_delta_vs_total": 0.001,
            "target0_improved_vs_shuffle": 0.60,
            "target1_improved_vs_shuffle": 0.61,
            "n_bidirectional_recordings": 4,
        }

    monkeypatch.setattr("scripts.audit_extreme_quantile_cutoff_sensitivity.load_case_row", fake_load_case_row)

    summary = summarize_cutoff(
        {"label": "x", "low_quantile": 0.2, "high_quantile": 0.8, "paths": ["a", "b"]},
        min_positive_seed_fraction=0.8,
    )

    assert summary["n_candidate_seeds"] == 2
    assert summary["robust_cutoff_candidate"]
