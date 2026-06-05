"""Aggregate shuffle-seed sensitivity for composite behavior target candidates."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_CASES = (
    {
        "target_mode": "post_error_fast_response_le_1",
        "family": "broad_named_anatomy",
        "holdout": "CSHL045",
    },
    {
        "target_mode": "post_error_fast_response_le_1",
        "family": "broad_named_anatomy",
        "holdout": "NR_0019",
    },
)


def seed_path(seed: int) -> str:
    if seed == 0:
        return "docs/composite_behavior_target_family_gate_projected_hdf5.json"
    return f"docs/composite_behavior_target_family_gate_projected_hdf5_seed_{seed}.json"


def load_case_row(seed: int, case: dict) -> dict:
    rel_path = seed_path(seed)
    payload = json.loads((REPO_ROOT / rel_path).read_text())
    for row in payload.get("rows", []):
        if (
            row.get("target_mode") == case["target_mode"]
            and row.get("family") == case["family"]
            and row.get("holdout") == case["holdout"]
        ):
            return row | {"seed": seed, "path": rel_path}
    raise KeyError(f"case row not found for seed={seed}: {case}")


def summarize_case(
    *,
    seeds: list[int],
    case: dict,
    min_positive_seed_fraction: float,
) -> dict:
    seed_rows = [load_case_row(seed, case) for seed in seeds]
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
        "family": case["family"],
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
        "robust_composite_behavior_seed_candidate": robust,
        "seed_rows": seed_rows,
    }


def build_report(
    *,
    seeds: list[int] | None = None,
    cases: tuple[dict, ...] = DEFAULT_CASES,
    min_positive_seed_fraction: float = 0.8,
) -> dict:
    seeds = list(range(5)) if seeds is None else seeds
    rows = [
        summarize_case(
            seeds=seeds,
            case=case,
            min_positive_seed_fraction=min_positive_seed_fraction,
        )
        for case in cases
    ]
    robust = [row for row in rows if row["robust_composite_behavior_seed_candidate"]]
    return {
        "cases": list(cases),
        "thresholds": {
            "seeds": seeds,
            "min_positive_seed_fraction": min_positive_seed_fraction,
            "strict_candidate_required_all_seeds": True,
        },
        "summary": {
            "decision": (
                "composite_behavior_seed_candidate"
                if robust else
                "no_composite_behavior_seed_candidate"
            ),
            "n_cases": len(rows),
            "n_robust_composite_behavior_seed_candidates": len(robust),
            "max_positive_shuffle_delta_fraction": max(
                (row["positive_shuffle_delta_fraction"] for row in rows),
                default=0.0,
            ),
            "max_candidate_seed_fraction": max(
                (row["n_candidate_seeds"] / row["n_seeds"] for row in rows),
                default=0.0,
            ),
            "gpu_training_ready": False,
            "next_action": (
                "Do not train: the composite behavior candidates do not remain strict "
                "candidates across shuffle seeds."
                if not robust
                else "Run an independent manifest or pre-registered replication before GPU training."
            ),
        },
        "rows": rows,
        "robust_composite_behavior_seed_candidates": robust,
    }


def render_markdown(report: dict) -> str:
    summary = report["summary"]
    lines = [
        "# Composite Behavior Target Seed Sensitivity",
        "",
        (
            "Reruns the projected-panel composite behavior candidates across "
            "within-recording shuffle seeds."
        ),
        "",
        f"- cases: `{summary['n_cases']}`",
        f"- robust composite behavior seed candidates: `{summary['n_robust_composite_behavior_seed_candidates']}`",
        f"- max positive shuffle-delta fraction: `{summary['max_positive_shuffle_delta_fraction']:.3f}`",
        f"- max candidate seed fraction: `{summary['max_candidate_seed_fraction']:.3f}`",
        f"- decision: `{summary['decision']}`",
        f"- gpu training ready: `{summary['gpu_training_ready']}`",
        "",
        "| target | family | holdout | positive seeds | candidate seeds | mean delta shuffle | min/max delta shuffle | mean delta total | mean targets | bidir range |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["rows"]:
        lines.append(
            f"| {row['target_mode']} | {row['family']} | {row['holdout']} | "
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
        default=REPO_ROOT / "docs/composite_behavior_target_seed_sensitivity.json",
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=REPO_ROOT / "docs/composite_behavior_target_seed_sensitivity.md",
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
