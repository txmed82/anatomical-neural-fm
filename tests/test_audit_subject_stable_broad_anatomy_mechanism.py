from scripts.audit_subject_stable_broad_anatomy_mechanism import (
    source_feature_mode,
    source_kind,
    summarize_rows,
)


def test_source_parsing_tracks_known_subject_stable_sources() -> None:
    assert source_kind("reaction_recording_centered") == "reaction"
    assert source_kind("derived_recording_centered") == "derived"
    assert source_kind("wheel_targets") == "wheel"
    assert source_feature_mode("reaction_recording_centered") == "recording_centered"
    assert source_feature_mode("wheel_targets") == "recording_centered"


def test_summarize_rows_distinguishes_contribution_from_exact_gate() -> None:
    summary = summarize_rows([
        {
            "bidirectional_family_candidates": ["broad_named_anatomy"],
            "family_gate_candidates": [],
            "broad_family_contribution": {"classification": "bidirectional_family_candidate"},
        }
    ])

    assert summary["n_bidirectional_family_candidates"] == 1
    assert summary["n_family_gate_candidates"] == 0
    assert summary["decision"] == "contribution_only_subject_stable_broad_family_mechanism"


def test_summarize_rows_promotes_only_exact_gate_candidates() -> None:
    summary = summarize_rows([
        {
            "bidirectional_family_candidates": ["midbrain"],
            "family_gate_candidates": [{"family": "midbrain"}],
            "broad_family_contribution": {"classification": "weak_or_mixed"},
        }
    ])

    assert summary["n_family_gate_candidates"] == 1
    assert summary["decision"] == "subject_stable_family_gate_candidate"
