"""Summarize leave-subject-out runs captured in a combined cloud log."""
from __future__ import annotations

import argparse
import json
import math
import re
from collections import defaultdict
from pathlib import Path


RUN_HEADER = re.compile(r"^=== holdout=(.+?) arm=(.+?) seed=(\d+) ===")


def parse_log(path: Path) -> dict[tuple[str, str, int], dict]:
    runs: dict[tuple[str, str, int], dict] = {}
    current: tuple[str, str, int] | None = None
    for line in path.read_text(errors="replace").splitlines():
        match = RUN_HEADER.match(line)
        if match:
            current = (match.group(1), match.group(2), int(match.group(3)))
            runs.setdefault(current, {"evals": [], "done": False})
            continue
        if current is None or not line.startswith("{"):
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if record.get("event") == "eval":
            runs[current]["evals"].append(record)
        elif record.get("event") == "done":
            runs[current]["done"] = True
    return runs


def best_eval(records: list[dict]) -> dict | None:
    best = None
    for record in records:
        auc = record.get("eval_auc")
        if not isinstance(auc, (int, float)) or math.isnan(auc):
            continue
        if best is None or auc > best.get("eval_auc", float("-inf")):
            best = record
    return best


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("log_path", type=Path)
    args = parser.parse_args()

    runs = parse_log(args.log_path)
    rows = []
    for (holdout, arm, seed), data in sorted(runs.items()):
        best = best_eval(data["evals"])
        if best is None:
            continue
        rows.append((holdout, arm, seed, data["done"], best))

    print("# Leave-subject-out Log Analysis\n")
    print(f"log: `{args.log_path}`\n")
    print("## Per-Run Best AUC\n")
    print("| holdout | arm | seed | complete | best_AUC | step |")
    print("|---|---|---:|:---:|---:|---:|")
    for holdout, arm, seed, done, best in rows:
        print(
            f"| {holdout} | {arm} | {seed} | {'yes' if done else 'no'} | "
            f"{best['eval_auc']:.3f} | {best['step']} |"
        )

    by_holdout: dict[str, dict[str, list[tuple[int, float]]]] = defaultdict(lambda: defaultdict(list))
    for holdout, arm, seed, _done, best in rows:
        by_holdout[holdout][arm].append((seed, float(best["eval_auc"])))

    print("\n## Delta vs Shared Baseline\n")
    print("| holdout | arm | n_pairs | mean_delta | seed_deltas |")
    print("|---|---|---:|---:|---|")
    aggregate: dict[str, list[float]] = defaultdict(list)
    for holdout in sorted(by_holdout):
        baseline = dict(by_holdout[holdout].get("shared_baseline", []))
        for arm in sorted(a for a in by_holdout[holdout] if a != "shared_baseline"):
            deltas = []
            for seed, auc in sorted(by_holdout[holdout][arm]):
                if seed in baseline:
                    deltas.append(auc - baseline[seed])
            if not deltas:
                continue
            aggregate[arm].extend(deltas)
            delta_str = ",".join(f"{delta:+.3f}" for delta in deltas)
            mean_delta = sum(deltas) / len(deltas)
            print(f"| {holdout} | {arm} | {len(deltas)} | {mean_delta:+.3f} | {delta_str} |")

    print("\n## Aggregate Delta vs Shared Baseline\n")
    print("| arm | n_pairs | mean_delta | positive_pairs |")
    print("|---|---:|---:|---:|")
    for arm in sorted(aggregate):
        deltas = aggregate[arm]
        positive = sum(1 for delta in deltas if delta > 0)
        mean_delta = sum(deltas) / len(deltas)
        print(f"| {arm} | {len(deltas)} | {mean_delta:+.3f} | {positive}/{len(deltas)} |")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
