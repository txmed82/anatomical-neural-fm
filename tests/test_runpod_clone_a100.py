from __future__ import annotations

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
    )


def test_authenticated_repo_url_requires_github_https() -> None:
    with pytest.raises(ValueError):
        authenticated_repo_url("git@github.com:txmed82/anatomical-neural-fm.git")


def test_start_script_clones_branch_builds_data_and_pushes_results() -> None:
    script = build_start_script(config())

    assert "git clone --branch runpod-pilot-phases-3-5" in script
    assert "scripts/build_ibl_brainset_batch.py 6" in script
    assert "MAX_STEPS=600 EVAL_BATCHES=50 bash scripts/run_phase2_cloud_a100.sh" in script
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
