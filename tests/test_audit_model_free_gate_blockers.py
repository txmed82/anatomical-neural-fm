from scripts.audit_model_free_gate_blockers import GateRow, closeness, missing_checks, summarize


THRESHOLDS = {
    "min_centered_delta": 0.01,
    "min_target_improvement": 0.55,
    "min_bidirectional_recording_fraction": 0.75,
}


def row(
    label: str,
    *,
    centered_delta: float,
    target0: float,
    target1: float,
    bidirectional_fraction: float,
    bidirectional_recordings: int,
) -> GateRow:
    return GateRow(
        report="test",
        label=label,
        decision="candidate",
        centered_delta=centered_delta,
        target0=target0,
        target1=target1,
        bidirectional_fraction=bidirectional_fraction,
        positive_recording_fraction=1.0,
        n_bidirectional_recordings=bidirectional_recordings,
        n_recordings=4,
    )


def test_missing_checks_reports_each_failed_gate() -> None:
    result = missing_checks(
        row(
            "weak",
            centered_delta=-0.01,
            target0=0.60,
            target1=0.40,
            bidirectional_fraction=0.25,
            bidirectional_recordings=1,
        ),
        THRESHOLDS,
    )

    assert result == ["centered_delta", "target1", "recording_bidirectionality"]


def test_summarize_ranks_bidirectional_near_misses() -> None:
    rows = [
        row("candidate", centered_delta=0.02, target0=0.60, target1=0.60, bidirectional_fraction=0.75, bidirectional_recordings=3),
        row("near", centered_delta=0.08, target0=0.51, target1=0.55, bidirectional_fraction=0.50, bidirectional_recordings=2),
        row("weak", centered_delta=-0.01, target0=0.80, target1=0.30, bidirectional_fraction=0.0, bidirectional_recordings=0),
    ]

    summary = summarize(rows, THRESHOLDS)

    assert summary["n_rows"] == 3
    assert summary["n_candidates"] == 1
    assert summary["max_bidirectional_recordings"] == 3
    assert summary["blocker_counts"]["recording_bidirectionality"] == 2
    assert summary["top_bidirectional_rows"][0].label == "candidate"


def test_closeness_uses_worst_margin() -> None:
    assert closeness(
        row("near", centered_delta=0.08, target0=0.51, target1=0.55, bidirectional_fraction=0.50, bidirectional_recordings=2),
        THRESHOLDS,
    ) == -0.25
