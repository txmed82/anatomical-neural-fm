from collections import Counter

from scripts.audit_shared_parent_broadening import (
    RegionSignal,
    _safe_rate,
    support_summary,
    weighted_abs_delta,
)


def test_safe_rate_normalizes_by_units_trials_and_window() -> None:
    assert _safe_rate(40, units=2, trials=10, window_len=1.0) == 2.0
    assert _safe_rate(40, units=2, trials=10, window_len=2.0) == 1.0
    assert _safe_rate(40, units=0, trials=10, window_len=1.0) == 0.0


def test_weighted_abs_delta_uses_unit_weights_and_parent_filter() -> None:
    signals = {
        "A": RegionSignal(units=3, left_trials=10, right_trials=10, left_rate=1.0, right_rate=2.0),
        "B": RegionSignal(units=1, left_trials=10, right_trials=10, left_rate=4.0, right_rate=2.0),
    }

    assert weighted_abs_delta(signals) == 1.25
    assert weighted_abs_delta(signals, {"B"}) == 2.0


def test_support_summary_compares_holdout_to_other_subjects() -> None:
    counts = {
        "heldout": Counter({"A": 3, "B": 2, "C": 1}),
        "train1": Counter({"A": 5}),
        "train2": Counter({"C": 4, "D": 2}),
    }

    summary = support_summary("heldout", counts)

    assert summary["total_units"] == 6
    assert summary["n_parent_regions"] == 3
    assert summary["supported_units"] == 4
    assert summary["support_frac"] == 4 / 6
    assert summary["missing_top_regions"] == ["B"]
