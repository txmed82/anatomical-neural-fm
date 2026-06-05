"""Aggregate leave-subject-out cross-animal sweep results.

Expected layout:

    runs/leave_subject_out_a100/holdout_<subject>/cloud_choice_<arm>_seed<N>/log.jsonl

The output focuses on anatomy-vs-null deltas per held-out subject.
"""
from __future__ import annotations

import json
import math
import re
import sys
from collections import defaultdict
from pathlib import Path

try:
    from analyze_sweep import load_run
except ModuleNotFoundError:
    from scripts.analyze_sweep import load_run


PAIRED_TRUE_VS_SHUFFLE_GATE = 0.55


def _auc(scores: list[float], labels: list[int]) -> float:
    pos = [score for score, label in zip(scores, labels) if label == 1]
    neg = [score for score, label in zip(scores, labels) if label == 0]
    if not pos or not neg:
        return float("nan")
    all_scores = pos + neg
    ranks = [0] * len(all_scores)
    for rank, idx in enumerate(sorted(range(len(all_scores)), key=lambda i: all_scores[i]), start=1):
        ranks[idx] = rank
    pos_ranks = ranks[:len(pos)]
    n_pos, n_neg = len(pos), len(neg)
    return float((sum(pos_ranks) - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg))


def _safe_subject(dirname: str) -> str:
    return dirname.removeprefix("holdout_")


def collect(root: Path) -> dict[str, dict[str, dict[int, float]]]:
    runs: dict[str, dict[str, dict[int, float]]] = defaultdict(lambda: defaultdict(dict))
    pat = re.compile(r"cloud_choice_(.+)_seed(\d+)$")
    for holdout_dir in sorted(root.glob("holdout_*")):
        if not holdout_dir.is_dir():
            continue
        holdout = _safe_subject(holdout_dir.name)
        for run_dir in sorted(holdout_dir.glob("cloud_choice_*")):
            m = pat.match(run_dir.name)
            if not m:
                continue
            arm, seed = m.group(1), int(m.group(2))
            data = load_run(run_dir)
            if data is None or data["best"] is None:
                continue
            auc = data["best"].get("eval_auc")
            if isinstance(auc, (int, float)) and not math.isnan(auc):
                runs[holdout][arm][seed] = float(auc)
    return runs


def full_eval_auc_from_log(run_dir: Path) -> float | None:
    log_path = run_dir / "log.jsonl"
    if not log_path.exists():
        return None
    latest = None
    with log_path.open() as fh:
        for line in fh:
            try:
                record = json.loads(line)
            except Exception:
                continue
            if record.get("event") != "full_eval":
                continue
            auc = record.get("full_eval_auc")
            if isinstance(auc, (int, float)) and not math.isnan(auc):
                latest = float(auc)
    return latest


def full_eval_auc_from_predictions(run_dir: Path) -> float | None:
    path = run_dir / "eval_predictions.jsonl"
    if not path.exists():
        return None
    probs = []
    targets = []
    with path.open() as fh:
        for line in fh:
            try:
                row = json.loads(line)
            except Exception:
                continue
            if "prob" not in row or "target" not in row:
                continue
            probs.append(float(row["prob"]))
            targets.append(int(row["target"]))
    if not probs:
        return None
    auc = _auc(probs, targets)
    return None if math.isnan(auc) else auc


def collect_full(root: Path) -> dict[str, dict[str, dict[int, float]]]:
    runs: dict[str, dict[str, dict[int, float]]] = defaultdict(lambda: defaultdict(dict))
    pat = re.compile(r"cloud_choice_(.+)_seed(\d+)$")
    for holdout_dir in sorted(root.glob("holdout_*")):
        if not holdout_dir.is_dir():
            continue
        holdout = _safe_subject(holdout_dir.name)
        for run_dir in sorted(holdout_dir.glob("cloud_choice_*")):
            m = pat.match(run_dir.name)
            if not m:
                continue
            arm, seed = m.group(1), int(m.group(2))
            auc = full_eval_auc_from_log(run_dir)
            if auc is None:
                auc = full_eval_auc_from_predictions(run_dir)
            if auc is not None:
                runs[holdout][arm][seed] = auc
    return runs


def prediction_rows(run_dir: Path) -> list[dict]:
    path = run_dir / "eval_predictions.jsonl"
    if not path.exists():
        return []
    rows = []
    with path.open() as fh:
        for line in fh:
            try:
                row = json.loads(line)
            except Exception:
                continue
            if {"recording_id", "t0", "target", "prob"} <= set(row):
                rows.append(row)
    return rows


def recording_centered_auc(rows: list[dict]) -> float | None:
    if not rows:
        return None
    by_recording: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_recording[str(row["recording_id"])].append(row)
    scores = []
    labels = []
    for recording_rows in by_recording.values():
        probs = [float(row["prob"]) for row in recording_rows]
        center = mean(probs)
        scores.extend(prob - center for prob in probs)
        labels.extend(int(row["target"]) for row in recording_rows)
    auc = _auc(scores, labels)
    return None if math.isnan(auc) else auc


def collect_recording_centered(root: Path) -> dict[str, dict[str, dict[int, float]]]:
    runs: dict[str, dict[str, dict[int, float]]] = defaultdict(lambda: defaultdict(dict))
    pat = re.compile(r"cloud_choice_(.+)_seed(\d+)$")
    for holdout_dir in sorted(root.glob("holdout_*")):
        if not holdout_dir.is_dir():
            continue
        holdout = _safe_subject(holdout_dir.name)
        for run_dir in sorted(holdout_dir.glob("cloud_choice_*")):
            m = pat.match(run_dir.name)
            if not m:
                continue
            arm, seed = m.group(1), int(m.group(2))
            auc = recording_centered_auc(prediction_rows(run_dir))
            if auc is not None:
                runs[holdout][arm][seed] = auc
    return runs


def trial_key(row: dict) -> tuple[str, float, int]:
    return (str(row["recording_id"]), float(row["t0"]), int(row["target"]))


def paired_true_improvement(candidate_rows: list[dict], baseline_rows: list[dict]) -> tuple[int, float] | None:
    baseline_by_key = {trial_key(row): row for row in baseline_rows}
    improved = []
    for row in candidate_rows:
        baseline = baseline_by_key.get(trial_key(row))
        if baseline is None:
            continue
        delta = float(row["prob"]) - float(baseline["prob"])
        direction = 1.0 if int(row["target"]) == 1 else -1.0
        improved.append(direction * delta > 0)
    if not improved:
        return None
    return len(improved), sum(1 for value in improved if value) / len(improved)


def collect_true_vs_shuffle_gate(root: Path) -> dict[str, dict[int, tuple[int, float]]]:
    gates: dict[str, dict[int, tuple[int, float]]] = defaultdict(dict)
    pat = re.compile(r"cloud_choice_(.+)_seed(\d+)$")
    for holdout_dir in sorted(root.glob("holdout_*")):
        if not holdout_dir.is_dir():
            continue
        holdout = _safe_subject(holdout_dir.name)
        rows_by_seed_arm: dict[int, dict[str, list[dict]]] = defaultdict(dict)
        for run_dir in sorted(holdout_dir.glob("cloud_choice_*")):
            m = pat.match(run_dir.name)
            if not m:
                continue
            arm, seed = m.group(1), int(m.group(2))
            rows = prediction_rows(run_dir)
            if rows:
                rows_by_seed_arm[seed][arm] = rows
        for seed, by_arm in rows_by_seed_arm.items():
            if "region_only" not in by_arm or "region_shuffle" not in by_arm:
                continue
            result = paired_true_improvement(by_arm["region_only"], by_arm["region_shuffle"])
            if result is not None:
                gates[holdout][seed] = result
    return gates


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else float("nan")


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: analyze_leave_subject_out.py <root>")
        return 1
    root = Path(sys.argv[1])
    runs = collect(root)
    full_runs = collect_full(root)
    centered_runs = collect_recording_centered(root)
    paired_gates = collect_true_vs_shuffle_gate(root)
    arms = sorted({arm for by_arm in runs.values() for arm in by_arm})
    anatomy_arms = [a for a in arms if a != "shared_baseline"]

    print("# Leave-subject-out analysis\n")
    print(f"root: `{root}`\n")
    print("## Per-Holdout AUC and Delta vs Shared Null\n")
    print("| holdout | arm | n_seeds | mean_AUC | mean_delta_vs_shared | seed_deltas |")
    print("|---|---|---|---|---|---|")

    aggregate: dict[str, list[float]] = defaultdict(list)
    for holdout in sorted(runs):
        baseline = runs[holdout].get("shared_baseline", {})
        for arm in anatomy_arms:
            arm_runs = runs[holdout].get(arm, {})
            common = sorted(set(baseline) & set(arm_runs))
            if not common:
                continue
            aucs = [arm_runs[s] for s in common]
            deltas = [arm_runs[s] - baseline[s] for s in common]
            aggregate[arm].extend(deltas)
            delta_str = ",".join(f"{d:+.3f}" for d in deltas)
            print(
                f"| {holdout} | {arm} | {len(common)} | "
                f"{mean(aucs):.3f} | {mean(deltas):+.3f} | {delta_str} |"
            )

    print("\n## Aggregate Delta vs Shared Null\n")
    print("| arm | n_pairs | mean_delta | positive_pairs |")
    print("|---|---|---|---|")
    for arm in anatomy_arms:
        deltas = aggregate.get(arm, [])
        if not deltas:
            continue
        positive = sum(1 for d in deltas if d > 0)
        print(f"| {arm} | {len(deltas)} | {mean(deltas):+.3f} | {positive}/{len(deltas)} |")

    full_arms = sorted({arm for by_arm in full_runs.values() for arm in by_arm})
    full_anatomy_arms = [a for a in full_arms if a != "shared_baseline"]
    if full_anatomy_arms:
        print("\n## Full Held-Out-Trial AUC and Delta vs Shared Null\n")
        print("| holdout | arm | n_seeds | mean_full_AUC | mean_full_delta_vs_shared | seed_full_deltas |")
        print("|---|---|---|---|---|---|")
        full_aggregate: dict[str, list[float]] = defaultdict(list)
        for holdout in sorted(full_runs):
            baseline = full_runs[holdout].get("shared_baseline", {})
            for arm in full_anatomy_arms:
                arm_runs = full_runs[holdout].get(arm, {})
                common = sorted(set(baseline) & set(arm_runs))
                if not common:
                    continue
                aucs = [arm_runs[s] for s in common]
                deltas = [arm_runs[s] - baseline[s] for s in common]
                full_aggregate[arm].extend(deltas)
                delta_str = ",".join(f"{d:+.3f}" for d in deltas)
                print(
                    f"| {holdout} | {arm} | {len(common)} | "
                    f"{mean(aucs):.3f} | {mean(deltas):+.3f} | {delta_str} |"
                )

        print("\n## Full Held-Out-Trial Aggregate Delta vs Shared Null\n")
        print("| arm | n_pairs | mean_full_delta | positive_pairs |")
        print("|---|---|---|---|")
        for arm in full_anatomy_arms:
            deltas = full_aggregate.get(arm, [])
            if not deltas:
                continue
            positive = sum(1 for d in deltas if d > 0)
            print(f"| {arm} | {len(deltas)} | {mean(deltas):+.3f} | {positive}/{len(deltas)} |")

    centered_arms = sorted({arm for by_arm in centered_runs.values() for arm in by_arm})
    centered_anatomy_arms = [a for a in centered_arms if a != "shared_baseline"]
    if centered_anatomy_arms:
        print("\n## Recording-Centered Full-Trial AUC and Delta vs Shared Null\n")
        print("| holdout | arm | n_seeds | mean_centered_AUC | mean_centered_delta_vs_shared | seed_centered_deltas |")
        print("|---|---|---|---|---|---|")
        for holdout in sorted(centered_runs):
            baseline = centered_runs[holdout].get("shared_baseline", {})
            for arm in centered_anatomy_arms:
                arm_runs = centered_runs[holdout].get(arm, {})
                common = sorted(set(baseline) & set(arm_runs))
                if not common:
                    continue
                aucs = [arm_runs[s] for s in common]
                deltas = [arm_runs[s] - baseline[s] for s in common]
                delta_str = ",".join(f"{d:+.3f}" for d in deltas)
                print(
                    f"| {holdout} | {arm} | {len(common)} | "
                    f"{mean(aucs):.3f} | {mean(deltas):+.3f} | {delta_str} |"
                )

    if paired_gates:
        print("\n## Paired True-vs-Shuffle Trial Gate\n")
        print("| holdout | seed | paired_trials | true_prob_improved | threshold | verdict |")
        print("|---|---:|---:|---:|---:|---|")
        for holdout in sorted(paired_gates):
            for seed, (n_pairs, frac) in sorted(paired_gates[holdout].items()):
                verdict = "pass" if frac >= PAIRED_TRUE_VS_SHUFFLE_GATE else "fail"
                print(
                    f"| {holdout} | {seed} | {n_pairs} | {frac:.3f} | "
                    f"{PAIRED_TRUE_VS_SHUFFLE_GATE:.3f} | {verdict} |"
                )
    return 0


if __name__ == "__main__":
    sys.exit(main())
