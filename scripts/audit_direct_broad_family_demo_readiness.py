"""Assess whether the direct broad-family signal is demo-ready.

This is a synthesis audit after the response-extreme A100 pilot failed. It
separates a narrow model-free anatomical readout claim from a trained neural
model claim, so the roadmap does not accidentally treat the local trigger as a
GPU-ready result.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def load_a100_result(path: Path) -> dict:
    text = path.read_text()
    rows = []
    for line in text.splitlines():
        if not line.startswith("| "):
            continue
        parts = [part.strip() for part in line.strip().strip("|").split("|")]
        if len(parts) != 6 or parts[0] not in {"CSHL045", "NR_0019"}:
            continue
        rows.append({
            "holdout": parts[0],
            "arm": parts[1],
            "mean_delta_vs_shared": float(parts[4]),
        })
    region_rows = [row for row in rows if row["arm"] == "region_only"]
    true_positive = sum(row["mean_delta_vs_shared"] > 0.0 for row in region_rows)
    return {
        "summary": {
            "decision": "negative_training_pilot" if region_rows and true_positive == 0 else "training_pilot_needs_review",
            "n_true_positive": true_positive,
            "n_cases": len(region_rows),
        }
    }


def robust_rows(seed_sensitivity: dict) -> list[dict]:
    return list(seed_sensitivity.get("robust_response_extreme_seed_candidates", []))


def summarize(
    *,
    seed_sensitivity: dict,
    a100_result: dict,
    training_aligned: dict,
) -> dict:
    robust = robust_rows(seed_sensitivity)
    a100_summary = a100_result.get("summary", {})
    aligned_summary = training_aligned.get("summary", {})
    local_demo_rows = [
        row for row in robust
        if row.get("family") == "broad_named_anatomy"
        and row.get("n_candidate_seeds") == row.get("n_seeds")
        and row.get("min_bidirectional_recordings", 0) >= 3
    ]
    trained_negative = (
        a100_summary.get("decision") == "negative_training_pilot"
        and int(a100_summary.get("n_true_positive", -1)) == 0
    )
    aligned_negative = aligned_summary.get("decision") == "no_training_aligned_true_region_advantage"
    model_free_demo_ready = bool(local_demo_rows)
    trained_model_demo_ready = model_free_demo_ready and not trained_negative and not aligned_negative
    if trained_model_demo_ready:
        decision = "trained_model_demo_candidate"
    elif model_free_demo_ready and trained_negative and aligned_negative:
        decision = "model_free_demo_only"
    elif model_free_demo_ready:
        decision = "model_free_demo_needs_training_alignment_review"
    else:
        decision = "no_direct_broad_family_demo_candidate"
    return {
        "n_robust_local_rows": len(robust),
        "n_model_free_demo_rows": len(local_demo_rows),
        "model_free_demo_ready": model_free_demo_ready,
        "trained_model_demo_ready": trained_model_demo_ready,
        "trained_negative": trained_negative,
        "training_aligned_negative": aligned_negative,
        "decision": decision,
        "next_action": (
            "Package the result as a narrow model-free cross-animal anatomical readout, "
            "or implement a direct fixed broad-family-count model arm before any new GPU run."
            if decision == "model_free_demo_only"
            else "Continue local target/control redesign before paid training."
        ),
    }


def build_report(
    *,
    seed_sensitivity: dict,
    a100_result: dict,
    training_aligned: dict,
) -> dict:
    summary = summarize(
        seed_sensitivity=seed_sensitivity,
        a100_result=a100_result,
        training_aligned=training_aligned,
    )
    robust = robust_rows(seed_sensitivity)
    return {
        "summary": summary,
        "local_model_free_rows": [
            {
                "holdout": row["holdout"],
                "target_mode": row["target_mode"],
                "family": row["family"],
                "candidate_seeds": row["n_candidate_seeds"],
                "n_seeds": row["n_seeds"],
                "mean_delta_vs_shuffle": row["mean_centered_delta_vs_shuffle"],
                "mean_delta_vs_total": row["mean_centered_delta_vs_total"],
                "min_bidirectional_recordings": row["min_bidirectional_recordings"],
                "max_bidirectional_recordings": row["max_bidirectional_recordings"],
                "mean_target0": row["mean_target0"],
                "mean_target1": row["mean_target1"],
            }
            for row in robust
        ],
        "negative_training_evidence": {
            "a100_decision": a100_result.get("summary", {}).get("decision"),
            "a100_true_positive": (
                f"{a100_result.get('summary', {}).get('n_true_positive')}/"
                f"{a100_result.get('summary', {}).get('n_cases')}"
            ),
            "training_aligned_decision": training_aligned.get("summary", {}).get("decision"),
            "training_aligned_paid_gpu_trigger": training_aligned.get("summary", {}).get("paid_gpu_trigger"),
        },
        "interpretation": [
            "The fixed broad_named_anatomy aggregate remains the only positive response-extreme evidence.",
            "The learned parent-region embedding pilot and the shared parent-region ridge readout are both negative.",
            "A demo can currently claim only a narrow model-free cross-animal anatomical readout, not a trained anatomical foundation-model transfer signal.",
        ],
    }


def render_markdown(report: dict) -> str:
    summary = report["summary"]
    negative = report["negative_training_evidence"]
    lines = [
        "# Direct Broad-Family Demo Readiness",
        "",
        "Synthesis of the response-extreme fixed-family local trigger after the negative A100 pilot.",
        "",
        f"- decision: `{summary['decision']}`",
        f"- model-free demo ready: `{summary['model_free_demo_ready']}`",
        f"- trained-model demo ready: `{summary['trained_model_demo_ready']}`",
        f"- robust local rows: `{summary['n_robust_local_rows']}`",
        f"- model-free demo rows: `{summary['n_model_free_demo_rows']}`",
        f"- A100 decision: `{negative['a100_decision']}` ({negative['a100_true_positive']} true-positive cases)",
        f"- training-aligned readout: `{negative['training_aligned_decision']}`",
        f"- next action: {summary['next_action']}",
        "",
        "| holdout | target | family | candidate seeds | delta shuffle | delta total | targets | bidir range |",
        "|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in report["local_model_free_rows"]:
        lines.append(
            f"| {row['holdout']} | {row['target_mode']} | {row['family']} | "
            f"{row['candidate_seeds']}/{row['n_seeds']} | "
            f"{row['mean_delta_vs_shuffle']:+.4f} | {row['mean_delta_vs_total']:+.4f} | "
            f"{row['mean_target0']:.3f}/{row['mean_target1']:.3f} | "
            f"{row['min_bidirectional_recordings']}-{row['max_bidirectional_recordings']} |"
        )
    lines += [
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {item}" for item in report["interpretation"])
    lines += [
        "",
        "## Decision",
        "",
        summary["next_action"],
        "",
    ]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--seed-sensitivity",
        type=Path,
        default=REPO_ROOT / "docs/composite_behavior_response_extreme_seed_sensitivity.json",
    )
    parser.add_argument(
        "--a100-result",
        type=Path,
        default=REPO_ROOT / "docs/response_extreme_trigger_a100_results.md",
    )
    parser.add_argument(
        "--training-aligned",
        type=Path,
        default=REPO_ROOT / "docs/response_extreme_training_aligned_readout.json",
    )
    parser.add_argument(
        "--out-json",
        type=Path,
        default=REPO_ROOT / "docs/direct_broad_family_demo_readiness.json",
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=REPO_ROOT / "docs/direct_broad_family_demo_readiness.md",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(
        seed_sensitivity=load_json(args.seed_sensitivity),
        a100_result=load_a100_result(args.a100_result),
        training_aligned=load_json(args.training_aligned),
    )
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text(render_markdown(report) + "\n")
    print(f"wrote {args.out_json}")
    print(f"wrote {args.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
