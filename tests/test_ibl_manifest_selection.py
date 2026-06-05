from __future__ import annotations

import json

import h5py
import numpy as np

from scripts.build_ibl_brainset import trial_window_spike_mask
from scripts.build_ibl_brainset_batch import _manifest_insertions, missing_streams, select_shard, write_report
from scripts.select_ibl_manifest import compact_insertion, select_balanced


def test_compact_insertion_keeps_only_pass_with_units() -> None:
    row = compact_insertion({
        "id": "ins-a",
        "session": "eid-a",
        "name": "probe00",
        "session_info": {"subject": "mouse-a", "lab": "lab-a"},
        "json": {"qc": "PASS", "n_units": 123, "extended_qc": {"alignment_qc": 0.9}},
    })

    assert row == {
        "session_id": "eid-a",
        "probe_name": "probe00",
        "subject_id": "mouse-a",
        "lab": "lab-a",
        "start_time": None,
        "task_protocol": None,
        "insertion_id": "ins-a",
        "n_units_meta": 123,
        "qc": "PASS",
        "alignment_qc": 0.9,
    }
    assert compact_insertion({"json": {"qc": "FAIL", "n_units": 123}}) is None
    assert compact_insertion({"json": {"qc": "PASS", "n_units": 0}}) is None


def test_select_balanced_caps_subjects_and_prefers_more_units() -> None:
    candidates = [
        {"session_id": f"eid-{subject}-{i}", "probe_name": "probe00", "subject_id": subject,
         "lab": "lab", "n_units_meta": n_units}
        for subject, values in {"a": [100, 300, 200], "b": [250, 150], "c": [120]}.items()
        for i, n_units in enumerate(values)
    ]

    selected = select_balanced(candidates, target=5, max_per_subject=2, min_units=100)

    assert len(selected) == 5
    assert [r["n_units_meta"] for r in selected if r["subject_id"] == "a"] == [300, 200]
    assert max(sum(1 for r in selected if r["subject_id"] == s) for s in ["a", "b", "c"]) <= 2


def test_select_balanced_prefers_two_recordings_per_subject_when_available() -> None:
    candidates = [
        {"session_id": f"eid-{subject}-{i}", "probe_name": "probe00", "subject_id": subject,
         "lab": "lab", "n_units_meta": 200 - i}
        for subject in ["a", "b", "c", "d"]
        for i in range(2)
    ]

    selected = select_balanced(candidates, target=4, max_per_subject=2, min_units=100)

    assert sorted({r["subject_id"] for r in selected}) == ["a", "b"]
    assert len(selected) == 4


def test_select_balanced_round_robins_labs() -> None:
    candidates = [
        {"session_id": f"eid-{lab}-{subject}-{i}", "probe_name": "probe00",
         "subject_id": f"{lab}-{subject}", "lab": lab, "n_units_meta": 200}
        for lab in ["lab-a", "lab-b"]
        for subject in range(3)
        for i in range(2)
    ]

    selected = select_balanced(candidates, target=4, max_per_subject=2, min_units=100)

    assert {r["lab"] for r in selected} == {"lab-a", "lab-b"}
    assert len({r["subject_id"] for r in selected}) == 2


def test_manifest_insertions_accepts_committed_schema(tmp_path) -> None:
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps({
        "recordings": [
            {"session_id": "eid-a", "probe_name": "probe00"},
            {"eid": "eid-b", "probe": "probe01"},
        ],
    }))

    assert _manifest_insertions(path) == [
        {"session": "eid-a", "name": "probe00"},
        {"session": "eid-b", "name": "probe01"},
    ]


def test_select_shard_splits_manifest_contiguously() -> None:
    rows = [{"session": f"eid-{i}", "name": "probe00"} for i in range(10)]

    assert select_shard(rows, num_shards=3, shard_index=0) == rows[:3]
    assert select_shard(rows, num_shards=3, shard_index=1) == rows[3:6]
    assert select_shard(rows, num_shards=3, shard_index=2) == rows[6:]


def test_trial_window_spike_mask_keeps_only_training_windows() -> None:
    spike_times = np.array([0.9, 1.0, 1.4, 2.1, 3.0, 3.2, 4.2])
    stim_on = np.array([1.0, np.nan, 3.0])

    mask = trial_window_spike_mask(spike_times, stim_on, window_len=0.5)

    assert mask.tolist() == [False, True, True, False, True, True, False]


def test_batch_report_records_compact_build_options(tmp_path) -> None:
    out = tmp_path / "build.md"

    write_report(
        out,
        manifest=tmp_path / "manifest.json",
        selected=[{"session": "eid-a", "name": "probe00"}],
        built_rows=[],
        failed_rows=[],
        skipped_existing=[],
        elapsed_seconds=1.2,
        num_shards=1,
        shard_index=0,
        include_wheel=False,
        trial_window_only=True,
        window_len=1.25,
    )

    text = out.read_text()
    assert "Include wheel: `False`" in text
    assert "Trial-window-only spikes: `True`" in text
    assert "Window length: `1.25`" in text


def test_missing_streams_detects_existing_compact_behavior_gap(tmp_path) -> None:
    path = tmp_path / "rec.h5"
    with h5py.File(path, "w") as h5:
        h5.create_group("spikes")

    assert missing_streams(path, ["wheel"]) == ["wheel"]

    with h5py.File(path, "a") as h5:
        h5.create_group("wheel")

    assert missing_streams(path, ["wheel"]) == []
    assert missing_streams(tmp_path / "missing.h5", ["wheel"]) == ["wheel"]
