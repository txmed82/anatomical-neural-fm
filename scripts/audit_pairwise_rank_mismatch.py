"""Audit why paired true-vs-shuffle movement can disagree with ranking AUC.

The pairwise-rank pilot improved true-class probability relative to the shuffled
control, but failed the recording-centered AUC gate. This diagnostic separates
target-aware ranking gains from class-direction probability shifts.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import defaultdict
from pathlib import Path
from typing import Iterable

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from analyze_lso_prediction_ensemble import full_auc, prediction_key, read_prediction_rows  # noqa: E402


def true_class_probability(row: dict) -> float:
    prob = float(row["prob"])
    return prob if int(row["target"]) == 1 else 1.0 - prob


def paired_rows(true_rows: Iterable[dict], shuffle_rows: Iterable[dict]) -> list[tuple[dict, dict]]:
    true_by_key = {prediction_key(row): row for row in true_rows}
    shuffle_by_key = {prediction_key(row): row for row in shuffle_rows}
    return [(true_by_key[key], shuffle_by_key[key]) for key in sorted(set(true_by_key) & set(shuffle_by_key))]


def _mean(values: list[float]) -> float:
    return float(np.mean(values)) if values else float("nan")


def _fraction(values: list[bool]) -> float:
    return float(np.mean(values)) if values else float("nan")


def _finite(value: float) -> bool:
    return math.isfinite(float(value))


def classify_recording(summary: dict) -> str:
    target0 = summary["target0_true_class_improved_fraction"]
    target1 = summary["target1_true_class_improved_fraction"]
    auc_delta = summary["true_minus_shuffle_auc"]
    if _finite(target0) and _finite(target1):
        if target0 >= 0.8 and target1 <= 0.2:
            return "downward_probability_shift"
        if target1 >= 0.8 and target0 <= 0.2:
            return "upward_probability_shift"
        if target0 >= 0.55 and target1 >= 0.55 and auc_delta > 0.0:
            return "target_aware_ranking_gain"
    if _finite(auc_delta) and auc_delta > 0.0:
        return "weak_ranking_gain"
    return "mixed_or_failed_ranking"


def summarize_pairs(true_rows: list[dict], shuffle_rows: list[dict]) -> dict:
    pairs = paired_rows(true_rows, shuffle_rows)
    by_recording: dict[str, list[tuple[dict, dict]]] = defaultdict(list)
    for true_row, shuffle_row in pairs:
        by_recording[str(true_row["recording_id"])].append((true_row, shuffle_row))

    recordings = {}
    for recording_id, recording_pairs in sorted(by_recording.items()):
        true_recording_rows = [true_row for true_row, _shuffle_row in recording_pairs]
        shuffle_recording_rows = [shuffle_row for _true_row, shuffle_row in recording_pairs]
        target0 = [(t, s) for t, s in recording_pairs if int(t["target"]) == 0]
        target1 = [(t, s) for t, s in recording_pairs if int(t["target"]) == 1]
        raw_prob_deltas = [float(t["prob"]) - float(s["prob"]) for t, s in recording_pairs]
        true_class_deltas = [true_class_probability(t) - true_class_probability(s) for t, s in recording_pairs]
        target0_true_class_deltas = [
            true_class_probability(t) - true_class_probability(s) for t, s in target0
        ]
        target1_true_class_deltas = [
            true_class_probability(t) - true_class_probability(s) for t, s in target1
        ]
        summary = {
            "n": len(recording_pairs),
            "target0_n": len(target0),
            "target1_n": len(target1),
            "target1_fraction": _mean([float(int(t["target"])) for t, _s in recording_pairs]),
            "true_auc": full_auc(true_recording_rows),
            "shuffle_auc": full_auc(shuffle_recording_rows),
            "true_minus_shuffle_auc": full_auc(true_recording_rows) - full_auc(shuffle_recording_rows),
            "mean_raw_prob_delta": _mean(raw_prob_deltas),
            "raw_prob_delta_positive_fraction": _fraction([delta > 0.0 for delta in raw_prob_deltas]),
            "raw_prob_delta_negative_fraction": _fraction([delta < 0.0 for delta in raw_prob_deltas]),
            "paired_true_class_improved_fraction": _fraction([delta > 0.0 for delta in true_class_deltas]),
            "mean_true_class_delta": _mean(true_class_deltas),
            "target0_mean_raw_prob_delta": _mean([float(t["prob"]) - float(s["prob"]) for t, s in target0]),
            "target1_mean_raw_prob_delta": _mean([float(t["prob"]) - float(s["prob"]) for t, s in target1]),
            "target0_mean_true_class_delta": _mean(target0_true_class_deltas),
            "target1_mean_true_class_delta": _mean(target1_true_class_deltas),
            "target0_true_class_improved_fraction": _fraction([delta > 0.0 for delta in target0_true_class_deltas]),
            "target1_true_class_improved_fraction": _fraction([delta > 0.0 for delta in target1_true_class_deltas]),
        }
        summary["classification"] = classify_recording(summary)
        recordings[recording_id] = summary

    global_target0 = [
        (t, s) for t, s in pairs if int(t["target"]) == 0
    ]
    global_target1 = [
        (t, s) for t, s in pairs if int(t["target"]) == 1
    ]
    global_true_class_deltas = [
        true_class_probability(t) - true_class_probability(s) for t, s in pairs
    ]
    global_raw_deltas = [float(t["prob"]) - float(s["prob"]) for t, s in pairs]
    classifications = defaultdict(int)
    for summary in recordings.values():
        classifications[summary["classification"]] += 1

    return {
        "n": len(pairs),
        "target0_n": len(global_target0),
        "target1_n": len(global_target1),
        "target1_fraction": _mean([float(int(t["target"])) for t, _s in pairs]),
        "true_auc": full_auc([t for t, _s in pairs]),
        "shuffle_auc": full_auc([s for _t, s in pairs]),
        "true_minus_shuffle_auc": full_auc([t for t, _s in pairs]) - full_auc([s for _t, s in pairs]),
        "paired_true_class_improved_fraction": _fraction([delta > 0.0 for delta in global_true_class_deltas]),
        "mean_true_class_delta": _mean(global_true_class_deltas),
        "mean_raw_prob_delta": _mean(global_raw_deltas),
        "raw_prob_delta_negative_fraction": _fraction([delta < 0.0 for delta in global_raw_deltas]),
        "target0_true_class_improved_fraction": _fraction([
            true_class_probability(t) > true_class_probability(s) for t, s in global_target0
        ]),
        "target1_true_class_improved_fraction": _fraction([
            true_class_probability(t) > true_class_probability(s) for t, s in global_target1
        ]),
        "recording_classifications": dict(sorted(classifications.items())),
        "recordings": recordings,
    }


def audit(root: Path, holdout: str, seed: int) -> dict:
    true_rows = read_prediction_rows(root, holdout, "region_only", seed)
    shuffle_rows = read_prediction_rows(root, holdout, "region_shuffle", seed)
    summary = summarize_pairs(true_rows, shuffle_rows)
    decision = "target_aware_candidate"
    if summary["target0_true_class_improved_fraction"] >= 0.8 and summary["target1_true_class_improved_fraction"] <= 0.2:
        decision = "paired_metric_explained_by_downward_shift"
    elif summary["target1_true_class_improved_fraction"] >= 0.8 and summary["target0_true_class_improved_fraction"] <= 0.2:
        decision = "paired_metric_explained_by_upward_shift"
    elif summary["true_minus_shuffle_auc"] <= 0.0:
        decision = "paired_metric_not_recording_rank_stable"
    return {
        "root": str(root),
        "holdout": holdout,
        "seed": seed,
        "summary": summary,
        "decision": decision,
    }


def fmt_float(value: float, digits: int = 3) -> str:
    if not math.isfinite(float(value)):
        return "n/a"
    return f"{value:.{digits}f}"


def fmt_signed(value: float, digits: int = 3) -> str:
    if not math.isfinite(float(value)):
        return "n/a"
    return f"{value:+.{digits}f}"


def render_markdown(result: dict) -> str:
    summary = result["summary"]
    lines = [
        "# Pairwise Rank Mismatch Audit",
        "",
        f"Root: `{result['root']}`",
        f"Holdout: `{result['holdout']}` seed `{result['seed']}`",
        "",
        "## Global",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| decision | `{result['decision']}` |",
        f"| paired true-class improved | {fmt_float(summary['paired_true_class_improved_fraction'])} |",
        f"| true-minus-shuffle AUC | {fmt_signed(summary['true_minus_shuffle_auc'])} |",
        f"| mean raw probability delta | {fmt_signed(summary['mean_raw_prob_delta'])} |",
        f"| raw probability delta negative fraction | {fmt_float(summary['raw_prob_delta_negative_fraction'])} |",
        f"| target0 true-class improved | {fmt_float(summary['target0_true_class_improved_fraction'])} |",
        f"| target1 true-class improved | {fmt_float(summary['target1_true_class_improved_fraction'])} |",
        "",
        "## Recording Breakdown",
        "",
        "| recording | n | target1_frac | true-shuffle AUC | paired improved | target0 improved | target1 improved | mean raw delta | class |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for recording_id, row in summary["recordings"].items():
        lines.append(
            "| "
            f"`{recording_id}` | {row['n']} | {fmt_float(row['target1_fraction'])} | "
            f"{fmt_signed(row['true_minus_shuffle_auc'])} | "
            f"{fmt_float(row['paired_true_class_improved_fraction'])} | "
            f"{fmt_float(row['target0_true_class_improved_fraction'])} | "
            f"{fmt_float(row['target1_true_class_improved_fraction'])} | "
            f"{fmt_signed(row['mean_raw_prob_delta'])} | "
            f"`{row['classification']}` |"
        )
    lines += [
        "",
        "## Interpretation",
        "",
    ]
    if result["decision"] == "paired_metric_explained_by_downward_shift":
        lines.append(
            "The paired true-vs-shuffle improvement is explained by a mostly downward "
            "probability shift: target-0 trials improve, target-1 trials do not. This "
            "can pass a paired true-class-probability check in target-0-majority "
            "recordings without improving within-recording ranking."
        )
    elif result["decision"] == "paired_metric_explained_by_upward_shift":
        lines.append(
            "The paired true-vs-shuffle improvement is explained by a mostly upward "
            "probability shift: target-1 trials improve, target-0 trials do not."
        )
    else:
        lines.append(
            "The paired true-vs-shuffle metric is not sufficient by itself. The next "
            "objective or gate should require target-0 and target-1 improvements together "
            "inside each recording, or optimize a direct recording-local AUC surrogate."
        )
    lines.append("")
    lines.append(
        "Next objective implication: replace the scalar paired-probability gate with a "
        "balanced bidirectional criterion: true labels should beat the shuffled control "
        "for target-0 and target-1 subsets separately, and improve recording-local ranking."
    )
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--holdout", default="CSH_ZAD_019")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--out-json", type=Path)
    parser.add_argument("--out-md", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = audit(args.root, args.holdout, args.seed)
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        print(f"wrote {args.out_json}")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(render_markdown(result))
        print(f"wrote {args.out_md}")
    if not args.out_json and not args.out_md:
        print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
