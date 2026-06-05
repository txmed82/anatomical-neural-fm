"""Summarize leave-subject-out model-free region audits."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_rows(input_dir: Path, pattern: str) -> list[dict]:
    rows = []
    for path in sorted(input_dir.glob(pattern)):
        data = json.loads(path.read_text())
        summary = data["summary"]
        paired = summary["paired_true_vs_shuffle"]
        rows.append({
            "source": path,
            "holdout": ",".join(data["holdout"]),
            "decision": summary["decision"],
            "true_centered_auc": summary["metrics"]["region_true"]["eval_centered_auc"],
            "shuffle_centered_auc": summary["metrics"]["region_shuffle"]["eval_centered_auc"],
            "delta_centered_auc": summary["deltas"]["true_minus_shuffle_centered_auc"],
            "paired_improved": paired["improved_fraction"],
            "target0_improved": paired["target0_improved_fraction"],
            "target1_improved": paired["target1_improved_fraction"],
            "positive_recordings": summary["recordings_positive_true_minus_shuffle"],
            "n_recordings": summary["n_recordings"],
            "recording_support_fraction": summary["recording_support_fraction"],
            "n_train_trials": data["n_train_trials"],
            "n_eval_trials": data["n_eval_trials"],
            "n_regions": data["n_regions"],
        })
    return rows


def summarize(rows: list[dict]) -> dict:
    candidates = [row for row in rows if row["decision"] == "model_free_anatomy_candidate"]
    positive_delta = [row for row in rows if row["delta_centered_auc"] > 0.0]
    mean_delta = (
        sum(row["delta_centered_auc"] for row in rows) / len(rows)
        if rows else 0.0
    )
    return {
        "n_holdouts": len(rows),
        "n_candidates": len(candidates),
        "candidate_holdouts": [row["holdout"] for row in candidates],
        "n_positive_delta_holdouts": len(positive_delta),
        "positive_delta_holdouts": [row["holdout"] for row in positive_delta],
        "mean_delta_centered_auc": mean_delta,
        "decision": (
            "model_free_panel_candidate"
            if candidates else "no_model_free_panel_signal"
        ),
    }


def render_markdown(report: dict) -> str:
    rows = report["rows"]
    summary = report["summary"]
    lines = [
        "# Matched Support80 Model-Free Panel Audit",
        "",
        (
            "Closed-form ridge classifier on trial-level parent-region spike counts, "
            "run leave-subject-out across the HDF5-confirmed matched support80 panel."
        ),
        "",
        f"- holdouts: `{summary['n_holdouts']}`",
        f"- candidates: `{summary['n_candidates']}`",
        f"- positive centered-delta holdouts: `{summary['n_positive_delta_holdouts']}/{summary['n_holdouts']}`",
        f"- mean true-minus-shuffle centered AUC: `{summary['mean_delta_centered_auc']:+.3f}`",
        f"- decision: `{summary['decision']}`",
        "",
        "| holdout | decision | true_centered | shuffle_centered | delta | paired | target0 | target1 | rec_support |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['holdout']} | {row['decision']} | "
            f"{row['true_centered_auc']:.3f} | {row['shuffle_centered_auc']:.3f} | "
            f"{row['delta_centered_auc']:+.3f} | {row['paired_improved']:.3f} | "
            f"{row['target0_improved']:.3f} | {row['target1_improved']:.3f} | "
            f"{row['positive_recordings']}/{row['n_recordings']} |"
        )
    lines += [
        "",
        (
            "Decision: do not promote this panel to a broad training sweep. "
            "Positive centered deltas are not bidirectional and not broadly supported "
            "across recordings."
        ),
        "",
    ]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--pattern", default="*_stimulus_side.json")
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument("--out-md", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows = load_rows(args.input_dir, args.pattern)
    report = {"summary": summarize(rows), "rows": [
        row | {"source": str(row["source"])} for row in rows
    ]}
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text(render_markdown(report))
    print(f"wrote {args.out_json}")
    print(f"wrote {args.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
