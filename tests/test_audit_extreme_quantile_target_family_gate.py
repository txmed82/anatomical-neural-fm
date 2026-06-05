import numpy as np

from scripts.audit_extreme_quantile_target_family_gate import _extreme_labels, summarize


def test_extreme_labels_drop_middle_trials() -> None:
    values = np.arange(8, dtype=np.float64)
    labels = _extreme_labels(
        values,
        np.ones(8, dtype=bool),
        low_quantile=0.25,
        high_quantile=0.75,
        high_is_target1=True,
    )

    assert labels[:2].tolist() == [0.0, 0.0]
    assert np.isnan(labels[2:6]).all()
    assert labels[6:].tolist() == [1.0, 1.0]


def test_extreme_labels_can_invert_latency_direction() -> None:
    values = np.arange(8, dtype=np.float64)
    labels = _extreme_labels(
        values,
        np.ones(8, dtype=bool),
        low_quantile=0.25,
        high_quantile=0.75,
        high_is_target1=False,
    )

    assert labels[:2].tolist() == [1.0, 1.0]
    assert np.isnan(labels[2:6]).all()
    assert labels[6:].tolist() == [0.0, 0.0]


def test_summarize_reports_extreme_quantile_candidate_decision() -> None:
    row = {
        "decision": "candidate",
        "target_mode": "target",
        "family": "broad_named_anatomy",
        "holdout": "KS014",
        "centered_delta_vs_shuffle": 0.01,
        "centered_delta_vs_total": 0.01,
        "target0_improved_vs_shuffle": 0.60,
        "target1_improved_vs_shuffle": 0.61,
        "bidirectional_recording_fraction": 0.75,
        "n_bidirectional_recordings": 3,
        "n_recordings": 4,
    }
    summary = summarize([row], {"target": {"n_trials": 100, "eligible_recordings": 4, "n_recordings": 4}})

    assert summary["n_candidates"] == 1
    assert summary["decision"] == "extreme_quantile_target_family_candidate"
