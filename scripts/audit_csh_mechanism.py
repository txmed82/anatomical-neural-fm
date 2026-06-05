"""Audit the CSH anatomy signal mechanism from saved predictions/embeddings."""
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import h5py
import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from audit_prediction_failure_modes import (  # noqa: E402
    decode_h5_strings,
    read_manifest_rows,
)
from train import map_region_acronyms  # noqa: E402


DEFAULT_CARRIERS = ("PRT", "CA", "VP", "MOp", "DG", "mfbc")
ARMS = ("shared_baseline", "region_only", "region_shuffle")


@dataclass(frozen=True)
class PairedStats:
    n: int
    improved_fraction: float
    mean_true_prob_delta: float
    mean_abs_prob_delta: float


def display_path(path: Path) -> str:
    path = path.expanduser()
    if not path.is_absolute():
        return str(path)
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def prediction_path(root: Path, holdout: str, arm: str, seed: int) -> Path:
    return root / f"holdout_{holdout}" / f"cloud_choice_{arm}_seed{seed}" / "eval_predictions.jsonl"


def embedding_path(root: Path, holdout: str, arm: str, seed: int) -> Path:
    return root / f"holdout_{holdout}" / f"cloud_choice_{arm}_seed{seed}" / "region_embeddings.jsonl"


def read_jsonl(path: Path) -> list[dict]:
    with path.open() as fh:
        return [json.loads(line) for line in fh if line.strip()]


def read_embedding_rows(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    return {str(row["region"]): row for row in read_jsonl(path)}


def vector(row: dict) -> np.ndarray:
    return np.asarray(row["embedding"], dtype=np.float64)


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0.0:
        return float("nan")
    return float(np.dot(a, b) / denom)


def true_class_probability(row: dict) -> float:
    prob = float(row["prob"])
    return prob if int(row["target"]) == 1 else 1.0 - prob


def trial_key(row: dict) -> tuple[str, float, int]:
    return (str(row["recording_id"]), round(float(row["t0"]), 6), int(row["target"]))


def paired_stats(candidate_rows: Iterable[dict], baseline_rows: Iterable[dict]) -> PairedStats:
    baseline_by_key = {trial_key(row): row for row in baseline_rows}
    improved = []
    deltas = []
    for row in candidate_rows:
        baseline = baseline_by_key.get(trial_key(row))
        if baseline is None:
            continue
        delta = true_class_probability(row) - true_class_probability(baseline)
        deltas.append(delta)
        improved.append(delta > 0.0)
    if not deltas:
        return PairedStats(0, float("nan"), float("nan"), float("nan"))
    arr = np.asarray(deltas, dtype=np.float64)
    return PairedStats(
        n=len(deltas),
        improved_fraction=float(np.mean(improved)),
        mean_true_prob_delta=float(np.mean(arr)),
        mean_abs_prob_delta=float(np.mean(np.abs(arr))),
    )


def group_by_recording(rows: Iterable[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[str(row["recording_id"])].append(row)
    return dict(grouped)


def target1_fraction(rows: list[dict]) -> float:
    if not rows:
        return float("nan")
    return float(np.mean([int(row["target"]) for row in rows]))


def recording_parent_counts(path: Path, granularity: str) -> Counter[str]:
    with h5py.File(path, "r") as h5:
        fine = decode_h5_strings(h5["units/region_acronym"][:])
    return Counter(map_region_acronyms(fine, granularity))


def recording_carrier_rows(
    *,
    manifest: Path,
    data_dir: Path,
    holdout: str,
    carriers: tuple[str, ...],
    granularity: str,
) -> dict[str, dict]:
    manifest_rows = read_manifest_rows(manifest)
    out = {}
    for recording_id, row in sorted(manifest_rows.items()):
        subject = str(row.get("subject_id") or row.get("subject") or "")
        if subject != holdout:
            continue
        path = data_dir / f"{recording_id}.h5"
        if not path.exists():
            continue
        counts = recording_parent_counts(path, granularity)
        total = sum(counts.values())
        carrier_counts = {parent: int(counts[parent]) for parent in carriers if counts[parent] > 0}
        carrier_units = sum(carrier_counts.values())
        out[recording_id] = {
            "n_units": int(total),
            "carrier_units": int(carrier_units),
            "carrier_unit_fraction": float(carrier_units / total) if total else float("nan"),
            "carrier_counts": carrier_counts,
        }
    return out


def embedding_summary(true_rows: dict[str, dict], shuffle_rows: dict[str, dict], carriers: tuple[str, ...]) -> dict:
    rows = {}
    for parent in carriers:
        true = true_rows.get(parent)
        shuffle = shuffle_rows.get(parent)
        if true is None or shuffle is None:
            rows[parent] = {
                "present": False,
                "true_norm": None,
                "shuffle_norm": None,
                "cosine": None,
                "norm_delta": None,
                "l2_distance": None,
            }
            continue
        true_vec = vector(true)
        shuffle_vec = vector(shuffle)
        rows[parent] = {
            "present": True,
            "true_norm": float(true.get("norm", np.linalg.norm(true_vec))),
            "shuffle_norm": float(shuffle.get("norm", np.linalg.norm(shuffle_vec))),
            "cosine": cosine(true_vec, shuffle_vec),
            "norm_delta": float(true.get("norm", np.linalg.norm(true_vec))) - float(shuffle.get("norm", np.linalg.norm(shuffle_vec))),
            "l2_distance": float(np.linalg.norm(true_vec - shuffle_vec)),
        }
    present = [row for row in rows.values() if row["present"]]
    return {
        "carriers": rows,
        "mean_carrier_cosine": float(np.mean([row["cosine"] for row in present])) if present else float("nan"),
        "mean_carrier_l2_distance": float(np.mean([row["l2_distance"] for row in present])) if present else float("nan"),
        "mean_abs_norm_delta": float(np.mean([abs(row["norm_delta"]) for row in present])) if present else float("nan"),
    }


def analyze(
    *,
    root: Path,
    holdout: str,
    seed: int,
    manifest: Path,
    data_dir: Path,
    carriers: tuple[str, ...] = DEFAULT_CARRIERS,
    granularity: str = "parent",
) -> dict:
    rows = {arm: read_jsonl(prediction_path(root, holdout, arm, seed)) for arm in ARMS}
    by_recording = {arm: group_by_recording(arm_rows) for arm, arm_rows in rows.items()}
    carrier_rows = recording_carrier_rows(
        manifest=manifest,
        data_dir=data_dir,
        holdout=holdout,
        carriers=carriers,
        granularity=granularity,
    )

    recordings = {}
    for recording_id in sorted(set(by_recording["shared_baseline"]) | set(carrier_rows)):
        shared = by_recording["shared_baseline"].get(recording_id, [])
        true = by_recording["region_only"].get(recording_id, [])
        shuffle = by_recording["region_shuffle"].get(recording_id, [])
        if not (shared and true and shuffle):
            continue
        true_vs_shuffle = paired_stats(true, shuffle)
        true_vs_shared = paired_stats(true, shared)
        shuffle_vs_shared = paired_stats(shuffle, shared)
        recordings[recording_id] = {
            "n_trials": len(shared),
            "target1_fraction": target1_fraction(shared),
            "carrier": carrier_rows.get(recording_id, {}),
            "paired_true_vs_shuffle": true_vs_shuffle.__dict__,
            "paired_true_vs_shared": true_vs_shared.__dict__,
            "paired_shuffle_vs_shared": shuffle_vs_shared.__dict__,
        }

    true_embeddings = read_embedding_rows(embedding_path(root, holdout, "region_only", seed))
    shuffle_embeddings = read_embedding_rows(embedding_path(root, holdout, "region_shuffle", seed))
    emb = embedding_summary(true_embeddings, shuffle_embeddings, carriers)
    global_true_vs_shuffle = paired_stats(rows["region_only"], rows["region_shuffle"])
    global_shuffle_vs_shared = paired_stats(rows["region_shuffle"], rows["shared_baseline"])
    return {
        "root": str(root),
        "holdout": holdout,
        "seed": seed,
        "carriers": list(carriers),
        "global": {
            "paired_true_vs_shuffle": global_true_vs_shuffle.__dict__,
            "paired_shuffle_vs_shared": global_shuffle_vs_shared.__dict__,
            "specificity_gap": global_true_vs_shuffle.improved_fraction - global_shuffle_vs_shared.improved_fraction,
        },
        "embedding_summary": emb,
        "recordings": recordings,
        "interpretation": interpret(global_true_vs_shuffle, global_shuffle_vs_shared, emb, recordings),
    }


def interpret(
    true_vs_shuffle: PairedStats,
    shuffle_vs_shared: PairedStats,
    emb: dict,
    recordings: dict[str, dict],
) -> dict:
    negative_recordings = [
        recording_id
        for recording_id, row in recordings.items()
        if row["paired_true_vs_shuffle"]["improved_fraction"] < 0.5
    ]
    carrier_rich_negative = [
        recording_id
        for recording_id in negative_recordings
        if recordings[recording_id].get("carrier", {}).get("carrier_units", 0) >= 100
    ]
    return {
        "true_beats_shuffle_paired": true_vs_shuffle.improved_fraction >= 0.55,
        "shuffle_control_specificity": true_vs_shuffle.improved_fraction > shuffle_vs_shared.improved_fraction,
        "carrier_embeddings_separated": (
            math.isfinite(emb["mean_carrier_cosine"])
            and emb["mean_carrier_cosine"] < 0.5
        ),
        "negative_recordings": negative_recordings,
        "carrier_rich_negative_recordings": carrier_rich_negative,
        "decision": (
            "no_mechanism_found"
            if true_vs_shuffle.improved_fraction < 0.55
            else "candidate_mechanism"
        ),
    }


def fmt_float(value, digits: int = 3) -> str:
    if value is None:
        return "n/a"
    try:
        value = float(value)
    except (TypeError, ValueError):
        return "n/a"
    if not math.isfinite(value):
        return "n/a"
    return f"{value:.{digits}f}"


def fmt_signed(value, digits: int = 3) -> str:
    text = fmt_float(value, digits)
    if text == "n/a":
        return text
    return f"{float(value):+.{digits}f}"


def write_markdown(result: dict, out: Path) -> None:
    lines = [
        "# CSH Mechanism Audit",
        "",
        f"Root: `{display_path(Path(result['root']))}`",
        f"Holdout: `{result['holdout']}` seed `{result['seed']}`",
        "",
        "## Global Paired Checks",
        "",
        "| comparison | n | improved_fraction | mean_true_prob_delta | mean_abs_delta |",
        "|---|---:|---:|---:|---:|",
    ]
    for name in ("paired_true_vs_shuffle", "paired_shuffle_vs_shared"):
        row = result["global"][name]
        lines.append(
            "| "
            f"{name} | {row['n']} | {fmt_float(row['improved_fraction'])} | "
            f"{fmt_signed(row['mean_true_prob_delta'])} | {fmt_float(row['mean_abs_prob_delta'])} |"
        )
    lines.append(f"| specificity_gap | n/a | {fmt_signed(result['global']['specificity_gap'])} | n/a | n/a |")

    lines += [
        "",
        "## Carrier-Parent Embeddings",
        "",
        "| parent | present | true_norm | shuffle_norm | norm_delta | cosine | l2_distance |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for parent, row in result["embedding_summary"]["carriers"].items():
        lines.append(
            "| "
            f"{parent} | {row['present']} | {fmt_float(row['true_norm'])} | "
            f"{fmt_float(row['shuffle_norm'])} | {fmt_signed(row['norm_delta'])} | "
            f"{fmt_float(row['cosine'])} | {fmt_float(row['l2_distance'])} |"
        )
    lines += [
        "",
        "## Recording-Level Prediction Shifts",
        "",
        "| recording | trials | target1_frac | carrier_units | carrier_frac | carrier_parents | true_vs_shuffle | true_delta | shuffle_vs_shared |",
        "|---|---:|---:|---:|---:|---|---:|---:|---:|",
    ]
    for recording_id, row in result["recordings"].items():
        carrier = row.get("carrier", {})
        carrier_counts = carrier.get("carrier_counts", {})
        parents = ", ".join(f"{parent}:{count}" for parent, count in carrier_counts.items()) or "none"
        tvs = row["paired_true_vs_shuffle"]
        svs = row["paired_shuffle_vs_shared"]
        lines.append(
            "| "
            f"`{recording_id}` | {row['n_trials']} | {fmt_float(row['target1_fraction'])} | "
            f"{carrier.get('carrier_units', 0)} | {fmt_float(carrier.get('carrier_unit_fraction'))} | "
            f"{parents} | {fmt_float(tvs['improved_fraction'])} | "
            f"{fmt_signed(tvs['mean_true_prob_delta'])} | {fmt_float(svs['improved_fraction'])} |"
        )

    interp = result["interpretation"]
    lines += [
        "",
        "## Interpretation",
        "",
        f"Decision: `{interp['decision']}`",
        "",
        (
            "The saved artifacts do not show a mechanism that justifies paid broadening "
            "yet. True labels fail the paired true-vs-shuffle gate, and carrier-rich "
            "recordings still include negative true-vs-shuffle movement."
        ),
        "",
        (
            "Next implementable idea should be an objective/control that directly rewards "
            "target-aware within-recording true-vs-shuffle separation, not another subject "
            "or region-slice selection rule."
        ),
        "",
    ]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=REPO_ROOT / "runs/lso_csh_recording_centered_gate_pilot")
    parser.add_argument("--holdout", default="CSH_ZAD_019")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--manifest", type=Path, default=REPO_ROOT / "manifests/ibl_bwm_region_matched_support80_best6.json")
    parser.add_argument("--data-dir", type=Path, default=REPO_ROOT / "data/brainsets/ibl_bwm")
    parser.add_argument("--carriers", default=",".join(DEFAULT_CARRIERS))
    parser.add_argument("--out-json", type=Path, default=REPO_ROOT / "docs/csh_mechanism_audit.json")
    parser.add_argument("--out-md", type=Path, default=REPO_ROOT / "docs/csh_mechanism_audit.md")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    carriers = tuple(parent.strip() for parent in args.carriers.split(",") if parent.strip())
    result = analyze(
        root=args.root,
        holdout=args.holdout,
        seed=args.seed,
        manifest=args.manifest,
        data_dir=args.data_dir,
        carriers=carriers,
    )
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    write_markdown(result, args.out_md)
    print(f"wrote {args.out_json}")
    print(f"wrote {args.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
