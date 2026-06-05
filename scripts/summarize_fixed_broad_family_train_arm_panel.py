"""Summarize local fixed broad-family train-arm runs."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CASES = (
    ("CSHL045", "post_error_response_extreme_25_75_le_1"),
    ("NR_0019", "post_error_response_extreme_33_67_le_1"),
)


def repo_relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def load_summary(root: Path, holdout: str, control: str) -> dict:
    run_dir = root / f"holdout_{holdout}" / f"fixed_broad_family_count_{control}_seed0"
    summary_path = run_dir / "fixed_family_summary.json"
    if summary_path.exists():
        payload = json.loads(summary_path.read_text())
        payload["path"] = repo_relative(summary_path)
        return payload
    prediction_path = run_dir / "eval_predictions.jsonl"
    rows = [json.loads(line) for line in prediction_path.read_text().splitlines() if line.strip()]
    metrics = metrics_from_prediction_rows(rows)
    return {
        "family": "broad_named_anatomy",
        "feature_mode": "recording_centered",
        "n_eval": metrics["n"],
        "eval_auc": metrics["auc"],
        "eval_centered_auc": metrics["centered_auc"],
        "path": repo_relative(prediction_path),
    }


def auc(scores: np.ndarray, labels: np.ndarray) -> float:
    pos = scores[labels == 1]
    neg = scores[labels == 0]
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    n_pos, n_neg = len(pos), len(neg)
    all_scores = np.concatenate([pos, neg])
    ranks = np.argsort(np.argsort(all_scores)) + 1
    sum_pos_ranks = ranks[:n_pos].sum()
    return float((sum_pos_ranks - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg))


def metrics_from_prediction_rows(rows: list[dict]) -> dict:
    probs = np.asarray([float(row["prob"]) for row in rows], dtype=np.float64)
    labels = np.asarray([int(row["target"]) for row in rows], dtype=np.int64)
    centered = probs.copy()
    recording_ids = [str(row["recording_id"]) for row in rows]
    for recording_id in sorted(set(recording_ids)):
        mask = np.asarray([value == recording_id for value in recording_ids], dtype=bool)
        centered[mask] -= centered[mask].mean()
    return {
        "n": len(rows),
        "auc": auc(probs, labels),
        "centered_auc": auc(centered, labels),
    }


def build_report(root: Path, cases: tuple[tuple[str, str], ...] = DEFAULT_CASES) -> dict:
    rows = []
    for holdout, target_mode in cases:
        true = load_summary(root, holdout, "none")
        shuffle = load_summary(root, holdout, "within_recording_shuffle")
        rows.append({
            "holdout": holdout,
            "target_mode": target_mode,
            "family": true["family"],
            "feature_mode": true["feature_mode"],
            "n_eval": true["n_eval"],
            "true_centered_auc": true["eval_centered_auc"],
            "shuffle_centered_auc": shuffle["eval_centered_auc"],
            "centered_delta_vs_shuffle": true["eval_centered_auc"] - shuffle["eval_centered_auc"],
            "true_auc": true["eval_auc"],
            "shuffle_auc": shuffle["eval_auc"],
            "auc_delta_vs_shuffle": true["eval_auc"] - shuffle["eval_auc"],
            "true_path": true["path"],
            "shuffle_path": shuffle["path"],
        })
    positive = [row for row in rows if row["centered_delta_vs_shuffle"] > 0.0]
    is_runpod = "runpod" in str(root).lower()
    return {
        "root": repo_relative(root),
        "summary": {
            "decision": (
                (
                    "fixed_broad_family_train_arm_runpod_candidate"
                    if is_runpod
                    else "fixed_broad_family_train_arm_local_candidate"
                )
                if len(positive) == len(rows) and rows
                else "no_fixed_broad_family_train_arm_local_candidate"
            ),
            "n_cases": len(rows),
            "n_positive_centered_delta": len(positive),
            "paid_gpu_trigger": False,
            "next_action": (
                (
                    "Package this as bounded cloud fixed-feature train-path evidence, then decide whether the remaining goal requires a transformer/foundation-model mechanism."
                    if is_runpod
                    else "Run the bounded RunPod preflight for this exact fixed-family arm, then launch one low-cost true/shuffle panel only if cost and zero-pod checks pass."
                )
                if len(positive) == len(rows) and rows
                else "Do not launch a fixed-family GPU panel; inspect local train-arm mismatch first."
            ),
        },
        "rows": rows,
    }


def render_markdown(report: dict) -> str:
    summary = report["summary"]
    panel_label = "RunPod" if "runpod" in str(report["root"]).lower() else "Local"
    lines = [
        f"# Fixed Broad-Family Train Arm {panel_label} Panel",
        "",
        f"{panel_label} `train.py --arm fixed_broad_family_count` panel for the two response-extreme demo cases.",
        "",
        f"- decision: `{summary['decision']}`",
        f"- positive centered-delta cases: `{summary['n_positive_centered_delta']}/{summary['n_cases']}`",
        f"- paid GPU trigger: `{summary['paid_gpu_trigger']}`",
        f"- next action: {summary['next_action']}",
        "",
        "| holdout | target | family | feature | n eval | true centered AUC | shuffle centered AUC | delta |",
        "|---|---|---|---|---:|---:|---:|---:|",
    ]
    for row in report["rows"]:
        lines.append(
            f"| {row['holdout']} | {row['target_mode']} | {row['family']} | {row['feature_mode']} | "
            f"{row['n_eval']} | {row['true_centered_auc']:.4f} | {row['shuffle_centered_auc']:.4f} | "
            f"{row['centered_delta_vs_shuffle']:+.4f} |"
        )
    lines += ["", "## Run Artifacts", ""]
    for row in report["rows"]:
        lines.append(f"- {row['holdout']} true: `{row['true_path']}`")
        lines.append(f"- {row['holdout']} shuffle: `{row['shuffle_path']}`")
    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=REPO_ROOT / "runs/local_fixed_broad_family_count_panel")
    parser.add_argument("--out-json", type=Path, default=REPO_ROOT / "docs/fixed_broad_family_train_arm_local_panel.json")
    parser.add_argument("--out-md", type=Path, default=REPO_ROOT / "docs/fixed_broad_family_train_arm_local_panel.md")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(args.root)
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text(render_markdown(report))
    print(f"wrote {args.out_json}")
    print(f"wrote {args.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
