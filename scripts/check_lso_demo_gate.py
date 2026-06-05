"""Check whether an LSO result root passes the anatomy-transfer demo gate."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from analyze_leave_subject_out import (
        PAIRED_TRUE_VS_SHUFFLE_GATE,
        collect_full,
        collect_recording_centered,
        collect_true_vs_shuffle_gate,
    )
except ModuleNotFoundError:
    from scripts.analyze_leave_subject_out import (
        PAIRED_TRUE_VS_SHUFFLE_GATE,
        collect_full,
        collect_recording_centered,
        collect_true_vs_shuffle_gate,
    )


def _seed_result(
    seed: int,
    full: dict[str, dict[int, float]],
    centered: dict[str, dict[int, float]],
    paired: dict[int, tuple[int, float]],
    paired_threshold: float,
) -> dict:
    full_shared = full.get("shared_baseline", {}).get(seed)
    full_true = full.get("region_only", {}).get(seed)
    full_shuffle = full.get("region_shuffle", {}).get(seed)
    centered_shared = centered.get("shared_baseline", {}).get(seed)
    centered_true = centered.get("region_only", {}).get(seed)
    centered_shuffle = centered.get("region_shuffle", {}).get(seed)
    paired_result = paired.get(seed)
    paired_n = None if paired_result is None else paired_result[0]
    paired_frac = None if paired_result is None else paired_result[1]

    checks = {
        "full_auc_true_beats_shared": (
            full_true is not None and full_shared is not None and full_true > full_shared
        ),
        "full_auc_true_beats_shuffle": (
            full_true is not None and full_shuffle is not None and full_true > full_shuffle
        ),
        "centered_auc_true_beats_shared": (
            centered_true is not None and centered_shared is not None and centered_true > centered_shared
        ),
        "centered_auc_true_beats_shuffle": (
            centered_true is not None and centered_shuffle is not None and centered_true > centered_shuffle
        ),
        "paired_true_beats_shuffle_threshold": (
            paired_frac is not None and paired_frac >= paired_threshold
        ),
    }
    return {
        "seed": seed,
        "metrics": {
            "full_auc_shared": full_shared,
            "full_auc_region_only": full_true,
            "full_auc_region_shuffle": full_shuffle,
            "centered_auc_shared": centered_shared,
            "centered_auc_region_only": centered_true,
            "centered_auc_region_shuffle": centered_shuffle,
            "paired_trials": paired_n,
            "paired_true_prob_improved": paired_frac,
            "paired_threshold": paired_threshold,
        },
        "checks": checks,
        "pass": all(checks.values()),
    }


def evaluate_gate(root: Path, holdout: str, paired_threshold: float = PAIRED_TRUE_VS_SHUFFLE_GATE) -> dict:
    full = collect_full(root).get(holdout, {})
    centered = collect_recording_centered(root).get(holdout, {})
    paired = collect_true_vs_shuffle_gate(root).get(holdout, {})
    seeds = sorted(
        set(full.get("shared_baseline", {}))
        | set(full.get("region_only", {}))
        | set(full.get("region_shuffle", {}))
        | set(centered.get("shared_baseline", {}))
        | set(centered.get("region_only", {}))
        | set(centered.get("region_shuffle", {}))
        | set(paired)
    )
    seed_results = [_seed_result(seed, full, centered, paired, paired_threshold) for seed in seeds]
    passing = [row for row in seed_results if row["pass"]]
    return {
        "root": str(root),
        "holdout": holdout,
        "paired_threshold": paired_threshold,
        "n_seeds": len(seed_results),
        "n_passing_seeds": len(passing),
        "pass": bool(seed_results) and len(passing) == len(seed_results),
        "seed_results": seed_results,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--holdout", default="CSH_ZAD_019")
    parser.add_argument("--paired-threshold", type=float, default=PAIRED_TRUE_VS_SHUFFLE_GATE)
    parser.add_argument("--out", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = evaluate_gate(args.root, args.holdout, args.paired_threshold)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text)
        print(f"wrote {args.out}")
    else:
        print(text, end="")
    return 0 if result["pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
