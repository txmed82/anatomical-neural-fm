"""Filter extreme-quantile region scan to interpretable anatomical labels."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

NON_SPECIFIC_REGIONS = frozenset({"root", "void"})


def is_interpretable_region(region: str, non_specific: set[str] | frozenset[str] = NON_SPECIFIC_REGIONS) -> bool:
    return str(region) not in non_specific


def summarize_rows(rows: list[dict], *, excluded_regions: set[str] | frozenset[str]) -> dict:
    kept = [row for row in rows if is_interpretable_region(row["region"], excluded_regions)]
    excluded = [row for row in rows if not is_interpretable_region(row["region"], excluded_regions)]
    candidates = [row for row in kept if row["decision"] == "candidate"]
    top_rows = sorted(
        kept,
        key=lambda row: (
            row["decision"] == "candidate",
            row["n_bidirectional_recordings"],
            row["bidirectional_recording_fraction"],
            row["centered_delta_vs_shuffle"],
            min(row["target0_improved_vs_shuffle"], row["target1_improved_vs_shuffle"]),
            row["eval_nonzero_fraction"],
        ),
        reverse=True,
    )
    excluded_candidate_rows = [
        {"target_mode": row["target_mode"], "region": row["region"], "holdout": row["holdout"]}
        for row in excluded
        if row["decision"] == "candidate"
    ]
    return {
        "n_input_rows": len(rows),
        "n_rows": len(kept),
        "n_excluded_rows": len(excluded),
        "excluded_regions": sorted(excluded_regions),
        "n_regions": len({row["region"] for row in kept}),
        "n_excluded_regions": len({row["region"] for row in excluded}),
        "n_candidates": len(candidates),
        "n_excluded_candidates": len(excluded_candidate_rows),
        "n_positive_centered_delta": sum(1 for row in kept if row["centered_delta_vs_shuffle"] > 0.0),
        "max_bidirectional_recording_fraction": max(
            (row["bidirectional_recording_fraction"] for row in kept),
            default=0.0,
        ),
        "candidate_rows": [
            {"target_mode": row["target_mode"], "region": row["region"], "holdout": row["holdout"]}
            for row in candidates
        ],
        "excluded_candidate_rows": excluded_candidate_rows,
        "top_rows": top_rows[:20],
        "decision": (
            "extreme_quantile_interpretable_region_candidate"
            if candidates
            else "no_extreme_quantile_interpretable_region_candidate"
        ),
    }


def build_report(source: Path, *, excluded_regions: set[str] | frozenset[str] = NON_SPECIFIC_REGIONS) -> dict:
    payload = json.loads(source.read_text())
    summary = summarize_rows(payload["rows"], excluded_regions=excluded_regions)
    return {
        "source": str(source),
        "target_mode": payload.get("target_mode"),
        "feature_mode": payload.get("feature_mode"),
        "region_granularity": payload.get("region_granularity"),
        "quantiles": payload.get("quantiles"),
        "summary": summary,
        "rows": [row for row in payload["rows"] if is_interpretable_region(row["region"], excluded_regions)],
    }


def render_markdown(report: dict) -> str:
    summary = report["summary"]
    lines = [
        "# Extreme-Quantile Interpretable Region Filter",
        "",
        (
            "Filters the strict parent-region specificity scan to remove non-specific "
            "ontology/meta labels before considering a result anatomically interpretable."
        ),
        "",
        f"- source: `{report['source']}`",
        f"- excluded regions: `{', '.join(summary['excluded_regions'])}`",
        f"- rows retained: `{summary['n_rows']}/{summary['n_input_rows']}`",
        f"- retained regions: `{summary['n_regions']}`",
        f"- retained candidates: `{summary['n_candidates']}`",
        f"- excluded candidates: `{summary['n_excluded_candidates']}`",
        f"- decision: `{summary['decision']}`",
        "",
        "## Top Retained Rows",
        "",
        "| region | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs | eval nonzero |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary["top_rows"][:16]:
        lines.append(
            f"| {row['region']} | {row['holdout']} | {row['decision']} | "
            f"{row['centered_delta_vs_shuffle']:+.3f} | {row['centered_delta_vs_total']:+.3f} | "
            f"{row['target0_improved_vs_shuffle']:.3f} | {row['target1_improved_vs_shuffle']:.3f} | "
            f"{row['n_bidirectional_recordings']}/{row['n_recordings']} | "
            f"{row['eval_nonzero_fraction']:.3f} |"
        )
    lines += [
        "",
        "## Decision",
        "",
        (
            "No interpretable parent region passes the strict local gate after removing "
            "non-specific ontology labels. The only strict region pass was excluded."
            if summary["n_candidates"] == 0
            else "At least one interpretable region passes; validate it across shuffle seeds before GPU training."
        ),
        "",
    ]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source-json",
        type=Path,
        default=REPO_ROOT / "docs/extreme_quantile_region_specificity.json",
    )
    parser.add_argument("--exclude-region", nargs="*", default=sorted(NON_SPECIFIC_REGIONS))
    parser.add_argument(
        "--out-json",
        type=Path,
        default=REPO_ROOT / "docs/extreme_quantile_interpretable_region_filter.json",
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=REPO_ROOT / "docs/extreme_quantile_interpretable_region_filter.md",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(args.source_json, excluded_regions=set(args.exclude_region))
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text(render_markdown(report))
    print(f"wrote {args.out_json}")
    print(f"wrote {args.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
