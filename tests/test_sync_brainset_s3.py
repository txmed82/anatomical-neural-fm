from __future__ import annotations

import json

from botocore.exceptions import ClientError

from scripts.sync_brainset_s3 import (
    cache_audit_rows,
    local_h5_files,
    manifest_recording_rows,
    manifest_recording_names,
    parse_args,
    region_from_args,
    s3_key,
    select_shard_rows,
    upload_files,
    upload_log_file,
    verify_local_cache_rows,
    write_audit_report,
)


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
    assert manifest_recording_rows(path) == [
        {"session_id": "eid-a", "probe_name": "probe00"},
        {"eid": "eid-b", "probe": "probe01"},
    ]


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


def test_upload_log_file_uses_prefix_and_relative_key(tmp_path) -> None:
    class FakeClient:
        def __init__(self) -> None:
            self.calls = []

        def upload_file(self, local: str, bucket: str, key: str) -> None:
            self.calls.append((local, bucket, key))

    path = tmp_path / "run.log"
    path.write_text("hello")
    client = FakeClient()

    count = upload_log_file(
        client,
        bucket="cache",
        prefix="brainsets/ibl_bwm",
        local_path=path,
        key="logs/shard01.log",
    )

    assert count == 1
    assert client.calls == [(str(path), "cache", "brainsets/ibl_bwm/logs/shard01.log")]


def test_upload_files_can_skip_existing_remote_keys(tmp_path) -> None:
    class FakeClient:
        def __init__(self) -> None:
            self.uploads = []

        def head_object(self, *, Bucket: str, Key: str) -> None:
            if Key == "brainsets/ibl_bwm/existing.h5":
                return None
            raise ClientError({"Error": {"Code": "404"}}, "HeadObject")

        def upload_file(self, local: str, bucket: str, key: str) -> None:
            self.uploads.append((local, bucket, key))

    existing = tmp_path / "existing.h5"
    new = tmp_path / "new.h5"
    existing.write_text("x")
    new.write_text("x")
    client = FakeClient()

    count = upload_files(
        client,
        bucket="cache",
        prefix="brainsets/ibl_bwm",
        files=[existing, new],
        skip_existing=True,
    )

    assert count == 1
    assert client.uploads == [(str(new), "cache", "brainsets/ibl_bwm/new.h5")]


def test_cache_audit_rows_splits_present_and_missing() -> None:
    matched, missing = cache_audit_rows(
        {"a.h5", "b.h5", "c.h5"},
        {"a.h5", "c.h5", "extra.h5"},
    )

    assert matched == ["a.h5", "c.h5"]
    assert missing == ["b.h5"]


def test_verify_local_cache_rows_checks_built_files_are_remote(tmp_path) -> None:
    built = tmp_path / "built.h5"
    missing = tmp_path / "missing.h5"
    built.write_text("x")
    missing.write_text("x")

    matched, missing_names = verify_local_cache_rows([built, missing], {"built.h5", "other.h5"})

    assert matched == ["built.h5"]
    assert missing_names == ["missing.h5"]


def test_write_audit_report_includes_gate_counts(tmp_path) -> None:
    report = tmp_path / "audit.md"
    manifest = tmp_path / "manifest.json"
    manifest.write_text("{}")

    write_audit_report(
        report,
        manifest=manifest,
        bucket="cache",
        prefix="brainsets/ibl_bwm",
        matched=["a.h5"],
        missing=["b.h5", "c.h5"],
    )

    text = report.read_text()
    assert "Present: 1/3 (33.3%)" in text
    assert "`b.h5`" in text
    assert "`a.h5`" in text


def test_select_shard_rows_splits_manifest_contiguously() -> None:
    rows = [{"session_id": f"eid-{i}", "probe_name": "probe00"} for i in range(5)]

    assert select_shard_rows(rows, num_shards=2, shard_index=0) == rows[:2]
    assert select_shard_rows(rows, num_shards=2, shard_index=1) == rows[2:]


def test_write_audit_report_includes_optional_shard_plan(tmp_path) -> None:
    report = tmp_path / "audit.md"
    manifest = tmp_path / "manifest.json"
    manifest.write_text("{}")
    rows = [
        {"session_id": "eid-a", "probe_name": "probe00"},
        {"session_id": "eid-b", "probe_name": "probe00"},
        {"session_id": "eid-c", "probe_name": "probe01"},
    ]

    write_audit_report(
        report,
        manifest=manifest,
        bucket="cache",
        prefix="brainsets/ibl_bwm",
        matched=["eid-a_probe00.h5"],
        missing=["eid-b_probe00.h5", "eid-c_probe01.h5"],
        manifest_rows=rows,
        num_shards=2,
        compact_build_args="--no-wheel --trial-window-only --window-len 1.0",
    )

    text = report.read_text()
    assert "## Shard Build Plan" in text
    assert "| 0 | 1 | 1 | 0 |" in text
    assert "| 1 | 2 | 0 | 2 |" in text
    assert "--no-wheel --trial-window-only --window-len 1.0" in text
    assert "#### Shard 1" in text
    assert "`eid-c_probe01.h5`" in text


def test_region_from_args_uses_env_datacenter(monkeypatch) -> None:
    monkeypatch.setattr("sys.argv", ["sync_brainset_s3.py", "audit"])
    args = parse_args()

    assert region_from_args(args, {"BRAINSET_S3_DATACENTER": "US-IL-1"}) == "us-il-1"
