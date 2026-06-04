from collections import Counter

from scripts.plan_matched_region_manifest import (
    lab_counts,
    manifest_from_existing,
    selected_subject_counts,
    support_against_others,
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


def test_count_helpers_are_stable():
    rows = [
        {"subject_id": "S1", "lab": "lab-a"},
        {"subject_id": "S1", "lab": "lab-a"},
        {"subject_id": "S2", "lab": "lab-b"},
    ]

    assert selected_subject_counts(rows) == Counter({"S1": 2, "S2": 1})
    assert lab_counts(rows) == Counter({"lab-a": 2, "lab-b": 1})


def test_manifest_from_existing_overrides_region_granularity(tmp_path):
    path = tmp_path / "manifest.json"
    path.write_text('{"selection": {"region_granularity": "fine"}, "recordings": []}')

    manifest = manifest_from_existing(path, "parent")

    assert manifest["selection"]["region_granularity"] == "parent"
