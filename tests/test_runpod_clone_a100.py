from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from dataclasses import replace
from types import SimpleNamespace

import pytest

from scripts.runpod_clone_a100 import (
    ClonePilotConfig,
    authenticated_repo_url,
    build_pod_body,
    build_start_script,
    pod_is_provisioned,
    remote_log_last_modified,
    remote_log_touched,
    s3_log_key,
    summarize_pod,
)


def config() -> ClonePilotConfig:
    return ClonePilotConfig(
        branch="runpod-pilot-phases-3-5",
        repo_url="https://github.com/txmed82/anatomical-neural-fm.git",
        datacenter="US-MO-1",
        compute_type="GPU",
        cpu_flavor="cpu3c,cpu3g,cpu3m",
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
    assert "export MANIFEST=manifests/ibl_bwm_phase4.json" in script
    assert "export OUT_ROOT=runs/phase2_cloud_a100" in script
    assert "- target mode: stimulus_side" in script
    assert "bash scripts/run_phase2_cloud_a100.sh" in script
    assert "=== phase 3-5 body complete ===" in script
    assert "git push origin HEAD:runpod-pilot-phases-3-5" in script
    assert "DELETE" in script


def test_start_script_can_export_sweep_env() -> None:
    cfg = replace(
        config(),
        sweep_env=("SUBJECTS=NR_0019", "REGION_GRANULARITY=parent"),
    )

    script = build_start_script(cfg)

    assert "export SUBJECTS=NR_0019" in script
    assert "export REGION_GRANULARITY=parent" in script
    assert "- sweep env: \\`SUBJECTS=NR_0019, REGION_GRANULARITY=parent\\`" in script


def test_start_script_rejects_invalid_sweep_env() -> None:
    cfg = replace(config(), sweep_env=("BAD-NAME=value",))

    with pytest.raises(ValueError):
        build_start_script(cfg)


def test_pod_body_uses_container_disk_no_network_volume() -> None:
    body = build_pod_body("pilot", config(), "runpod", "github")

    assert "networkVolumeId" not in body
    assert body["volumeInGb"] == 0
    assert body["containerDiskInGb"] == 80
    assert body["dockerEntrypoint"] == ["bash", "-lc"]
    assert len(body["dockerStartCmd"]) == 1
    assert body["gpuTypeIds"] == ["NVIDIA A100 80GB PCIe"]
    assert body["env"]["RUNPOD_API_KEY"] == "runpod"
    assert body["env"]["GITHUB_TOKEN"] == "github"


def test_pod_body_can_use_availability_datacenter_and_gpu_list() -> None:
    cfg = replace(
        config(),
        datacenter="ANY",
        gpu_type="NVIDIA L4,NVIDIA RTX A4000",
    )

    body = build_pod_body("pilot", cfg, "runpod", "github")

    assert "dataCenterIds" not in body
    assert body["dataCenterPriority"] == "availability"
    assert body["gpuTypeIds"] == ["NVIDIA L4", "NVIDIA RTX A4000"]


def test_pod_body_can_use_cpu_flavors() -> None:
    cfg = replace(
        config(),
        compute_type="CPU",
        cpu_flavor="cpu3c,cpu5g",
        container_disk_gb=20,
        volume_gb=80,
    )

    body = build_pod_body("pilot", cfg, "runpod", "github")

    assert body["computeType"] == "CPU"
    assert body["cpuFlavorIds"] == ["cpu3c", "cpu5g"]
    assert body["cpuFlavorPriority"] == "availability"
    assert body["containerDiskInGb"] == 20
    assert body["volumeInGb"] == 80
    assert "gpuTypeIds" not in body
    assert "gpuCount" not in body


def test_summarize_pod_reports_provisioning_state() -> None:
    summary = summarize_pod(
        {
            "id": "pod",
            "name": "pilot",
            "desiredStatus": "RUNNING",
            "costPerHr": 0.06,
            "machineId": "machine",
            "cpuFlavorId": "cpu3c",
            "publicIp": "",
            "volumeInGb": 0,
            "machine": {},
            "lastStatusChange": "Rented by User",
        }
    )

    assert summary["machineReady"] is False
    assert summary["publicIp"] == ""
    assert summary["cpuFlavorId"] == "cpu3c"
    assert summary["volumeInGb"] == 0
    assert summary["lastStatusChange"] == "Rented by User"


def test_pod_is_provisioned_ignores_machine_id_without_runtime_access() -> None:
    assert not pod_is_provisioned({"machineId": "assigned", "machine": {}, "publicIp": ""})
    assert pod_is_provisioned({"machineId": "assigned", "machine": {"id": "machine"}, "publicIp": ""})
    assert pod_is_provisioned({"machineId": "assigned", "machine": {}, "publicIp": "203.0.113.10"})


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
    assert "## Missing Sweep Summary" in script
    assert "Treat this" in script


def test_start_script_marks_missing_sweep_summary_as_incomplete() -> None:
    script = build_start_script(config())

    assert "elif [ -f runs/phase2_cloud_a100/within_summary.md ]" in script
    assert "## Missing Sweep Summary" in script
    assert "Existing result doc already has a summary; preserving it." in script
    assert (
        "No \\`runs/phase2_cloud_a100/summary.md\\`, \\`within_summary.md\\`, or\n"
        "\\`cross_summary.md\\` file was present"
    ) in script


def test_start_script_force_adds_diagnostic_jsonl_artifacts() -> None:
    script = build_start_script(config())

    assert "eval_predictions.jsonl" in script
    assert "region_embeddings.jsonl" in script
    assert "git add -f --" in script


def test_start_script_can_skip_pod_verification() -> None:
    cfg = replace(config(), skip_verification=True)

    script = build_start_script(cfg)

    assert "=== skipping local verification ===" in script
    assert "uv run pytest -q" not in script
    assert "uv run python scripts/00_ibl_smoke_test.py" not in script
    assert "uv run python scripts/build_cell_type_priors.py" in script
    assert "uv sync --no-dev" in script


def test_start_script_can_run_data_build_only() -> None:
    cfg = replace(config(), skip_cell_type_priors=True, skip_sweep=True)

    script = build_start_script(cfg)

    assert "=== skipping cell-type priors ===" in script
    assert "uv run python scripts/build_cell_type_priors.py" not in script
    assert "=== skipping phase 3-5 sweep ===" in script
    assert "=== pushing data-build startup marker ===" not in script
    assert "upload-log --local-path" in script
    assert "bash scripts/run_phase2_cloud_a100.sh" not in script
    assert "- skip cell-type priors: True" in script
    assert "- skip sweep: True" in script
    assert "scripts/build_ibl_brainset_batch.py --manifest manifests/ibl_bwm_phase4.json" in script
    assert "scripts/write_dataset_manifest.py" in script


def test_start_script_can_use_minimal_data_setup() -> None:
    cfg = replace(
        config(),
        skip_cell_type_priors=True,
        skip_sweep=True,
        setup_mode="minimal-data",
        s3_bucket="brainset-cache",
    )

    script = build_start_script(cfg)

    assert "- setup mode: minimal-data" in script
    assert "uv sync" not in script
    assert "python3 -m pip install --user boto3 h5py numpy one-api iblatlas temporaldata" in script
    assert "python3 scripts/sync_brainset_s3.py download" in script
    assert "python3 scripts/build_ibl_brainset_batch.py" in script
    assert "python3 scripts/sync_brainset_s3.py verify-local" in script
    assert "scripts/write_dataset_manifest.py" not in script
    assert "=== skipping dataset manifest (minimal-data setup) ===" in script


def test_start_script_can_run_startup_smoke_only() -> None:
    cfg = replace(
        config(),
        skip_verification=True,
        skip_cell_type_priors=True,
        skip_sweep=True,
        setup_mode="minimal-data",
        s3_bucket="brainset-cache",
        startup_smoke_only=True,
    )

    script = build_start_script(cfg)

    assert "- startup smoke only: True" in script
    assert "=== startup smoke complete ===" in script
    assert "exit 0" in script
    assert "scripts/build_ibl_brainset_batch.py" not in script.split("=== startup smoke complete ===", 1)[0]


def test_start_script_can_run_dependency_diagnostic() -> None:
    cfg = replace(
        config(),
        skip_verification=True,
        skip_cell_type_priors=True,
        s3_bucket="brainset-cache",
        dependency_diagnostic=True,
    )

    script = build_start_script(cfg)

    assert "- dependency diagnostic: True" in script
    assert "=== dependency sync start ===" in script
    assert "=== dependency sync complete ===" in script
    assert "=== dependency diagnostic ===" in script
    assert "cuda_available" in script
    assert "=== dependency diagnostic complete ===" in script
    assert "scripts/build_ibl_brainset_batch.py" not in script.split("=== dependency diagnostic complete ===", 1)[0]
    assert "=== body failed rc=$rc line=$LINENO cmd=$BASH_COMMAND ===" in script


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


def test_start_script_can_sync_brainset_cache() -> None:
    cfg = replace(
        config(),
        s3_bucket="brainset-cache",
        s3_prefix="ibl/test",
        s3_endpoint_url="https://s3.example.test",
    )

    script = build_start_script(cfg)

    assert "=== downloading cached BrainSet data ===" in script
    assert (
        "scripts/sync_brainset_s3.py download --manifest manifests/ibl_bwm_phase4.json "
        "--bucket brainset-cache --prefix ibl/test --endpoint-url https://s3.example.test"
    ) in script
    assert "=== uploading built BrainSet data ===" in script
    assert (
        "scripts/sync_brainset_s3.py upload --manifest manifests/ibl_bwm_phase4.json "
        "--bucket brainset-cache --prefix ibl/test --endpoint-url https://s3.example.test --skip-existing"
    ) in script
    assert "=== verifying BrainSet cache upload ===" in script
    assert (
        "scripts/sync_brainset_s3.py verify-local --manifest manifests/ibl_bwm_phase4.json "
        "--bucket brainset-cache --prefix ibl/test --endpoint-url https://s3.example.test "
        "--report runs/phase2_cloud_a100/cache_audit.md"
    ) in script
    assert "## Cache Audit" in script


def test_start_script_can_run_incremental_cache_build() -> None:
    cfg = replace(
        config(),
        setup_mode="minimal-data",
        skip_verification=True,
        skip_cell_type_priors=True,
        skip_sweep=True,
        build_mode="incremental",
        manifest_path="manifests/ibl_bwm_region_matched_candidates_missing_s3.json",
        s3_bucket="brainset-cache",
        s3_prefix="ibl/test",
        s3_datacenter="US-IL-1",
        output_root="runs/matched_region_missing_incremental",
        build_extra_args="--no-wheel --trial-window-only --window-len 1.0 --clear-one-cache",
    )

    script = build_start_script(cfg)

    assert "- build mode: incremental" in script
    assert "scripts/build_ibl_brainset_incremental.py" in script
    assert "--manifest manifests/ibl_bwm_region_matched_candidates_missing_s3.json" in script
    assert "--bucket brainset-cache --prefix ibl/test --datacenter US-IL-1" in script
    assert "--no-wheel --trial-window-only --window-len 1.0 --clear-one-cache" in script
    assert "scripts/build_ibl_brainset_batch.py" not in script
    assert "=== auditing BrainSet cache upload ===" in script
    assert "scripts/sync_brainset_s3.py audit --manifest manifests/ibl_bwm_region_matched_candidates_missing_s3.json" in script
    assert "verify-local --manifest manifests/ibl_bwm_region_matched_candidates_missing_s3.json" not in script
    assert "## Incremental Build Summary" in script


def test_s3_log_key_matches_uploaded_result_log() -> None:
    cfg = replace(
        config(),
        s3_prefix="brainsets/ibl_bwm",
        result_doc="docs/runpod_dependency_diagnostic.md",
    )

    assert s3_log_key(cfg) == "brainsets/ibl_bwm/logs/docs_runpod_dependency_diagnostic.log"


def test_remote_log_touched_uses_s3_last_modified(monkeypatch) -> None:
    seen = {}
    last_modified = datetime(2026, 6, 5, 1, 44, tzinfo=timezone.utc)

    class FakeS3:
        def head_object(self, *, Bucket: str, Key: str) -> dict:
            seen["bucket"] = Bucket
            seen["key"] = Key
            return {"LastModified": last_modified}

    monkeypatch.setitem(sys.modules, "boto3", SimpleNamespace(client=lambda *args, **kwargs: FakeS3()))
    cfg = replace(
        config(),
        s3_bucket="brainset-cache",
        s3_prefix="ibl/test",
        s3_endpoint_url="https://s3.example.test",
    )
    env = {"BRAINSET_S3_ACCESS_KEY": "access", "BRAINSET_S3_SECRET_KEY": "secret"}

    assert remote_log_touched(cfg, env, modified_after=last_modified - timedelta(seconds=1))
    assert not remote_log_touched(cfg, env, modified_after=last_modified + timedelta(seconds=1))
    assert not remote_log_touched(cfg, env, modified_after=last_modified)
    assert seen == {"bucket": "brainset-cache", "key": "ibl/test/logs/docs_cloud_phase3_5_results.log"}


def test_remote_log_last_modified_returns_fresh_timestamp(monkeypatch) -> None:
    last_modified = datetime(2026, 6, 5, 1, 44, tzinfo=timezone.utc)

    class FakeS3:
        def head_object(self, *, Bucket: str, Key: str) -> dict:
            return {"LastModified": last_modified}

    monkeypatch.setitem(sys.modules, "boto3", SimpleNamespace(client=lambda *args, **kwargs: FakeS3()))
    cfg = replace(config(), s3_bucket="brainset-cache", s3_datacenter="US-IL-1")
    env = {"BRAINSET_S3_ACCESS_KEY": "access", "BRAINSET_S3_SECRET_KEY": "secret"}

    assert remote_log_last_modified(cfg, env, modified_after=last_modified - timedelta(seconds=1)) == last_modified
    assert remote_log_last_modified(cfg, env, modified_after=last_modified) is None


def test_pod_body_passes_s3_credentials_when_cache_enabled(monkeypatch) -> None:
    monkeypatch.setenv("BRAINSET_S3_ACCESS_KEY", "access")
    monkeypatch.setenv("BRAINSET_S3_SECRET_KEY", "secret")
    cfg = replace(config(), s3_bucket="brainset-cache")

    body = build_pod_body("pilot", cfg, "runpod", "github")

    assert body["env"]["BRAINSET_S3_ACCESS_KEY"] == "access"
    assert body["env"]["BRAINSET_S3_SECRET_KEY"] == "secret"
