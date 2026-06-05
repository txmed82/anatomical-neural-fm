"""Aggregate cutoff sensitivity for the response-latency extreme candidate."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


DEFAULT_CUTOFFS = [
    {
        "label": "20/80",
        "low_quantile": 0.20,
        "high_quantile": 0.80,
        "paths": [f"docs/extreme_quantile_response_latency_20_80_seed_{seed}.json" for seed in range(5)],
    },
    {
        "label": "25/75",
        "low_quantile": 0.25,
        "high_quantile": 0.75,
        "paths": ["docs/extreme_quantile_target_family_gate.json"]
        + [f"docs/extreme_quantile_target_family_gate_seed_{seed}.json" for seed in range(1, 5)],
    },
    {
        "label": "30/70",
        "low_quantile": 0.30,
        "high_quantile": 0.70,
        "paths": [f"docs/extreme_quantile_response_latency_30_70_seed_{seed}.json" for seed in range(5)],
    },
]


CASE = {
    "target_mode": "response_latency_extreme",
    "family": "broad_named_anatomy",
    "holdout": "NR_0019",
}


def load_case_row(path: str, case: dict = CASE) -> dict:
    payload = json.loads((REPO_ROOT / path).read_text())
    for row in payload.get("rows", []):
        if (
            row.get("target_mode") == case["target_mode"]
            and row.get("family") == case["family"]
            and row.get("holdout") == case["holdout"]
        ):
            return row | {"path": path}
    raise KeyError(f"case row not found in {path}: {case}")


def summarize_cutoff(cutoff: dict, *, min_positive_seed_fraction: float) -> dict:
    seed_rows = [load_case_row(path) | {"seed": seed} for seed, path in enumerate(cutoff["paths"])]
    positive = [row for row in seed_rows if row["centered_delta_vs_shuffle"] >= 0.0]
    candidates = [row for row in seed_rows if row["decision"] == "candidate"]
    mean_shuffle = sum(row["centered_delta_vs_shuffle"] for row in seed_rows) / len(seed_rows)
    positive_fraction = len(positive) / len(seed_rows)
    robust = (
        positive_fraction >= min_positive_seed_fraction
        and len(candidates) == len(seed_rows)
        and mean_shuffle >= 0.0
    )
    return {
        "label": cutoff["label"],
        "low_quantile": cutoff["low_quantile"],
        "high_quantile": cutoff["high_quantile"],
        "n_seeds": len(seed_rows),
        "n_positive_shuffle_delta_seeds": len(positive),
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
        "robust_cutoff_candidate": robust,
        "seed_rows": seed_rows,
    }


def build_report(
    cutoffs: list[dict] = DEFAULT_CUTOFFS,
    *,
    min_positive_seed_fraction: float = 0.8,
) -> dict:
    rows = [
        summarize_cutoff(cutoff, min_positive_seed_fraction=min_positive_seed_fraction)
        for cutoff in cutoffs
    ]
    robust = [row for row in rows if row["robust_cutoff_candidate"]]
    best = max(
        rows,
        key=lambda row: (
            row["n_candidate_seeds"],
            row["positive_shuffle_delta_fraction"],
            row["mean_centered_delta_vs_shuffle"],
        ),
        default=None,
    )
    return {
        "case": CASE,
        "thresholds": {
            "min_positive_seed_fraction": min_positive_seed_fraction,
        },
        "summary": {
            "decision": (
                "extreme_quantile_cutoff_candidate"
                if robust else
                "no_extreme_quantile_cutoff_candidate"
            ),
            "n_cutoffs": len(rows),
            "n_robust_cutoff_candidates": len(robust),
            "best_cutoff": None if best is None else best["label"],
            "best_candidate_seeds": 0 if best is None else best["n_candidate_seeds"],
            "best_positive_shuffle_delta_fraction": 0.0 if best is None else best["positive_shuffle_delta_fraction"],
            "best_mean_centered_delta_vs_shuffle": 0.0 if best is None else best["mean_centered_delta_vs_shuffle"],
            "gpu_training_ready": False,
            "next_action": (
                "Do not train: cutoff changes do not make the extreme response-latency candidate "
                "robust to within-recording shuffled anatomy."
                if not robust
                else "Run independent manifest validation before GPU training."
            ),
        },
        "rows": rows,
        "robust_cutoff_candidates": robust,
    }


def render_markdown(report: dict) -> str:
    summary = report["summary"]
    case = report["case"]
    lines = [
        "# Extreme-Quantile Cutoff Sensitivity",
        "",
        (
            "Tests whether changing the response-latency extreme cutoff rescues the "
            "single-seed candidate across multiple within-recording shuffle seeds."
        ),
        "",
        f"- target: `{case['target_mode']}`",
        f"- family: `{case['family']}`",
        f"- holdout: `{case['holdout']}`",
        f"- cutoffs: `{summary['n_cutoffs']}`",
        f"- robust cutoff candidates: `{summary['n_robust_cutoff_candidates']}`",
        f"- best cutoff: `{summary['best_cutoff']}`",
        f"- decision: `{summary['decision']}`",
        "",
        "| cutoff | positive seeds | candidate seeds | mean delta shuffle | min/max delta shuffle | mean delta total | mean targets | bidir range |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["rows"]:
        lines.append(
            f"| {row['label']} | "
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
    parser.add_argument("--min-positive-seed-fraction", type=float, default=0.8)
    parser.add_argument(
        "--out-json",
        type=Path,
        default=REPO_ROOT / "docs/extreme_quantile_cutoff_sensitivity.json",
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=REPO_ROOT / "docs/extreme_quantile_cutoff_sensitivity.md",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(min_positive_seed_fraction=args.min_positive_seed_fraction)
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text(render_markdown(report))
    print(f"wrote {args.out_json}")
    print(f"wrote {args.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
