from scripts.audit_prospect_lead_candidate_validation import build_report, row_key


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


def test_row_key_matches_target_family_holdout() -> None:
    row = gate_row("response_latency", "thalamic", "MFD_06", decision="candidate", n_recordings=1)

    assert row_key(row) == ("response_latency", "thalamic", "MFD_06")


def test_validation_blocks_single_recording_subset_only_candidate() -> None:
    prospect = {"rows": [gate_row("response_latency", "thalamic", "MFD_06", decision="candidate", n_recordings=1)]}
    full = {"rows": [gate_row("response_latency", "thalamic", "MFD_06", decision="reject: shuffle", n_recordings=4)]}

    report = build_report(prospect, full, min_candidate_recordings=3)

    assert report["summary"]["decision"] == "no_validated_prospect_lead_candidate"
    assert report["summary"]["n_prospect_candidates"] == 1
    assert report["summary"]["n_single_recording_candidates"] == 1
    assert report["summary"]["n_subset_only_candidates"] == 1
    assert report["summary"]["gpu_training_ready"] is False


def test_validation_accepts_full_manifest_candidate_with_enough_recordings() -> None:
    row = gate_row("response_latency", "thalamic", "MFD_06", decision="candidate", n_recordings=3)

    report = build_report({"rows": [row]}, {"rows": [row]}, min_candidate_recordings=3)

    assert report["summary"]["decision"] == "prospect_lead_candidate_validated"
    assert report["summary"]["n_validated_candidates"] == 1
    assert report["summary"]["gpu_training_ready"] is False
