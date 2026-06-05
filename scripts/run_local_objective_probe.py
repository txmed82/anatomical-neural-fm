"""Run a tiny no-spend CSH objective probe on local CPU.

The goal is not to produce demo evidence. It is to reject obviously bad
objective variants before any RunPod launch by requiring deterministic
predictions, the strict bidirectional anatomy gate, and the mismatch audit.
"""
from __future__ import annotations

import argparse
import subprocess
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class ProbeConfig:
    root: Path
    holdout: str = "CSH_ZAD_019"
    seed: int = 0
    loss_mode: str = "recording_local_auc_surrogate"
    batch_sampling: str = "recording_target_balanced"
    region_shuffle_control: str = "within_recording_shuffle"
    manifest: Path = REPO_ROOT / "manifests/ibl_bwm_region_matched_support80_best6.json"
    max_steps: int = 5
    eval_batches: int = 1
    dim: int = 16
    depth: int = 1
    num_latents: int = 4
    dim_head: int = 8
    batch_size: int = 2
    force: bool = False


def run_dir(config: ProbeConfig, arm: str) -> Path:
    return config.root / f"holdout_{config.holdout}" / f"cloud_choice_{arm}_seed{config.seed}"


def arm_complete(path: Path) -> bool:
    return (path / "eval_predictions.jsonl").exists()


def train_command(config: ProbeConfig, arm: str) -> list[str]:
    out_dir = run_dir(config, arm)
    command_arm = "region_only" if arm == "region_shuffle" else arm
    command = [
        "uv", "run", "python", "scripts/train.py",
        "--device", "cpu",
        "--manifest", str(config.manifest),
        "--out-dir", str(out_dir),
        "--target-mode", "stimulus_side",
        "--split-mode", "animal",
        "--holdout", config.holdout,
        "--arm", command_arm,
        "--region-filter", "shared_regions",
        "--region-granularity", "parent",
        "--batch-size", str(config.batch_size),
        "--batch-sampling", config.batch_sampling,
        "--loss-mode", config.loss_mode,
        "--max-steps", str(config.max_steps),
        "--eval-every", str(config.max_steps),
        "--eval-batches", str(config.eval_batches),
        "--log-every", str(config.max_steps),
        "--best-metric", "full_eval_centered_auc",
        "--full-eval-on-best",
        "--save-eval-predictions",
        "--save-region-embeddings",
        "--dim", str(config.dim),
        "--depth", str(config.depth),
        "--num-latents", str(config.num_latents),
        "--dim-head", str(config.dim_head),
        "--warmup-steps", str(max(1, min(config.max_steps, 5))),
        "--seed", str(config.seed),
    ]
    if arm == "region_shuffle":
        command.extend(["--region-label-control", config.region_shuffle_control])
    return command


def run_checked(command: list[str], *, cwd: Path = REPO_ROOT, tolerate_gate_fail: bool = False) -> int:
    result = subprocess.run(command, cwd=cwd)
    if result.returncode != 0 and not (tolerate_gate_fail and result.returncode == 2):
        raise subprocess.CalledProcessError(result.returncode, command)
    return result.returncode


def run_probe(config: ProbeConfig) -> dict[str, int]:
    config.root.mkdir(parents=True, exist_ok=True)
    for arm in ("shared_baseline", "region_only", "region_shuffle"):
        out_dir = run_dir(config, arm)
        if config.force and out_dir.exists():
            subprocess.run(["rm", "-rf", str(out_dir)], check=True)
        if arm_complete(out_dir):
            print(f"skip complete: {out_dir}")
            continue
        out_dir.mkdir(parents=True, exist_ok=True)
        print(f"=== local probe arm={arm} loss={config.loss_mode} ===")
        run_checked(train_command(config, arm))

    gate_json = REPO_ROOT / "docs" / f"{config.root.name}_anatomy_specific_gate.json"
    mismatch_json = REPO_ROOT / "docs" / f"{config.root.name}_mismatch.json"
    mismatch_md = REPO_ROOT / "docs" / f"{config.root.name}_mismatch.md"
    failure_json = REPO_ROOT / "docs" / f"{config.root.name}_failure_modes.json"
    failure_md = REPO_ROOT / "docs" / f"{config.root.name}_failure_modes.md"

    run_checked([
        "uv", "run", "python", "scripts/analyze_anatomy_specific_permutation.py",
        str(config.root),
        "--holdout", config.holdout,
        "--out", str(gate_json),
    ], tolerate_gate_fail=True)
    run_checked([
        "uv", "run", "python", "scripts/audit_pairwise_rank_mismatch.py",
        str(config.root),
        "--holdout", config.holdout,
        "--seed", str(config.seed),
        "--out-json", str(mismatch_json),
        "--out-md", str(mismatch_md),
    ])
    run_checked([
        "uv", "run", "python", "scripts/audit_prediction_failure_modes.py",
        str(config.root),
        "--holdout", config.holdout,
        "--out", str(failure_json),
        "--md-out", str(failure_md),
    ])
    return {
        "gate_json": int(gate_json.exists()),
        "mismatch_json": int(mismatch_json.exists()),
        "failure_json": int(failure_json.exists()),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=REPO_ROOT / "runs/local_csh_auc_surrogate_probe")
    parser.add_argument("--holdout", default="CSH_ZAD_019")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--loss-mode", default="recording_local_auc_surrogate")
    parser.add_argument("--batch-sampling", default="recording_target_balanced")
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--max-steps", type=int, default=5)
    parser.add_argument("--eval-batches", type=int, default=1)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = ProbeConfig(
        root=args.root,
        holdout=args.holdout,
        seed=args.seed,
        loss_mode=args.loss_mode,
        batch_sampling=args.batch_sampling,
        batch_size=args.batch_size,
        max_steps=args.max_steps,
        eval_batches=args.eval_batches,
        force=args.force,
    )
    if args.dry_run:
        for arm in ("shared_baseline", "region_only", "region_shuffle"):
            print(" ".join(train_command(config, arm)))
        return 0
    run_probe(config)
    print(f"wrote local objective probe artifacts for {config.root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
