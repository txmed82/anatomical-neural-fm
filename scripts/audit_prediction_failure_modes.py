"""Audit prediction-level failure modes for an LSO anatomy run.

This is an analysis-only diagnostic. It joins saved prediction exports with the
manifest/HDF5 unit metadata to quantify whether the apparent anatomy signal is
dominated by recording offsets, class-balance effects, or unsupported held-out
regions.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

import h5py
import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from analyze_lso_prediction_ensemble import (  # noqa: E402
    ARMS,
    complete_seeds,
    full_auc,
    paired_improvement,
    read_prediction_rows,
    recording_centered_auc,
)
from train import map_region_acronyms  # noqa: E402


def display_path(path: Path) -> str:
    path = path.expanduser()
    if not path.is_absolute():
        return str(path)
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def recording_id_from_manifest_row(row: dict) -> str:
    eid = row.get("session_id") or row.get("eid") or row.get("session")
    probe = row.get("probe_name") or row.get("probe") or row.get("name")
    if not eid or not probe:
        raise ValueError(f"manifest row lacks session/probe keys: {row}")
    return f"{eid}_{probe}"


def read_manifest_rows(path: Path) -> dict[str, dict]:
    payload = json.loads(path.read_text())
    rows = payload["recordings"] if isinstance(payload, dict) else payload
    return {recording_id_from_manifest_row(row): row for row in rows}


def decode_h5_strings(values) -> list[str]:
    out = []
    for value in values:
        if isinstance(value, bytes):
            out.append(value.decode("utf-8"))
        else:
            out.append(str(value))
    return out


def recording_region_counts(path: Path, granularity: str) -> Counter[str]:
    with h5py.File(path, "r") as h5:
        fine_regions = decode_h5_strings(h5["units/region_acronym"][:])
    return Counter(map_region_acronyms(fine_regions, granularity))


def region_support_summary(
    *,
    manifest_rows: dict[str, dict],
    data_dir: Path,
    holdout: str,
    granularity: str,
) -> dict[str, dict]:
    counts_by_recording: dict[str, Counter[str]] = {}
    subjects_by_recording: dict[str, str] = {}
    for recording_id, row in manifest_rows.items():
        path = data_dir / f"{recording_id}.h5"
        if not path.exists():
            continue
        subject = str(row.get("subject_id") or row.get("subject") or "")
        subjects_by_recording[recording_id] = subject
        counts_by_recording[recording_id] = recording_region_counts(path, granularity)

    train_counts = Counter()
    for recording_id, counts in counts_by_recording.items():
        if subjects_by_recording.get(recording_id) != holdout:
            train_counts.update(counts)

    out = {}
    for recording_id, counts in sorted(counts_by_recording.items()):
        if subjects_by_recording.get(recording_id) != holdout:
            continue
        total = sum(counts.values())
        supported = sum(count for region, count in counts.items() if train_counts[region] > 0)
        top = counts.most_common(8)
        out[recording_id] = {
            "n_units": int(total),
            "n_regions": len(counts),
            "unit_support_fraction": float(supported / total) if total else float("nan"),
            "top_regions": [
                {
                    "region": region,
                    "units": int(count),
                    "train_units": int(train_counts[region]),
                    "supported": bool(train_counts[region] > 0),
                }
                for region, count in top
            ],
            "missing_top_regions": [
                region for region, _count in top if train_counts[region] == 0
            ],
        }
    return out


def rows_by_recording(rows: Iterable[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[str(row["recording_id"])].append(row)
    return dict(grouped)


def target_fraction(rows: list[dict]) -> float:
    if not rows:
        return float("nan")
    return float(np.mean([int(row["target"]) for row in rows]))


def mean_prob(rows: list[dict]) -> float:
    if not rows:
        return float("nan")
    return float(np.mean([float(row["prob"]) for row in rows]))


def probability_std(rows: list[dict]) -> float:
    if not rows:
        return float("nan")
    return float(np.std([float(row["prob"]) for row in rows]))


def finite_corr(xs: list[float], ys: list[float]) -> float:
    pairs = [(x, y) for x, y in zip(xs, ys) if math.isfinite(x) and math.isfinite(y)]
    if len(pairs) < 2:
        return float("nan")
    x = np.asarray([p[0] for p in pairs], dtype=np.float64)
    y = np.asarray([p[1] for p in pairs], dtype=np.float64)
    if float(np.std(x)) == 0.0 or float(np.std(y)) == 0.0:
        return float("nan")
    return float(np.corrcoef(x, y)[0, 1])


def seed_prediction_summary(rows_by_arm: dict[str, list[dict]]) -> dict:
    metrics = {}
    for arm, rows in rows_by_arm.items():
        full = full_auc(rows)
        centered = recording_centered_auc(rows)
        metrics[arm] = {
            "n": len(rows),
            "full_auc": full,
            "recording_centered_auc": centered,
            "offset_auc_delta": full - centered,
            "mean_prob": mean_prob(rows),
            "prob_std": probability_std(rows),
        }

    recording_ids = sorted({
        str(row["recording_id"])
        for rows in rows_by_arm.values()
        for row in rows
    })
    recording_rows = {}
    for recording_id in recording_ids:
        arm_rows = {
            arm: rows_by_recording(rows).get(recording_id, [])
            for arm, rows in rows_by_arm.items()
        }
        if not all(arm_rows.get(arm) for arm in ARMS):
            continue
        shared = arm_rows["shared_baseline"]
        true_rows = arm_rows["region_only"]
        shuffle = arm_rows["region_shuffle"]
        recording_rows[recording_id] = {
            "n": len(shared),
            "target1_fraction": target_fraction(shared),
            "target_imbalance": abs(target_fraction(shared) - 0.5),
            "arm_auc": {arm: full_auc(rows) for arm, rows in arm_rows.items()},
            "arm_mean_prob": {arm: mean_prob(rows) for arm, rows in arm_rows.items()},
            "arm_prob_std": {arm: probability_std(rows) for arm, rows in arm_rows.items()},
            "region_only_mean_prob_delta_vs_shared": mean_prob(true_rows) - mean_prob(shared),
            "region_shuffle_mean_prob_delta_vs_shared": mean_prob(shuffle) - mean_prob(shared),
            "region_only_minus_shuffle_auc": full_auc(true_rows) - full_auc(shuffle),
            "paired_region_only_vs_shuffle": paired_improvement(true_rows, shuffle)["improved_fraction"],
        }

    target_fracs = [
        row["target1_fraction"]
        for _recording_id, row in sorted(recording_rows.items())
    ]
    offset_correlations = {}
    for arm in ARMS:
        means = [
            recording_rows[recording_id]["arm_mean_prob"][arm]
            for recording_id in sorted(recording_rows)
        ]
        offset_correlations[f"{arm}_mean_prob_vs_target1_fraction"] = finite_corr(
            means, target_fracs
        )

    return {
        "metrics": metrics,
        "recordings": recording_rows,
        "offset_correlations": offset_correlations,
        "paired": {
            "region_only_vs_shuffle": paired_improvement(
                rows_by_arm["region_only"], rows_by_arm["region_shuffle"]
            ),
            "region_only_vs_shared": paired_improvement(
                rows_by_arm["region_only"], rows_by_arm["shared_baseline"]
            ),
            "region_shuffle_vs_shared": paired_improvement(
                rows_by_arm["region_shuffle"], rows_by_arm["shared_baseline"]
            ),
        },
    }


def analyze(
    *,
    root: Path,
    holdout: str,
    manifest: Path,
    data_dir: Path,
    region_granularity: str,
    seeds: list[int] | None = None,
) -> dict:
    selected_seeds = seeds if seeds is not None else complete_seeds(root, holdout)
    if not selected_seeds:
        raise ValueError(f"No complete seeds found for {holdout!r} under {root}")
    seed_summaries = {}
    for seed in selected_seeds:
        rows_by_arm = {
            arm: read_prediction_rows(root, holdout, arm, seed)
            for arm in ARMS
        }
        seed_summaries[str(seed)] = seed_prediction_summary(rows_by_arm)

    return {
        "root": str(root),
        "holdout": holdout,
        "seeds": selected_seeds,
        "manifest": str(manifest),
        "data_dir": str(data_dir),
        "region_granularity": region_granularity,
        "seed_summaries": seed_summaries,
        "region_support": region_support_summary(
            manifest_rows=read_manifest_rows(manifest),
            data_dir=data_dir,
            holdout=holdout,
            granularity=region_granularity,
        ),
    }


def fmt_float(value: float, digits: int = 3) -> str:
    if not math.isfinite(value):
        return "n/a"
    return f"{value:.{digits}f}"


def fmt_signed(value: float, digits: int = 3) -> str:
    if not math.isfinite(value):
        return "n/a"
    return f"{value:+.{digits}f}"


def write_markdown(result: dict, out_path: Path) -> None:
    seed = str(result["seeds"][0])
    summary = result["seed_summaries"][seed]
    metrics = summary["metrics"]
    lines = [
        "# Prediction Failure-Mode Audit",
        "",
        f"Root: `{display_path(Path(result['root']))}`",
        f"Holdout: `{result['holdout']}`",
        f"Region granularity: `{result['region_granularity']}`",
        "",
        "## Offset Contribution",
        "",
        "| arm | full_AUC | recording_centered_AUC | full_minus_centered | mean_prob | prob_std |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for arm in ARMS:
        row = metrics[arm]
        lines.append(
            "| "
            f"{arm} | {fmt_float(row['full_auc'])} | "
            f"{fmt_float(row['recording_centered_auc'])} | "
            f"{fmt_signed(row['offset_auc_delta'])} | "
            f"{fmt_float(row['mean_prob'])} | {fmt_float(row['prob_std'])} |"
        )

    lines += [
        "",
        "## Per-Recording Prediction Behavior",
        "",
        "| recording | n | target1_frac | imbalance | true_auc | shuffle_auc | true-shuffle_auc | true_mean_delta_vs_shared | shuffle_mean_delta_vs_shared | true_vs_shuffle_paired | parent_support | missing_top_parent_regions |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    support = result["region_support"]
    for recording_id, row in summary["recordings"].items():
        support_row = support.get(recording_id, {})
        missing = support_row.get("missing_top_regions", [])
        lines.append(
            "| "
            f"`{recording_id}` | {row['n']} | "
            f"{fmt_float(row['target1_fraction'])} | "
            f"{fmt_float(row['target_imbalance'])} | "
            f"{fmt_float(row['arm_auc']['region_only'])} | "
            f"{fmt_float(row['arm_auc']['region_shuffle'])} | "
            f"{fmt_signed(row['region_only_minus_shuffle_auc'])} | "
            f"{fmt_signed(row['region_only_mean_prob_delta_vs_shared'])} | "
            f"{fmt_signed(row['region_shuffle_mean_prob_delta_vs_shared'])} | "
            f"{fmt_float(row['paired_region_only_vs_shuffle'])} | "
            f"{fmt_float(float(support_row.get('unit_support_fraction', float('nan'))))} | "
            f"{', '.join(missing) if missing else 'none'} |"
        )

    lines += [
        "",
        "## Recording Offset Correlations",
        "",
        "| measure | correlation |",
        "|---|---:|",
    ]
    for name, value in summary["offset_correlations"].items():
        lines.append(f"| `{name}` | {fmt_float(value)} |")

    paired = summary["paired"]
    lines += [
        "",
        "## Paired Trial Checks",
        "",
        "| comparison | n | improved_fraction | mean_true_prob_delta |",
        "|---|---:|---:|---:|",
    ]
    for name, row in paired.items():
        lines.append(
            "| "
            f"`{name}` | {row['n']} | "
            f"{fmt_float(row['improved_fraction'])} | "
            f"{fmt_signed(row['mean_true_prob_delta'])} |"
        )

    true_offset = metrics["region_only"]["offset_auc_delta"]
    shuffle_offset = metrics["region_shuffle"]["offset_auc_delta"]
    true_vs_shuffle = paired["region_only_vs_shuffle"]["improved_fraction"]
    min_support = min(
        row.get("unit_support_fraction", float("nan"))
        for row in support.values()
    ) if support else float("nan")
    lines += [
        "",
        "## Interpretation",
        "",
        (
            "The current failure is not explained by missing held-out parent-region "
            f"coverage alone: the minimum held-out recording support is {fmt_float(min_support)}."
        ),
        "",
        (
            "The stronger signal is calibration/offset behavior. `region_shuffle` gains "
            f"{fmt_signed(shuffle_offset)} AUC from recording-level offsets, while "
            f"`region_only` gets {fmt_signed(true_offset)}. After removing those offsets, "
            "the true-label advantage is too small to support a demo claim."
        ),
        "",
        (
            f"The paired true-vs-shuffle fraction is {fmt_float(true_vs_shuffle)}, so true "
            "anatomical labels are not moving trial probabilities toward the correct class "
            "more reliably than the recording-matched shuffled control."
        ),
        "",
        (
            "Next experiment design should therefore make recording-matched negatives and "
            "recording-centered evaluation primary, and should avoid selecting on raw AUC."
        ),
        "",
    ]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--holdout", default="CSH_ZAD_019")
    parser.add_argument("--manifest", type=Path, default=REPO_ROOT / "manifests/ibl_bwm_region_matched_support80_best6.json")
    parser.add_argument("--data-dir", type=Path, default=REPO_ROOT / "data/brainsets/ibl_bwm")
    parser.add_argument("--region-granularity", choices=["fine", "parent", "grandparent"], default="parent")
    parser.add_argument("--seeds", nargs="*", type=int)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--md-out", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = analyze(
        root=args.root,
        holdout=args.holdout,
        manifest=args.manifest,
        data_dir=args.data_dir,
        region_granularity=args.region_granularity,
        seeds=args.seeds,
    )
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        print(f"wrote {args.out}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))
    if args.md_out:
        write_markdown(result, args.md_out)
        print(f"wrote {args.md_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
