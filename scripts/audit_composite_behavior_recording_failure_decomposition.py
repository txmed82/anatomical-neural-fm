"""Decompose recording-level failures for the composite behavior near miss."""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
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


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def summarize_case(
    *,
    seeds: list[int],
    case: dict,
    min_target_improvement: float,
) -> dict:
    seed_rows = [load_case_row(seed, case) for seed in seeds]
    by_recording: dict[str, list[dict]] = defaultdict(list)
    for row in seed_rows:
        for rec_row in row.get("recording_target_rows", []):
            by_recording[rec_row["recording"]].append(rec_row | {"seed": row["seed"]})

    recording_rows = []
    for recording, rows in sorted(by_recording.items()):
        bidir_rows = [
            row for row in rows
            if (
                row["target0_improved"] >= min_target_improvement
                and row["target1_improved"] >= min_target_improvement
            )
        ]
        target0_pass = [row for row in rows if row["target0_improved"] >= min_target_improvement]
        target1_pass = [row for row in rows if row["target1_improved"] >= min_target_improvement]
        recording_rows.append({
            "recording": recording,
            "n_seeds": len(rows),
            "n_bidirectional_seeds": len(bidir_rows),
            "n_target0_pass_seeds": len(target0_pass),
            "n_target1_pass_seeds": len(target1_pass),
            "mean_target0_improved": _mean([row["target0_improved"] for row in rows]),
            "mean_target1_improved": _mean([row["target1_improved"] for row in rows]),
            "min_target0_improved": min(row["target0_improved"] for row in rows),
            "min_target1_improved": min(row["target1_improved"] for row in rows),
            "mean_true_class_delta": _mean([row["mean_true_class_delta"] for row in rows]),
            "mean_improved_fraction": _mean([row["improved_fraction"] for row in rows]),
            "mean_trials": _mean([row["n_trials"] for row in rows]),
        })
    stable_recordings = [
        row for row in recording_rows
        if row["n_bidirectional_seeds"] == row["n_seeds"]
    ]
    weak_recordings = [
        row for row in recording_rows
        if row["n_bidirectional_seeds"] < row["n_seeds"]
    ]
    weakest = sorted(
        recording_rows,
        key=lambda row: (
            row["n_bidirectional_seeds"],
            min(row["mean_target0_improved"], row["mean_target1_improved"]),
            row["mean_true_class_delta"],
        ),
    )
    return {
        "target_mode": case["target_mode"],
        "family": case["family"],
        "holdout": case["holdout"],
        "n_seeds": len(seeds),
        "n_recordings": len(recording_rows),
        "n_stable_bidirectional_recordings": len(stable_recordings),
        "n_unstable_recordings": len(weak_recordings),
        "mean_bidirectional_seed_fraction": _mean([
            row["n_bidirectional_seeds"] / row["n_seeds"] for row in recording_rows
        ]),
        "min_recording_bidirectional_seed_fraction": min(
            (row["n_bidirectional_seeds"] / row["n_seeds"] for row in recording_rows),
            default=0.0,
        ),
        "recording_rows": recording_rows,
        "weakest_recordings": weakest[:8],
        "seed_rows": [
            {
                "seed": row["seed"],
                "decision": row["decision"],
                "n_bidirectional_recordings": row["n_bidirectional_recordings"],
                "n_recordings": row["n_recordings"],
                "centered_delta_vs_shuffle": row["centered_delta_vs_shuffle"],
                "centered_delta_vs_total": row["centered_delta_vs_total"],
            }
            for row in seed_rows
        ],
    }


def build_report(
    *,
    seeds: list[int] | None = None,
    cases: tuple[dict, ...] = DEFAULT_CASES,
    min_target_improvement: float = 0.55,
) -> dict:
    seeds = list(range(5)) if seeds is None else seeds
    rows = [
        summarize_case(
            seeds=seeds,
            case=case,
            min_target_improvement=min_target_improvement,
        )
        for case in cases
    ]
    return {
        "cases": list(cases),
        "thresholds": {
            "seeds": seeds,
            "min_target_improvement": min_target_improvement,
        },
        "summary": {
            "decision": "composite_behavior_recording_bidirectionality_failure",
            "n_cases": len(rows),
            "n_recordings": sum(row["n_recordings"] for row in rows),
            "n_stable_bidirectional_recordings": sum(row["n_stable_bidirectional_recordings"] for row in rows),
            "n_unstable_recordings": sum(row["n_unstable_recordings"] for row in rows),
            "min_recording_bidirectional_seed_fraction": min(
                (row["min_recording_bidirectional_seed_fraction"] for row in rows),
                default=0.0,
            ),
            "gpu_training_ready": False,
            "next_action": (
                "Do not train: the composite near miss is limited by unstable "
                "same-recording target-class support, not by ridge regularization."
            ),
        },
        "rows": rows,
    }


def render_markdown(report: dict) -> str:
    summary = report["summary"]
    lines = [
        "# Composite Behavior Recording Failure Decomposition",
        "",
        (
            "Decomposes the projected post-error fast-response broad-anatomy near miss "
            "into per-recording target-class support across shuffle seeds."
        ),
        "",
        f"- cases: `{summary['n_cases']}`",
        f"- recordings: `{summary['n_recordings']}`",
        f"- stable bidirectional recordings: `{summary['n_stable_bidirectional_recordings']}`",
        f"- unstable recordings: `{summary['n_unstable_recordings']}`",
        (
            "- min recording bidirectional seed fraction: "
            f"`{summary['min_recording_bidirectional_seed_fraction']:.3f}`"
        ),
        f"- decision: `{summary['decision']}`",
        f"- gpu training ready: `{summary['gpu_training_ready']}`",
        "",
    ]
    for case in report["rows"]:
        lines += [
            f"## {case['holdout']}",
            "",
            f"- stable bidirectional recordings: `{case['n_stable_bidirectional_recordings']}/{case['n_recordings']}`",
            f"- mean bidirectional seed fraction: `{case['mean_bidirectional_seed_fraction']:.3f}`",
            "",
            "| recording | bidir seeds | target0 seeds | target1 seeds | mean target0 | mean target1 | min target0 | min target1 | mean delta | trials |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
        for row in case["weakest_recordings"]:
            lines.append(
                f"| {row['recording']} | {row['n_bidirectional_seeds']}/{row['n_seeds']} | "
                f"{row['n_target0_pass_seeds']}/{row['n_seeds']} | "
                f"{row['n_target1_pass_seeds']}/{row['n_seeds']} | "
                f"{row['mean_target0_improved']:.3f} | {row['mean_target1_improved']:.3f} | "
                f"{row['min_target0_improved']:.3f} | {row['min_target1_improved']:.3f} | "
                f"{row['mean_true_class_delta']:+.4f} | {row['mean_trials']:.1f} |"
            )
        lines.append("")
    lines += [
        "## Decision",
        "",
        summary["next_action"],
        "",
    ]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", nargs="*", type=int, default=list(range(5)))
    parser.add_argument("--min-target-improvement", type=float, default=0.55)
    parser.add_argument(
        "--out-json",
        type=Path,
        default=REPO_ROOT / "docs/composite_behavior_recording_failure_decomposition.json",
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=REPO_ROOT / "docs/composite_behavior_recording_failure_decomposition.md",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(seeds=args.seeds, min_target_improvement=args.min_target_improvement)
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text(render_markdown(report))
    print(f"wrote {args.out_json}")
    print(f"wrote {args.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
