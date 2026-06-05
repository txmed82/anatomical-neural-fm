"""Gate fixed broad-family train-arm prediction rows against shuffled anatomy."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.audit_model_free_positive_holdouts import recording_target_rows  # noqa: E402
from scripts.audit_model_free_recording_bidirectional_gate import recording_bidirectional_summary  # noqa: E402
from scripts.summarize_fixed_broad_family_train_arm_panel import (  # noqa: E402
    auc,
    metrics_from_prediction_rows,
    repo_relative,
)
DEFAULT_CASES = (
    ("CSHL045", "post_error_response_extreme_25_75_le_1"),
    ("NR_0019", "post_error_response_extreme_33_67_le_1"),
)


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def prediction_path(root: Path, holdout: str, control: str) -> Path:
    return root / f"holdout_{holdout}" / f"fixed_broad_family_count_{control}_seed0" / "eval_predictions.jsonl"


def paired_rows(true_rows: list[dict], shuffle_rows: list[dict]) -> list[tuple[dict, dict]]:
    by_key = {
        (str(row["recording_id"]), float(row["t0"]), int(row["target"])): row
        for row in shuffle_rows
    }
    pairs = []
    for row in true_rows:
        key = (str(row["recording_id"]), float(row["t0"]), int(row["target"]))
        if key not in by_key:
            raise ValueError(f"missing shuffled prediction for {key}")
        pairs.append((row, by_key[key]))
    if len(pairs) != len(shuffle_rows):
        raise ValueError("true/shuffle prediction row sets do not have identical trial keys")
    return pairs


def centered_auc_from_scores(scores: np.ndarray, labels: np.ndarray, recording_ids: list[str]) -> float:
    centered = scores.copy()
    for recording_id in sorted(set(recording_ids)):
        mask = np.asarray([value == recording_id for value in recording_ids], dtype=bool)
        centered[mask] -= centered[mask].mean()
    return auc(centered, labels)


def gate_decision(
    row: dict,
    *,
    min_centered_delta: float,
    min_target_improvement: float,
    min_bidirectional_recording_fraction: float,
) -> str:
    if row["centered_delta_vs_shuffle"] < min_centered_delta:
        return "reject: centered delta"
    if row["target0_improved_vs_shuffle"] < min_target_improvement:
        return "reject: target0"
    if row["target1_improved_vs_shuffle"] < min_target_improvement:
        return "reject: target1"
    if row["bidirectional_recording_fraction"] < min_bidirectional_recording_fraction:
        return "reject: recording bidirectionality"
    return "candidate"


def audit_case(
    root: Path,
    holdout: str,
    target_mode: str,
    *,
    min_centered_delta: float,
    min_target_improvement: float,
    min_bidirectional_recording_fraction: float,
) -> dict:
    true_path = prediction_path(root, holdout, "none")
    shuffle_path = prediction_path(root, holdout, "within_recording_shuffle")
    true_rows = read_jsonl(true_path)
    shuffle_rows = read_jsonl(shuffle_path)
    pairs = paired_rows(true_rows, shuffle_rows)
    labels = np.asarray([int(true["target"]) for true, _shuffle in pairs], dtype=np.int64)
    true_scores = np.asarray([float(true["logit"]) for true, _shuffle in pairs], dtype=np.float64)
    shuffle_scores = np.asarray([float(shuffle["logit"]) for _true, shuffle in pairs], dtype=np.float64)
    recording_ids = [str(true["recording_id"]) for true, _shuffle in pairs]
    true_class_delta = np.where(labels > 0, true_scores - shuffle_scores, shuffle_scores - true_scores)
    target0 = labels <= 0
    target1 = labels > 0
    true_metrics = metrics_from_prediction_rows(true_rows)
    shuffle_metrics = metrics_from_prediction_rows(shuffle_rows)
    rec_rows = recording_target_rows(true_scores, shuffle_scores, labels, recording_ids)
    bidirectional = recording_bidirectional_summary(rec_rows, min_target_improvement=min_target_improvement)
    row = {
        "holdout": holdout,
        "target_mode": target_mode,
        "n_trials": len(pairs),
        "true_centered_auc": true_metrics["centered_auc"],
        "shuffle_centered_auc": shuffle_metrics["centered_auc"],
        "centered_delta_vs_shuffle": true_metrics["centered_auc"] - shuffle_metrics["centered_auc"],
        "true_logit_centered_auc": centered_auc_from_scores(true_scores, labels, recording_ids),
        "shuffle_logit_centered_auc": centered_auc_from_scores(shuffle_scores, labels, recording_ids),
        "paired_improved_vs_shuffle": float(np.mean(true_class_delta > 0.0)),
        "target0_improved_vs_shuffle": float(np.mean(true_class_delta[target0] > 0.0)),
        "target1_improved_vs_shuffle": float(np.mean(true_class_delta[target1] > 0.0)),
        "mean_true_class_delta": float(np.mean(true_class_delta)),
        "recording_target_rows": rec_rows,
        "n_bidirectional_recordings": bidirectional["n_bidirectional_recordings"],
        "n_evaluable_recordings": bidirectional["n_evaluable_recordings"],
        "bidirectional_recording_fraction": bidirectional["bidirectional_recording_fraction"],
        "bidirectional_recordings": bidirectional["bidirectional_recordings"],
        "true_path": repo_relative(true_path),
        "shuffle_path": repo_relative(shuffle_path),
    }
    row["decision"] = gate_decision(
        row,
        min_centered_delta=min_centered_delta,
        min_target_improvement=min_target_improvement,
        min_bidirectional_recording_fraction=min_bidirectional_recording_fraction,
    )
    return row


def build_report(
    root: Path,
    *,
    cases: tuple[tuple[str, str], ...] = DEFAULT_CASES,
    min_centered_delta: float = 0.0,
    min_target_improvement: float = 0.55,
    min_bidirectional_recording_fraction: float = 0.75,
) -> dict:
    rows = [
        audit_case(
            root,
            holdout,
            target_mode,
            min_centered_delta=min_centered_delta,
            min_target_improvement=min_target_improvement,
            min_bidirectional_recording_fraction=min_bidirectional_recording_fraction,
        )
        for holdout, target_mode in cases
    ]
    candidates = [row for row in rows if row["decision"] == "candidate"]
    global_target_pass = [
        row for row in rows
        if row["target0_improved_vs_shuffle"] >= min_target_improvement
        and row["target1_improved_vs_shuffle"] >= min_target_improvement
    ]
    return {
        "root": repo_relative(root),
        "thresholds": {
            "min_centered_delta": min_centered_delta,
            "min_target_improvement": min_target_improvement,
            "min_bidirectional_recording_fraction": min_bidirectional_recording_fraction,
        },
        "summary": {
            "decision": (
                "fixed_broad_family_prediction_gate_candidate"
                if candidates else "no_fixed_broad_family_prediction_gate_candidate"
            ),
            "n_cases": len(rows),
            "n_candidates": len(candidates),
            "candidate_holdouts": [row["holdout"] for row in candidates],
            "n_global_target_pass": len(global_target_pass),
            "n_positive_centered_delta": sum(row["centered_delta_vs_shuffle"] > 0.0 for row in rows),
            "paid_gpu_trigger": False,
            "next_action": (
                "Package the fixed-feature cloud demo around the candidate holdout(s), and keep the transformer/foundation-model claim separate."
                if candidates
                else "Do not claim the fixed-feature cloud demo clears the strict prediction gate."
            ),
        },
        "rows": rows,
    }


def render_markdown(report: dict) -> str:
    summary = report["summary"]
    lines = [
        "# Fixed Broad-Family Train Arm Prediction Gate",
        "",
        "Trial-paired true-vs-shuffled anatomy gate for the fixed broad-family RunPod prediction files.",
        "",
        f"- decision: `{summary['decision']}`",
        f"- candidates: `{summary['n_candidates']}/{summary['n_cases']}`",
        f"- candidate holdouts: `{', '.join(summary['candidate_holdouts']) or '<none>'}`",
        f"- global target pass: `{summary['n_global_target_pass']}/{summary['n_cases']}`",
        f"- positive centered-delta cases: `{summary['n_positive_centered_delta']}/{summary['n_cases']}`",
        f"- paid GPU trigger: `{summary['paid_gpu_trigger']}`",
        f"- next action: {summary['next_action']}",
        "",
        "| holdout | target | delta AUC | target0 | target1 | bidir recs | decision |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for row in report["rows"]:
        lines.append(
            f"| {row['holdout']} | {row['target_mode']} | "
            f"{row['centered_delta_vs_shuffle']:+.4f} | "
            f"{row['target0_improved_vs_shuffle']:.3f} | "
            f"{row['target1_improved_vs_shuffle']:.3f} | "
            f"{row['n_bidirectional_recordings']}/{row['n_evaluable_recordings']} | "
            f"{row['decision']} |"
        )
    lines += ["", "## Recording Rows", ""]
    for row in report["rows"]:
        lines += [
            f"### {row['holdout']}",
            "",
            "| recording | trials | target0 | target1 | improved | mean true-class delta |",
            "|---|---:|---:|---:|---:|---:|",
        ]
        for rec in row["recording_target_rows"]:
            lines.append(
                f"| {rec['recording']} | {rec['n_trials']} | "
                f"{rec['target0_improved']:.3f} | {rec['target1_improved']:.3f} | "
                f"{rec['improved_fraction']:.3f} | {rec['mean_true_class_delta']:+.4f} |"
            )
        lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=REPO_ROOT / "runs/fixed_broad_family_train_arm_panel_runpod")
    parser.add_argument("--min-centered-delta", type=float, default=0.0)
    parser.add_argument("--min-target-improvement", type=float, default=0.55)
    parser.add_argument("--min-bidirectional-recording-fraction", type=float, default=0.75)
    parser.add_argument("--out-json", type=Path, default=REPO_ROOT / "docs/fixed_broad_family_train_arm_prediction_gate.json")
    parser.add_argument("--out-md", type=Path, default=REPO_ROOT / "docs/fixed_broad_family_train_arm_prediction_gate.md")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(
        args.root,
        min_centered_delta=args.min_centered_delta,
        min_target_improvement=args.min_target_improvement,
        min_bidirectional_recording_fraction=args.min_bidirectional_recording_fraction,
    )
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text(render_markdown(report))
    print(f"wrote {args.out_json}")
    print(f"wrote {args.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
