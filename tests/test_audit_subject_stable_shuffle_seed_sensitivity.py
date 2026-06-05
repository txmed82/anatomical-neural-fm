import scripts.audit_subject_stable_shuffle_seed_sensitivity as mod


def row(seed: int, delta: float, *, decision: str = "reject: shuffle") -> dict:
    return {
        "seed": seed,
        "decision": decision,
        "centered_delta_vs_shuffle": delta,
        "centered_delta_vs_total": 0.01,
        "target0_improved_vs_shuffle": 0.60,
        "target1_improved_vs_shuffle": 0.61,
        "n_bidirectional_recordings": 3,
    }


def test_summarize_case_requires_positive_fraction_mean_and_all_candidate(monkeypatch) -> None:
    rows = {
        0: row(0, 0.01, decision="candidate"),
        1: row(1, 0.02, decision="candidate"),
        2: row(2, 0.03, decision="reject: target0"),
    }
    monkeypatch.setattr(mod, "load_case_row", lambda _case, seed: rows[seed])

    summary = mod.summarize_case(
        {"source": "x", "target_mode": "t", "family": "f", "holdout": "h"},
        [0, 1, 2],
        min_positive_seed_fraction=0.8,
    )

    assert summary["positive_shuffle_delta_fraction"] == 1.0
    assert summary["n_candidate_seeds"] == 2
    assert summary["robust_shuffle_seed_candidate"] is False


def test_build_report_marks_no_robust_candidate_when_mean_delta_negative(monkeypatch) -> None:
    rows = {
        0: row(0, 0.01, decision="candidate"),
        1: row(1, 0.01, decision="candidate"),
        2: row(2, -0.04, decision="candidate"),
    }
    monkeypatch.setattr(mod, "load_case_row", lambda _case, seed: rows[seed])

    report = mod.build_report(
        [{"source": "x", "target_mode": "t", "family": "f", "holdout": "h"}],
        seeds=[0, 1, 2],
        min_positive_seed_fraction=0.5,
    )

    assert report["summary"]["decision"] == "no_subject_stable_shuffle_seed_candidate"
    assert report["summary"]["n_robust_shuffle_seed_candidates"] == 0
    assert report["summary"]["gpu_training_ready"] is False


def test_build_report_accepts_all_seed_candidate_with_positive_mean(monkeypatch) -> None:
    rows = {
        0: row(0, 0.01, decision="candidate"),
        1: row(1, 0.02, decision="candidate"),
        2: row(2, 0.03, decision="candidate"),
    }
    monkeypatch.setattr(mod, "load_case_row", lambda _case, seed: rows[seed])

    report = mod.build_report(
        [{"source": "x", "target_mode": "t", "family": "f", "holdout": "h"}],
        seeds=[0, 1, 2],
        min_positive_seed_fraction=0.8,
    )

    assert report["summary"]["decision"] == "subject_stable_shuffle_seed_candidate"
    assert report["summary"]["n_robust_shuffle_seed_candidates"] == 1
    assert report["summary"]["gpu_training_ready"] is False
