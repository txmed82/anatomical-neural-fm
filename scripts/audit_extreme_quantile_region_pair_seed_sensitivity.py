"""Aggregate shuffle-seed sensitivity for exploratory interpretable region pairs."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_CASES = [
    {
        "target_mode": "response_latency_extreme",
        "region_pair": "PRT+VP",
        "holdout": "CSH_ZAD_019",
    },
    {
        "target_mode": "response_latency_extreme",
        "region_pair": "cc+VP",
        "holdout": "CSH_ZAD_019",
    },
]


def seed_path(seed: int) -> str:
    if seed == 0:
        return "docs/extreme_quantile_interpretable_region_pair_scan.json"
    return f"docs/extreme_quantile_interpretable_region_pair_scan_seed_{seed}.json"


def load_case_row(case: dict, seed: int) -> dict:
    rel_path = seed_path(seed)
    payload = json.loads((REPO_ROOT / rel_path).read_text())
    for row in payload.get("rows", []):
        if (
            row.get("target_mode") == case["target_mode"]
            and row.get("region_pair") == case["region_pair"]
            and row.get("holdout") == case["holdout"]
        ):
            return row | {"seed": seed, "path": rel_path}
    raise KeyError(f"case row not found for seed={seed}: {case}")


def summarize_case(case: dict, seeds: list[int], *, min_positive_seed_fraction: float) -> dict:
    seed_rows = [load_case_row(case, seed) for seed in seeds]
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
        "target_mode": case["target_mode"],
        "region_pair": case["region_pair"],
        "holdout": case["holdout"],
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
        "robust_region_pair_seed_candidate": robust,
        "seed_rows": seed_rows,
    }


def build_report(
    *,
    cases: list[dict] = DEFAULT_CASES,
    seeds: list[int] | None = None,
    min_positive_seed_fraction: float = 0.8,
) -> dict:
    seeds = list(range(5)) if seeds is None else seeds
    rows = [
        summarize_case(case, seeds, min_positive_seed_fraction=min_positive_seed_fraction)
        for case in cases
    ]
    robust = [row for row in rows if row["robust_region_pair_seed_candidate"]]
    return {
        "cases": cases,
        "thresholds": {
            "seeds": seeds,
            "min_positive_seed_fraction": min_positive_seed_fraction,
        },
        "summary": {
            "decision": (
                "extreme_quantile_region_pair_seed_candidate"
                if robust else
                "no_extreme_quantile_region_pair_seed_candidate"
            ),
            "n_cases": len(rows),
            "n_robust_region_pair_seed_candidates": len(robust),
            "max_positive_shuffle_delta_fraction": max(
                (row["positive_shuffle_delta_fraction"] for row in rows),
                default=0.0,
            ),
            "gpu_training_ready": False,
            "next_action": (
                "Do not train: exploratory interpretable region-pair candidates do not "
                "remain strict candidates across shuffle seeds."
                if not robust
                else "Run prospective manifest validation before GPU training."
            ),
        },
        "rows": rows,
        "robust_region_pair_seed_candidates": robust,
    }


def render_markdown(report: dict) -> str:
    summary = report["summary"]
    lines = [
        "# Extreme-Quantile Region Pair Seed Sensitivity",
        "",
        "Reruns exploratory interpretable two-region pair candidates across shuffle seeds.",
        "",
        f"- cases: `{summary['n_cases']}`",
        f"- robust region-pair seed candidates: `{summary['n_robust_region_pair_seed_candidates']}`",
        f"- max positive shuffle-delta fraction: `{summary['max_positive_shuffle_delta_fraction']:.3f}`",
        f"- decision: `{summary['decision']}`",
        f"- gpu training ready: `{summary['gpu_training_ready']}`",
        "",
        "| target | pair | holdout | positive seeds | candidate seeds | mean delta shuffle | min/max delta shuffle | mean delta total | mean targets | bidir range |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["rows"]:
        lines.append(
            f"| {row['target_mode']} | {row['region_pair']} | {row['holdout']} | "
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
        default=REPO_ROOT / "docs/extreme_quantile_region_pair_seed_sensitivity.json",
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=REPO_ROOT / "docs/extreme_quantile_region_pair_seed_sensitivity.md",
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
