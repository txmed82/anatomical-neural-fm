from scripts.audit_low_contrast_choice_seed_sensitivity import summarize_case


def test_low_contrast_seed_summary_rejects_seed_fragile_candidate(monkeypatch) -> None:
    rows = {
        0: {"decision": "candidate", "centered_delta_vs_shuffle": 0.02, "n_bidirectional_recordings": 3},
        1: {"decision": "reject: target1", "centered_delta_vs_shuffle": 0.01, "n_bidirectional_recordings": 1},
    }

    def fake_load_case_row(_seed: int, _case: dict) -> dict:
        return {
            "centered_delta_vs_total": 0.20,
            "target0_improved_vs_shuffle": 0.55,
            "target1_improved_vs_shuffle": 0.56,
            "n_recordings": 4,
        } | rows[_seed]

    monkeypatch.setattr(
        "scripts.audit_low_contrast_choice_seed_sensitivity.load_case_row",
        fake_load_case_row,
    )

    summary = summarize_case(
        seeds=[0, 1],
        case={"target_mode": "low_contrast_choice_le_0.125", "family": "fiber_tracts", "holdout": "CSH_ZAD_019"},
        min_positive_seed_fraction=1.0,
    )

    assert summary["n_positive_shuffle_delta_seeds"] == 2
    assert summary["n_candidate_seeds"] == 1
    assert not summary["robust_low_contrast_choice_seed_candidate"]


def test_low_contrast_seed_summary_accepts_all_candidate_seeds(monkeypatch) -> None:
    def fake_load_case_row(_seed: int, _case: dict) -> dict:
        return {
            "decision": "candidate",
            "centered_delta_vs_shuffle": 0.02,
            "centered_delta_vs_total": 0.20,
            "target0_improved_vs_shuffle": 0.60,
            "target1_improved_vs_shuffle": 0.61,
            "n_bidirectional_recordings": 3,
            "n_recordings": 4,
        }

    monkeypatch.setattr(
        "scripts.audit_low_contrast_choice_seed_sensitivity.load_case_row",
        fake_load_case_row,
    )

    summary = summarize_case(
        seeds=[0, 1],
        case={"target_mode": "low_contrast_choice_le_0.125", "family": "fiber_tracts", "holdout": "CSH_ZAD_019"},
        min_positive_seed_fraction=1.0,
    )

    assert summary["n_candidate_seeds"] == 2
    assert summary["robust_low_contrast_choice_seed_candidate"]
