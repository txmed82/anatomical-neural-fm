"""Trainable readout audit for the direct broad-family anatomical signal.

This is a no-spend bridge between the packaged model-free ridge result and any
future GPU model arm. It keeps the same fixed broad_named_anatomy feature and
promotion gate, but fits a deterministic logistic readout with gradient descent.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "vendor" / "torch_brain"))

from audit_composite_behavior_target_family_gate import precompute_target  # noqa: E402
from audit_model_free_positive_holdouts import recording_target_rows  # noqa: E402
from audit_model_free_recording_bidirectional_gate import recording_bidirectional_summary  # noqa: E402
from audit_model_free_region_signal import centered_auc, paired_improvement, per_recording_auc  # noqa: E402
from audit_shared_family_target_control_gate import family_gate_decision, summarize_rows  # noqa: E402
from torch_brain.dataset import Dataset  # noqa: E402
from train import _auc, build_vocab, select_recording_ids  # noqa: E402


DEFAULT_CASES: tuple[tuple[str, str], ...] = (
    ("CSHL045", "post_error_response_extreme_25_75_le_1"),
    ("NR_0019", "post_error_response_extreme_33_67_le_1"),
)


def zscore_train_eval(train_x: np.ndarray, eval_x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mean = train_x.mean(axis=0, keepdims=True)
    std = train_x.std(axis=0, keepdims=True)
    std[std < 1e-6] = 1.0
    return (train_x - mean) / std, (eval_x - mean) / std


def fit_logistic_scores(
    train_x: np.ndarray,
    train_y: np.ndarray,
    eval_x: np.ndarray,
    *,
    seed: int,
    steps: int,
    lr: float,
    l2: float,
) -> tuple[np.ndarray, np.ndarray]:
    train_z, eval_z = zscore_train_eval(train_x.astype(np.float64), eval_x.astype(np.float64))
    train_design = np.concatenate([train_z, np.ones((train_z.shape[0], 1), dtype=np.float64)], axis=1)
    eval_design = np.concatenate([eval_z, np.ones((eval_z.shape[0], 1), dtype=np.float64)], axis=1)
    rng = np.random.default_rng(seed)
    weights = rng.normal(0.0, 0.01, size=train_design.shape[1])
    y = train_y.astype(np.float64)
    for _ in range(steps):
        logits = np.clip(train_design @ weights, -40.0, 40.0)
        probs = 1.0 / (1.0 + np.exp(-logits))
        grad = train_design.T @ (probs - y) / len(y)
        grad[:-1] += l2 * weights[:-1] / len(y)
        weights -= lr * grad
    return train_design @ weights, eval_design @ weights


def evaluate_feature_set(
    *,
    name: str,
    train_x: np.ndarray,
    train_y: np.ndarray,
    eval_x: np.ndarray,
    eval_y: np.ndarray,
    eval_recordings: list[str],
    seed: int,
    steps: int,
    lr: float,
    l2: float,
) -> dict:
    train_scores, eval_scores = fit_logistic_scores(
        train_x,
        train_y,
        eval_x,
        seed=seed,
        steps=steps,
        lr=lr,
        l2=l2,
    )
    return {
        "name": name,
        "train_auc": _auc(train_scores, train_y),
        "eval_auc": _auc(eval_scores, eval_y),
        "eval_centered_auc": centered_auc(eval_scores, eval_y, eval_recordings),
        "eval_scores": eval_scores,
        "per_recording_auc": per_recording_auc(eval_scores, eval_y, eval_recordings),
    }


def evaluate_trainable_family_row(
    *,
    target_mode: str,
    family: str,
    holdout: str,
    family_index: int,
    train_family_true: np.ndarray,
    eval_family_true: np.ndarray,
    train_family_shuffle: np.ndarray,
    eval_family_shuffle: np.ndarray,
    train_total: np.ndarray,
    eval_total: np.ndarray,
    train_y: np.ndarray,
    eval_y: np.ndarray,
    eval_recordings: list[str],
    train_seed: int,
    steps: int,
    lr: float,
    l2: float,
    min_centered_delta: float,
    min_total_delta: float,
    min_target_improvement: float,
    min_bidirectional_recording_fraction: float,
) -> dict:
    true = evaluate_feature_set(
        name=f"{family}_true",
        train_x=train_family_true[:, [family_index]],
        train_y=train_y,
        eval_x=eval_family_true[:, [family_index]],
        eval_y=eval_y,
        eval_recordings=eval_recordings,
        seed=train_seed,
        steps=steps,
        lr=lr,
        l2=l2,
    )
    shuffle = evaluate_feature_set(
        name=f"{family}_shuffle",
        train_x=train_family_shuffle[:, [family_index]],
        train_y=train_y,
        eval_x=eval_family_shuffle[:, [family_index]],
        eval_y=eval_y,
        eval_recordings=eval_recordings,
        seed=train_seed + 10_000,
        steps=steps,
        lr=lr,
        l2=l2,
    )
    total = evaluate_feature_set(
        name="total_spikes",
        train_x=train_total,
        train_y=train_y,
        eval_x=eval_total,
        eval_y=eval_y,
        eval_recordings=eval_recordings,
        seed=train_seed + 20_000,
        steps=steps,
        lr=lr,
        l2=l2,
    )
    paired_shuffle = paired_improvement(true["eval_scores"], shuffle["eval_scores"], eval_y)
    paired_total = paired_improvement(true["eval_scores"], total["eval_scores"], eval_y)
    true_recording_auc = per_recording_auc(true["eval_scores"], eval_y, eval_recordings)
    shuffle_recording_auc = per_recording_auc(shuffle["eval_scores"], eval_y, eval_recordings)
    recording_deltas = {rid: true_recording_auc[rid] - shuffle_recording_auc[rid] for rid in sorted(true_recording_auc)}
    rec_target_rows = recording_target_rows(true["eval_scores"], shuffle["eval_scores"], eval_y, eval_recordings)
    bidirectional = recording_bidirectional_summary(rec_target_rows, min_target_improvement=min_target_improvement)
    row = {
        "target_mode": target_mode,
        "family": family,
        "holdout": holdout,
        "train_seed": train_seed,
        "train_auc": true["train_auc"],
        "eval_auc": true["eval_auc"],
        "eval_centered_auc": true["eval_centered_auc"],
        "shuffle_centered_auc": shuffle["eval_centered_auc"],
        "total_centered_auc": total["eval_centered_auc"],
        "centered_delta_vs_shuffle": true["eval_centered_auc"] - shuffle["eval_centered_auc"],
        "centered_delta_vs_total": true["eval_centered_auc"] - total["eval_centered_auc"],
        "paired_improved_vs_shuffle": paired_shuffle["improved_fraction"],
        "target0_improved_vs_shuffle": paired_shuffle["target0_improved_fraction"],
        "target1_improved_vs_shuffle": paired_shuffle["target1_improved_fraction"],
        "paired_improved_vs_total": paired_total["improved_fraction"],
        "target0_improved_vs_total": paired_total["target0_improved_fraction"],
        "target1_improved_vs_total": paired_total["target1_improved_fraction"],
        "recordings_positive_vs_shuffle": int(sum(delta > 0.0 for delta in recording_deltas.values())),
        "n_recordings": len(recording_deltas),
        "n_bidirectional_recordings": bidirectional["n_bidirectional_recordings"],
        "bidirectional_recording_fraction": bidirectional["bidirectional_recording_fraction"],
        "recording_target_rows": rec_target_rows,
    }
    row["decision"] = family_gate_decision(
        row,
        min_centered_delta=min_centered_delta,
        min_total_delta=min_total_delta,
        min_target_improvement=min_target_improvement,
        min_bidirectional_recording_fraction=min_bidirectional_recording_fraction,
    )
    return row


def screen_payload(
    payload: dict,
    *,
    holdout: str,
    family: str,
    train_seeds: list[int],
    steps: int,
    lr: float,
    l2: float,
    min_centered_delta: float,
    min_total_delta: float,
    min_target_improvement: float,
    min_bidirectional_recording_fraction: float,
) -> list[dict]:
    subject_ids = np.asarray(payload["subject_ids"], dtype=object)
    train_mask = subject_ids != holdout
    eval_mask = subject_ids == holdout
    if not np.any(train_mask) or not np.any(eval_mask):
        return []
    if len(set(payload["y"][train_mask])) < 2 or len(set(payload["y"][eval_mask])) < 2:
        return []
    if family not in payload["family_names"]:
        return []
    family_index = payload["family_names"].index(family)
    eval_recordings = [rid for rid, use in zip(payload["recording_ids"], eval_mask) if bool(use)]
    return [
        evaluate_trainable_family_row(
            target_mode=payload["target_mode"],
            family=family,
            holdout=holdout,
            family_index=family_index,
            train_family_true=payload["family_true"][train_mask],
            eval_family_true=payload["family_true"][eval_mask],
            train_family_shuffle=payload["family_shuffle"][train_mask],
            eval_family_shuffle=payload["family_shuffle"][eval_mask],
            train_total=payload["total"][train_mask],
            eval_total=payload["total"][eval_mask],
            train_y=payload["y"][train_mask],
            eval_y=payload["y"][eval_mask],
            eval_recordings=eval_recordings,
            train_seed=train_seed,
            steps=steps,
            lr=lr,
            l2=l2,
            min_centered_delta=min_centered_delta,
            min_total_delta=min_total_delta,
            min_target_improvement=min_target_improvement,
            min_bidirectional_recording_fraction=min_bidirectional_recording_fraction,
        )
        for train_seed in train_seeds
    ]


def summarize(rows: list[dict]) -> dict:
    base = summarize_rows(rows)
    by_case = {}
    for row in rows:
        key = f"{row['holdout']}::{row['target_mode']}::{row['family']}"
        case_rows = by_case.setdefault(
            key,
            {
                "holdout": row["holdout"],
                "target_mode": row["target_mode"],
                "family": row["family"],
                "n_train_seeds": 0,
                "n_candidate_seeds": 0,
                "mean_centered_delta_vs_shuffle": 0.0,
                "mean_centered_delta_vs_total": 0.0,
                "min_bidirectional_recordings": row["n_bidirectional_recordings"],
                "max_bidirectional_recordings": row["n_bidirectional_recordings"],
                "mean_target0": 0.0,
                "mean_target1": 0.0,
            },
        )
        case_rows["n_train_seeds"] += 1
        case_rows["n_candidate_seeds"] += int(row["decision"] == "candidate")
        case_rows["mean_centered_delta_vs_shuffle"] += row["centered_delta_vs_shuffle"]
        case_rows["mean_centered_delta_vs_total"] += row["centered_delta_vs_total"]
        case_rows["mean_target0"] += row["target0_improved_vs_shuffle"]
        case_rows["mean_target1"] += row["target1_improved_vs_shuffle"]
        case_rows["min_bidirectional_recordings"] = min(
            case_rows["min_bidirectional_recordings"],
            row["n_bidirectional_recordings"],
        )
        case_rows["max_bidirectional_recordings"] = max(
            case_rows["max_bidirectional_recordings"],
            row["n_bidirectional_recordings"],
        )
    cases = []
    for case in by_case.values():
        n = case["n_train_seeds"]
        for key in (
            "mean_centered_delta_vs_shuffle",
            "mean_centered_delta_vs_total",
            "mean_target0",
            "mean_target1",
        ):
            case[key] /= n
        cases.append(case)
    robust_cases = [case for case in cases if case["n_candidate_seeds"] == case["n_train_seeds"] and case["n_train_seeds"] > 0]
    base.update({
        "n_cases": len(cases),
        "n_robust_cases": len(robust_cases),
        "case_summaries": sorted(cases, key=lambda row: (row["n_candidate_seeds"], row["mean_centered_delta_vs_shuffle"]), reverse=True),
        "decision": "direct_broad_family_trainable_candidate" if robust_cases else "no_direct_broad_family_trainable_candidate",
        "paid_gpu_trigger": False,
        "next_action": (
            "Implement this exact fixed-family-count arm in the training code before any new GPU run."
            if robust_cases
            else "Do not launch GPU training from this branch; keep the model-free package and redesign the trainable arm or target/control locally."
        ),
    })
    return base


def render_markdown(report: dict) -> str:
    summary = report["summary"]
    lines = [
        "# Direct Broad-Family Trainable Readout",
        "",
        "No-spend logistic-readout audit over the same fixed broad_named_anatomy response-extreme features used by the model-free package.",
        "",
        f"- decision: `{summary['decision']}`",
        f"- rows: `{summary['n_rows']}`",
        f"- candidate rows: `{summary['n_candidates']}`",
        f"- robust cases: `{summary['n_robust_cases']}/{summary['n_cases']}`",
        f"- paid GPU trigger: `{summary['paid_gpu_trigger']}`",
        f"- next action: {summary['next_action']}",
        "",
        "| holdout | target | family | candidate seeds | delta shuffle | delta total | targets | bidir range |",
        "|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in summary["case_summaries"]:
        lines.append(
            f"| {row['holdout']} | {row['target_mode']} | {row['family']} | "
            f"{row['n_candidate_seeds']}/{row['n_train_seeds']} | "
            f"{row['mean_centered_delta_vs_shuffle']:+.4f} | {row['mean_centered_delta_vs_total']:+.4f} | "
            f"{row['mean_target0']:.3f}/{row['mean_target1']:.3f} | "
            f"{row['min_bidirectional_recordings']}-{row['max_bidirectional_recordings']} |"
        )
    lines += ["", "## Per-Seed Rows", "", "| holdout | target | train seed | decision | delta shuffle | delta total | targets | bidir |", "|---|---|---:|---|---:|---:|---:|---:|"]
    for row in summary["top_rows"]:
        lines.append(
            f"| {row['holdout']} | {row['target_mode']} | {row['train_seed']} | {row['decision']} | "
            f"{row['centered_delta_vs_shuffle']:+.4f} | {row['centered_delta_vs_total']:+.4f} | "
            f"{row['target0_improved_vs_shuffle']:.3f}/{row['target1_improved_vs_shuffle']:.3f} | "
            f"{row['n_bidirectional_recordings']}/{row['n_recordings']} |"
        )
    lines.append("")
    return "\n".join(lines)


def parse_cases(values: list[str]) -> list[tuple[str, str]]:
    cases = []
    for value in values:
        if ":" not in value:
            raise ValueError(f"case must be HOLDOUT:TARGET, got {value!r}")
        holdout, target = value.split(":", 1)
        cases.append((holdout, target))
    return cases


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=REPO_ROOT / "data/brainsets/ibl_bwm")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=REPO_ROOT / "manifests/ibl_bwm_local_cached_external_support80_projected_hdf5.json",
    )
    parser.add_argument("--case", nargs="*", default=[f"{holdout}:{target}" for holdout, target in DEFAULT_CASES])
    parser.add_argument("--family", default="broad_named_anatomy")
    parser.add_argument("--feature-mode", default="recording_centered", choices=["counts", "fractions", "recording_centered", "recording_zscore", "unit_residuals"])
    parser.add_argument("--region-granularity", default="parent", choices=["fine", "parent", "grandparent"])
    parser.add_argument("--window-len", type=float, default=1.0)
    parser.add_argument("--feature-seed", type=int, default=0)
    parser.add_argument("--train-seed", nargs="*", type=int, default=[0, 1, 2])
    parser.add_argument("--steps", type=int, default=1000)
    parser.add_argument("--lr", type=float, default=0.1)
    parser.add_argument("--l2", type=float, default=1.0)
    parser.add_argument("--min-class-trials", type=int, default=30)
    parser.add_argument("--min-centered-delta", type=float, default=0.0)
    parser.add_argument("--min-total-delta", type=float, default=0.0)
    parser.add_argument("--min-target-improvement", type=float, default=0.55)
    parser.add_argument("--min-bidirectional-recording-fraction", type=float, default=0.75)
    parser.add_argument("--out-json", type=Path, default=REPO_ROOT / "docs/direct_broad_family_trainable_readout.json")
    parser.add_argument("--out-md", type=Path, default=REPO_ROOT / "docs/direct_broad_family_trainable_readout.md")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ds = Dataset(dataset_dir=args.data_dir, keep_files_open=True)
    selected_rids = select_recording_ids(ds, args.manifest, args.data_dir)
    vocab = build_vocab(ds, args.region_granularity, selected_rids)
    rows = []
    for holdout, target in parse_cases(args.case):
        payload = precompute_target(
            ds=ds,
            vocab=vocab,
            selected_rids=selected_rids,
            target_name=target,
            families=(args.family,),
            feature_mode=args.feature_mode,
            region_granularity=args.region_granularity,
            window_len=args.window_len,
            seed=args.feature_seed,
            min_class_trials=args.min_class_trials,
        )
        rows.extend(screen_payload(
            payload,
            holdout=holdout,
            family=args.family,
            train_seeds=args.train_seed,
            steps=args.steps,
            lr=args.lr,
            l2=args.l2,
            min_centered_delta=args.min_centered_delta,
            min_total_delta=args.min_total_delta,
            min_target_improvement=args.min_target_improvement,
            min_bidirectional_recording_fraction=args.min_bidirectional_recording_fraction,
        ))
    report = {
        "manifest": str(args.manifest),
        "family": args.family,
        "feature_mode": args.feature_mode,
        "region_granularity": args.region_granularity,
        "cases": [{"holdout": holdout, "target_mode": target} for holdout, target in parse_cases(args.case)],
        "train_seeds": args.train_seed,
        "optimizer": {"steps": args.steps, "lr": args.lr, "l2": args.l2},
        "thresholds": {
            "min_centered_delta": args.min_centered_delta,
            "min_total_delta": args.min_total_delta,
            "min_target_improvement": args.min_target_improvement,
            "min_bidirectional_recording_fraction": args.min_bidirectional_recording_fraction,
        },
        "summary": summarize(rows),
        "rows": rows,
    }
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text(render_markdown(report))
    print(f"wrote {args.out_json}")
    print(f"wrote {args.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
