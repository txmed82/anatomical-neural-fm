from __future__ import annotations

import pytest

from scripts.runpod_first_a100 import (
    RunpodConfig,
    build_pod_body,
    build_start_script,
    s3_endpoint,
)


def test_s3_endpoint_known_datacenter() -> None:
    assert s3_endpoint("US-MO-1") == "https://s3api-us-mo-1.runpod.io/"


def test_s3_endpoint_rejects_unknown_datacenter() -> None:
    with pytest.raises(ValueError):
        s3_endpoint("US-UNKNOWN-1")


def test_start_script_has_runtime_guard_and_self_termination() -> None:
    script = build_start_script(1234)

    assert "timeout 1234 bash scripts/run_phase2_cloud_a100.sh" in script
    assert "DELETE" in script
    assert "tar -xzf anatomical-neural-fm-pilot.tar.gz" in script


def test_pod_body_requests_a100_network_volume() -> None:
    body = build_pod_body(
        name="pilot",
        volume_id="vol123",
        config=RunpodConfig(
            datacenter="US-MO-1",
            gpu_type="NVIDIA A100 80GB PCIe",
            volume_gb=40,
            container_disk_gb=30,
            max_runtime_seconds=1234,
            image_name="runpod/pytorch:test",
        ),
        api_key="secret",
    )

    assert body["cloudType"] == "SECURE"
    assert body["gpuTypeIds"] == ["NVIDIA A100 80GB PCIe"]
    assert body["networkVolumeId"] == "vol123"
    assert body["dataCenterIds"] == ["US-MO-1"]
    assert body["dockerStartCmd"][0:2] == ["bash", "-lc"]
