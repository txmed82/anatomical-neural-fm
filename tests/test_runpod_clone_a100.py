from __future__ import annotations

from dataclasses import replace

import pytest

from scripts.runpod_clone_a100 import (
    ClonePilotConfig,
    authenticated_repo_url,
    build_pod_body,
    build_start_script,
)


def config() -> ClonePilotConfig:
    return ClonePilotConfig(
        branch="runpod-pilot-phases-3-5",
        repo_url="https://github.com/txmed82/anatomical-neural-fm.git",
        datacenter="US-MO-1",
        gpu_type="NVIDIA A100 80GB PCIe",
        image_name="runpod/pytorch:test",
        container_disk_gb=80,
        volume_gb=0,
        max_runtime_seconds=1234,
        build_recordings=6,
        max_steps=600,
        eval_batches=50,
        manifest_path="manifests/ibl_bwm_phase4.json",
        seeds="0 1 2",
        target_mode="stimulus_side",
        sweep_script="scripts/run_phase2_cloud_a100.sh",
        output_root="runs/phase2_cloud_a100",
        result_doc="docs/cloud_phase3_5_results.md",
    )


def test_authenticated_repo_url_requires_github_https() -> None:
    with pytest.raises(ValueError):
        authenticated_repo_url("git@github.com:txmed82/anatomical-neural-fm.git")


def test_start_script_clones_branch_builds_data_and_pushes_results() -> None:
    script = build_start_script(config())

    assert "git clone --branch runpod-pilot-phases-3-5" in script
    assert "scripts/select_ibl_manifest.py --target 6 --out manifests/ibl_bwm_phase4.json" in script
    assert "scripts/build_ibl_brainset_batch.py --manifest manifests/ibl_bwm_phase4.json" in script
    assert "cat > /tmp/run_phase3_5_body.sh <<'RUNSCRIPT'" in script
    assert "export SEEDS='0 1 2'" in script
    assert "export MAX_STEPS=600" in script
    assert "export EVAL_BATCHES=50" in script
    assert "export TARGET_MODE=stimulus_side" in script
    assert "export OUT_ROOT=runs/phase2_cloud_a100" in script
    assert "- target mode: stimulus_side" in script
    assert "bash scripts/run_phase2_cloud_a100.sh" in script
    assert "git push origin HEAD:runpod-pilot-phases-3-5" in script
    assert "DELETE" in script


def test_pod_body_uses_container_disk_no_network_volume() -> None:
    body = build_pod_body("pilot", config(), "runpod", "github")

    assert "networkVolumeId" not in body
    assert body["volumeInGb"] == 0
    assert body["containerDiskInGb"] == 80
    assert body["gpuTypeIds"] == ["NVIDIA A100 80GB PCIe"]
    assert body["env"]["RUNPOD_API_KEY"] == "runpod"
    assert body["env"]["GITHUB_TOKEN"] == "github"


def test_start_script_can_run_leave_subject_out_report() -> None:
    cfg = replace(
        config(),
        sweep_script="scripts/run_leave_subject_out_a100.sh",
        output_root="runs/leave_subject_out_a100",
        result_doc="docs/leave_subject_out_results.md",
    )

    script = build_start_script(cfg)

    assert "bash scripts/run_leave_subject_out_a100.sh" in script
    assert "export OUT_ROOT=runs/leave_subject_out_a100" in script
    assert "cat > docs/leave_subject_out_results.md" in script
    assert "runs/leave_subject_out_a100/summary.md" in script


def test_start_script_can_skip_pod_verification() -> None:
    cfg = replace(config(), skip_verification=True)

    script = build_start_script(cfg)

    assert "=== skipping local verification ===" in script
    assert "uv run pytest -q" not in script
    assert "uv run python scripts/00_ibl_smoke_test.py" not in script
    assert "uv run python scripts/build_cell_type_priors.py" in script


def test_start_script_can_pass_build_shard_args() -> None:
    cfg = replace(
        config(),
        build_extra_args="--num-shards 8 --shard-index 0 --allow-partial",
    )

    script = build_start_script(cfg)

    assert (
        "scripts/build_ibl_brainset_batch.py --manifest manifests/ibl_bwm_phase4.json "
        "--report runs/phase2_cloud_a100/build_report.md "
        "--num-shards 8 --shard-index 0 --allow-partial"
    ) in script
    assert "## Build Report" in script
