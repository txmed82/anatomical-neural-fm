from scripts.audit_shared_broad_anatomy_repair_sweep import (
    missing_requirements,
    rank_rows,
    score_row,
    target_holdout_rows,
)


def base_row(**updates) -> dict:
    row = {
        "target_mode": "choice",
        "family": "broad_named_anatomy",
        "holdout": "SWC_043",
        "centered_delta_vs_shuffle": 0.01,
        "centered_delta_vs_total": 0.02,
        "target0_improved_vs_shuffle": 0.56,
        "target1_improved_vs_shuffle": 0.57,
        "bidirectional_recording_fraction": 0.5,
        "n_recordings": 4,
        "n_bidirectional_recordings": 2,
        "decision": "reject: recording bidirectionality",
    }
    return row | updates


def test_target_holdout_rows_keeps_only_focus_rows() -> None:
    rows = [
        base_row(),
        base_row(holdout="SWC_038"),
        base_row(target_mode="feedback", holdout="NYU-12"),
        base_row(family="fiber_tracts"),
    ]

    assert [(row["target_mode"], row["holdout"]) for row in target_holdout_rows(rows)] == [
        ("choice", "SWC_043"),
        ("feedback", "NYU-12"),
    ]


def test_score_row_reports_missing_requirements() -> None:
    row = score_row(
        base_row(
            centered_delta_vs_total=-0.01,
            target0_improved_vs_shuffle=0.54,
        ),
        min_target_improvement=0.55,
        min_bidirectional_recording_fraction=0.75,
    )

    assert row["required_bidirectional_recordings"] == 3
    assert row["missing_bidirectional_recordings"] == 1
    assert row["target0_margin"] == -0.010000000000000009
    assert row["missing_requirements"] == ["total_delta", "target0", "recording_bidirectionality"]


def test_rank_rows_prefers_fewer_missing_bidirectional_hits_then_margin() -> None:
    better = score_row(
        base_row(target0_improved_vs_shuffle=0.56, n_bidirectional_recordings=2),
        min_target_improvement=0.55,
        min_bidirectional_recording_fraction=0.75,
    )
    worse = score_row(
        base_row(target0_improved_vs_shuffle=0.60, n_bidirectional_recordings=1),
        min_target_improvement=0.55,
        min_bidirectional_recording_fraction=0.75,
    )

    assert rank_rows([worse, better])[0] is better


def test_missing_requirements_empty_for_candidate_like_row() -> None:
    assert missing_requirements(
        base_row(bidirectional_recording_fraction=0.75),
        min_target_improvement=0.55,
        min_bidirectional_recording_fraction=0.75,
    ) == []
