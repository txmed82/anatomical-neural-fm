from collections import Counter

from scripts.audit_shared_parent_broadening import (
    RegionSignal,
    _safe_rate,
    cosine_similarity,
    rank_candidate_compositions,
    reference_mass_present,
    support_summary,
    weighted_abs_delta,
    weighted_jaccard,
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


def test_weighted_jaccard_compares_unit_count_overlap() -> None:
    left = Counter({"A": 3, "B": 2})
    right = Counter({"A": 1, "B": 4, "C": 5})

    assert weighted_jaccard(left, right) == 3 / 12
    assert weighted_jaccard(Counter(), Counter()) == 0.0


def test_cosine_similarity_uses_count_vector_shape() -> None:
    assert cosine_similarity(Counter({"A": 1}), Counter({"A": 2})) == 1.0
    assert cosine_similarity(Counter({"A": 1}), Counter({"B": 2})) == 0.0
    assert cosine_similarity(Counter(), Counter({"B": 2})) == 0.0


def test_reference_mass_present_tracks_reference_weight() -> None:
    reference = Counter({"A": 3, "B": 2, "C": 1})
    candidate = Counter({"A": 10, "C": 1})

    assert reference_mass_present(reference, candidate) == 4 / 6
    assert reference_mass_present(reference, candidate, ["B", "C"]) == 1 / 3


def test_rank_candidate_compositions_prefers_csh_like_counts() -> None:
    counts = {
        "ref": Counter({"A": 10, "B": 5, "C": 1}),
        "close": Counter({"A": 8, "B": 5, "D": 1}),
        "far": Counter({"E": 12, "F": 4}),
    }
    signals = {
        "close": {
            "A": RegionSignal(units=8, left_trials=10, right_trials=10, left_rate=1.0, right_rate=2.0),
            "B": RegionSignal(units=5, left_trials=10, right_trials=10, left_rate=1.0, right_rate=1.0),
        },
        "far": {
            "E": RegionSignal(units=12, left_trials=10, right_trials=10, left_rate=1.0, right_rate=3.0),
        },
    }

    ranked = rank_candidate_compositions(counts, signals, reference_subject="ref", top_n=2)

    assert [row.subject for row in ranked] == ["close", "far"]
    assert ranked[0].ref_top_overlap == 2
    assert ranked[0].ref_top_mass_present == 1.0
    assert ranked[0].weighted_abs_spike_delta == 8 / 13
