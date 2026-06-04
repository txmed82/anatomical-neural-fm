from __future__ import annotations

import json

from scripts.sync_brainset_s3 import local_h5_files, manifest_recording_names, s3_key


def test_manifest_recording_names_accepts_committed_schema(tmp_path) -> None:
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps({
        "recordings": [
            {"session_id": "eid-a", "probe_name": "probe00"},
            {"eid": "eid-b", "probe": "probe01"},
        ],
    }))

    assert manifest_recording_names(path) == {
        "eid-a_probe00.h5",
        "eid-b_probe01.h5",
    }


def test_s3_key_normalizes_prefix() -> None:
    assert s3_key("brainsets/ibl_bwm", "rec.h5") == "brainsets/ibl_bwm/rec.h5"
    assert s3_key("/brainsets/ibl_bwm/", "rec.h5") == "brainsets/ibl_bwm/rec.h5"
    assert s3_key("", "rec.h5") == "rec.h5"


def test_local_h5_files_filters_by_manifest_names(tmp_path) -> None:
    keep = tmp_path / "keep.h5"
    drop = tmp_path / "drop.h5"
    other = tmp_path / "other.txt"
    keep.write_text("x")
    drop.write_text("x")
    other.write_text("x")

    assert local_h5_files(tmp_path, {"keep.h5"}) == [keep]
