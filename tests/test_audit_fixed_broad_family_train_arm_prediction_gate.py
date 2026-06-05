import json
from pathlib import Path

from scripts.audit_fixed_broad_family_train_arm_prediction_gate import build_report, paired_rows


def row(recording: str, t0: float, target: int, logit: float) -> dict:
    return {
        "recording_id": recording,
        "t0": t0,
        "target": target,
        "logit": logit,
        "prob": 1.0 / (1.0 + pow(2.718281828, -logit)),
    }


def write_predictions(root: Path, holdout: str, control: str, rows: list[dict]) -> None:
    path = root / f"holdout_{holdout}" / f"fixed_broad_family_count_{control}_seed0"
    path.mkdir(parents=True)
    (path / "eval_predictions.jsonl").write_text("\n".join(json.dumps(item) for item in rows) + "\n")


def test_paired_rows_requires_matching_trial_keys() -> None:
    true = [row("r", 1.0, 0, -1.0)]
    shuffle = [row("r", 2.0, 0, -1.0)]

    try:
        paired_rows(true, shuffle)
    except ValueError as exc:
        assert "missing shuffled prediction" in str(exc)
    else:
        raise AssertionError("expected missing prediction error")


def test_prediction_gate_rejects_when_recording_bidirectionality_fails(tmp_path: Path) -> None:
    cases = (("A", "target_a"),)
    true = [
        row("r0", 0.0, 0, -2.0),
        row("r0", 1.0, 1, 2.0),
        row("r1", 0.0, 0, 2.0),
        row("r1", 1.0, 1, 2.0),
    ]
    shuffle = [
        row("r0", 0.0, 0, 2.0),
        row("r0", 1.0, 1, -2.0),
        row("r1", 0.0, 0, 1.0),
        row("r1", 1.0, 1, -2.0),
    ]
    write_predictions(tmp_path, "A", "none", true)
    write_predictions(tmp_path, "A", "within_recording_shuffle", shuffle)

    report = build_report(
        tmp_path,
        cases=cases,
        min_target_improvement=0.5,
        min_bidirectional_recording_fraction=1.0,
    )

    assert report["summary"]["decision"] == "no_fixed_broad_family_prediction_gate_candidate"
    assert report["rows"][0]["decision"] == "reject: recording bidirectionality"
    assert report["rows"][0]["n_bidirectional_recordings"] == 1


def test_prediction_gate_marks_candidate_when_all_recordings_are_bidirectional(tmp_path: Path) -> None:
    cases = (("A", "target_a"),)
    true = [
        row("r0", 0.0, 0, -2.0),
        row("r0", 1.0, 1, 2.0),
        row("r1", 0.0, 0, -1.0),
        row("r1", 1.0, 1, 1.0),
    ]
    shuffle = [
        row("r0", 0.0, 0, 2.0),
        row("r0", 1.0, 1, -2.0),
        row("r1", 0.0, 0, 1.0),
        row("r1", 1.0, 1, -1.0),
    ]
    write_predictions(tmp_path, "A", "none", true)
    write_predictions(tmp_path, "A", "within_recording_shuffle", shuffle)

    report = build_report(tmp_path, cases=cases, min_bidirectional_recording_fraction=1.0)

    assert report["summary"]["decision"] == "fixed_broad_family_prediction_gate_candidate"
    assert report["summary"]["candidate_holdouts"] == ["A"]
    assert report["rows"][0]["decision"] == "candidate"
