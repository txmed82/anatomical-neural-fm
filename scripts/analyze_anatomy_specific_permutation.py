"""Run a recording-level permutation gate for anatomy-specific LSO evidence."""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

try:
    from analyze_lso_prediction_ensemble import (
        ARMS,
        analyze,
    )
except ModuleNotFoundError:
    from scripts.analyze_lso_prediction_ensemble import (
        ARMS,
        analyze,
    )


def _recording_deltas(ensemble: dict) -> dict[str, float]:
    true_recordings = ensemble["ensemble_metrics"]["region_only"]["recording_auc"]
    shuffle_recordings = ensemble["ensemble_metrics"]["region_shuffle"]["recording_auc"]
    return {
        recording_id: true_recordings[recording_id]["auc"] - shuffle_recordings[recording_id]["auc"]
        for recording_id in sorted(set(true_recordings) & set(shuffle_recordings))
    }


def sign_flip_p_value(deltas: dict[str, float]) -> dict:
    values = list(deltas.values())
    observed = sum(values) / len(values) if values else float("nan")
    if not values:
        return {
            "observed_mean_delta": observed,
            "n_recordings": 0,
            "one_sided_p": None,
            "null_distribution": [],
        }
    null = []
    for signs in itertools.product((-1.0, 1.0), repeat=len(values)):
        null.append(sum(sign * value for sign, value in zip(signs, values)) / len(values))
    p_value = sum(value >= observed for value in null) / len(null)
    return {
        "observed_mean_delta": observed,
        "n_recordings": len(values),
        "one_sided_p": p_value,
        "null_distribution": sorted(null),
    }


def anatomy_specific_gate(
    root: Path,
    holdout: str,
    *,
    alpha: float = 0.05,
    min_recording_support_fraction: float = 0.75,
    min_centered_delta: float = 0.01,
    min_specificity_gap: float = 0.0,
) -> dict:
    ensemble = analyze(root, holdout)
    deltas = _recording_deltas(ensemble)
    permutation = sign_flip_p_value(deltas)
    n_positive = sum(value > 0.0 for value in deltas.values())
    support_fraction = 0.0 if not deltas else n_positive / len(deltas)
    metrics = ensemble["ensemble_metrics"]
    paired = ensemble["ensemble_paired"]
    centered_delta = metrics["region_only"]["centered_auc"] - metrics["region_shuffle"]["centered_auc"]
    full_delta = metrics["region_only"]["full_auc"] - metrics["region_shuffle"]["full_auc"]
    specificity_gap = (
        paired["region_only_vs_shuffle"]["improved_fraction"]
        - paired["shuffle_vs_shared"]["improved_fraction"]
    )
    checks = {
        "positive_centered_delta": centered_delta >= min_centered_delta,
        "positive_specificity_gap": specificity_gap > min_specificity_gap,
        "recording_support": support_fraction >= min_recording_support_fraction,
        "recording_permutation": (
            permutation["one_sided_p"] is not None and permutation["one_sided_p"] <= alpha
        ),
    }
    return {
        "root": str(root),
        "holdout": holdout,
        "arms": list(ARMS),
        "thresholds": {
            "alpha": alpha,
            "min_centered_delta": min_centered_delta,
            "min_specificity_gap": min_specificity_gap,
            "min_recording_support_fraction": min_recording_support_fraction,
        },
        "metrics": {
            "centered_auc_region_only": metrics["region_only"]["centered_auc"],
            "centered_auc_region_shuffle": metrics["region_shuffle"]["centered_auc"],
            "centered_auc_delta_vs_shuffle": centered_delta,
            "full_auc_region_only": metrics["region_only"]["full_auc"],
            "full_auc_region_shuffle": metrics["region_shuffle"]["full_auc"],
            "full_auc_delta_vs_shuffle": full_delta,
            "paired_true_vs_shuffle": paired["region_only_vs_shuffle"]["improved_fraction"],
            "paired_shuffle_vs_shared": paired["shuffle_vs_shared"]["improved_fraction"],
            "paired_specificity_gap": specificity_gap,
            "recording_deltas": deltas,
            "recordings_positive": n_positive,
            "n_recordings": len(deltas),
            "recording_support_fraction": support_fraction,
            "recording_sign_flip": permutation,
        },
        "checks": checks,
        "pass": all(checks.values()),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--holdout", default="CSH_ZAD_019")
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--min-recording-support-fraction", type=float, default=0.75)
    parser.add_argument("--min-centered-delta", type=float, default=0.01)
    parser.add_argument("--min-specificity-gap", type=float, default=0.0)
    parser.add_argument("--out", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = anatomy_specific_gate(
        args.root,
        args.holdout,
        alpha=args.alpha,
        min_recording_support_fraction=args.min_recording_support_fraction,
        min_centered_delta=args.min_centered_delta,
        min_specificity_gap=args.min_specificity_gap,
    )
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
