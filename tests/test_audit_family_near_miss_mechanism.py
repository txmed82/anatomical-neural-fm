import numpy as np

from scripts.audit_family_near_miss_mechanism import (
    classify_family_row,
    family_contribution_rows,
    recording_family_rows,
)


def test_family_contribution_rows_tracks_target_specific_delta() -> None:
    true_contrib = np.asarray([
        [0.1, 0.2],
        [0.4, 0.1],
        [0.2, 0.7],
        [0.3, 0.6],
    ])
    shuffle_contrib = np.asarray([
        [0.3, 0.1],
        [0.2, 0.0],
        [0.1, 0.4],
        [0.4, 0.2],
    ])
    labels = np.asarray([0, 0, 1, 1])

    rows = family_contribution_rows(
        ["family_a", "family_b"],
        true_contrib,
        shuffle_contrib,
        labels,
        ["rec1", "rec1", "rec2", "rec2"],
    )
    by_family = {row["family"]: row for row in rows}

    assert by_family["family_a"]["target0_improved"] == 0.5
    assert by_family["family_a"]["target1_improved"] == 0.5
    assert by_family["family_b"]["target0_improved"] == 0.0
    assert by_family["family_b"]["target1_improved"] == 1.0
    assert by_family["family_b"]["positive_recordings"] == 1


def test_recording_family_rows_sorts_by_abs_delta() -> None:
    family_rows = [
        {"family": "a", "recording_mean_deltas": {"rec": 0.1}},
        {"family": "b", "recording_mean_deltas": {"rec": -0.5}},
        {"family": "c", "recording_mean_deltas": {"rec": 0.3}},
    ]

    rows = recording_family_rows(family_rows, top_n=2)

    assert rows["rec"] == [
        {"family": "b", "mean_true_class_delta": -0.5},
        {"family": "c", "mean_true_class_delta": 0.3},
    ]


def test_classify_family_row_requires_both_targets() -> None:
    assert classify_family_row(
        {"target0_improved": 0.6, "target1_improved": 0.7},
        min_target_improvement=0.55,
    ) == "bidirectional_family_candidate"
    assert classify_family_row(
        {"target0_improved": 0.6, "target1_improved": 0.2},
        min_target_improvement=0.55,
    ) == "target0_only"
