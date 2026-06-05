import numpy as np

from scripts.audit_model_free_positive_holdouts import (
    recording_target_rows,
    render_markdown,
    target_delta_summary,
    top_weight_rows,
)


def test_target_delta_summary_reports_class_specific_improvement() -> None:
    labels = np.asarray([0, 0, 1, 1], dtype=np.int64)
    true_scores = np.asarray([0.1, 0.3, 0.7, 0.2], dtype=np.float64)
    shuffle_scores = np.asarray([0.2, 0.2, 0.5, 0.4], dtype=np.float64)

    summary = target_delta_summary(true_scores, shuffle_scores, labels)

    assert summary["target0"]["n_trials"] == 2
    assert summary["target0"]["improved_fraction"] == 0.5
    assert summary["target1"]["n_trials"] == 2
    assert summary["target1"]["improved_fraction"] == 0.5
    assert np.isclose(summary["target0"]["mean_true_class_delta"], 0.0)
    assert np.isclose(summary["target1"]["mean_true_class_delta"], 0.0)


def test_recording_target_rows_breaks_down_targets_per_recording() -> None:
    labels = np.asarray([0, 1, 0, 1], dtype=np.int64)
    true_scores = np.asarray([0.1, 0.8, 0.9, 0.1], dtype=np.float64)
    shuffle_scores = np.asarray([0.2, 0.5, 0.7, 0.3], dtype=np.float64)
    recording_ids = ["b", "a", "b", "a"]

    rows = recording_target_rows(true_scores, shuffle_scores, labels, recording_ids)

    assert [row["recording"] for row in rows] == ["a", "b"]
    assert rows[0]["n_trials"] == 2
    assert rows[0]["target1_fraction"] == 1.0
    assert rows[0]["target1_improved"] == 0.5
    assert np.isnan(rows[0]["target0_improved"])
    assert rows[1]["target0_improved"] == 0.5
    assert np.isnan(rows[1]["target1_improved"])


def test_top_weight_rows_orders_positive_and_negative_weights() -> None:
    regions = ["VIS", "TH", "MB", "CTX"]
    weights = np.asarray([0.5, -0.7, 0.2, 1.1], dtype=np.float64)

    rows = top_weight_rows(regions, weights, n=2)

    assert rows["positive"] == [
        {"region": "CTX", "weight": 1.1},
        {"region": "VIS", "weight": 0.5},
    ]
    assert rows["negative"] == [
        {"region": "TH", "weight": -0.7},
        {"region": "MB", "weight": 0.2},
    ]


def test_render_markdown_marks_non_bidirectional_holdout() -> None:
    report = {
        "holdouts": [{
            "holdout": "NR_0019",
            "summary": {
                "delta_centered_auc": 0.079,
                "paired_true_vs_shuffle": {
                    "target0_improved_fraction": 0.776,
                    "target1_improved_fraction": 0.249,
                },
                "recordings_positive_true_minus_shuffle": 3,
                "n_recordings": 4,
            },
            "recording_target_rows": [],
            "top_region_weights": {"positive": [], "negative": []},
        }],
    }

    markdown = render_markdown(report)

    assert "not bidirectional" in markdown
    assert "not promotable" in markdown
