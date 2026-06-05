from scripts.audit_composite_behavior_target_l2_seed_sensitivity import build_report, seed_path, summarize_case_l2


def test_seed_path_uses_default_l2_artifacts() -> None:
    assert seed_path(10.0, 0) == "docs/composite_behavior_target_family_gate_projected_hdf5.json"
    assert seed_path(10.0, 3) == "docs/composite_behavior_target_family_gate_projected_hdf5_seed_3.json"
    assert (
        seed_path(1.0, 2)
        == "docs/composite_behavior_target_family_gate_projected_hdf5_l2_1_seed_2.json"
    )


def test_l2_summary_requires_candidate_in_all_seeds(monkeypatch) -> None:
    rows = [
        {
            "centered_delta_vs_shuffle": 0.10,
            "centered_delta_vs_total": 0.05,
            "target0_improved_vs_shuffle": 0.60,
            "target1_improved_vs_shuffle": 0.61,
            "n_bidirectional_recordings": 3,
            "decision": "candidate",
        },
        {
            "centered_delta_vs_shuffle": 0.11,
            "centered_delta_vs_total": 0.05,
            "target0_improved_vs_shuffle": 0.60,
            "target1_improved_vs_shuffle": 0.61,
            "n_bidirectional_recordings": 2,
            "decision": "reject: recording bidirectionality",
        },
    ]

    monkeypatch.setattr(
        "scripts.audit_composite_behavior_target_l2_seed_sensitivity.load_case_row",
        lambda l2, seed, case: rows[seed] | {"seed": seed, "l2": l2, "path": f"seed_{seed}.json"},
    )

    summary = summarize_case_l2(
        seeds=[0, 1],
        l2=1.0,
        case={"target_mode": "t", "family": "f", "holdout": "h"},
        min_positive_seed_fraction=0.8,
    )

    assert summary["n_positive_shuffle_delta_seeds"] == 2
    assert summary["n_candidate_seeds"] == 1
    assert not summary["robust_composite_behavior_l2_seed_candidate"]


def test_build_report_tracks_best_candidate_fraction(monkeypatch) -> None:
    rows = [
        {
            "target_mode": "t",
            "family": "f",
            "holdout": "h",
            "l2": 1.0,
            "n_seeds": 2,
            "n_positive_shuffle_delta_seeds": 2,
            "positive_shuffle_delta_fraction": 1.0,
            "n_candidate_seeds": 1,
            "mean_centered_delta_vs_shuffle": 0.1,
            "min_centered_delta_vs_shuffle": 0.1,
            "max_centered_delta_vs_shuffle": 0.1,
            "mean_centered_delta_vs_total": 0.1,
            "mean_target0": 0.6,
            "mean_target1": 0.6,
            "min_bidirectional_recordings": 2,
            "max_bidirectional_recordings": 3,
            "robust_composite_behavior_l2_seed_candidate": False,
            "seed_rows": [],
        },
        {
            "target_mode": "t",
            "family": "f",
            "holdout": "h",
            "l2": 100.0,
            "n_seeds": 2,
            "n_positive_shuffle_delta_seeds": 2,
            "positive_shuffle_delta_fraction": 1.0,
            "n_candidate_seeds": 2,
            "mean_centered_delta_vs_shuffle": 0.1,
            "min_centered_delta_vs_shuffle": 0.1,
            "max_centered_delta_vs_shuffle": 0.1,
            "mean_centered_delta_vs_total": 0.1,
            "mean_target0": 0.6,
            "mean_target1": 0.6,
            "min_bidirectional_recordings": 3,
            "max_bidirectional_recordings": 3,
            "robust_composite_behavior_l2_seed_candidate": True,
            "seed_rows": [],
        },
    ]

    monkeypatch.setattr(
        "scripts.audit_composite_behavior_target_l2_seed_sensitivity.summarize_case_l2",
        lambda **kwargs: rows.pop(0),
    )

    report = build_report(
        seeds=[0, 1],
        l2_values=(1.0, 100.0),
        cases=({"target_mode": "t", "family": "f", "holdout": "h"},),
    )

    assert report["summary"]["decision"] == "composite_behavior_l2_seed_candidate"
    assert report["summary"]["max_candidate_seed_fraction"] == 1.0
    assert not report["summary"]["gpu_training_ready"]
