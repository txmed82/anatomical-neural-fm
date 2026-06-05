import scripts.audit_prospect_lead_subject_stability as mod


def rec(recording: str, target0: float, target1: float) -> dict:
    return {
        "recording": recording,
        "target0_improved": target0,
        "target1_improved": target1,
        "improved_fraction": (target0 + target1) / 2,
        "mean_true_class_delta": 0.0,
        "n_trials": 10,
    }


def gate_row(
    target: str,
    family: str,
    holdout: str,
    *,
    decision: str,
    recording_rows: list[dict],
) -> dict:
    return {
        "target_mode": target,
        "family": family,
        "holdout": holdout,
        "decision": decision,
        "recording_target_rows": recording_rows,
    }


def test_summarize_recording_group_counts_bidirectional_rows() -> None:
    summary = mod.summarize_recording_group(
        [rec("lead", 0.60, 0.61), rec("weak", 0.80, 0.20)],
        min_target_improvement=0.55,
    )

    assert summary["n_recordings"] == 2
    assert summary["n_bidirectional_recordings"] == 1
    assert summary["bidirectional_fraction"] == 0.5
    assert summary["mean_target0"] == 0.70


def test_candidate_stability_rejects_same_subject_nonlead_failure() -> None:
    prospect_row = gate_row(
        "response_latency",
        "thalamic",
        "MFD_06",
        decision="candidate",
        recording_rows=[rec("lead", 0.60, 0.61)],
    )
    full_row = gate_row(
        "response_latency",
        "thalamic",
        "MFD_06",
        decision="reject: target1",
        recording_rows=[rec("lead", 0.60, 0.61), rec("nonlead", 1.0, 0.0)],
    )

    row = mod.candidate_stability_row(
        feature_mode="recording_centered",
        prospect_row=prospect_row,
        full_row=full_row,
        lead_ids={"lead"},
        min_target_improvement=0.55,
    )

    assert row["lead"]["n_bidirectional_recordings"] == 1
    assert row["nonlead"]["n_bidirectional_recordings"] == 0
    assert row["same_subject_stable"] is False


def test_candidate_stability_accepts_full_candidate_with_nonlead_support() -> None:
    prospect_row = gate_row(
        "response_latency",
        "thalamic",
        "MFD_06",
        decision="candidate",
        recording_rows=[rec("lead", 0.60, 0.61)],
    )
    full_row = gate_row(
        "response_latency",
        "thalamic",
        "MFD_06",
        decision="candidate",
        recording_rows=[rec("lead", 0.60, 0.61), rec("nonlead", 0.62, 0.63)],
    )

    row = mod.candidate_stability_row(
        feature_mode="recording_centered",
        prospect_row=prospect_row,
        full_row=full_row,
        lead_ids={"lead"},
        min_target_improvement=0.55,
    )

    assert row["nonlead"]["bidirectional_fraction"] == 1.0
    assert row["same_subject_stable"] is True
