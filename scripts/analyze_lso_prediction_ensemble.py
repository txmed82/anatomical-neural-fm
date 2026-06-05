"""Diagnose seed-ensemble and per-recording behavior for LSO prediction files."""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Iterable

import numpy as np


ARMS = ("shared_baseline", "region_only", "region_shuffle")


def auc(scores: Iterable[float], labels: Iterable[int]) -> float:
    scores_arr = np.asarray(list(scores), dtype=np.float64)
    labels_arr = np.asarray(list(labels), dtype=np.int64)
    pos = scores_arr[labels_arr == 1]
    neg = scores_arr[labels_arr == 0]
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    wins = (pos[:, None] > neg[None, :]).sum()
    ties = (pos[:, None] == neg[None, :]).sum()
    return float((wins + 0.5 * ties) / (len(pos) * len(neg)))


def read_prediction_rows(root: Path, holdout: str, arm: str, seed: int) -> list[dict]:
    path = root / f"holdout_{holdout}" / f"cloud_choice_{arm}_seed{seed}" / "eval_predictions.jsonl"
    with path.open() as fh:
        return [json.loads(line) for line in fh]


def available_seeds(root: Path, holdout: str) -> list[int]:
    holdout_dir = root / f"holdout_{holdout}"
    seeds: set[int] = set()
    for arm in ARMS:
        prefix = f"cloud_choice_{arm}_seed"
        for run_dir in holdout_dir.glob(f"{prefix}*"):
            if run_dir.is_dir():
                seeds.add(int(run_dir.name.removeprefix(prefix)))
    return sorted(seeds)


def prediction_key(row: dict) -> tuple[str, float, int]:
    return (str(row["recording_id"]), round(float(row["t0"]), 6), int(row["target"]))


def full_auc(rows: list[dict]) -> float:
    return auc((float(row["prob"]) for row in rows), (int(row["target"]) for row in rows))


def recording_centered_auc(rows: list[dict]) -> float:
    by_recording: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_recording[str(row["recording_id"])].append(row)
    scores: list[float] = []
    labels: list[int] = []
    for recording_rows in by_recording.values():
        probs = np.asarray([float(row["prob"]) for row in recording_rows], dtype=np.float64)
        centered = probs - float(np.mean(probs))
        scores.extend(float(score) for score in centered)
        labels.extend(int(row["target"]) for row in recording_rows)
    return auc(scores, labels)


def true_class_probability(row: dict) -> float:
    prob = float(row["prob"])
    return prob if int(row["target"]) == 1 else 1.0 - prob


def ensemble_rows(rows_by_seed: dict[int, list[dict]]) -> list[dict]:
    grouped: dict[tuple[str, float, int], list[dict]] = defaultdict(list)
    for rows in rows_by_seed.values():
        for row in rows:
            grouped[prediction_key(row)].append(row)
    rows = []
    n_seeds = len(rows_by_seed)
    for key, group in grouped.items():
        if len(group) != n_seeds:
            continue
        rows.append(
            {
                "recording_id": key[0],
                "t0": key[1],
                "target": key[2],
                "prob": float(np.mean([float(row["prob"]) for row in group])),
            }
        )
    return sorted(rows, key=prediction_key)


def paired_improvement(left_rows: list[dict], right_rows: list[dict]) -> dict:
    left = {prediction_key(row): row for row in left_rows}
    right = {prediction_key(row): row for row in right_rows}
    keys = sorted(set(left) & set(right))
    improved = []
    deltas = []
    by_recording: dict[str, list[bool]] = defaultdict(list)
    for key in keys:
        left_true = true_class_probability(left[key])
        right_true = true_class_probability(right[key])
        is_improved = left_true > right_true
        improved.append(is_improved)
        deltas.append(left_true - right_true)
        by_recording[key[0]].append(is_improved)
    return {
        "n": len(keys),
        "improved_fraction": float(np.mean(improved)) if improved else float("nan"),
        "mean_true_prob_delta": float(np.mean(deltas)) if deltas else float("nan"),
        "recordings": {
            recording_id: {
                "n": len(values),
                "improved_fraction": float(np.mean(values)),
            }
            for recording_id, values in sorted(by_recording.items())
        },
    }


def per_recording_auc(rows: list[dict]) -> dict[str, dict]:
    by_recording: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_recording[str(row["recording_id"])].append(row)
    return {
        recording_id: {
            "n": len(recording_rows),
            "auc": full_auc(recording_rows),
        }
        for recording_id, recording_rows in sorted(by_recording.items())
    }


def analyze(root: Path, holdout: str, seeds: list[int] | None = None) -> dict:
    selected_seeds = seeds if seeds is not None else available_seeds(root, holdout)
    rows = {
        arm: {seed: read_prediction_rows(root, holdout, arm, seed) for seed in selected_seeds}
        for arm in ARMS
    }
    ensembles = {arm: ensemble_rows(rows[arm]) for arm in ARMS}
    seed_metrics = {}
    for seed in selected_seeds:
        seed_metrics[str(seed)] = {
            arm: {
                "full_auc": full_auc(rows[arm][seed]),
                "centered_auc": recording_centered_auc(rows[arm][seed]),
            }
            for arm in ARMS
        }
        seed_metrics[str(seed)]["paired_region_only_vs_shuffle"] = paired_improvement(
            rows["region_only"][seed],
            rows["region_shuffle"][seed],
        )
    return {
        "root": str(root),
        "holdout": holdout,
        "seeds": selected_seeds,
        "seed_metrics": seed_metrics,
        "ensemble_metrics": {
            arm: {
                "n": len(ensembles[arm]),
                "full_auc": full_auc(ensembles[arm]),
                "centered_auc": recording_centered_auc(ensembles[arm]),
                "recording_auc": per_recording_auc(ensembles[arm]),
            }
            for arm in ARMS
        },
        "ensemble_paired": {
            "region_only_vs_shuffle": paired_improvement(
                ensembles["region_only"],
                ensembles["region_shuffle"],
            ),
            "region_only_vs_shared": paired_improvement(
                ensembles["region_only"],
                ensembles["shared_baseline"],
            ),
            "shuffle_vs_shared": paired_improvement(
                ensembles["region_shuffle"],
                ensembles["shared_baseline"],
            ),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--holdout", default="CSH_ZAD_019")
    parser.add_argument("--seeds", nargs="*", type=int)
    parser.add_argument("--out", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = analyze(args.root, args.holdout, args.seeds)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text)
        print(f"wrote {args.out}")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
