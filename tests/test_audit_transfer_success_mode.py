from collections import Counter

import pytest

from scripts.audit_shared_parent_broadening import RegionSignal
from scripts.audit_transfer_success_mode import (
    combine_signals,
    compatibility_for_subject,
    leave_subject_out_train_signals,
)


def signal(units: int, delta: float) -> RegionSignal:
    return RegionSignal(
        units=units,
        left_trials=10,
        right_trials=10,
        left_rate=1.0,
        right_rate=1.0 + delta,
    )


def test_combine_signals_weights_rates_by_units_and_trials() -> None:
    combined = combine_signals([
        RegionSignal(units=10, left_trials=2, right_trials=2, left_rate=1.0, right_rate=3.0),
        RegionSignal(units=30, left_trials=2, right_trials=2, left_rate=2.0, right_rate=4.0),
    ])

    assert combined.units == 40
    assert combined.left_rate == pytest.approx(1.75)
    assert combined.right_rate == pytest.approx(3.75)
    assert combined.delta_rate == pytest.approx(2.0)


def test_leave_subject_out_train_signals_excludes_holdout() -> None:
    signals = {
        "holdout": {"A": signal(10, -1.0)},
        "train1": {"A": signal(10, 1.0)},
        "train2": {"A": signal(30, 3.0)},
    }

    train = leave_subject_out_train_signals("holdout", signals)

    assert train["A"].units == 40
    assert train["A"].delta_rate == pytest.approx(2.5)


def test_compatibility_reports_coverage_alignment_and_opposition() -> None:
    counts = {
        "candidate": Counter({"A": 80, "B": 20, "C": 100}),
        "train": Counter({"A": 100, "B": 100, "C": 100}),
    }
    signals = {
        "candidate": {
            "A": signal(80, 0.20),
            "B": signal(20, -0.20),
            "C": signal(100, 0.20),
        },
        "train": {
            "A": signal(100, 0.10),
            "B": signal(100, 0.10),
            "C": signal(100, 0.10),
        },
    }

    row = compatibility_for_subject(
        "candidate",
        {"A": 3.0, "B": 1.0, "missing": 4.0},
        counts,
        signals,
    )

    assert row.slice_units == 100
    assert row.carriers_present == 2
    assert row.csh_weighted_coverage_frac == pytest.approx(0.5)
    assert row.train_aligned_unit_mass_frac == pytest.approx(0.8)
    assert row.train_aligned_parents == ("A",)
    assert row.train_opposed_parents == ("B",)
