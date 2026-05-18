"""Pull best-eval AUC per (arm, seed) from a sweep directory, compute paired comparison.

Usage:
    uv run python scripts/analyze_sweep.py runs/multi_seed_sweep/

Expects subdirs named like cloud_choice_{arm}_seed{N} each with a log.jsonl.
Outputs a markdown-formatted table + paired t-statistic + per-seed diffs.
"""
from __future__ import annotations

import json
import math
import re
import sys
from collections import defaultdict
from pathlib import Path


def load_run(run_dir: Path) -> dict | None:
    log_path = run_dir / "log.jsonl"
    if not log_path.exists():
        return None
    best = None
    final = None
    with open(log_path) as fh:
        for line in fh:
            try:
                rec = json.loads(line)
            except Exception:
                continue
            if rec.get("event") == "ckpt_best":
                best = rec  # last ckpt_best is the best
            elif rec.get("event") == "done":
                final = rec
    return {"best": best, "final": final}


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: analyze_sweep.py <sweep_dir>")
        return 1
    sweep_dir = Path(sys.argv[1])
    runs: dict[tuple[str, int], dict] = {}
    pat = re.compile(r"cloud_choice_(.+)_seed(\d+)$")
    for d in sorted(sweep_dir.glob("cloud_choice_*")):
        m = pat.match(d.name)
        if not m:
            print(f"  skipping (bad name): {d.name}")
            continue
        arm, seed = m.group(1), int(m.group(2))
        out = load_run(d)
        if out is None or out["best"] is None:
            print(f"  skipping (no logs): {d.name}")
            continue
        runs[(arm, seed)] = out

    # Group by arm
    by_arm: dict[str, dict[int, dict]] = defaultdict(dict)
    for (arm, seed), data in runs.items():
        by_arm[arm][seed] = data

    # Per-arm summary
    print(f"# Sweep analysis: {sweep_dir.name}\n")
    print("## Per-arm AUC summary (best eval across training)\n")
    print("| arm | n_seeds | mean_AUC | std | min | max | seeds |")
    print("|---|---|---|---|---|---|---|")
    per_arm_stats: dict[str, dict] = {}
    for arm in sorted(by_arm):
        aucs = [data["best"].get("eval_auc", float("nan"))
                for data in by_arm[arm].values()]
        aucs = [a for a in aucs if isinstance(a, (int, float)) and not math.isnan(a)]
        if not aucs:
            continue
        n = len(aucs)
        mean = sum(aucs) / n
        var = sum((a - mean) ** 2 for a in aucs) / max(1, n - 1)
        std = math.sqrt(var)
        per_arm_stats[arm] = {"n": n, "mean": mean, "std": std,
                              "min": min(aucs), "max": max(aucs),
                              "by_seed": {s: by_arm[arm][s]["best"]["eval_auc"]
                                          for s in sorted(by_arm[arm])}}
        seed_str = ",".join(f"{a:.3f}" for a in aucs)
        print(f"| {arm} | {n} | **{mean:.3f}** | {std:.3f} | {min(aucs):.3f} | {max(aucs):.3f} | {seed_str} |")

    # Paired comparisons: every non-baseline arm vs baseline
    if "baseline" in by_arm:
        for arm in sorted(by_arm):
            if arm == "baseline":
                continue
            print(f"\n## Paired comparison: {arm} − baseline\n")
            common = sorted(set(by_arm["baseline"]) & set(by_arm[arm]))
            diffs = []
            print(f"| seed | baseline AUC | {arm} AUC | Δ AUC |")
            print("|---|---|---|---|")
            for s in common:
                b = by_arm["baseline"][s]["best"]["eval_auc"]
                c = by_arm[arm][s]["best"]["eval_auc"]
                d = c - b
                diffs.append(d)
                print(f"| {s} | {b:.3f} | {c:.3f} | {d:+.3f} |")
            if not diffs:
                continue
            n = len(diffs)
            mean_d = sum(diffs) / n
            var_d = sum((d - mean_d) ** 2 for d in diffs) / max(1, n - 1)
            sd_d = math.sqrt(var_d)
            se_d = sd_d / math.sqrt(n)
            t_stat = mean_d / se_d if se_d > 0 else float("inf")
            n_positive = sum(1 for d in diffs if d > 0)
            print(f"\n**mean Δ AUC** = {mean_d:+.4f}    "
                  f"**paired SE** = {se_d:.4f}    "
                  f"**t** = {t_stat:.2f} (df={n - 1})    "
                  f"**positive seeds** = {n_positive}/{n}")
            if abs(t_stat) < 1.0:
                print("→ **No effect.**")
            elif abs(t_stat) < 2.0:
                print("→ **Suggestive but weak.**")
            elif n_positive >= n * 0.8:
                print("→ **Consistent effect across seeds — real signal.**")
            else:
                print("→ **Significant by t but inconsistent across seeds.**")
    return 0


if __name__ == "__main__":
    sys.exit(main())
