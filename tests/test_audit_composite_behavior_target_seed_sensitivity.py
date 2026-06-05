from scripts.audit_composite_behavior_target_seed_sensitivity import build_report, summarize_case


def test_summarize_case_requires_candidate_in_all_seeds(monkeypatch) -> None:
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
        "scripts.audit_composite_behavior_target_seed_sensitivity.load_case_row",
        lambda seed, case: rows[seed] | {"seed": seed, "path": f"seed_{seed}.json"},
    )

    summary = summarize_case(
        seeds=[0, 1],
        case={"target_mode": "t", "family": "f", "holdout": "h"},
        min_positive_seed_fraction=0.8,
    )

    assert summary["n_positive_shuffle_delta_seeds"] == 2
    assert summary["n_candidate_seeds"] == 1
    assert not summary["robust_composite_behavior_seed_candidate"]


def test_build_report_keeps_gpu_training_false(monkeypatch) -> None:
    row = {
        "target_mode": "t",
        "family": "f",
        "holdout": "h",
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
        "robust_composite_behavior_seed_candidate": False,
        "seed_rows": [],
    }

    monkeypatch.setattr(
        "scripts.audit_composite_behavior_target_seed_sensitivity.summarize_case",
        lambda **kwargs: row,
    )

    report = build_report(seeds=[0, 1], cases=({"target_mode": "t", "family": "f", "holdout": "h"},))

    assert report["summary"]["decision"] == "no_composite_behavior_seed_candidate"
    assert report["summary"]["max_candidate_seed_fraction"] == 0.5
    assert not report["summary"]["gpu_training_ready"]
