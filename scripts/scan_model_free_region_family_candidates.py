"""Scan predefined region-family aggregates for model-free transfer signal."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "vendor" / "torch_brain"))

from torch_brain.dataset import Dataset  # noqa: E402
from audit_model_free_region_signal import (  # noqa: E402
    build_region_vocab,
    make_feature_matrix,
)
from scan_model_free_region_candidates import scan_candidates  # noqa: E402
from train import (  # noqa: E402
    build_trial_samples,
    build_vocab,
    select_recording_ids,
    split_recordings_by_subject,
)


FAMILY_DEFINITIONS: dict[str, tuple[str, ...]] = {
    "cortical_visual": ("VISa", "VISp", "VISpl", "VISpm", "VISpor"),
    "cortical_auditory": ("AUDd", "AUDv"),
    "cortical_sensorimotor": (
        "MOp",
        "MOs",
        "SSp-bfd",
        "SSp-ll",
        "SSp-tr",
        "SSp-ul",
        "SSp-un",
        "SSs",
    ),
    "cortical_retrosplenial": ("RSPagl", "RSPd", "RSPv"),
    "hippocampal_formation": ("CA", "DG", "ENTm", "HIP", "RHP"),
    "thalamic": ("ATN", "DORpm", "LAT", "LGd", "MED", "MG", "PRT", "VAL", "VENT", "VL", "VP"),
    "midbrain": ("MBmot", "MBsen", "MBsta", "SCm", "SCs", "P-mot", "P-sen"),
    "basal_ganglia": ("CNU", "PALc", "STRd", "STRv", "VS"),
    "brainstem_interbrain": ("BS", "HB", "IB", "LZ", "ZI"),
    "fiber_tracts": ("cc", "cett", "eps", "epsc", "fa", "fiber tracts", "fxs", "hc", "lfbst", "mfbc", "mfbse", "scp"),
    "broad_named_anatomy": (
        "ATN",
        "AUDd",
        "AUDv",
        "BS",
        "CA",
        "CNU",
        "CTXpl",
        "CTXsp",
        "DG",
        "DORpm",
        "ENTm",
        "EPI",
        "FRP",
        "HB",
        "HIP",
        "IB",
        "LAT",
        "LGd",
        "LS",
        "LZ",
        "MBmot",
        "MBsen",
        "MBsta",
        "MED",
        "MG",
        "MOp",
        "MOs",
        "MSC",
        "OLF",
        "ORBm",
        "ORBvl",
        "PALc",
        "PRT",
        "PVR",
        "RHP",
        "RSPagl",
        "RSPd",
        "RSPv",
        "SCm",
        "SCs",
        "SSp-bfd",
        "SSp-ll",
        "SSp-tr",
        "SSp-ul",
        "SSp-un",
        "SSs",
        "STRd",
        "STRv",
        "VENT",
        "VISa",
        "VISp",
        "VISpl",
        "VISpm",
        "VISpor",
        "VL",
        "VP",
        "VS",
        "ZI",
    ),
}


def present_family_definitions(regions: list[str]) -> dict[str, tuple[str, ...]]:
    region_set = set(regions)
    return {
        name: tuple(region for region in members if region in region_set)
        for name, members in FAMILY_DEFINITIONS.items()
        if any(region in region_set for region in members)
    }


def aggregate_features(features: np.ndarray, regions: list[str], families: dict[str, tuple[str, ...]]) -> np.ndarray:
    region_to_col = {region: idx for idx, region in enumerate(regions)}
    out = np.zeros((features.shape[0], len(families)), dtype=np.float32)
    for family_idx, members in enumerate(families.values()):
        cols = [region_to_col[region] for region in members if region in region_to_col]
        if cols:
            out[:, family_idx] = features[:, cols].sum(axis=1)
    return out


def render_markdown(report: dict) -> str:
    lines = [
        "# CSH Model-Free Region-Family Candidate Scan",
        "",
        (
            "Predefined parent-region family aggregates scanned as model-free ridge "
            "features against within-recording shuffled labels and total-spike baseline."
        ),
        "",
        f"Holdout: `{', '.join(report['holdout'])}`",
        f"Families scanned: `{report['n_families']}`",
        f"Candidates: `{report['n_candidates']}`",
        "",
        "| family | outcome | eval_centered_AUC | delta_vs_shuffle | delta_vs_total | target0 | target1 | recordings | eval_nonzero | members |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in report["families"]:
        members = ", ".join(report["family_definitions"][row["region"]])
        lines.append(
            "| "
            f"{row['region']} | {row['outcome']} | {row['eval_centered_auc']:.3f} | "
            f"{row['centered_delta_vs_shuffle']:+.3f} | {row['centered_delta_vs_total']:+.3f} | "
            f"{row['target0_improved_vs_shuffle']:.3f} | {row['target1_improved_vs_shuffle']:.3f} | "
            f"{row['positive_recordings_vs_shuffle']}/{row['n_recordings']} | "
            f"{row['eval_nonzero_fraction']:.3f} | {members} |"
        )
    lines += [
        "",
        "Decision:",
        "",
        report["decision"],
        "",
    ]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=REPO_ROOT / "data/brainsets/ibl_bwm")
    parser.add_argument("--manifest", type=Path, default=REPO_ROOT / "manifests/ibl_bwm_region_matched_support80_best6.json")
    parser.add_argument("--holdout", nargs="*", default=["CSH_ZAD_019"])
    parser.add_argument("--target-mode", default="stimulus_side", choices=["choice", "stimulus_side", "feedback", "prior_side"])
    parser.add_argument("--region-granularity", default="parent", choices=["fine", "parent", "grandparent"])
    parser.add_argument("--window-len", type=float, default=1.0)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--l2", type=float, default=10.0)
    parser.add_argument("--min-centered-delta", type=float, default=0.01)
    parser.add_argument("--min-target-improvement", type=float, default=0.55)
    parser.add_argument("--out-json", type=Path, default=REPO_ROOT / "docs/csh_model_free_region_family_scan.json")
    parser.add_argument("--out-md", type=Path, default=REPO_ROOT / "docs/csh_model_free_region_family_scan.md")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ds = Dataset(dataset_dir=args.data_dir, keep_files_open=True)
    selected_recording_ids = select_recording_ids(ds, args.manifest, args.data_dir)
    vocab = build_vocab(ds, args.region_granularity, selected_recording_ids)
    split = split_recordings_by_subject(vocab["subject_by_rid"], args.holdout)
    train_trials = build_trial_samples(vocab["recs"], split.train_rids, args.window_len, args.target_mode)
    eval_trials = build_trial_samples(vocab["recs"], split.eval_rids, args.window_len, args.target_mode)
    regions = build_region_vocab(vocab["recs"], split.train_rids + split.eval_rids, args.region_granularity)
    family_definitions = present_family_definitions(regions)
    family_names = list(family_definitions)

    train_true_x, train_y, _ = make_feature_matrix(
        ds,
        vocab["recs"],
        train_trials,
        regions=regions,
        region_granularity=args.region_granularity,
        region_control="none",
        seed=args.seed,
        window_len=args.window_len,
    )
    eval_true_x, eval_y, eval_recording_ids = make_feature_matrix(
        ds,
        vocab["recs"],
        eval_trials,
        regions=regions,
        region_granularity=args.region_granularity,
        region_control="none",
        seed=args.seed,
        window_len=args.window_len,
    )
    train_shuffle_x, _train_y, _ = make_feature_matrix(
        ds,
        vocab["recs"],
        train_trials,
        regions=regions,
        region_granularity=args.region_granularity,
        region_control="within_recording_shuffle",
        seed=args.seed,
        window_len=args.window_len,
    )
    eval_shuffle_x, _eval_y, _ = make_feature_matrix(
        ds,
        vocab["recs"],
        eval_trials,
        regions=regions,
        region_granularity=args.region_granularity,
        region_control="within_recording_shuffle",
        seed=args.seed,
        window_len=args.window_len,
    )

    rows = scan_candidates(
        regions=family_names,
        train_true_x=aggregate_features(train_true_x, regions, family_definitions),
        train_shuffle_x=aggregate_features(train_shuffle_x, regions, family_definitions),
        train_y=train_y,
        eval_true_x=aggregate_features(eval_true_x, regions, family_definitions),
        eval_shuffle_x=aggregate_features(eval_shuffle_x, regions, family_definitions),
        eval_y=eval_y,
        eval_recording_ids=eval_recording_ids,
        l2=args.l2,
        min_centered_delta=args.min_centered_delta,
        min_target_improvement=args.min_target_improvement,
    )
    candidates = [row for row in rows if row["outcome"] == "candidate"]
    decision = (
        "At least one predefined region family passed the model-free gate; next step is "
        "multi-holdout model-free confirmation before any GPU spend."
        if candidates
        else (
            "No predefined region family passed the model-free promotion gate. The next "
            "no-spend branch should test an alternative conserved target or a larger "
            "matched-region manifest audit, not another GPU model run."
        )
    )
    report = {
        "holdout": split.holdout_subjects,
        "train_subjects": split.train_subjects,
        "target_mode": args.target_mode,
        "region_granularity": args.region_granularity,
        "window_len": args.window_len,
        "seed": args.seed,
        "l2": args.l2,
        "thresholds": {
            "min_centered_delta": args.min_centered_delta,
            "min_target_improvement": args.min_target_improvement,
            "min_positive_recordings": 3,
        },
        "n_train_trials": len(train_trials),
        "n_eval_trials": len(eval_trials),
        "n_families": len(family_names),
        "n_candidates": len(candidates),
        "family_definitions": {name: list(members) for name, members in family_definitions.items()},
        "decision": decision,
        "families": rows,
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
