"""Summarize local fixed broad-family train-arm runs."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


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
    path = root / f"holdout_{holdout}" / f"fixed_broad_family_count_{control}_seed0" / "fixed_family_summary.json"
    payload = json.loads(path.read_text())
    payload["path"] = repo_relative(path)
    return payload


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
    return {
        "root": repo_relative(root),
        "summary": {
            "decision": (
                "fixed_broad_family_train_arm_local_candidate"
                if len(positive) == len(rows) and rows
                else "no_fixed_broad_family_train_arm_local_candidate"
            ),
            "n_cases": len(rows),
            "n_positive_centered_delta": len(positive),
            "paid_gpu_trigger": False,
            "next_action": (
                "Run the bounded RunPod preflight for this exact fixed-family arm, then launch one low-cost true/shuffle panel only if cost and zero-pod checks pass."
                if len(positive) == len(rows) and rows
                else "Do not launch a fixed-family GPU panel; inspect local train-arm mismatch first."
            ),
        },
        "rows": rows,
    }


def render_markdown(report: dict) -> str:
    summary = report["summary"]
    lines = [
        "# Fixed Broad-Family Train Arm Local Panel",
        "",
        "Local `train.py --arm fixed_broad_family_count` panel for the two response-extreme demo cases.",
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
