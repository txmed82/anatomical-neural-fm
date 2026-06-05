from collections import Counter

from scripts.audit_shared_parent_broadening import RegionSignal
from scripts.define_parent_region_slice import select_carriers, score_slice


def signal(units: int, delta: float) -> RegionSignal:
    return RegionSignal(
        units=units,
        left_trials=10,
        right_trials=10,
        left_rate=1.0,
        right_rate=1.0 + delta,
    )


def test_select_carriers_requires_shared_mass_units_and_delta() -> None:
    counts = Counter({"A": 100, "B": 90, "C": 120, "D": 200})
    signals = {
        "A": signal(100, 0.20),
        "B": signal(90, 0.50),
        "C": signal(120, 0.05),
        "D": signal(200, 0.30),
    }

    carriers = select_carriers(
        counts,
        signals,
        train_panel={"A", "B", "C"},
        min_units=100,
        min_unit_mass=0.10,
        min_abs_delta=0.10,
    )

    assert [row.parent for row in carriers] == ["A"]


def test_score_slice_passes_only_when_units_carriers_and_alignment_clear() -> None:
    carriers = [
        select_carriers(
            Counter({"A": 100, "B": 100}),
            {"A": signal(100, 0.20), "B": signal(100, -0.20)},
            train_panel={"A", "B"},
            min_units=1,
            min_unit_mass=0.0,
            min_abs_delta=0.0,
        )[0],
        select_carriers(
            Counter({"A": 100, "B": 100}),
            {"A": signal(100, 0.20), "B": signal(100, -0.20)},
            train_panel={"A", "B"},
            min_units=1,
            min_unit_mass=0.0,
            min_abs_delta=0.0,
        )[1],
    ]

    passing = score_slice(
        label="candidate",
        subject="candidate",
        candidate_counts=Counter({"A": 80, "B": 70}),
        candidate_signals={"A": signal(80, 0.10), "B": signal(70, -0.10)},
        carriers=carriers,
        min_units_per_parent=50,
        min_slice_units=100,
        min_aligned_unit_mass_frac=0.75,
        min_carriers_with_units=2,
    )
    failing = score_slice(
        label="candidate",
        subject="candidate",
        candidate_counts=Counter({"A": 80, "B": 70}),
        candidate_signals={"A": signal(80, -0.10), "B": signal(70, -0.10)},
        carriers=carriers,
        min_units_per_parent=50,
        min_slice_units=100,
        min_aligned_unit_mass_frac=0.75,
        min_carriers_with_units=2,
    )

    assert passing.passes_gate is True
    assert passing.aligned_unit_mass_frac == 1.0
    assert failing.passes_gate is False
    assert failing.aligned_unit_mass_frac == 70 / 150
