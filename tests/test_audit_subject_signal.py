from pathlib import Path

from scripts.audit_subject_signal import (
    SubjectResult,
    best_result_by_subject,
    parse_lso_results,
    summarize_manifest_subjects,
)


def test_parse_lso_results_table(tmp_path: Path):
    path = tmp_path / "results.md"
    path.write_text(
        "\n".join([
            "| holdout | arm | n_seeds | mean_AUC | mean_delta_vs_shared | seed_deltas |",
            "|---|---|---|---|---|---|",
            "| DY_008 | pure_anatomy | 3 | 0.553 | +0.045 | +0.059,+0.027,+0.049 |",
            "| DY_008 | region_only | 3 | 0.549 | +0.041 | +0.043,+0.026,+0.054 |",
        ])
    )

    rows = parse_lso_results(path)

    assert rows == [
        SubjectResult("DY_008", "pure_anatomy", 3, 0.553, 0.045, (0.059, 0.027, 0.049)),
        SubjectResult("DY_008", "region_only", 3, 0.549, 0.041, (0.043, 0.026, 0.054)),
    ]


def test_summarize_manifest_subjects_groups_probe_and_alignment():
    manifest = {
        "recordings": [
            {
                "subject_id": "S1",
                "lab": "lab-a",
                "probe_name": "probe00",
                "task_protocol": "task",
                "n_units_meta": 10,
                "alignment_qc": 0.8,
            },
            {
                "subject_id": "S1",
                "lab": "lab-a",
                "probe_name": "probe01",
                "task_protocol": "task",
                "n_units_meta": 15,
                "alignment_qc": 1.0,
            },
        ]
    }

    rows = summarize_manifest_subjects(manifest)

    assert rows["S1"]["n_recordings"] == 2
    assert rows["S1"]["n_units_meta"] == 25
    assert rows["S1"]["labs"] == {"lab-a"}
    assert rows["S1"]["probes"]["probe00"] == 1
    assert rows["S1"]["alignment_qc"] == [0.8, 1.0]


def test_best_result_by_subject_uses_largest_delta():
    rows = [
        SubjectResult("S1", "pure_anatomy", 3, 0.52, 0.01, (0.01,)),
        SubjectResult("S1", "region_only", 3, 0.55, 0.04, (0.04,)),
    ]

    assert best_result_by_subject(rows)["S1"].arm == "region_only"
