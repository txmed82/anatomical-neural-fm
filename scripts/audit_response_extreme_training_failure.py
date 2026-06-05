"""Diagnose the negative response-extreme A100 training pilot.

The local trigger was a model-free broad-family count signal. The A100 pilot
trained neural models with learned region embeddings. This report checks which
parts of the local trigger carried over to cloud training and which did not.
"""
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
ROBUST_CASES = (
    ("CSHL045", "post_error_response_extreme_25_75_le_1", "broad_named_anatomy"),
    ("NR_0019", "post_error_response_extreme_33_67_le_1", "broad_named_anatomy"),
)


def _safe_float(value: object) -> float | None:
    if not isinstance(value, (int, float)) or math.isnan(float(value)):
        return None
    return float(value)


def load_local_rows(path: Path) -> dict[tuple[str, str, str], dict]:
    payload = json.loads(path.read_text())
    rows = payload.get("robust_response_extreme_seed_candidates", [])
    return {
        (str(row["holdout"]), str(row["target_mode"]), str(row["family"])): row
        for row in rows
    }


def load_projected_balances(path: Path) -> dict[str, dict]:
    payload = json.loads(path.read_text())
    return payload.get("summary", {}).get("target_balances", {})


def arm_from_config(config: dict) -> str:
    if config.get("arm") == "region_only" and config.get("region_label_control") != "none":
        return "region_shuffle"
    return str(config.get("arm"))


def parse_cloud_log(path: Path) -> list[dict]:
    runs = []
    current: dict | None = None
    for line in path.read_text().splitlines():
        if not line.startswith("{"):
            continue
        try:
            record = json.loads(line)
        except Exception:
            continue
        event = record.get("event")
        if event == "config":
            current = {
                "holdout": str((record.get("holdout") or [""])[0]),
                "target_mode": str(record.get("target_mode")),
                "arm": arm_from_config(record),
                "best_metric": str(record.get("best_metric")),
                "max_steps": int(record.get("max_steps") or 0),
                "eval_batches": int(record.get("eval_batches") or 0),
                "region_filter": str(record.get("region_filter")),
                "region_granularity": str(record.get("region_granularity")),
                "region_label_control": str(record.get("region_label_control")),
                "evals": [],
                "has_full_eval": False,
                "has_eval_predictions": False,
                "split": {},
                "done": {},
            }
            runs.append(current)
            continue
        if current is None:
            continue
        if event == "split":
            current["split"] = {
                "n_train_trials": int(record.get("n_train_trials") or 0),
                "n_eval_trials": int(record.get("n_eval_trials") or 0),
                "n_eval_rids": int(record.get("n_eval_rids") or 0),
                "n_allowed_regions": int(record.get("n_allowed_regions") or 0),
                "eval_class_balance": record.get("eval_class_balance") or {},
            }
        elif event == "eval":
            current["evals"].append({
                "step": int(record.get("step") or 0),
                "eval_loss": _safe_float(record.get("eval_loss")),
                "eval_auc": _safe_float(record.get("eval_auc")),
                "eval_n": int(record.get("eval_n") or 0),
            })
        elif event == "full_eval":
            current["has_full_eval"] = True
        elif event == "eval_predictions_saved":
            current["has_eval_predictions"] = True
        elif event == "done":
            current["done"] = {
                "wall_clock_s": _safe_float(record.get("wall_clock_s")),
                "best_metric": str(record.get("best_metric")),
                "best_metric_value": _safe_float(record.get("best_metric_value")),
            }
    return runs


def best_eval_by_loss(run: dict) -> dict | None:
    evals = [row for row in run.get("evals", []) if row.get("eval_loss") is not None]
    return min(evals, key=lambda row: row["eval_loss"]) if evals else None


def best_eval_by_auc(run: dict) -> dict | None:
    evals = [row for row in run.get("evals", []) if row.get("eval_auc") is not None]
    return max(evals, key=lambda row: row["eval_auc"]) if evals else None


def parse_cloud_result_markdown(path: Path) -> dict[tuple[str, str], dict]:
    rows = {}
    for line in path.read_text().splitlines():
        if not line.startswith("| "):
            continue
        parts = [part.strip() for part in line.strip().strip("|").split("|")]
        if len(parts) != 6 or parts[0] not in {"CSHL045", "NR_0019"}:
            continue
        rows[(parts[0], parts[1])] = {
            "holdout": parts[0],
            "arm": parts[1],
            "n_seeds": int(parts[2]),
            "mean_auc": float(parts[3]),
            "mean_delta_vs_shared": float(parts[4]),
            "seed_deltas": parts[5],
        }
    return rows


def cloud_runs_by_case(runs: list[dict]) -> dict[tuple[str, str], dict[str, dict]]:
    grouped: dict[tuple[str, str], dict[str, dict]] = defaultdict(dict)
    for run in runs:
        grouped[(run["holdout"], run["target_mode"])][run["arm"]] = run
    return dict(grouped)


def build_report(
    *,
    local_rows: dict[tuple[str, str, str], dict],
    projected_balances: dict[str, dict],
    cloud_runs: list[dict],
    cloud_result_rows: dict[tuple[str, str], dict],
) -> dict:
    grouped_runs = cloud_runs_by_case(cloud_runs)
    cases = []
    blockers = set()
    for holdout, target_mode, family in ROBUST_CASES:
        local = local_rows.get((holdout, target_mode, family), {})
        balance = projected_balances.get(target_mode, {})
        arms = grouped_runs.get((holdout, target_mode), {})
        shared = arms.get("shared_baseline")
        region = arms.get("region_only")
        shuffle = arms.get("region_shuffle")
        region_result = cloud_result_rows.get((holdout, "region_only"), {})
        shuffle_result = cloud_result_rows.get((holdout, "region_shuffle"), {})
        n_train = int((shared or region or {}).get("split", {}).get("n_train_trials") or 0)
        n_eval = int((shared or region or {}).get("split", {}).get("n_eval_trials") or 0)
        eval_n = int((best_eval_by_loss(shared or {}) or {}).get("eval_n") or 0)
        target_trials_match = n_train + n_eval == int(balance.get("n_trials") or -1)
        eval_sample_draws_per_trial = None if n_eval == 0 else eval_n / n_eval

        region_delta = region_result.get("mean_delta_vs_shared")
        shuffle_delta = shuffle_result.get("mean_delta_vs_shared")
        trained_true_lost = isinstance(region_delta, float) and region_delta <= 0.0
        shuffle_beats_true = (
            isinstance(region_delta, float)
            and isinstance(shuffle_delta, float)
            and shuffle_delta > region_delta
        )
        if trained_true_lost:
            blockers.add("trained_true_region_lost_to_shared")
        if shuffle_beats_true:
            blockers.add("shuffled_region_outperformed_true")
        if not (shared or {}).get("has_full_eval"):
            blockers.add("no_full_eval_or_prediction_diagnostics")
        if target_trials_match:
            target_alignment = "matched"
        else:
            target_alignment = "mismatch"
            blockers.add("target_trial_mismatch")

        cases.append({
            "holdout": holdout,
            "target_mode": target_mode,
            "family": family,
            "target_alignment": target_alignment,
            "projected_total_trials": int(balance.get("n_trials") or 0),
            "cloud_train_trials": n_train,
            "cloud_eval_trials": n_eval,
            "cloud_eval_sample_n": eval_n,
            "eval_sample_draws_per_trial": eval_sample_draws_per_trial,
            "local_mean_delta_vs_shuffle": local.get("mean_centered_delta_vs_shuffle"),
            "local_mean_delta_vs_total": local.get("mean_centered_delta_vs_total"),
            "local_candidate_seeds": local.get("n_candidate_seeds"),
            "local_n_seeds": local.get("n_seeds"),
            "local_bidir_range": [
                local.get("min_bidirectional_recordings"),
                local.get("max_bidirectional_recordings"),
            ],
            "cloud_region_delta_vs_shared": region_delta,
            "cloud_region_auc": region_result.get("mean_auc"),
            "cloud_shuffle_delta_vs_shared": shuffle_delta,
            "cloud_shuffle_auc": shuffle_result.get("mean_auc"),
            "cloud_region_best_loss_eval": best_eval_by_loss(region or {}),
            "cloud_region_best_auc_eval": best_eval_by_auc(region or {}),
            "cloud_shared_best_loss_eval": best_eval_by_loss(shared or {}),
            "cloud_best_metric": (region or shared or {}).get("best_metric"),
            "cloud_has_full_eval": bool((region or {}).get("has_full_eval") or (shared or {}).get("has_full_eval")),
            "cloud_has_eval_predictions": bool(
                (region or {}).get("has_eval_predictions") or (shared or {}).get("has_eval_predictions")
            ),
            "training_wall_clock_s": (region or {}).get("done", {}).get("wall_clock_s"),
            "failure_modes": [
                name for name, active in (
                    ("trained_true_region_lost_to_shared", trained_true_lost),
                    ("shuffled_region_outperformed_true", shuffle_beats_true),
                    ("sampled_eval_loss_selection", (region or {}).get("best_metric") == "eval_loss"),
                    ("no_full_eval_or_prediction_diagnostics", not bool((region or {}).get("has_full_eval"))),
                    ("local_feature_not_training_arm", True),
                )
                if active
            ],
        })

    decision = (
        "local_to_training_readout_mismatch"
        if {"trained_true_region_lost_to_shared", "shuffled_region_outperformed_true"} <= blockers
        else "response_extreme_training_failure_needs_review"
    )
    return {
        "summary": {
            "n_cases": len(cases),
            "decision": decision,
            "blockers": sorted(blockers),
            "next_recommended_action": "local_training_aligned_readout_diagnostic",
            "paid_gpu_trigger": False,
        },
        "cases": cases,
        "interpretation": [
            "Response-extreme target construction transferred to cloud: cloud train+eval trials match projected local trial counts.",
            "The local trigger was a recording-centered broad-family count feature, not the trained parent-region embedding arm.",
            "The cloud pilot selected by sampled eval_loss and did not save full-eval predictions, so the trained output cannot be checked with the strict recording-centered paired gate.",
            "True region labels underperformed the shared baseline in both tested cases while shuffled labels were non-negative, so more paid seeds are not justified before a local training-aligned diagnostic.",
        ],
        "next_steps": [
            "Run a no-spend local readout using the exact cloud feature space: parent shared-region count vector plus true/shuffled controls, not only broad_named_anatomy aggregates.",
            "If a future GPU run is justified, require SAVE_DIAGNOSTICS=1, FULL_EVAL_ON_BEST=1, and BEST_METRIC=full_eval_centered_auc so the trained outputs can be scored by the same recording-centered gate.",
            "Consider a model arm that exposes the local successful feature directly, such as a fixed broad-family-count readout, before returning to learned region embeddings.",
        ],
    }


def render_markdown(report: dict) -> str:
    lines = [
        "# Response-Extreme Training Failure Audit",
        "",
        "Compares the local response-extreme training trigger with the completed A100 pilot.",
        "",
        f"- cases: `{report['summary']['n_cases']}`",
        f"- decision: `{report['summary']['decision']}`",
        f"- paid GPU trigger: `{report['summary']['paid_gpu_trigger']}`",
        f"- next recommended action: `{report['summary']['next_recommended_action']}`",
        f"- blockers: `{', '.join(report['summary']['blockers']) or 'none'}`",
        "",
        "| holdout | target | target trials | cloud train/eval | eval sample draws/trial | local delta shuffle | cloud true delta | cloud shuffle delta | failure modes |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in report["cases"]:
        draws_per_trial = row["eval_sample_draws_per_trial"]
        lines.append(
            "| "
            f"{row['holdout']} | {row['target_mode']} | {row['projected_total_trials']} | "
            f"{row['cloud_train_trials']}/{row['cloud_eval_trials']} | "
            f"{row['cloud_eval_sample_n']} ({0.0 if draws_per_trial is None else draws_per_trial:.2f}) | "
            f"{row['local_mean_delta_vs_shuffle']:+.4f} | "
            f"{row['cloud_region_delta_vs_shared']:+.3f} | "
            f"{row['cloud_shuffle_delta_vs_shared']:+.3f} | "
            f"{', '.join(row['failure_modes'])} |"
        )
    lines += [
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {item}" for item in report["interpretation"])
    lines += [
        "",
        "## Next Steps",
        "",
    ]
    lines.extend(f"{idx}. {item}" for idx, item in enumerate(report["next_steps"], start=1))
    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--seed-sensitivity",
        type=Path,
        default=REPO_ROOT / "docs/composite_behavior_response_extreme_seed_sensitivity.json",
    )
    parser.add_argument(
        "--projected-gate",
        type=Path,
        default=REPO_ROOT / "docs/composite_behavior_response_extreme_family_gate_projected_hdf5.json",
    )
    parser.add_argument(
        "--cloud-log",
        type=Path,
        default=REPO_ROOT / "docs/cloud_phase3_5_runpod.log",
    )
    parser.add_argument(
        "--cloud-result",
        type=Path,
        default=REPO_ROOT / "docs/response_extreme_trigger_a100_results.md",
    )
    parser.add_argument(
        "--out-json",
        type=Path,
        default=REPO_ROOT / "docs/response_extreme_training_failure_audit.json",
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=REPO_ROOT / "docs/response_extreme_training_failure_audit.md",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(
        local_rows=load_local_rows(args.seed_sensitivity),
        projected_balances=load_projected_balances(args.projected_gate),
        cloud_runs=parse_cloud_log(args.cloud_log),
        cloud_result_rows=parse_cloud_result_markdown(args.cloud_result),
    )
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text(render_markdown(report))
    print(f"wrote {args.out_json}")
    print(f"wrote {args.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
