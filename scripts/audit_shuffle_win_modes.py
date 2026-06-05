"""Audit why shuffled anatomical labels beat true labels in LSO prediction runs."""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

try:
    from analyze_lso_prediction_ensemble import (
        ARMS,
        available_seeds,
        complete_seeds,
        full_auc,
        paired_improvement,
        prediction_key,
        read_prediction_rows,
        recording_centered_auc,
    )
except ModuleNotFoundError:
    from scripts.analyze_lso_prediction_ensemble import (
        ARMS,
        available_seeds,
        complete_seeds,
        full_auc,
        paired_improvement,
        prediction_key,
        read_prediction_rows,
        recording_centered_auc,
    )


def true_class_probability(row: dict) -> float:
    prob = float(row["prob"])
    return prob if int(row["target"]) == 1 else 1.0 - prob


def mean_target_separation(rows: list[dict]) -> float:
    target0 = [float(row["prob"]) for row in rows if int(row["target"]) == 0]
    target1 = [float(row["prob"]) for row in rows if int(row["target"]) == 1]
    if not target0 or not target1:
        return float("nan")
    return float(np.mean(target1) - np.mean(target0))


def centered_target_separation(rows: list[dict]) -> float:
    centered_rows = []
    by_recording: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_recording[str(row["recording_id"])].append(row)
    for recording_rows in by_recording.values():
        mean_prob = float(np.mean([float(row["prob"]) for row in recording_rows]))
        for row in recording_rows:
            centered = dict(row)
            centered["prob"] = float(row["prob"]) - mean_prob
            centered_rows.append(centered)
    return mean_target_separation(centered_rows)


def probability_std(rows: list[dict]) -> float:
    if not rows:
        return float("nan")
    return float(np.std([float(row["prob"]) for row in rows]))


def recording_summary(rows_by_arm: dict[str, list[dict]]) -> dict[str, dict]:
    recording_ids = sorted({
        str(row["recording_id"])
        for rows in rows_by_arm.values()
        for row in rows
    })
    out = {}
    for recording_id in recording_ids:
        arm_rows = {
            arm: [row for row in rows if str(row["recording_id"]) == recording_id]
            for arm, rows in rows_by_arm.items()
        }
        if not all(arm_rows.get(arm) for arm in ARMS):
            continue
        true_rows = arm_rows["region_only"]
        shuffle_rows = arm_rows["region_shuffle"]
        shared_rows = arm_rows["shared_baseline"]
        out[recording_id] = {
            "n": len(true_rows),
            "full_auc": {arm: full_auc(rows) for arm, rows in arm_rows.items()},
            "target_separation": {
                arm: mean_target_separation(rows) for arm, rows in arm_rows.items()
            },
            "centered_target_separation": {
                arm: centered_target_separation(rows) for arm, rows in arm_rows.items()
            },
            "prob_std": {arm: probability_std(rows) for arm, rows in arm_rows.items()},
            "true_minus_shuffle_centered_sep": (
                centered_target_separation(true_rows) - centered_target_separation(shuffle_rows)
            ),
            "true_minus_shared_centered_sep": (
                centered_target_separation(true_rows) - centered_target_separation(shared_rows)
            ),
            "paired_true_vs_shuffle": paired_improvement(true_rows, shuffle_rows)["improved_fraction"],
        }
    return out


def seed_summary(root: Path, holdout: str, seed: int) -> dict:
    rows_by_arm = {arm: read_prediction_rows(root, holdout, arm, seed) for arm in ARMS}
    metrics = {
        arm: {
            "full_auc": full_auc(rows),
            "centered_auc": recording_centered_auc(rows),
            "target_separation": mean_target_separation(rows),
            "centered_target_separation": centered_target_separation(rows),
            "prob_std": probability_std(rows),
        }
        for arm, rows in rows_by_arm.items()
    }
    paired = {
        "region_only_vs_shuffle": paired_improvement(
            rows_by_arm["region_only"],
            rows_by_arm["region_shuffle"],
        ),
        "region_shuffle_vs_shared": paired_improvement(
            rows_by_arm["region_shuffle"],
            rows_by_arm["shared_baseline"],
        ),
        "region_only_vs_shared": paired_improvement(
            rows_by_arm["region_only"],
            rows_by_arm["shared_baseline"],
        ),
    }
    return {
        "seed": seed,
        "metrics": metrics,
        "deltas": {
            "true_minus_shuffle_centered_auc": (
                metrics["region_only"]["centered_auc"] - metrics["region_shuffle"]["centered_auc"]
            ),
            "true_minus_shuffle_full_auc": (
                metrics["region_only"]["full_auc"] - metrics["region_shuffle"]["full_auc"]
            ),
            "true_minus_shuffle_centered_target_separation": (
                metrics["region_only"]["centered_target_separation"]
                - metrics["region_shuffle"]["centered_target_separation"]
            ),
            "shuffle_minus_shared_centered_target_separation": (
                metrics["region_shuffle"]["centered_target_separation"]
                - metrics["shared_baseline"]["centered_target_separation"]
            ),
        },
        "paired": paired,
        "recordings": recording_summary(rows_by_arm),
    }


def ensemble_rows(rows_by_seed: dict[int, list[dict]]) -> list[dict]:
    grouped: dict[tuple[str, float, int], list[dict]] = defaultdict(list)
    for rows in rows_by_seed.values():
        for row in rows:
            grouped[prediction_key(row)].append(row)
    n_seeds = len(rows_by_seed)
    out = []
    for key, rows in grouped.items():
        if len(rows) != n_seeds:
            continue
        out.append({
            "recording_id": key[0],
            "t0": key[1],
            "target": key[2],
            "prob": float(np.mean([float(row["prob"]) for row in rows])),
        })
    return sorted(out, key=prediction_key)


def run_summary(root: Path, holdout: str, label: str | None = None) -> dict:
    seeds = complete_seeds(root, holdout)
    if not seeds:
        raise ValueError(f"No complete seeds found for {root}")
    seed_rows = [seed_summary(root, holdout, seed) for seed in seeds]
    ensemble_by_arm = {
        arm: ensemble_rows({
            seed: read_prediction_rows(root, holdout, arm, seed)
            for seed in seeds
        })
        for arm in ARMS
    }
    ensemble = seed_summary_from_rows(ensemble_by_arm)
    return {
        "label": label or root.name,
        "root": str(root),
        "holdout": holdout,
        "available_seeds": available_seeds(root, holdout),
        "complete_seeds": seeds,
        "incomplete_seeds": [
            seed for seed in available_seeds(root, holdout) if seed not in seeds
        ],
        "seed_summaries": seed_rows,
        "ensemble": ensemble,
        "interpretation": interpret(ensemble),
    }


def seed_summary_from_rows(rows_by_arm: dict[str, list[dict]]) -> dict:
    metrics = {
        arm: {
            "full_auc": full_auc(rows),
            "centered_auc": recording_centered_auc(rows),
            "target_separation": mean_target_separation(rows),
            "centered_target_separation": centered_target_separation(rows),
            "prob_std": probability_std(rows),
        }
        for arm, rows in rows_by_arm.items()
    }
    return {
        "metrics": metrics,
        "deltas": {
            "true_minus_shuffle_centered_auc": (
                metrics["region_only"]["centered_auc"] - metrics["region_shuffle"]["centered_auc"]
            ),
            "true_minus_shuffle_full_auc": (
                metrics["region_only"]["full_auc"] - metrics["region_shuffle"]["full_auc"]
            ),
            "true_minus_shuffle_centered_target_separation": (
                metrics["region_only"]["centered_target_separation"]
                - metrics["region_shuffle"]["centered_target_separation"]
            ),
            "shuffle_minus_shared_centered_target_separation": (
                metrics["region_shuffle"]["centered_target_separation"]
                - metrics["shared_baseline"]["centered_target_separation"]
            ),
        },
        "paired": {
            "region_only_vs_shuffle": paired_improvement(
                rows_by_arm["region_only"],
                rows_by_arm["region_shuffle"],
            ),
            "region_shuffle_vs_shared": paired_improvement(
                rows_by_arm["region_shuffle"],
                rows_by_arm["shared_baseline"],
            ),
            "region_only_vs_shared": paired_improvement(
                rows_by_arm["region_only"],
                rows_by_arm["shared_baseline"],
            ),
        },
        "recordings": recording_summary(rows_by_arm),
    }


def interpret(summary: dict) -> dict:
    deltas = summary["deltas"]
    paired = summary["paired"]
    shuffle_wins_centered = deltas["true_minus_shuffle_centered_auc"] < 0
    shuffle_has_larger_centered_sep = (
        deltas["true_minus_shuffle_centered_target_separation"] < 0
    )
    return {
        "shuffle_wins_centered_auc": shuffle_wins_centered,
        "shuffle_has_larger_centered_target_separation": shuffle_has_larger_centered_sep,
        "true_prob_improvement_fraction": paired["region_only_vs_shuffle"]["improved_fraction"],
        "shuffle_vs_shared_improvement_fraction": paired["region_shuffle_vs_shared"]["improved_fraction"],
        "diagnosis": (
            "shuffle_labels_create_stronger_within_recording_target_separation"
            if shuffle_wins_centered and shuffle_has_larger_centered_sep
            else "true_labels_not_outperformed_by_shuffle_on_centered_separation"
        ),
    }


def write_markdown(result: dict, path: Path) -> None:
    lines = ["# Shuffle Win Mode Audit", ""]
    for run in result["runs"]:
        ensemble = run["ensemble"]
        metrics = ensemble["metrics"]
        deltas = ensemble["deltas"]
        lines.extend([
            f"## {run['label']}",
            "",
            f"- complete seeds: `{run['complete_seeds']}`",
            f"- incomplete seeds: `{run['incomplete_seeds']}`",
            f"- diagnosis: `{run['interpretation']['diagnosis']}`",
            f"- region_only centered AUC: `{metrics['region_only']['centered_auc']:.3f}`",
            f"- region_shuffle centered AUC: `{metrics['region_shuffle']['centered_auc']:.3f}`",
            f"- true-minus-shuffle centered AUC: `{deltas['true_minus_shuffle_centered_auc']:+.3f}`",
            f"- true-minus-shuffle centered target separation: `{deltas['true_minus_shuffle_centered_target_separation']:+.3f}`",
            f"- paired true-vs-shuffle: `{ensemble['paired']['region_only_vs_shuffle']['improved_fraction']:.3f}`",
            "",
            "| recording | true centered sep | shuffle centered sep | true-shuffle centered sep | paired true-vs-shuffle |",
            "|---|---:|---:|---:|---:|",
        ])
        for recording_id, row in ensemble["recordings"].items():
            true_sep = row["centered_target_separation"]["region_only"]
            shuffle_sep = row["centered_target_separation"]["region_shuffle"]
            lines.append(
                f"| {recording_id} | {true_sep:.3f} | {shuffle_sep:.3f} | "
                f"{row['true_minus_shuffle_centered_sep']:+.3f} | "
                f"{row['paired_true_vs_shuffle']:.3f} |"
            )
        lines.append("")
    path.write_text("\n".join(lines) + "\n")


def parse_root_arg(value: str) -> tuple[str | None, Path]:
    if "=" not in value:
        return None, Path(value)
    label, root = value.split("=", 1)
    return label, Path(root)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("roots", nargs="+", help="Result roots, optionally label=path.")
    parser.add_argument("--holdout", default="CSH_ZAD_019")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--md-out", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    runs = []
    for value in args.roots:
        label, root = parse_root_arg(value)
        runs.append(run_summary(root, args.holdout, label))
    result = {"holdout": args.holdout, "runs": runs}
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text)
        print(f"wrote {args.out}")
    else:
        print(text, end="")
    if args.md_out:
        args.md_out.parent.mkdir(parents=True, exist_ok=True)
        write_markdown(result, args.md_out)
        print(f"wrote {args.md_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
