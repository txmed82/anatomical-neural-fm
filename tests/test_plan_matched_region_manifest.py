from collections import Counter

from scripts.plan_matched_region_manifest import (
    best_support_subset,
    lab_counts,
    filter_metadata_failures_to_manifest,
    filter_manifest_to_subjects,
    local_subject_row,
    manifest_from_existing,
    selected_subject_counts,
    subjects_passing_support_gate,
    support_summary,
    support_against_others,
    write_report,
    write_manifest,
)


class Args:
    target = 4
    scan_limit = 100
    max_per_subject = 2
    min_units = 200
    region_granularity = "parent"


def test_write_manifest_records_selection_metadata():
    selected = [
        {"subject_id": "S1", "lab": "lab-a", "n_units_meta": 250},
        {"subject_id": "S2", "lab": "lab-b", "n_units_meta": 300},
    ]

    manifest = write_manifest(selected=selected, candidates=selected, args=Args())

    assert manifest["n_recordings"] == 2
    assert manifest["n_subjects"] == 2
    assert manifest["selection"]["region_granularity"] == "parent"
    assert manifest["selection"]["candidate_pool_subjects"] == 2


def test_support_against_others_scores_heldout_region_overlap():
    local_subjects = {
        "S1": {"regions": Counter({"A": 3, "B": 1})},
        "S2": {"regions": Counter({"A": 5, "C": 2})},
        "S3": {"regions": Counter({"D": 9})},
    }

    support = support_against_others(local_subjects, "S1")

    assert support is not None
    assert support["unit_support_frac"] == 0.75
    assert support["top_supported"] == 1
    assert support["top_total"] == 2
    assert support["missing_top"] == ["B"]


def test_support_summary_is_machine_readable():
    local_subjects = {
        "S1": {"recording_ids": ["a"], "n_units": 4, "regions": Counter({"A": 3, "B": 1})},
        "S2": {"recording_ids": ["b", "c"], "n_units": 5, "regions": Counter({"A": 5})},
    }

    summary = support_summary(local_subjects)

    assert summary["S1"]["cached_recordings"] == 1
    assert summary["S1"]["n_units"] == 4
    assert summary["S1"]["unit_support_frac"] == 0.75
    assert summary["S1"]["missing_top"] == ["B"]


def test_subjects_passing_support_gate_iterates_to_stable_set():
    local_subjects = {
        "S1": {"regions": Counter({"A": 9, "B": 1})},
        "S2": {"regions": Counter({"A": 8, "B": 2})},
        "bad": {"regions": Counter({"X": 10})},
    }

    assert subjects_passing_support_gate(local_subjects, 0.8) == {"S1", "S2"}


def test_subjects_passing_support_gate_can_filter_initial_scores_only():
    local_subjects = {
        "S1": {"regions": Counter({"A": 8, "B": 2})},
        "S2": {"regions": Counter({"A": 8, "C": 2})},
        "bridge": {"regions": Counter({"B": 2, "C": 2, "D": 6})},
    }

    assert subjects_passing_support_gate(local_subjects, 0.9, iterative=False) == {"S1", "S2"}
    assert subjects_passing_support_gate(local_subjects, 0.9, iterative=True) == set()


def test_count_helpers_are_stable():
    rows = [
        {"subject_id": "S1", "lab": "lab-a"},
        {"subject_id": "S1", "lab": "lab-a"},
        {"subject_id": "S2", "lab": "lab-b"},
    ]

    assert selected_subject_counts(rows) == Counter({"S1": 2, "S2": 1})
    assert lab_counts(rows) == Counter({"lab-a": 2, "lab-b": 1})


def test_filter_manifest_to_subjects_updates_counts():
    manifest = {
        "selection": {"target": 3},
        "n_recordings": 3,
        "n_subjects": 3,
        "labs": ["lab-a", "lab-b", "lab-c"],
        "recordings": [
            {"subject_id": "S1", "lab": "lab-a"},
            {"subject_id": "S2", "lab": "lab-b"},
            {"subject_id": "S3", "lab": "lab-c"},
        ],
    }

    filtered = filter_manifest_to_subjects(manifest, {"S1", "S3"}, min_support=0.8)

    assert filtered["n_recordings"] == 2
    assert filtered["n_subjects"] == 2
    assert filtered["labs"] == ["lab-a", "lab-c"]
    assert filtered["selection"]["filter_min_support"] == 0.8
    assert filtered["selection"]["pre_filter_recordings"] == 3


def test_filter_metadata_failures_to_manifest_keeps_only_selected_recordings():
    manifest = {
        "recordings": [
            {"session_id": "eid-a", "probe_name": "probe00"},
        ],
    }
    failures = [
        {"session": "eid-a", "probe": "probe00", "error": "missing"},
        {"session": "eid-b", "probe": "probe01", "error": "missing"},
    ]

    filtered = filter_metadata_failures_to_manifest(failures, manifest)

    assert filtered == [{"session": "eid-a", "probe": "probe00", "error": "missing"}]


def test_best_support_subset_prefers_high_pass_fraction_with_min_subjects():
    local_subjects = {
        "S1": {"recording_ids": ["1"], "n_units": 10, "regions": Counter({"A": 8, "B": 2})},
        "S2": {"recording_ids": ["2"], "n_units": 10, "regions": Counter({"A": 8, "B": 2})},
        "S3": {"recording_ids": ["3"], "n_units": 10, "regions": Counter({"A": 8, "B": 2})},
        "bad": {"recording_ids": ["4"], "n_units": 10, "regions": Counter({"X": 10})},
    }

    subjects, meta = best_support_subset(local_subjects, min_support=0.8, min_subjects=3)

    assert subjects == {"S1", "S2", "S3"}
    assert meta["pass_count"] == 3
    assert meta["subject_count"] == 3
    assert meta["pass_frac"] == 1.0


def test_manifest_from_existing_overrides_region_granularity(tmp_path):
    path = tmp_path / "manifest.json"
    path.write_text('{"selection": {"region_granularity": "fine"}, "recordings": []}')

    manifest = manifest_from_existing(path, "parent")

    assert manifest["selection"]["region_granularity"] == "parent"


def test_local_subject_row_accumulates_region_counts():
    rows = {}

    local_subject_row(rows, subject="S1", recording_id="rec-a", regions=["A", "A", "B"])
    local_subject_row(rows, subject="S1", recording_id="rec-b", regions=["B", "C"])

    assert rows["S1"]["recording_ids"] == ["rec-a", "rec-b"]
    assert rows["S1"]["n_units"] == 5
    assert rows["S1"]["regions"] == Counter({"A": 2, "B": 2, "C": 1})


def test_write_report_notes_metadata_region_source_and_failures(tmp_path):
    manifest = {
        "n_recordings": 2,
        "n_subjects": 2,
        "selection": {"region_granularity": "parent"},
        "recordings": [
            {"subject_id": "S1", "lab": "lab-a", "n_units_meta": 250, "probe_name": "probe00"},
            {"subject_id": "S2", "lab": "lab-b", "n_units_meta": 260, "probe_name": "probe01"},
        ],
    }
    local_subjects = {}
    local_subject_row(local_subjects, subject="S1", recording_id="eid-a_probe00", regions=["A", "B"])
    out = tmp_path / "report.md"

    write_report(
        manifest=manifest,
        local_subjects=local_subjects,
        out_path=out,
        data_dir=tmp_path / "data",
        region_source="OpenAlyx cluster/channel metadata",
        metadata_failures=[{"session": "eid-b", "probe": "probe01", "error": "missing"}],
    )

    text = out.read_text()
    assert "Region source: OpenAlyx cluster/channel metadata" in text
    assert "## Metadata Region Failures" in text
    assert "| eid-b | probe01 | missing |" in text
    assert "confirm support again after the HDF5 build" in text
