import pytest

from scripts.audit_csh_mechanism import (
    embedding_summary,
    interpret,
    paired_stats,
)
from scripts.audit_csh_mechanism import PairedStats


def test_paired_stats_uses_true_class_probability_direction() -> None:
    candidate = [
        {"recording_id": "r", "t0": 0.0, "target": 0, "prob": 0.30},
        {"recording_id": "r", "t0": 1.0, "target": 1, "prob": 0.60},
    ]
    baseline = [
        {"recording_id": "r", "t0": 0.0, "target": 0, "prob": 0.40},
        {"recording_id": "r", "t0": 1.0, "target": 1, "prob": 0.65},
    ]

    stats = paired_stats(candidate, baseline)

    assert stats.n == 2
    assert stats.improved_fraction == 0.5
    assert stats.mean_true_prob_delta == pytest.approx(0.025)


def test_embedding_summary_compares_carrier_vectors() -> None:
    true = {
        "CA": {"norm": 1.0, "embedding": [1.0, 0.0]},
        "DG": {"norm": 1.0, "embedding": [0.0, 1.0]},
    }
    shuffle = {
        "CA": {"norm": 1.0, "embedding": [1.0, 0.0]},
        "DG": {"norm": 2.0, "embedding": [1.0, 0.0]},
    }

    summary = embedding_summary(true, shuffle, ("CA", "DG", "MOp"))

    assert summary["carriers"]["CA"]["cosine"] == pytest.approx(1.0)
    assert summary["carriers"]["DG"]["cosine"] == pytest.approx(0.0)
    assert summary["carriers"]["MOp"]["present"] is False
    assert summary["mean_carrier_cosine"] == pytest.approx(0.5)


def test_interpret_requires_paired_gate_even_for_carrier_rich_recording() -> None:
    interp = interpret(
        PairedStats(n=10, improved_fraction=0.44, mean_true_prob_delta=-0.1, mean_abs_prob_delta=0.1),
        PairedStats(n=10, improved_fraction=0.55, mean_true_prob_delta=0.1, mean_abs_prob_delta=0.1),
        {"mean_carrier_cosine": 0.8},
        {
            "rec": {
                "carrier": {"carrier_units": 200},
                "paired_true_vs_shuffle": {"improved_fraction": 0.4},
            }
        },
    )

    assert interp["decision"] == "no_mechanism_found"
    assert interp["true_beats_shuffle_paired"] is False
    assert interp["carrier_rich_negative_recordings"] == ["rec"]
