"""Aggregate leave-subject-out cross-animal sweep results.

Expected layout:

    runs/leave_subject_out_a100/holdout_<subject>/cloud_choice_<arm>_seed<N>/log.jsonl

The output focuses on anatomy-vs-null deltas per held-out subject.
"""
from __future__ import annotations

import math
import re
import sys
from collections import defaultdict
from pathlib import Path

try:
    from analyze_sweep import load_run
except ModuleNotFoundError:
    from scripts.analyze_sweep import load_run


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


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else float("nan")


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: analyze_leave_subject_out.py <root>")
        return 1
    root = Path(sys.argv[1])
    runs = collect(root)
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
    return 0


if __name__ == "__main__":
    sys.exit(main())
