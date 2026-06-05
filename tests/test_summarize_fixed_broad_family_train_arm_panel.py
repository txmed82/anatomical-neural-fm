import json
from pathlib import Path

from scripts.summarize_fixed_broad_family_train_arm_panel import build_report


def write_summary(root: Path, holdout: str, control: str, centered_auc: float) -> None:
    path = root / f"holdout_{holdout}" / f"fixed_broad_family_count_{control}_seed0"
    path.mkdir(parents=True)
    (path / "fixed_family_summary.json").write_text(
        json.dumps({
            "family": "broad_named_anatomy",
            "feature_mode": "recording_centered",
            "n_eval": 10,
            "eval_auc": centered_auc,
            "eval_centered_auc": centered_auc,
        })
        + "\n"
    )


def test_fixed_train_arm_panel_requires_positive_centered_delta_for_all_cases(tmp_path: Path) -> None:
    cases = (
        ("A", "target_a"),
        ("B", "target_b"),
    )
    write_summary(tmp_path, "A", "none", 0.7)
    write_summary(tmp_path, "A", "within_recording_shuffle", 0.6)
    write_summary(tmp_path, "B", "none", 0.55)
    write_summary(tmp_path, "B", "within_recording_shuffle", 0.56)

    report = build_report(tmp_path, cases)

    assert report["summary"]["decision"] == "no_fixed_broad_family_train_arm_local_candidate"
    assert report["summary"]["n_positive_centered_delta"] == 1
    assert report["rows"][0]["centered_delta_vs_shuffle"] == 0.09999999999999998


def test_fixed_train_arm_panel_marks_candidate_when_all_cases_are_positive(tmp_path: Path) -> None:
    cases = (
        ("A", "target_a"),
        ("B", "target_b"),
    )
    write_summary(tmp_path, "A", "none", 0.7)
    write_summary(tmp_path, "A", "within_recording_shuffle", 0.6)
    write_summary(tmp_path, "B", "none", 0.57)
    write_summary(tmp_path, "B", "within_recording_shuffle", 0.56)

    report = build_report(tmp_path, cases)

    assert report["summary"]["decision"] == "fixed_broad_family_train_arm_local_candidate"
    assert report["summary"]["n_positive_centered_delta"] == 2
    assert not report["summary"]["paid_gpu_trigger"]


def write_predictions(root: Path, holdout: str, control: str, probs: list[float]) -> None:
    path = root / f"holdout_{holdout}" / f"fixed_broad_family_count_{control}_seed0"
    path.mkdir(parents=True)
    rows = [
        {"recording_id": "r", "target": target, "prob": prob}
        for target, prob in zip([0, 0, 1, 1], probs)
    ]
    (path / "eval_predictions.jsonl").write_text("\n".join(json.dumps(row) for row in rows) + "\n")


def test_fixed_train_arm_panel_can_fall_back_to_prediction_rows(tmp_path: Path) -> None:
    cases = (("A", "target_a"),)
    write_predictions(tmp_path, "A", "none", [0.1, 0.2, 0.8, 0.9])
    write_predictions(tmp_path, "A", "within_recording_shuffle", [0.1, 0.9, 0.2, 0.8])

    report = build_report(tmp_path, cases)

    assert report["summary"]["decision"] == "fixed_broad_family_train_arm_local_candidate"
    assert report["rows"][0]["n_eval"] == 4
    assert report["rows"][0]["true_path"].endswith("eval_predictions.jsonl")
