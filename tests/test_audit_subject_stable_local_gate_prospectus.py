from scripts.audit_subject_stable_local_gate_prospectus import (
    build_report,
    is_subject_stable,
    normalize_row,
)


def raw_row(**overrides) -> dict:
    row = {
        "target_mode": "response_latency",
        "family": "broad_named_anatomy",
        "holdout": "KS014",
        "decision": "reject: shuffle",
        "centered_delta_vs_shuffle": -0.001,
        "centered_delta_vs_total": 0.01,
        "target0_improved_vs_shuffle": 0.60,
        "target1_improved_vs_shuffle": 0.61,
        "n_bidirectional_recordings": 3,
        "n_recordings": 4,
        "bidirectional_recording_fraction": 0.75,
    }
    row.update(overrides)
    return row


def test_is_subject_stable_requires_recording_count_and_fraction() -> None:
    assert is_subject_stable(raw_row(), min_recordings=3, min_bidirectional_fraction=0.75)
    assert not is_subject_stable(raw_row(n_recordings=2), min_recordings=3, min_bidirectional_fraction=0.75)
    assert not is_subject_stable(
        raw_row(bidirectional_recording_fraction=0.50),
        min_recordings=3,
        min_bidirectional_fraction=0.75,
    )


def test_normalize_row_keeps_failures_and_gate_score() -> None:
    row = normalize_row("source", raw_row())

    assert row["source"] == "source"
    assert row["failures"] == ["shuffle"]
    assert row["n_failures"] == 1
    assert row["gate_score"] == -0.001


def test_build_report_counts_subject_stable_near_misses(monkeypatch) -> None:
    import scripts.audit_subject_stable_local_gate_prospectus as mod

    payloads = {
        "stable.json": {"rows": [raw_row()]},
        "unstable.json": {"rows": [raw_row(n_recordings=1, bidirectional_recording_fraction=1.0)]},
    }

    def fake_read_json(path):
        return payloads.get(path.name)

    monkeypatch.setattr(mod, "read_json", fake_read_json)
    report = build_report(
        {"stable": "stable.json", "unstable": "unstable.json"},
        min_recordings=3,
        min_bidirectional_fraction=0.75,
    )

    assert report["summary"]["n_rows"] == 2
    assert report["summary"]["n_subject_stable_rows"] == 1
    assert report["summary"]["n_subject_stable_candidates"] == 0
    assert report["summary"]["n_subject_stable_one_failure_rows"] == 1
    assert report["summary"]["failure_counts"] == {"shuffle": 1}
