"""Aggregate shuffle-seed sensitivity for extreme-quantile region candidates."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

CASE = {
    "target_mode": "response_latency_extreme",
    "region": "root",
    "holdout": "CSH_ZAD_019",
}


def seed_path(seed: int) -> str:
    if seed == 0:
        return "docs/extreme_quantile_region_specificity.json"
    return f"docs/extreme_quantile_region_specificity_seed_{seed}.json"


def load_case_row(seed: int, case: dict = CASE) -> dict:
    rel_path = seed_path(seed)
    payload = json.loads((REPO_ROOT / rel_path).read_text())
    for row in payload.get("rows", []):
        if (
            row.get("target_mode") == case["target_mode"]
            and row.get("region") == case["region"]
            and row.get("holdout") == case["holdout"]
        ):
            return row | {"seed": seed, "path": rel_path}
    raise KeyError(f"case row not found for seed={seed}: {case}")


def summarize_case(seeds: list[int], *, min_positive_seed_fraction: float) -> dict:
    seed_rows = [load_case_row(seed) for seed in seeds]
    positive_shuffle = [row for row in seed_rows if row["centered_delta_vs_shuffle"] >= 0.0]
    candidates = [row for row in seed_rows if row["decision"] == "candidate"]
    mean_shuffle = sum(row["centered_delta_vs_shuffle"] for row in seed_rows) / len(seed_rows)
    positive_fraction = len(positive_shuffle) / len(seed_rows)
    robust = (
        positive_fraction >= min_positive_seed_fraction
        and mean_shuffle >= 0.0
        and len(candidates) == len(seed_rows)
    )
    return {
        "target_mode": CASE["target_mode"],
        "region": CASE["region"],
        "holdout": CASE["holdout"],
        "n_seeds": len(seed_rows),
        "n_positive_shuffle_delta_seeds": len(positive_shuffle),
        "positive_shuffle_delta_fraction": positive_fraction,
        "n_candidate_seeds": len(candidates),
        "mean_centered_delta_vs_shuffle": mean_shuffle,
        "min_centered_delta_vs_shuffle": min(row["centered_delta_vs_shuffle"] for row in seed_rows),
        "max_centered_delta_vs_shuffle": max(row["centered_delta_vs_shuffle"] for row in seed_rows),
        "mean_centered_delta_vs_total": sum(row["centered_delta_vs_total"] for row in seed_rows) / len(seed_rows),
        "mean_target0": sum(row["target0_improved_vs_shuffle"] for row in seed_rows) / len(seed_rows),
        "mean_target1": sum(row["target1_improved_vs_shuffle"] for row in seed_rows) / len(seed_rows),
        "min_bidirectional_recordings": min(row["n_bidirectional_recordings"] for row in seed_rows),
        "max_bidirectional_recordings": max(row["n_bidirectional_recordings"] for row in seed_rows),
        "robust_region_seed_candidate": robust,
        "seed_rows": seed_rows,
    }


def build_report(*, seeds: list[int] | None = None, min_positive_seed_fraction: float = 0.8) -> dict:
    seeds = list(range(5)) if seeds is None else seeds
    row = summarize_case(seeds, min_positive_seed_fraction=min_positive_seed_fraction)
    robust = [row] if row["robust_region_seed_candidate"] else []
    return {
        "case": CASE,
        "thresholds": {
            "seeds": seeds,
            "min_positive_seed_fraction": min_positive_seed_fraction,
        },
        "summary": {
            "decision": (
                "extreme_quantile_region_seed_candidate"
                if robust else
                "no_extreme_quantile_region_seed_candidate"
            ),
            "n_cases": 1,
            "n_robust_region_seed_candidates": len(robust),
            "max_positive_shuffle_delta_fraction": row["positive_shuffle_delta_fraction"],
            "gpu_training_ready": False,
            "next_action": (
                "Do not train: the coarse root-region row beats shuffle across seeds, "
                "but target and recording bidirectionality do not remain stable."
                if not robust
                else "Run anatomical specificity validation before GPU training."
            ),
        },
        "rows": [row],
        "robust_region_seed_candidates": robust,
    }


def render_markdown(report: dict) -> str:
    summary = report["summary"]
    lines = [
        "# Extreme-Quantile Region Seed Sensitivity",
        "",
        "Reruns the strict parent-region candidate across multiple within-recording shuffle seeds.",
        "",
        f"- cases: `{summary['n_cases']}`",
        f"- robust region-seed candidates: `{summary['n_robust_region_seed_candidates']}`",
        f"- max positive shuffle-delta fraction: `{summary['max_positive_shuffle_delta_fraction']:.3f}`",
        f"- decision: `{summary['decision']}`",
        "",
        "| target | region | holdout | positive seeds | candidate seeds | mean delta shuffle | min/max delta shuffle | mean delta total | mean targets | bidir range |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["rows"]:
        lines.append(
            f"| {row['target_mode']} | {row['region']} | {row['holdout']} | "
            f"{row['n_positive_shuffle_delta_seeds']}/{row['n_seeds']} | "
            f"{row['n_candidate_seeds']}/{row['n_seeds']} | "
            f"{row['mean_centered_delta_vs_shuffle']:+.4f} | "
            f"{row['min_centered_delta_vs_shuffle']:+.4f}/{row['max_centered_delta_vs_shuffle']:+.4f} | "
            f"{row['mean_centered_delta_vs_total']:+.4f} | "
            f"{row['mean_target0']:.3f}/{row['mean_target1']:.3f} | "
            f"{row['min_bidirectional_recordings']}-{row['max_bidirectional_recordings']} |"
        )
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
    parser.add_argument("--seeds", nargs="*", type=int, default=list(range(5)))
    parser.add_argument("--min-positive-seed-fraction", type=float, default=0.8)
    parser.add_argument(
        "--out-json",
        type=Path,
        default=REPO_ROOT / "docs/extreme_quantile_region_seed_sensitivity.json",
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=REPO_ROOT / "docs/extreme_quantile_region_seed_sensitivity.md",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(seeds=args.seeds, min_positive_seed_fraction=args.min_positive_seed_fraction)
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text(render_markdown(report))
    print(f"wrote {args.out_json}")
    print(f"wrote {args.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
