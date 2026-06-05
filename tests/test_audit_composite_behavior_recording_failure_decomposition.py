from scripts.audit_composite_behavior_recording_failure_decomposition import build_report, summarize_case


def rec(recording: str, target0: float, target1: float) -> dict:
    return {
        "recording": recording,
        "target0_improved": target0,
        "target1_improved": target1,
        "mean_true_class_delta": target0 + target1 - 1.0,
        "improved_fraction": (target0 + target1) / 2.0,
        "n_trials": 100,
    }


def test_summarize_case_tracks_unstable_recordings(monkeypatch) -> None:
    seed_rows = [
        {
            "seed": 0,
            "decision": "candidate",
            "n_bidirectional_recordings": 2,
            "n_recordings": 2,
            "centered_delta_vs_shuffle": 0.1,
            "centered_delta_vs_total": 0.1,
            "recording_target_rows": [rec("stable", 0.6, 0.7), rec("weak", 0.6, 0.7)],
        },
        {
            "seed": 1,
            "decision": "reject: recording bidirectionality",
            "n_bidirectional_recordings": 1,
            "n_recordings": 2,
            "centered_delta_vs_shuffle": 0.1,
            "centered_delta_vs_total": 0.1,
            "recording_target_rows": [rec("stable", 0.7, 0.8), rec("weak", 0.4, 0.7)],
        },
    ]

    monkeypatch.setattr(
        "scripts.audit_composite_behavior_recording_failure_decomposition.load_case_row",
        lambda seed, case: seed_rows[seed],
    )

    summary = summarize_case(
        seeds=[0, 1],
        case={"target_mode": "t", "family": "f", "holdout": "h"},
        min_target_improvement=0.55,
    )

    assert summary["n_stable_bidirectional_recordings"] == 1
    assert summary["n_unstable_recordings"] == 1
    assert summary["mean_bidirectional_seed_fraction"] == 0.75
    weak = next(row for row in summary["recording_rows"] if row["recording"] == "weak")
    assert weak["n_bidirectional_seeds"] == 1
    assert weak["n_target0_pass_seeds"] == 1
    assert weak["n_target1_pass_seeds"] == 2


def test_build_report_keeps_gpu_training_false(monkeypatch) -> None:
    row = {
        "target_mode": "t",
        "family": "f",
        "holdout": "h",
        "n_seeds": 2,
        "n_recordings": 1,
        "n_stable_bidirectional_recordings": 0,
        "n_unstable_recordings": 1,
        "mean_bidirectional_seed_fraction": 0.5,
        "min_recording_bidirectional_seed_fraction": 0.5,
        "recording_rows": [],
        "weakest_recordings": [],
        "seed_rows": [],
    }

    monkeypatch.setattr(
        "scripts.audit_composite_behavior_recording_failure_decomposition.summarize_case",
        lambda **kwargs: row,
    )

    report = build_report(cases=({"target_mode": "t", "family": "f", "holdout": "h"},), seeds=[0, 1])

    assert report["summary"]["decision"] == "composite_behavior_recording_bidirectionality_failure"
    assert report["summary"]["n_unstable_recordings"] == 1
    assert not report["summary"]["gpu_training_ready"]
