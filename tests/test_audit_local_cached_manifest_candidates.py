from types import SimpleNamespace
from pathlib import Path

import numpy as np

from scripts.audit_local_cached_manifest_candidates import (
    candidate_panels,
    load_extra_manifest_panels,
    manifest_panel_label,
    manifest_output_path,
    recording_manifest_row,
    score_panel,
    split_recording_id,
)


def test_split_recording_id_keeps_probe_suffix() -> None:
    assert split_recording_id("session-with-dashes_probe01") == ("session-with-dashes", "probe01")


def test_recording_manifest_row_contains_selectable_fields() -> None:
    rec = SimpleNamespace(
        subject=SimpleNamespace(id="S1"),
        units=SimpleNamespace(id=np.asarray(["u1", "u2"])),
    )

    row = recording_manifest_row("eid_probe00", rec)

    assert row == {
        "session_id": "eid",
        "probe_name": "probe00",
        "subject_id": "S1",
        "n_units": 2,
    }


def test_candidate_panels_adds_min_subject_recording_panel() -> None:
    all_rids = ["a_probe00", "b_probe00", "c_probe00", "d_probe00"]
    subject_by_rid = {
        "a_probe00": "S1",
        "b_probe00": "S1",
        "c_probe00": "S2",
        "d_probe00": "S3",
    }

    panels = dict(candidate_panels(
        all_rids,
        subject_by_rid,
        baseline_recording_ids=["a_probe00", "c_probe00"],
        min_subject_recordings=2,
    ))

    assert panels["current_support80_hdf5"] == ["a_probe00", "c_probe00"]
    assert panels["all_local_cached"] == sorted(all_rids)
    assert panels["local_cached_min2_recordings_per_subject"] == ["a_probe00", "b_probe00"]


def test_candidate_panels_includes_extra_manifest_panels() -> None:
    panels = dict(candidate_panels(
        ["a_probe00", "b_probe00"],
        {"a_probe00": "S1", "b_probe00": "S2"},
        baseline_recording_ids=["a_probe00"],
        extra_manifest_panels=[("projected", ["a_probe00", "b_probe00"])],
        min_subject_recordings=2,
    ))

    assert panels["projected"] == ["a_probe00", "b_probe00"]


def test_manifest_output_path_uses_readable_suffixes() -> None:
    assert str(manifest_output_path(
        prefix=Path("manifests/ibl_bwm_local_cached"),
        label="all_local_cached",
    )) == "manifests/ibl_bwm_local_cached_all.json"
    assert str(manifest_output_path(
        prefix=Path("manifests/ibl_bwm_local_cached"),
        label="local_cached_min2_recordings_per_subject",
    )) == "manifests/ibl_bwm_local_cached_min2_subjects.json"


def test_manifest_panel_label_removes_dataset_prefix() -> None:
    assert manifest_panel_label(Path("manifests/ibl_bwm_external_support80_projected_hdf5.json")) == (
        "external_support80_projected_hdf5"
    )


def test_load_extra_manifest_panels_keeps_only_cached_recordings(tmp_path: Path) -> None:
    manifest = tmp_path / "ibl_bwm_projected.json"
    manifest.write_text(
        """{
  "recordings": [
    {"session_id": "a", "probe_name": "probe00"},
    {"session_id": "missing", "probe_name": "probe01"}
  ]
}
"""
    )

    panels = load_extra_manifest_panels([manifest], ["a_probe00"])

    assert panels == [("projected", ["a_probe00"])]


def test_score_panel_requires_target_balance_and_family_units_per_subject() -> None:
    rids = ["a_probe00", "b_probe00", "c_probe00", "d_probe00"]
    subject_by_rid = {
        "a_probe00": "S1",
        "b_probe00": "S1",
        "c_probe00": "S2",
        "d_probe00": "S2",
    }
    target_counts = {
        target: {
            rid: {"target0": 50, "target1": 50, "min_class": 50, "n_trials": 100}
            for rid in rids
        }
        for target in ("choice", "stimulus_side", "feedback", "prior_side")
    }
    family_counts = {
        rid: {"thalamic": 30, "hippocampal_formation": 0}
        for rid in rids
    }
    target_counts["choice"]["d_probe00"]["min_class"] = 20

    panel = score_panel(
        "panel",
        rids,
        subject_by_rid=subject_by_rid,
        target_counts=target_counts,
        family_counts=family_counts,
        min_class_trials=40,
        min_family_units=25,
        min_subject_recordings=2,
    )

    thalamic_choice = next(
        row for row in panel["top_target_family_rows"]
        if row["target_mode"] == "choice" and row["family"] == "thalamic"
    )
    assert thalamic_choice["all_subjects_pass"] is False
    assert thalamic_choice["passing_subjects"] == 1
    thalamic_stimulus = next(
        row for row in panel["top_target_family_rows"]
        if row["target_mode"] == "stimulus_side" and row["family"] == "thalamic"
    )
    assert thalamic_stimulus["all_subjects_pass"] is True
    assert panel["n_passing_target_family_rows"] >= 1
