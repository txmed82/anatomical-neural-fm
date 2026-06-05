import json

import h5py

from scripts.audit_behavior_cache_preflight import (
    audit_cache,
    build_commands,
    render_markdown,
    recording_name,
)


def test_recording_name_accepts_manifest_aliases() -> None:
    assert recording_name({"session_id": "eid-a", "probe_name": "probe00"}) == "eid-a_probe00.h5"
    assert recording_name({"eid": "eid-b", "probe": "probe01"}) == "eid-b_probe01.h5"


def test_audit_cache_counts_missing_behavior_streams(tmp_path) -> None:
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({
        "recordings": [
            {"session_id": "eid-a", "probe_name": "probe00"},
            {"session_id": "eid-b", "probe_name": "probe01"},
            {"session_id": "eid-c", "probe_name": "probe00"},
        ]
    }))
    data_dir = tmp_path / "cache"
    data_dir.mkdir()
    with h5py.File(data_dir / "eid-a_probe00.h5", "w") as h5:
        h5.create_group("spikes")
        h5.create_group("wheel")
    with h5py.File(data_dir / "eid-b_probe01.h5", "w") as h5:
        h5.create_group("spikes")

    report = audit_cache(data_dir=data_dir, manifest=manifest, required_streams=("wheel",))

    assert report["summary"]["n_manifest_recordings"] == 3
    assert report["summary"]["n_present_files"] == 2
    assert report["summary"]["n_missing_files"] == 1
    assert report["summary"]["stream_counts"]["wheel"] == 1
    assert report["summary"]["n_recordings_needing_behavior_rebuild"] == 2
    assert report["summary"]["decision"] == "behavior_cache_rebuild_required"


def test_build_commands_keep_wheel_and_shard_manifest(tmp_path) -> None:
    manifest = tmp_path / "manifest.json"
    commands = build_commands(manifest, num_shards=2, out_dir=tmp_path / "cache")

    assert len(commands) == 2
    assert "--shard-index 0" in commands[0]
    assert "--shard-index 1" in commands[1]
    assert "--trial-window-only --window-len 1.0" in commands[0]
    assert "--rebuild-missing-stream wheel" in commands[0]
    assert "--no-wheel" not in commands[0]


def test_render_markdown_includes_gate_and_targets(tmp_path) -> None:
    report = {
        "summary": {
            "n_manifest_recordings": 1,
            "n_present_files": 1,
            "n_missing_files": 0,
            "stream_counts": {"wheel": 0},
            "n_recordings_needing_behavior_rebuild": 1,
            "decision": "behavior_cache_rebuild_required",
            "next_gate": "rerun local gate",
        },
        "recording_rows": [
            {"recording": "eid-a_probe00", "missing_streams": ["wheel"], "needs_behavior_rebuild": True}
        ],
    }

    text = render_markdown(report, ["uv run python scripts/build_ibl_brainset_batch.py"])

    assert "# Behavior Cache Preflight" in text
    assert "wheel movement onset" in text
    assert "rerun local gate" in text
