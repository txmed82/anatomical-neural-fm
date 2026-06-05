"""Audit diagnostic prediction/embedding exports for the CSH anatomy run."""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from train import _auc  # noqa: E402


DEFAULT_CARRIERS = ("PRT", "CA", "VP", "MOp", "DG", "mfbc")


@dataclass(frozen=True)
class PredictionRun:
    arm: str
    seed: int
    path: Path
    rows: tuple[dict, ...]


@dataclass(frozen=True)
class PredictionMetrics:
    n: int
    auc: float
    acc: float
    mean_prob_target0: float
    mean_prob_target1: float


@dataclass(frozen=True)
class PairedDeltaMetrics:
    n: int
    mean_delta: float
    mean_abs_delta: float
    mean_delta_target0: float
    mean_delta_target1: float
    frac_true_probability_improved: float


def display_path(path: Path) -> str:
    path = path.expanduser()
    if not path.is_absolute():
        return str(path)
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def parse_run_path(path: Path) -> tuple[str, int] | None:
    match = re.search(r"cloud_choice_(?P<arm>.+)_seed(?P<seed>\d+)", str(path.parent))
    if not match:
        return None
    return match.group("arm"), int(match.group("seed"))


def load_prediction_runs(root: Path) -> list[PredictionRun]:
    runs = []
    for path in sorted(root.glob("**/eval_predictions.jsonl")):
        parsed = parse_run_path(path)
        if parsed is None:
            continue
        rows = tuple(json.loads(line) for line in path.read_text().splitlines() if line.strip())
        arm, seed = parsed
        runs.append(PredictionRun(arm=arm, seed=seed, path=path, rows=rows))
    return runs


def prediction_metrics(rows: Iterable[dict]) -> PredictionMetrics:
    rows = tuple(rows)
    if not rows:
        return PredictionMetrics(0, float("nan"), float("nan"), float("nan"), float("nan"))
    probs = np.asarray([float(row["prob"]) for row in rows], dtype=np.float64)
    targets = np.asarray([int(row["target"]) for row in rows], dtype=np.int64)
    acc = float(np.mean((probs > 0.5) == targets.astype(bool)))
    target0 = probs[targets == 0]
    target1 = probs[targets == 1]
    return PredictionMetrics(
        n=len(rows),
        auc=_auc(probs, targets),
        acc=acc,
        mean_prob_target0=float(np.mean(target0)) if len(target0) else float("nan"),
        mean_prob_target1=float(np.mean(target1)) if len(target1) else float("nan"),
    )


def trial_key(row: dict) -> tuple[str, float, int]:
    return (str(row["recording_id"]), float(row["t0"]), int(row["target"]))


def paired_delta_metrics(candidate_rows: Iterable[dict], baseline_rows: Iterable[dict]) -> PairedDeltaMetrics:
    baseline_by_key = {trial_key(row): row for row in baseline_rows}
    deltas = []
    targets = []
    true_prob_improved = []
    for row in candidate_rows:
        key = trial_key(row)
        baseline = baseline_by_key.get(key)
        if baseline is None:
            continue
        target = int(row["target"])
        delta = float(row["prob"]) - float(baseline["prob"])
        deltas.append(delta)
        targets.append(target)
        direction = 1.0 if target == 1 else -1.0
        true_prob_improved.append(direction * delta > 0)
    if not deltas:
        return PairedDeltaMetrics(0, float("nan"), float("nan"), float("nan"), float("nan"), float("nan"))
    deltas_np = np.asarray(deltas, dtype=np.float64)
    targets_np = np.asarray(targets, dtype=np.int64)
    improved_np = np.asarray(true_prob_improved, dtype=bool)
    target0 = deltas_np[targets_np == 0]
    target1 = deltas_np[targets_np == 1]
    return PairedDeltaMetrics(
        n=len(deltas),
        mean_delta=float(np.mean(deltas_np)),
        mean_abs_delta=float(np.mean(np.abs(deltas_np))),
        mean_delta_target0=float(np.mean(target0)) if len(target0) else float("nan"),
        mean_delta_target1=float(np.mean(target1)) if len(target1) else float("nan"),
        frac_true_probability_improved=float(np.mean(improved_np)),
    )


def by_recording_metrics(run: PredictionRun) -> list[tuple[str, PredictionMetrics]]:
    rows_by_recording: dict[str, list[dict]] = defaultdict(list)
    for row in run.rows:
        rows_by_recording[str(row["recording_id"])].append(row)
    return [
        (recording, prediction_metrics(rows))
        for recording, rows in sorted(rows_by_recording.items())
    ]


def rows_for_recording(rows: Iterable[dict], recording: str) -> list[dict]:
    return [row for row in rows if str(row["recording_id"]) == recording]


def fmt_float(value: float, digits: int = 3) -> str:
    if math.isnan(value):
        return "n/a"
    return f"{value:.{digits}f}"


def fmt_signed(value: float | None, digits: int = 3) -> str:
    if value is None or math.isnan(value):
        return "n/a"
    return f"{value:+.{digits}f}"


def load_embedding_rows(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    rows = {}
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        rows[str(row["region"])] = row
    return rows


def embedding_path_for(root: Path, arm: str, seed: int) -> Path:
    matches = sorted(root.glob(f"**/cloud_choice_{arm}_seed{seed}/region_embeddings.jsonl"))
    return matches[0] if matches else root / "__missing__"


def cosine(a: list[float], b: list[float]) -> float:
    av = np.asarray(a, dtype=np.float64)
    bv = np.asarray(b, dtype=np.float64)
    denom = float(np.linalg.norm(av) * np.linalg.norm(bv))
    if denom == 0.0:
        return float("nan")
    return float(np.dot(av, bv) / denom)


def write_report(root: Path, out_path: Path, carriers: Iterable[str] = DEFAULT_CARRIERS) -> None:
    runs = load_prediction_runs(root)
    by_key = {(run.arm, run.seed): run for run in runs}
    lines = [
        "# CSH Diagnostic Output Audit",
        "",
        f"Root: `{display_path(root)}`",
        "",
        "## Available Prediction Artifacts",
        "",
        "| arm | seed | rows | AUC | accuracy | mean_prob_target0 | mean_prob_target1 | delta_vs_shared_same_seed | path |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for run in sorted(runs, key=lambda row: (row.seed, row.arm)):
        metrics = prediction_metrics(run.rows)
        baseline = by_key.get(("shared_baseline", run.seed))
        baseline_auc = None if baseline is None else prediction_metrics(baseline.rows).auc
        delta = None if baseline_auc is None else metrics.auc - baseline_auc
        lines.append(
            "| "
            f"{run.arm} | {run.seed} | {metrics.n} | {fmt_float(metrics.auc)} | "
            f"{fmt_float(metrics.acc)} | {fmt_float(metrics.mean_prob_target0)} | "
            f"{fmt_float(metrics.mean_prob_target1)} | {fmt_signed(delta)} | "
            f"`{display_path(run.path)}` |"
        )

    lines += [
        "",
        "## Per-Recording AUC",
        "",
        "| arm | seed | recording | rows | AUC | accuracy |",
        "|---|---:|---|---:|---:|---:|",
    ]
    for run in sorted(runs, key=lambda row: (row.seed, row.arm)):
        for recording, metrics in by_recording_metrics(run):
            lines.append(
                "| "
                f"{run.arm} | {run.seed} | `{recording}` | {metrics.n} | "
                f"{fmt_float(metrics.auc)} | {fmt_float(metrics.acc)} |"
            )

    lines += [
        "",
        "## Seed-0 Per-Recording Delta vs Shared Baseline",
        "",
        "| arm | recording | rows | AUC | baseline_AUC | delta_AUC | mean_prob_delta | mean_abs_prob_delta | true_prob_improved |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    baseline_run = by_key.get(("shared_baseline", 0))
    for arm in ("region_only", "region_shuffle"):
        run = by_key.get((arm, 0))
        if run is None or baseline_run is None:
            continue
        recordings = sorted({str(row["recording_id"]) for row in run.rows})
        for recording in recordings:
            arm_rows = rows_for_recording(run.rows, recording)
            base_rows = rows_for_recording(baseline_run.rows, recording)
            arm_metrics = prediction_metrics(arm_rows)
            base_metrics = prediction_metrics(base_rows)
            paired = paired_delta_metrics(arm_rows, base_rows)
            lines.append(
                "| "
                f"{arm} | `{recording}` | {paired.n} | {fmt_float(arm_metrics.auc)} | "
                f"{fmt_float(base_metrics.auc)} | {fmt_signed(arm_metrics.auc - base_metrics.auc)} | "
                f"{fmt_signed(paired.mean_delta)} | {fmt_float(paired.mean_abs_delta)} | "
                f"{fmt_float(paired.frac_true_probability_improved)} |"
            )

    lines += [
        "",
        "## Seed-0 Paired Trial Probability Shift vs Shared Baseline",
        "",
        "| arm | paired_trials | mean_prob_delta | mean_abs_prob_delta | mean_delta_target0 | mean_delta_target1 | true_prob_improved |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    if baseline_run is not None:
        for arm in ("region_only", "region_shuffle"):
            run = by_key.get((arm, 0))
            if run is None:
                continue
            paired = paired_delta_metrics(run.rows, baseline_run.rows)
            lines.append(
                "| "
                f"{arm} | {paired.n} | {fmt_signed(paired.mean_delta)} | "
                f"{fmt_float(paired.mean_abs_delta)} | {fmt_signed(paired.mean_delta_target0)} | "
                f"{fmt_signed(paired.mean_delta_target1)} | {fmt_float(paired.frac_true_probability_improved)} |"
            )

    true_emb = load_embedding_rows(embedding_path_for(root, "region_only", 0))
    shuffle_emb = load_embedding_rows(embedding_path_for(root, "region_shuffle", 0))
    lines += [
        "",
        "## Seed-0 Region Embedding Diagnostics",
        "",
        "| region | true_norm | shuffled_norm | true_shuffle_cosine |",
        "|---|---:|---:|---:|",
    ]
    for region in carriers:
        true_row = true_emb.get(region)
        shuffle_row = shuffle_emb.get(region)
        cos = None
        if true_row and shuffle_row:
            cos = cosine(true_row["embedding"], shuffle_row["embedding"])
        lines.append(
            "| "
            f"{region} | {fmt_float(float(true_row['norm'])) if true_row else 'n/a'} | "
            f"{fmt_float(float(shuffle_row['norm'])) if shuffle_row else 'n/a'} | "
            f"{fmt_float(cos) if cos is not None else 'n/a'} |"
        )

    region_run = by_key.get(("region_only", 0))
    shuffle_run = by_key.get(("region_shuffle", 0))
    baseline_run = by_key.get(("shared_baseline", 0))
    region_delta = None
    shuffle_delta = None
    region_paired = None
    shuffle_paired = None
    if region_run and baseline_run:
        region_delta = prediction_metrics(region_run.rows).auc - prediction_metrics(baseline_run.rows).auc
        region_paired = paired_delta_metrics(region_run.rows, baseline_run.rows)
    if shuffle_run and baseline_run:
        shuffle_delta = prediction_metrics(shuffle_run.rows).auc - prediction_metrics(baseline_run.rows).auc
        shuffle_paired = paired_delta_metrics(shuffle_run.rows, baseline_run.rows)
    lines += [
        "",
        "## Interpretation",
        "",
        (
            "This is a partial diagnostic run, not a completed three-seed sweep. The "
            "pod terminated before `summary.md`, but it preserved full held-out "
            "prediction exports for seed 0 `shared_baseline`, `region_only`, and "
            "`region_shuffle`, plus seed 1 `shared_baseline`."
        ),
        "",
        (
            f"For seed 0, exported predictions give `region_only` delta "
            f"{fmt_signed(region_delta)} AUC vs the exported shared baseline and "
            f"`region_shuffle` delta {fmt_signed(shuffle_delta)} AUC. Use this "
            "artifact-level result to inspect where the canonical aggregate lift "
            "comes from before launching additional candidate subjects."
        ),
        "",
    ]
    if region_paired and shuffle_paired:
        lines += [
            (
                "Paired trial comparisons show that both seed-0 anatomy arms mostly "
                "shift probabilities upward relative to the shared baseline rather "
                "than moving probabilities toward the true class: `region_only` "
                f"mean probability delta {fmt_signed(region_paired.mean_delta)} "
                f"with true-class improvement on {fmt_float(region_paired.frac_true_probability_improved)} "
                "of paired trials, and `region_shuffle` mean probability delta "
                f"{fmt_signed(shuffle_paired.mean_delta)} with true-class improvement on "
                f"{fmt_float(shuffle_paired.frac_true_probability_improved)} of paired trials."
            ),
            "",
            (
                "The strongest true-label per-recording gains are on the two "
                "`5adab0b7` probes, but the shuffled-label control also improves "
                "those probes. That makes the surviving seed-0 full-trial signal "
                "look more like calibration/probe-specific behavior than a clean "
                "anatomical identity code."
            ),
            "",
        ]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=REPO_ROOT / "runs/lso_csh_diagnostic_outputs")
    parser.add_argument("--out", type=Path, default=REPO_ROOT / "docs/csh_diagnostic_output_audit.md")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    write_report(args.root, args.out)
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
