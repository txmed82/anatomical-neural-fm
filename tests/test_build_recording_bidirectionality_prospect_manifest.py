from scripts.build_recording_bidirectionality_prospect_manifest import build_manifest, recording_id


def test_recording_id_uses_session_and_probe_fields() -> None:
    assert recording_id({"session_id": "eid1", "probe_name": "probe00"}) == "eid1_probe00"
    assert recording_id({"eid": "eid2", "probe": "probe01"}) == "eid2_probe01"


def test_build_manifest_selects_requested_recordings_and_reports_missing() -> None:
    base = {
        "recordings": [
            {"session_id": "eid1", "probe_name": "probe00", "subject_id": "S1", "lab": "lab-a", "qc": "PASS"},
            {"session_id": "eid2", "probe_name": "probe01", "subject_id": "S2", "lab": "lab-b", "qc": "PASS"},
        ]
    }

    report = build_manifest(base, ["eid2_probe01", "missing_probe00"])

    assert report["n_recordings"] == 1
    assert report["n_subjects"] == 1
    assert report["subjects"] == ["S2"]
    assert report["missing_recording_ids"] == ["missing_probe00"]
    assert report["recordings"][0]["recording_id"] == "eid2_probe01"
