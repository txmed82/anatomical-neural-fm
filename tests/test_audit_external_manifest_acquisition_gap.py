from scripts.audit_external_manifest_acquisition_gap import (
    build_subject_gap_rows,
    is_support_qualified,
    local_recording_ids,
    recording_id,
)


def test_recording_id_uses_session_and_probe_fields() -> None:
    assert recording_id({"session_id": "eid", "probe_name": "probe00"}) == "eid_probe00"


def test_local_recording_ids_reads_all_local_panel() -> None:
    payload = {
        "panels": [
            {"label": "current_support80_hdf5", "recording_ids": ["a_probe00"]},
            {"label": "all_local_cached", "recording_ids": ["a_probe00", "b_probe01"]},
        ]
    }

    assert local_recording_ids(payload) == {"a_probe00", "b_probe01"}


def test_support_qualified_requires_support_and_recording_floor() -> None:
    support = {"S1": {"unit_support_frac": 0.81}}

    assert is_support_qualified("S1", support, 2, min_support=0.8, min_recordings=2)
    assert not is_support_qualified("S1", support, 1, min_support=0.8, min_recordings=2)
    assert not is_support_qualified("S1", support, 2, min_support=0.9, min_recordings=2)


def test_build_subject_gap_rows_counts_missing_hdf5_for_qualified_subjects() -> None:
    broad = {
        "recordings": [
            {"session_id": "a", "probe_name": "probe00", "subject_id": "S1"},
            {"session_id": "b", "probe_name": "probe00", "subject_id": "S1"},
            {"session_id": "c", "probe_name": "probe00", "subject_id": "S2"},
            {"session_id": "d", "probe_name": "probe00", "subject_id": "S2"},
        ],
        "region_support": {
            "S1": {"unit_support_frac": 0.85, "top_supported": 8, "top_total": 8, "missing_top": []},
            "S2": {"unit_support_frac": 0.60, "top_supported": 5, "top_total": 8, "missing_top": ["X"]},
        },
    }

    rows = build_subject_gap_rows(
        broad,
        {"a_probe00"},
        min_support=0.8,
        min_recordings=2,
    )

    s1 = next(row for row in rows if row["subject"] == "S1")
    assert s1["support_qualified"] is True
    assert s1["local_hdf5_recordings"] == 1
    assert s1["missing_hdf5_recordings"] == 1
    s2 = next(row for row in rows if row["subject"] == "S2")
    assert s2["support_qualified"] is False
