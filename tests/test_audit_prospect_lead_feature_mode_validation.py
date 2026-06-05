import json
from pathlib import Path

import scripts.audit_prospect_lead_feature_mode_validation as mod


def gate_row(
    target: str,
    family: str,
    holdout: str,
    *,
    decision: str,
    n_recordings: int,
) -> dict:
    return {
        "target_mode": target,
        "family": family,
        "holdout": holdout,
        "decision": decision,
        "centered_delta_vs_shuffle": 0.01,
        "centered_delta_vs_total": 0.02,
        "target0_improved_vs_shuffle": 0.60,
        "target1_improved_vs_shuffle": 0.61,
        "n_bidirectional_recordings": n_recordings,
        "n_recordings": n_recordings,
        "bidirectional_recording_fraction": 1.0,
    }


def payload(rows: list[dict]) -> dict:
    candidates = [row for row in rows if row["decision"] == "candidate"]
    return {
        "summary": {
            "n_candidates": len(candidates),
            "max_bidirectional_recordings": max((row["n_bidirectional_recordings"] for row in rows), default=0),
            "max_bidirectional_recording_fraction": max(
                (row["bidirectional_recording_fraction"] for row in rows), default=0.0
            ),
        },
        "rows": rows,
    }


def test_feature_mode_report_blocks_subset_only_candidates(tmp_path: Path, monkeypatch) -> None:
    prospect = tmp_path / "prospect.json"
    full = tmp_path / "full.json"
    prospect.write_text(json.dumps(payload([
        gate_row("response_latency", "thalamic", "MFD_06", decision="candidate", n_recordings=1)
    ])))
    full.write_text(json.dumps(payload([
        gate_row("response_latency", "thalamic", "MFD_06", decision="reject: shuffle", n_recordings=3)
    ])))
    monkeypatch.setattr(mod, "REPO_ROOT", tmp_path)

    report = mod.build_feature_mode_report(
        {"recording_centered": {"prospect": "prospect.json", "full": "full.json"}},
        min_candidate_recordings=3,
    )

    assert report["summary"]["decision"] == "no_validated_prospect_lead_feature_mode_candidate"
    assert report["summary"]["n_prospect_candidates"] == 1
    assert report["summary"]["n_validated_candidates"] == 0
    assert report["summary"]["n_single_recording_candidates"] == 1
    assert report["summary"]["n_subset_only_candidates"] == 1
    assert report["summary"]["gpu_training_ready"] is False


def test_feature_mode_report_counts_validated_candidate(tmp_path: Path, monkeypatch) -> None:
    row = gate_row("response_latency", "thalamic", "MFD_06", decision="candidate", n_recordings=3)
    prospect = tmp_path / "prospect.json"
    full = tmp_path / "full.json"
    prospect.write_text(json.dumps(payload([row])))
    full.write_text(json.dumps(payload([row])))
    monkeypatch.setattr(mod, "REPO_ROOT", tmp_path)

    report = mod.build_feature_mode_report(
        {"recording_centered": {"prospect": "prospect.json", "full": "full.json"}},
        min_candidate_recordings=3,
    )

    assert report["summary"]["decision"] == "prospect_lead_feature_mode_candidate_validated"
    assert report["summary"]["n_validated_candidates"] == 1
    assert report["summary"]["gpu_training_ready"] is False
