"""Audit parent-region support for the CSH_ZAD_019 broadening result."""
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "vendor" / "torch_brain"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from audit_csh_zad_019_signal import parse_lso_rows, parse_split_diagnostics  # noqa: E402
from torch_brain.dataset import Dataset  # noqa: E402
from train import build_trial_samples, manifest_recording_ids, map_region_acronyms  # noqa: E402


@dataclass(frozen=True)
class RegionSignal:
    units: int
    left_trials: int
    right_trials: int
    left_rate: float
    right_rate: float

    @property
    def delta_rate(self) -> float:
        return self.right_rate - self.left_rate

    @property
    def abs_delta_rate(self) -> float:
        return abs(self.delta_rate)


@dataclass(frozen=True)
class CandidateComposition:
    subject: str
    total_units: int
    parent_regions: int
    weighted_jaccard: float
    cosine: float
    ref_unit_mass_present: float
    ref_top_mass_present: float
    ref_top_overlap: int
    weighted_abs_spike_delta: float


def display_path(path: Path) -> str:
    path = path.expanduser()
    if not path.is_absolute():
        return str(path)
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def load_recordings(data_dir: Path, manifest_path: Path) -> tuple[Dataset, list[str]]:
    ds = Dataset(dataset_dir=data_dir, keep_files_open=True)
    requested = manifest_recording_ids(manifest_path)
    missing = sorted(set(requested) - set(ds.recording_ids))
    if missing:
        preview = ", ".join(missing[:5])
        suffix = "" if len(missing) <= 5 else f", ... ({len(missing)} total)"
        raise SystemExit(f"Manifest recordings missing from {data_dir}: {preview}{suffix}")
    return ds, requested


def subject_parent_unit_counts(ds: Dataset, recording_ids: Iterable[str]) -> dict[str, Counter[str]]:
    counts: dict[str, Counter[str]] = defaultdict(Counter)
    for rid in recording_ids:
        rec = ds.get_recording(rid)
        subject = str(rec.subject.id)
        parents = map_region_acronyms(rec.units.region_acronym.astype(str).tolist(), "parent")
        counts[subject].update(parents)
    return dict(counts)


def _safe_rate(spikes: int, units: int, trials: int, window_len: float) -> float:
    denom = units * trials * window_len
    return 0.0 if denom <= 0 else spikes / denom


def recording_parent_spike_counts(rec, window_len: float, target_mode: str) -> dict[str, dict[str, int]]:
    parents = np.asarray(map_region_acronyms(rec.units.region_acronym.astype(str).tolist(), "parent"))
    unique_parents = sorted(set(str(parent) for parent in parents))
    parent_to_idx = {parent: idx for idx, parent in enumerate(unique_parents)}
    unit_parent_idx = np.asarray([parent_to_idx[str(parent)] for parent in parents], dtype=np.int64)
    timestamps = np.asarray(rec.spikes.timestamps)
    spike_unit_index = np.asarray(rec.spikes.unit_index, dtype=np.int64)
    rows = {
        parent: {
            "left_spikes": 0,
            "right_spikes": 0,
            "left_trials": 0,
            "right_trials": 0,
            "units": int(np.sum(parents == parent)),
        }
        for parent in unique_parents
    }
    rid = "recording"
    for _rid, t0, target in build_trial_samples({rid: rec}, [rid], window_len, target_mode):
        side = "right" if target == 1.0 else "left"
        start = int(np.searchsorted(timestamps, t0, side="left"))
        stop = int(np.searchsorted(timestamps, t0 + window_len, side="right"))
        if stop > start:
            parent_counts = np.bincount(unit_parent_idx[spike_unit_index[start:stop]], minlength=len(unique_parents))
        else:
            parent_counts = np.zeros(len(unique_parents), dtype=np.int64)
        for parent, idx in parent_to_idx.items():
            rows[parent][f"{side}_spikes"] += int(parent_counts[idx])
            rows[parent][f"{side}_trials"] += 1
    return rows


def subject_parent_signals(
    ds: Dataset,
    recording_ids: Iterable[str],
    *,
    window_len: float,
    target_mode: str,
) -> dict[str, dict[str, RegionSignal]]:
    raw: dict[str, dict[str, dict[str, int]]] = defaultdict(lambda: defaultdict(lambda: {
        "left_spikes": 0,
        "right_spikes": 0,
        "left_trials": 0,
        "right_trials": 0,
        "units": 0,
    }))
    for rid in recording_ids:
        rec = ds.get_recording(rid)
        subject = str(rec.subject.id)
        for parent, row in recording_parent_spike_counts(rec, window_len, target_mode).items():
            agg = raw[subject][parent]
            agg["left_spikes"] += row["left_spikes"]
            agg["right_spikes"] += row["right_spikes"]
            agg["left_trials"] += row["left_trials"]
            agg["right_trials"] += row["right_trials"]
            agg["units"] += row["units"]
    out: dict[str, dict[str, RegionSignal]] = {}
    for subject, regions in raw.items():
        out[subject] = {}
        for parent, row in regions.items():
            units = row["units"]
            left_trials = row["left_trials"]
            right_trials = row["right_trials"]
            out[subject][parent] = RegionSignal(
                units=units,
                left_trials=left_trials,
                right_trials=right_trials,
                left_rate=_safe_rate(row["left_spikes"], units, left_trials, window_len),
                right_rate=_safe_rate(row["right_spikes"], units, right_trials, window_len),
            )
    return out


def weighted_abs_delta(signals: dict[str, RegionSignal], parents: Iterable[str] | None = None) -> float:
    selected = [signals[parent] for parent in (parents or signals.keys()) if parent in signals]
    total_units = sum(row.units for row in selected)
    if total_units == 0:
        return 0.0
    return sum(row.abs_delta_rate * row.units for row in selected) / total_units


def weighted_jaccard(a: Counter[str], b: Counter[str]) -> float:
    keys = set(a) | set(b)
    denominator = sum(max(a[key], b[key]) for key in keys)
    if denominator == 0:
        return 0.0
    return sum(min(a[key], b[key]) for key in keys) / denominator


def cosine_similarity(a: Counter[str], b: Counter[str]) -> float:
    keys = set(a) | set(b)
    a_norm = math.sqrt(sum(a[key] ** 2 for key in keys))
    b_norm = math.sqrt(sum(b[key] ** 2 for key in keys))
    if a_norm == 0.0 or b_norm == 0.0:
        return 0.0
    return sum(a[key] * b[key] for key in keys) / (a_norm * b_norm)


def reference_mass_present(
    reference: Counter[str],
    candidate: Counter[str],
    parents: Iterable[str] | None = None,
) -> float:
    selected = list(parents or reference.keys())
    total = sum(reference[parent] for parent in selected)
    if total == 0:
        return 0.0
    return sum(reference[parent] for parent in selected if candidate[parent] > 0) / total


def rank_candidate_compositions(
    unit_counts: dict[str, Counter[str]],
    signals: dict[str, dict[str, RegionSignal]],
    *,
    reference_subject: str,
    top_n: int = 12,
) -> list[CandidateComposition]:
    reference = unit_counts[reference_subject]
    ref_top = [parent for parent, _count in reference.most_common(top_n)]
    rows = []
    for subject, counts in unit_counts.items():
        if subject == reference_subject:
            continue
        rows.append(
            CandidateComposition(
                subject=subject,
                total_units=sum(counts.values()),
                parent_regions=len(counts),
                weighted_jaccard=weighted_jaccard(reference, counts),
                cosine=cosine_similarity(reference, counts),
                ref_unit_mass_present=reference_mass_present(reference, counts),
                ref_top_mass_present=reference_mass_present(reference, counts, ref_top),
                ref_top_overlap=len(set(ref_top) & set(counts)),
                weighted_abs_spike_delta=weighted_abs_delta(signals.get(subject, {})),
            )
        )
    return sorted(rows, key=lambda row: (row.weighted_jaccard, row.cosine), reverse=True)


def support_summary(subject: str, counts: dict[str, Counter[str]]) -> dict:
    heldout = counts[subject]
    train = Counter()
    for other, row in counts.items():
        if other != subject:
            train.update(row)
    supported_units = sum(count for parent, count in heldout.items() if train[parent] > 0)
    total_units = sum(heldout.values())
    top = heldout.most_common(8)
    return {
        "total_units": total_units,
        "n_parent_regions": len(heldout),
        "supported_units": supported_units,
        "support_frac": 0.0 if total_units == 0 else supported_units / total_units,
        "top_regions": top,
        "missing_top_regions": [parent for parent, _count in top if train[parent] == 0],
    }


def parse_result_rows(*paths: Path) -> dict[tuple[str, str], dict]:
    rows = []
    for path in paths:
        rows.extend(parse_lso_rows(path, display_path(path)))
    out = {}
    for row in rows:
        out[(row.holdout, row.arm)] = {
            "mean_delta": row.mean_delta,
            "seed_deltas": row.seed_deltas,
            "n_seeds": row.n_seeds,
        }
    return out


def split_allowed_regions(log_path: Path, holdout: str) -> set[str]:
    return {
        parent
        for diag in parse_split_diagnostics(log_path, holdout)
        if diag.region_filter == "shared_regions" and diag.region_granularity == "parent"
        for parent in diag.allowed_regions
    }


def write_report(
    *,
    manifest_path: Path,
    data_dir: Path,
    two_holdout_results: Path,
    csh_results: Path,
    log_path: Path,
    out_path: Path,
    target_mode: str,
    window_len: float,
) -> None:
    ds, recording_ids = load_recordings(data_dir, manifest_path)
    unit_counts = subject_parent_unit_counts(ds, recording_ids)
    signals = subject_parent_signals(ds, recording_ids, window_len=window_len, target_mode=target_mode)
    result_lookup = parse_result_rows(two_holdout_results, csh_results)
    holdouts = ["CSH_ZAD_019", "KS014", "MFD_06"]
    allowed = {
        "CSH_ZAD_019": set(json.loads((REPO_ROOT / "docs/csh_zad_019_demo_metrics.json").read_text())["shared_parent_split"]["allowed_regions"]),
        "KS014": split_allowed_regions(log_path, "KS014"),
        "MFD_06": split_allowed_regions(log_path, "MFD_06"),
    }

    lines = [
        "# Parent-Region Support And Signal Audit",
        "",
        f"Manifest: `{display_path(manifest_path)}`",
        f"Data cache: `{display_path(data_dir)}`",
        f"Target: `{target_mode}` over {window_len:.1f}s stimulus-aligned windows",
        "",
        "## Summary",
        "",
        "| holdout | region_only_delta | shuffle_delta | parent_regions | unit_support | weighted_abs_spike_delta | shared-split_abs_spike_delta | top_missing_parent_regions |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for subject in holdouts:
        support = support_summary(subject, unit_counts)
        region = result_lookup.get((subject, "region_only"), {})
        shuffle = result_lookup.get((subject, "region_shuffle"), {})
        all_signal = weighted_abs_delta(signals.get(subject, {}))
        split_signal = weighted_abs_delta(signals.get(subject, {}), allowed.get(subject, set()))
        lines.append(
            "| "
            f"{subject} | {region.get('mean_delta', 0.0):+.3f} | "
            f"{shuffle.get('mean_delta', 0.0):+.3f} | "
            f"{support['n_parent_regions']} | {support['support_frac']:.1%} | "
            f"{all_signal:.3f} | {split_signal:.3f} | "
            f"{', '.join(support['missing_top_regions']) or 'none'} |"
        )

    lines += [
        "",
        "## Top Parent Regions",
        "",
    ]
    for subject in holdouts:
        lines += [
            f"### {subject}",
            "",
            "| parent | units | left_rate_hz | right_rate_hz | right_minus_left_hz | in_shared_split |",
            "|---|---:|---:|---:|---:|---|",
        ]
        subject_signals = signals.get(subject, {})
        for parent, units in unit_counts[subject].most_common(12):
            row = subject_signals[parent]
            lines.append(
                "| "
                f"{parent} | {units} | {row.left_rate:.3f} | {row.right_rate:.3f} | "
                f"{row.delta_rate:+.3f} | {'yes' if parent in allowed.get(subject, set()) else 'no'} |"
            )
        lines.append("")

    common = set.intersection(*(allowed[subject] for subject in holdouts))
    lines += [
        "## Interpretation",
        "",
        (
            "The weak broadening subjects are not missing global parent-region support. They "
            "have higher support than the strong CSH_ZAD_019 holdout, which rules out a simple "
            "'more shared support means stronger transfer' explanation. The sharper difference "
            "is composition. "
            f"Only {len(common)} parent regions are shared by all three strict splits "
            f"({', '.join(sorted(common))})."
        ),
        "",
        (
            "This supports treating the current result as an anatomical-composition problem, "
            "not a simple data-volume failure. The next paid experiment should not rerun the "
            "same two holdouts unchanged; it should either preselect holdouts whose parent-region "
            "composition resembles CSH_ZAD_019 or restrict all compared holdouts to a common "
            "parent-region panel before training."
        ),
        "",
    ]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines))


def write_candidate_ranking(
    *,
    manifest_path: Path,
    data_dir: Path,
    out_path: Path,
    target_mode: str,
    window_len: float,
    reference_subject: str = "CSH_ZAD_019",
) -> None:
    ds, recording_ids = load_recordings(data_dir, manifest_path)
    unit_counts = subject_parent_unit_counts(ds, recording_ids)
    signals = subject_parent_signals(ds, recording_ids, window_len=window_len, target_mode=target_mode)
    ranked = rank_candidate_compositions(unit_counts, signals, reference_subject=reference_subject)
    reference = unit_counts[reference_subject]
    ref_top = reference.most_common(12)
    best = ranked[0] if ranked else None

    lines = [
        "# CSH_ZAD_019 Composition Candidate Ranking",
        "",
        f"Manifest: `{display_path(manifest_path)}`",
        f"Data cache: `{display_path(data_dir)}`",
        f"Reference holdout: `{reference_subject}`",
        f"Target: `{target_mode}` over {window_len:.1f}s stimulus-aligned windows",
        "",
        "## Reference Composition",
        "",
        f"`{reference_subject}` has {sum(reference.values())} units across {len(reference)} parent regions.",
        "",
        "| parent | units | unit_mass |",
        "|---|---:|---:|",
    ]
    for parent, units in ref_top:
        lines.append(f"| {parent} | {units} | {units / sum(reference.values()):.1%} |")

    lines += [
        "",
        "## Ranked Candidate Holdouts",
        "",
        (
            "The ranking compares each possible held-out subject with `CSH_ZAD_019` using "
            "parent-region unit-count vectors from the matched 28-recording cache. Weighted "
            "Jaccard is the primary score because it penalizes both missing CSH regions and "
            "large extra-region mass; cosine is a secondary shape-similarity check."
        ),
        "",
        "| rank | subject | units | parents | weighted_jaccard | cosine | CSH_unit_mass_present | CSH_top12_mass_present | CSH_top12_overlap | weighted_abs_spike_delta |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for idx, row in enumerate(ranked, start=1):
        lines.append(
            "| "
            f"{idx} | {row.subject} | {row.total_units} | {row.parent_regions} | "
            f"{row.weighted_jaccard:.3f} | {row.cosine:.3f} | "
            f"{row.ref_unit_mass_present:.1%} | {row.ref_top_mass_present:.1%} | "
            f"{row.ref_top_overlap}/12 | {row.weighted_abs_spike_delta:.3f} |"
        )

    lines += [
        "",
        "## Recommendation",
        "",
    ]
    if best:
        lines += [
            (
                f"`{best.subject}` is the best next paid holdout if the goal is to test whether "
                "the strong CSH_ZAD_019 result generalizes to another animal with similar "
                "parent-region composition."
            ),
            "",
        ]
    lines += [
        (
            "`KS014` and `MFD_06` were useful broadening controls, but this ranking explains why "
            "rerunning them unchanged is unlikely to be the cheapest next step: they are among "
            "the least CSH-like subjects by parent-region composition."
        ),
        "",
        (
            "Next paid gate under the budget cap: run one shared-parent true-vs-shuffled control "
            "on the top-ranked candidate first. Continue to a second candidate only if the true "
            "arm beats the shuffled arm and the shared null by a meaningful margin on the first "
            "candidate. This keeps the next cloud spend small and evidence-driven."
        ),
        "",
    ]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=REPO_ROOT / "manifests/ibl_bwm_region_matched_support80_best6.json")
    parser.add_argument("--data-dir", type=Path, default=REPO_ROOT / "data/brainsets/ibl_bwm")
    parser.add_argument("--two-holdout-results", type=Path, default=REPO_ROOT / "docs/lso_two_holdout_shared_parent_shuffle_results.md")
    parser.add_argument("--csh-results", type=Path, default=REPO_ROOT / "docs/lso_csh_zad_019_shared_parent_shuffle_results.md")
    parser.add_argument("--log", type=Path, default=REPO_ROOT / "docs/cloud_phase3_5_runpod.log")
    parser.add_argument("--out", type=Path, default=REPO_ROOT / "docs/parent_region_support_signal_audit.md")
    parser.add_argument("--ranking-out", type=Path, default=REPO_ROOT / "docs/csh_composition_candidate_ranking.md")
    parser.add_argument("--target-mode", default="stimulus_side", choices=["choice", "stimulus_side", "feedback", "prior_side"])
    parser.add_argument("--window-len", type=float, default=1.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    write_report(
        manifest_path=args.manifest,
        data_dir=args.data_dir,
        two_holdout_results=args.two_holdout_results,
        csh_results=args.csh_results,
        log_path=args.log,
        out_path=args.out,
        target_mode=args.target_mode,
        window_len=args.window_len,
    )
    write_candidate_ranking(
        manifest_path=args.manifest,
        data_dir=args.data_dir,
        out_path=args.ranking_out,
        target_mode=args.target_mode,
        window_len=args.window_len,
    )
    print(f"wrote {args.out}")
    print(f"wrote {args.ranking_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
