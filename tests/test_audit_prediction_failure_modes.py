import json
from pathlib import Path

import h5py
import pytest

from scripts.audit_prediction_failure_modes import analyze


def write_predictions(root: Path, holdout: str, arm: str, seed: int, rows: list[dict]) -> None:
    run_dir = root / f"holdout_{holdout}" / f"cloud_choice_{arm}_seed{seed}"
    run_dir.mkdir(parents=True)
    (run_dir / "eval_predictions.jsonl").write_text(
        "\n".join(json.dumps(row) for row in rows) + "\n"
    )


def write_recording(path: Path, regions: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with h5py.File(path, "w") as h5:
        units = h5.create_group("units")
        units.create_dataset(
            "region_acronym",
            data=[region.encode("utf-8") for region in regions],
        )


def test_analyze_quantifies_offsets_and_region_support(tmp_path: Path) -> None:
    root = tmp_path / "runs"
    data_dir = tmp_path / "data"
    manifest = tmp_path / "manifest.json"
    holdout = "heldout"
    manifest.write_text(json.dumps({
        "recordings": [
            {"session_id": "eval-a", "probe_name": "probe00", "subject_id": holdout},
            {"session_id": "eval-b", "probe_name": "probe00", "subject_id": holdout},
            {"session_id": "train-a", "probe_name": "probe00", "subject_id": "train"},
        ]
    }))
    write_recording(data_dir / "eval-a_probe00.h5", ["VISp", "VISp", "CA1"])
    write_recording(data_dir / "eval-b_probe00.h5", ["VISp", "DG"])
    write_recording(data_dir / "train-a_probe00.h5", ["VISp"])

    base_rows = [
        {"recording_id": "eval-a_probe00", "t0": 0.0, "target": 0, "prob": 0.40},
        {"recording_id": "eval-a_probe00", "t0": 1.0, "target": 1, "prob": 0.60},
        {"recording_id": "eval-b_probe00", "t0": 0.0, "target": 0, "prob": 0.40},
        {"recording_id": "eval-b_probe00", "t0": 1.0, "target": 1, "prob": 0.60},
    ]
    true_rows = [
        {"recording_id": "eval-a_probe00", "t0": 0.0, "target": 0, "prob": 0.45},
        {"recording_id": "eval-a_probe00", "t0": 1.0, "target": 1, "prob": 0.55},
        {"recording_id": "eval-b_probe00", "t0": 0.0, "target": 0, "prob": 0.30},
        {"recording_id": "eval-b_probe00", "t0": 1.0, "target": 1, "prob": 0.70},
    ]
    shuffle_rows = [
        {"recording_id": "eval-a_probe00", "t0": 0.0, "target": 0, "prob": 0.35},
        {"recording_id": "eval-a_probe00", "t0": 1.0, "target": 1, "prob": 0.65},
        {"recording_id": "eval-b_probe00", "t0": 0.0, "target": 0, "prob": 0.35},
        {"recording_id": "eval-b_probe00", "t0": 1.0, "target": 1, "prob": 0.65},
    ]
    write_predictions(root, holdout, "shared_baseline", 0, base_rows)
    write_predictions(root, holdout, "region_only", 0, true_rows)
    write_predictions(root, holdout, "region_shuffle", 0, shuffle_rows)

    result = analyze(
        root=root,
        holdout=holdout,
        manifest=manifest,
        data_dir=data_dir,
        region_granularity="fine",
    )

    seed = result["seed_summaries"]["0"]
    assert seed["metrics"]["region_only"]["n"] == 4
    assert seed["recordings"]["eval-a_probe00"]["region_only_minus_shuffle_auc"] == pytest.approx(0.0)
    assert seed["recordings"]["eval-a_probe00"]["paired_region_only_vs_shuffle"] == pytest.approx(0.0)
    assert result["region_support"]["eval-a_probe00"]["unit_support_fraction"] == pytest.approx(2 / 3)
    assert result["region_support"]["eval-a_probe00"]["missing_top_regions"] == ["CA1"]
