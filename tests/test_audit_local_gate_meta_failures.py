import json

from scripts.audit_local_gate_meta_failures import build_report, row_failures, row_gate_score


def passing_row(**overrides) -> dict:
    row = {
        "target_mode": "choice",
        "family": "depth",
        "holdout": "S1",
        "decision": "candidate",
        "centered_delta_vs_shuffle": 0.02,
        "centered_delta_vs_total": 0.01,
        "target0_improved_vs_shuffle": 0.60,
        "target1_improved_vs_shuffle": 0.61,
        "bidirectional_recording_fraction": 0.75,
        "n_bidirectional_recordings": 3,
        "n_recordings": 4,
    }
    row.update(overrides)
    return row


def test_row_failures_names_all_failed_gate_terms() -> None:
    failures = row_failures(passing_row(
        centered_delta_vs_shuffle=-0.01,
        target1_improved_vs_shuffle=0.30,
        bidirectional_recording_fraction=0.50,
    ))

    assert failures == ["shuffle", "target1", "recording_bidirectionality"]


def test_row_gate_score_is_min_margin_to_threshold() -> None:
    score = row_gate_score(passing_row(target0_improved_vs_shuffle=0.54))

    assert round(score, 3) == -0.010


def test_build_report_aggregates_artifact_rows(tmp_path, monkeypatch) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "gate.json").write_text(json.dumps({
        "summary": {"n_candidates": 0, "max_bidirectional_recording_fraction": 0.5, "decision": "no_candidate"},
        "rows": [
            passing_row(decision="candidate"),
            passing_row(decision="reject: target0", target0_improved_vs_shuffle=0.40),
        ],
    }))

    import scripts.audit_local_gate_meta_failures as mod

    monkeypatch.setattr(mod, "REPO_ROOT", tmp_path)
    report = build_report({"fake_gate": "docs/gate.json"})

    assert report["summary"]["n_rows"] == 2
    assert report["summary"]["n_candidates"] == 1
    assert report["summary"]["failure_counts"]["target0"] == 1
    assert report["by_source"]["fake_gate"]["n_one_failure_rows"] == 1


def test_build_report_ranks_one_failure_rows_before_two_failure_rows(tmp_path, monkeypatch) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "gate.json").write_text(json.dumps({
        "summary": {"n_candidates": 0, "max_bidirectional_recording_fraction": 0.5, "decision": "no_candidate"},
        "rows": [
            passing_row(decision="reject: target0", target0_improved_vs_shuffle=0.40, target1_improved_vs_shuffle=0.40),
            passing_row(decision="reject: target0", target0_improved_vs_shuffle=0.54),
        ],
    }))

    import scripts.audit_local_gate_meta_failures as mod

    monkeypatch.setattr(mod, "REPO_ROOT", tmp_path)
    report = build_report({"fake_gate": "docs/gate.json"})

    assert report["near_misses"][0]["n_failures"] == 1
    assert report["near_misses"][0]["target0_improved_vs_shuffle"] == 0.54
