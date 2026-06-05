import argparse

from scripts.preflight_parent_slice_runpod import SLICE_PARENTS, slice_config
from scripts.preflight_two_holdout_runpod import build_launch_command, shell_join


def test_parent_slice_preflight_targets_nyu12_fixed_region_include() -> None:
    args = argparse.Namespace(
        max_runtime_seconds=5400,
        max_provision_seconds=7200,
        max_dollars=10.0,
        assumed_cost_per_hr=3.0,
        datacenter="ANY",
        gpu_type="NVIDIA A100 80GB PCIe,NVIDIA A100-SXM4-80GB",
        s3_bucket="rppfvo6ifn",
        s3_datacenter="US-IL-1",
        subject="NYU-12",
        region_include=SLICE_PARENTS,
        name_prefix="anfm-nyu12-parent-slice",
        output_root="runs/lso_nyu12_parent_slice",
        result_doc="docs/lso_nyu12_parent_slice_results.md",
    )

    config = slice_config(args)
    command = build_launch_command(config)
    joined = shell_join(command)

    assert "--output-root runs/lso_nyu12_parent_slice" in joined
    assert "--result-doc docs/lso_nyu12_parent_slice_results.md" in joined
    assert "--name-prefix anfm-nyu12-parent-slice" in joined
    assert "--sweep-env SUBJECTS=NYU-12" in joined
    assert "--sweep-env REGION_FILTER=include_regions" in joined
    assert "--sweep-env REGION_GRANULARITY=parent" in joined
    assert f"--sweep-env REGION_INCLUDE={SLICE_PARENTS}" in joined
    assert "--sweep-env SUBJECTS=NR_0019" not in joined
