import json

from scripts.audit_response_extreme_training_failure import (
    build_report,
    parse_cloud_log,
    parse_cloud_result_markdown,
)


def test_parse_cloud_log_labels_region_shuffle_from_config(tmp_path) -> None:
    path = tmp_path / "cloud.log"
    records = [
        {
            "event": "config",
            "holdout": ["CSHL045"],
            "target_mode": "post_error_response_extreme_25_75_le_1",
            "arm": "region_only",
            "region_label_control": "shuffle",
            "best_metric": "eval_loss",
            "max_steps": 300,
            "eval_batches": 20,
            "region_filter": "shared_regions",
            "region_granularity": "parent",
        },
        {
            "event": "split",
            "n_train_trials": 10,
            "n_eval_trials": 4,
            "n_eval_rids": 1,
            "n_allowed_regions": 3,
            "eval_class_balance": {"L": 2, "R": 2},
        },
        {"event": "eval", "step": 150, "eval_loss": 0.7, "eval_auc": 0.4, "eval_n": 4},
        {"event": "eval", "step": 300, "eval_loss": 0.6, "eval_auc": 0.5, "eval_n": 4},
        {"event": "done", "wall_clock_s": 2.0, "best_metric": "eval_loss", "best_metric_value": 0.6},
    ]
    path.write_text("\n".join(json.dumps(row) for row in records))

    runs = parse_cloud_log(path)

    assert runs[0]["arm"] == "region_shuffle"
    assert runs[0]["split"]["n_train_trials"] == 10
    assert runs[0]["evals"][1]["eval_auc"] == 0.5


def test_build_report_marks_negative_training_pilot(tmp_path) -> None:
    md = tmp_path / "result.md"
    md.write_text(
        "\n".join(
            [
                "| holdout | arm | n_seeds | mean_AUC | mean_delta_vs_shared | seed_deltas |",
                "|---|---|---|---|---|---|",
                "| CSHL045 | region_only | 1 | 0.496 | -0.065 | -0.065 |",
                "| CSHL045 | region_shuffle | 1 | 0.602 | +0.041 | +0.041 |",
            ]
        )
    )
    cloud_runs = [
        {
            "holdout": "CSHL045",
            "target_mode": "post_error_response_extreme_25_75_le_1",
            "arm": "shared_baseline",
            "best_metric": "eval_loss",
            "evals": [{"step": 150, "eval_loss": 0.69, "eval_auc": 0.56, "eval_n": 4}],
            "split": {"n_train_trials": 10, "n_eval_trials": 4},
            "done": {"wall_clock_s": 1.0},
            "has_full_eval": False,
            "has_eval_predictions": False,
        },
        {
            "holdout": "CSHL045",
            "target_mode": "post_error_response_extreme_25_75_le_1",
            "arm": "region_only",
            "best_metric": "eval_loss",
            "evals": [{"step": 150, "eval_loss": 0.68, "eval_auc": 0.49, "eval_n": 4}],
            "split": {"n_train_trials": 10, "n_eval_trials": 4},
            "done": {"wall_clock_s": 1.0},
            "has_full_eval": False,
            "has_eval_predictions": False,
        },
        {
            "holdout": "CSHL045",
            "target_mode": "post_error_response_extreme_25_75_le_1",
            "arm": "region_shuffle",
            "best_metric": "eval_loss",
            "evals": [{"step": 150, "eval_loss": 0.67, "eval_auc": 0.60, "eval_n": 4}],
            "split": {"n_train_trials": 10, "n_eval_trials": 4},
            "done": {"wall_clock_s": 1.0},
            "has_full_eval": False,
            "has_eval_predictions": False,
        },
    ]

    report = build_report(
        local_rows={
            ("CSHL045", "post_error_response_extreme_25_75_le_1", "broad_named_anatomy"): {
                "mean_centered_delta_vs_shuffle": 0.05,
                "mean_centered_delta_vs_total": 0.03,
                "n_candidate_seeds": 5,
                "n_seeds": 5,
                "min_bidirectional_recordings": 3,
                "max_bidirectional_recordings": 3,
            }
        },
        projected_balances={"post_error_response_extreme_25_75_le_1": {"n_trials": 14}},
        cloud_runs=cloud_runs,
        cloud_result_rows=parse_cloud_result_markdown(md),
    )

    assert report["summary"]["decision"] == "local_to_training_readout_mismatch"
    assert not report["summary"]["paid_gpu_trigger"]
    assert report["cases"][0]["target_alignment"] == "matched"
    assert "shuffled_region_outperformed_true" in report["cases"][0]["failure_modes"]
