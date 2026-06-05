"""Diagnose what separates the CSH transfer success from failed follow-ups."""
from __future__ import annotations

import argparse
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from audit_shared_parent_broadening import (  # noqa: E402
    RegionSignal,
    display_path,
    load_recordings,
    recording_parent_spike_counts,
    subject_parent_signals,
    subject_parent_unit_counts,
)
from audit_transfer_failure_modes import controlled_result_lookup, fmt_pct, fmt_signed  # noqa: E402
from define_parent_region_slice import (  # noqa: E402
    select_carriers,
)
from train import map_region_acronyms  # noqa: E402


DEFAULT_HOLDOUTS = ("CSH_ZAD_019", "KS014", "MFD_06", "NR_0019", "NYU-12", "SWC_038", "SWC_043")
DEFAULT_MIN_REFERENCE_UNITS = 100
DEFAULT_MIN_REFERENCE_UNIT_MASS = 0.03
DEFAULT_MIN_REFERENCE_ABS_DELTA = 0.10


@dataclass(frozen=True)
class TransferCompatibility:
    subject: str
    slice_units: int
    carriers_present: int
    csh_weighted_coverage_frac: float
    train_aligned_unit_mass_frac: float | None
    train_aligned_parents: tuple[str, ...]
    train_opposed_parents: tuple[str, ...]
    train_zero_parents: tuple[str, ...]
    min_weighted_abs_train_delta: float
    min_weighted_abs_holdout_delta: float


@dataclass(frozen=True)
class RecordingSlice:
    recording: str
    subject: str
    slice_units: int
    carriers_present: int
    train_aligned_unit_mass_frac: float | None
    present_parents: tuple[str, ...]
    aligned_parents: tuple[str, ...]


def combine_signals(rows: Iterable[RegionSignal]) -> RegionSignal:
    rows = list(rows)
    units = sum(row.units for row in rows)
    left_trials = sum(row.left_trials for row in rows)
    right_trials = sum(row.right_trials for row in rows)
    if units == 0:
        return RegionSignal(units=0, left_trials=left_trials, right_trials=right_trials, left_rate=0.0, right_rate=0.0)
    left_rate = sum(row.left_rate * row.units * row.left_trials for row in rows)
    right_rate = sum(row.right_rate * row.units * row.right_trials for row in rows)
    left_denom = sum(row.units * row.left_trials for row in rows)
    right_denom = sum(row.units * row.right_trials for row in rows)
    return RegionSignal(
        units=units,
        left_trials=left_trials,
        right_trials=right_trials,
        left_rate=0.0 if left_denom == 0 else left_rate / left_denom,
        right_rate=0.0 if right_denom == 0 else right_rate / right_denom,
    )


def leave_subject_out_train_signals(
    subject: str,
    signals: dict[str, dict[str, RegionSignal]],
) -> dict[str, RegionSignal]:
    parents = sorted({parent for other, rows in signals.items() if other != subject for parent in rows})
    out = {}
    for parent in parents:
        out[parent] = combine_signals(rows[parent] for other, rows in signals.items() if other != subject and parent in rows)
    return out


def sign(value: float) -> int:
    if value > 0.0:
        return 1
    if value < 0.0:
        return -1
    return 0


def compatibility_for_subject(
    subject: str,
    carrier_weights: dict[str, float],
    counts: dict[str, Counter[str]],
    signals: dict[str, dict[str, RegionSignal]],
) -> TransferCompatibility:
    carrier_parents = tuple(carrier_weights)
    train_signals = leave_subject_out_train_signals(subject, signals)
    aligned_units = 0
    slice_units = 0
    present_weight = 0.0
    total_carrier_weight = sum(carrier_weights.values())
    aligned_parents = []
    opposed_parents = []
    zero_parents = []
    min_weighted_abs_train_delta = 0.0
    min_weighted_abs_holdout_delta = 0.0
    carriers_present = 0
    for parent in carrier_parents:
        units = counts.get(subject, Counter())[parent]
        if units <= 0 or parent not in signals.get(subject, {}) or parent not in train_signals:
            continue
        carriers_present += 1
        slice_units += units
        present_weight += carrier_weights[parent]
        holdout_delta = signals[subject][parent].delta_rate
        train_delta = train_signals[parent].delta_rate
        weight = min(units, train_signals[parent].units)
        min_weighted_abs_train_delta += weight * abs(train_delta)
        min_weighted_abs_holdout_delta += weight * abs(holdout_delta)
        if sign(holdout_delta) == 0 or sign(train_delta) == 0:
            zero_parents.append(parent)
        elif sign(holdout_delta) == sign(train_delta):
            aligned_units += units
            aligned_parents.append(parent)
        else:
            opposed_parents.append(parent)
    total_weight = sum(min(counts.get(subject, Counter())[parent], train_signals[parent].units) for parent in carrier_parents if parent in train_signals)
    return TransferCompatibility(
        subject=subject,
        slice_units=slice_units,
        carriers_present=carriers_present,
        csh_weighted_coverage_frac=0.0 if total_carrier_weight == 0.0 else present_weight / total_carrier_weight,
        train_aligned_unit_mass_frac=None if slice_units == 0 else aligned_units / slice_units,
        train_aligned_parents=tuple(aligned_parents),
        train_opposed_parents=tuple(opposed_parents),
        train_zero_parents=tuple(zero_parents),
        min_weighted_abs_train_delta=0.0 if total_weight == 0 else min_weighted_abs_train_delta / total_weight,
        min_weighted_abs_holdout_delta=0.0 if total_weight == 0 else min_weighted_abs_holdout_delta / total_weight,
    )


def recording_parent_counts_and_signals(rec, *, window_len: float, target_mode: str) -> tuple[Counter[str], dict[str, RegionSignal]]:
    parents = map_region_acronyms(rec.units.region_acronym.astype(str).tolist(), "parent")
    counts = Counter(parents)
    raw = recording_parent_spike_counts(rec, window_len, target_mode)
    signals = {}
    for parent, row in raw.items():
        units = row["units"]
        left_trials = row["left_trials"]
        right_trials = row["right_trials"]
        left_denom = units * left_trials * window_len
        right_denom = units * right_trials * window_len
        signals[parent] = RegionSignal(
            units=units,
            left_trials=left_trials,
            right_trials=right_trials,
            left_rate=0.0 if left_denom == 0 else row["left_spikes"] / left_denom,
            right_rate=0.0 if right_denom == 0 else row["right_spikes"] / right_denom,
        )
    return counts, signals


def recording_slice_scores(
    ds,
    recording_ids: Iterable[str],
    carrier_weights: dict[str, float],
    train_signals_by_subject: dict[str, dict[str, RegionSignal]],
    *,
    window_len: float,
    target_mode: str,
) -> list[RecordingSlice]:
    rows = []
    carrier_parents = tuple(carrier_weights)
    for rid in recording_ids:
        rec = ds.get_recording(rid)
        subject = str(rec.subject.id)
        counts, signals = recording_parent_counts_and_signals(rec, window_len=window_len, target_mode=target_mode)
        train_signals = train_signals_by_subject[subject]
        slice_units = 0
        aligned_units = 0
        present = []
        aligned = []
        for parent in carrier_parents:
            units = counts[parent]
            if units <= 0 or parent not in signals or parent not in train_signals:
                continue
            present.append(parent)
            slice_units += units
            if sign(signals[parent].delta_rate) != 0 and sign(signals[parent].delta_rate) == sign(train_signals[parent].delta_rate):
                aligned_units += units
                aligned.append(parent)
        rows.append(
            RecordingSlice(
                recording=rid,
                subject=subject,
                slice_units=slice_units,
                carriers_present=len(present),
                train_aligned_unit_mass_frac=None if slice_units == 0 else aligned_units / slice_units,
                present_parents=tuple(present),
                aligned_parents=tuple(aligned),
            )
        )
    return sorted(rows, key=lambda row: (row.slice_units, row.train_aligned_unit_mass_frac or 0.0), reverse=True)


def parent_table(
    subject: str,
    carrier_parents: Iterable[str],
    counts: dict[str, Counter[str]],
    signals: dict[str, dict[str, RegionSignal]],
) -> list[str]:
    train_signals = leave_subject_out_train_signals(subject, signals)
    lines = [
        "| parent | units | train_units | holdout_delta_hz | train_delta_hz | sign_relation |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for parent in carrier_parents:
        units = counts.get(subject, Counter())[parent]
        if units <= 0:
            continue
        holdout_delta = signals[subject][parent].delta_rate
        train = train_signals.get(parent)
        if train is None:
            relation = "missing_train"
            train_units = 0
            train_delta = None
        else:
            train_units = train.units
            train_delta = train.delta_rate
            if sign(holdout_delta) == 0 or sign(train_delta) == 0:
                relation = "zero"
            elif sign(holdout_delta) == sign(train_delta):
                relation = "aligned"
            else:
                relation = "opposed"
        lines.append(
            "| "
            f"{parent} | {units} | {train_units} | {holdout_delta:+.3f} | "
            f"{'n/a' if train_delta is None else f'{train_delta:+.3f}'} | {relation} |"
        )
    return lines


def write_report(
    *,
    manifest_path: Path,
    data_dir: Path,
    result_paths: Iterable[Path],
    out_path: Path,
    target_mode: str,
    window_len: float,
    reference_subject: str,
    holdouts: Iterable[str],
) -> None:
    ds, recording_ids = load_recordings(data_dir, manifest_path)
    counts = subject_parent_unit_counts(ds, recording_ids)
    signals = subject_parent_signals(ds, recording_ids, window_len=window_len, target_mode=target_mode)
    train_panel = Counter()
    for subject, row in counts.items():
        if subject != reference_subject:
            train_panel.update(row)
    carriers = select_carriers(
        counts[reference_subject],
        signals[reference_subject],
        train_panel=set(train_panel),
        min_units=DEFAULT_MIN_REFERENCE_UNITS,
        min_unit_mass=DEFAULT_MIN_REFERENCE_UNIT_MASS,
        min_abs_delta=DEFAULT_MIN_REFERENCE_ABS_DELTA,
    )
    carrier_parents = [carrier.parent for carrier in carriers]
    carrier_weights = {carrier.parent: carrier.weighted_abs_delta for carrier in carriers}
    compatibility = [
        compatibility_for_subject(subject, carrier_weights, counts, signals)
        for subject in holdouts
        if subject in counts
    ]
    results = controlled_result_lookup(result_paths)
    train_signals_by_subject = {
        subject: leave_subject_out_train_signals(subject, signals)
        for subject in counts
    }
    recording_rows = recording_slice_scores(
        ds,
        recording_ids,
        carrier_weights,
        train_signals_by_subject,
        window_len=window_len,
        target_mode=target_mode,
    )

    lines = [
        "# Transfer Success-Mode Audit",
        "",
        f"Manifest: `{display_path(manifest_path)}`",
        f"Data cache: `{display_path(data_dir)}`",
        f"Reference success: `{reference_subject}`",
        f"Target: `{target_mode}` over {window_len:.1f}s stimulus-aligned windows",
        "",
        "## Question",
        "",
        (
            "The previous failure-mode audit showed that global parent-region support, "
            "composition similarity, trial count, class balance, and raw parent-level "
            "contrast do not explain why only `CSH_ZAD_019` has a strong controlled "
            "true-vs-shuffled transfer signal. This audit asks a more model-facing "
            "question: for the CSH-derived carrier parents, does each held-out animal "
            "match the sign of the leave-subject-out training aggregate?"
        ),
        "",
        "## CSH Carrier Parents",
        "",
        "| parent | CSH_units | CSH_delta_hz | units_x_abs_delta |",
        "|---|---:|---:|---:|",
    ]
    for carrier in carriers:
        lines.append(
            "| "
            f"{carrier.parent} | {carrier.units} | {carrier.delta_rate:+.3f} | "
            f"{carrier.weighted_abs_delta:.1f} |"
        )

    lines += [
        "",
        "## Subject Compatibility With LSO Training Aggregate",
        "",
        "| holdout | true_delta | shuffle_delta | true_minus_shuffle | slice_units | carriers_present | CSH_weighted_coverage | train_aligned_unit_mass | aligned_parents | opposed_parents | min_weighted_abs_train_delta | min_weighted_abs_holdout_delta |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|---|---:|---:|",
    ]
    for row in compatibility:
        region = results.get((row.subject, "region_only"))
        shuffle = results.get((row.subject, "region_shuffle"))
        true_delta = None if region is None else region.mean_delta
        shuffle_delta = None if shuffle is None else shuffle.mean_delta
        true_minus_shuffle = None if true_delta is None or shuffle_delta is None else true_delta - shuffle_delta
        lines.append(
            "| "
            f"{row.subject} | {fmt_signed(true_delta)} | {fmt_signed(shuffle_delta)} | "
            f"{fmt_signed(true_minus_shuffle)} | {row.slice_units} | {row.carriers_present}/{len(carrier_parents)} | "
            f"{fmt_pct(row.csh_weighted_coverage_frac)} | {fmt_pct(row.train_aligned_unit_mass_frac)} | "
            f"{', '.join(row.train_aligned_parents) or 'none'} | "
            f"{', '.join(row.train_opposed_parents) or 'none'} | "
            f"{row.min_weighted_abs_train_delta:.3f} | {row.min_weighted_abs_holdout_delta:.3f} |"
        )

    lines += [
        "",
        "## Carrier Parent Details",
        "",
    ]
    for subject in holdouts:
        if subject not in counts:
            continue
        lines += [f"### {subject}", ""]
        lines.extend(parent_table(subject, carrier_parents, counts, signals))
        lines.append("")

    lines += [
        "## Top Recording-Level Carrier Slices",
        "",
        "| recording | subject | slice_units | carriers_present | train_aligned_unit_mass | present_parents | aligned_parents |",
        "|---|---|---:|---:|---:|---|---|",
    ]
    for row in recording_rows[:12]:
        lines.append(
            "| "
            f"{row.recording} | {row.subject} | {row.slice_units} | {row.carriers_present}/{len(carrier_parents)} | "
            f"{fmt_pct(row.train_aligned_unit_mass_frac)} | "
            f"{', '.join(row.present_parents) or 'none'} | {', '.join(row.aligned_parents) or 'none'} |"
        )

    lines += [
        "",
        "## Interpretation",
        "",
        (
            "The fixed `NYU-12` slice failed even though it matched the sign of the "
            "leave-subject-out training aggregate. That rules out a simple sign-alignment "
            "fix. NYU-12 covers only the `CA`, `VP`, and `DG` part of the CSH carrier "
            "pattern and misses the strongest CSH carrier (`PRT`) plus `MOp`; its "
            "CSH-weighted carrier coverage is therefore much lower than the reference "
            "success. In contrast, `MFD_06` and `NR_0019` fail the train-aggregate "
            "alignment screen outright."
        ),
        "",
        (
            "Next gate: before any further GPU spend, require a candidate to clear "
            "support, CSH carrier-weight coverage, and LSO-train compatibility: enough "
            "units in at least two carrier parents, at least 70% of the CSH carrier "
            "weighted signal represented, at least 75% carrier-slice unit mass "
            "sign-aligned to the leave-subject-out training aggregate, and a "
            "pre-registered shuffled-label control. This is stricter than the NYU-12 "
            "gate and directly addresses the paid-run failure."
        ),
        "",
    ]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=REPO_ROOT / "manifests/ibl_bwm_region_matched_support80_best6.json")
    parser.add_argument("--data-dir", type=Path, default=REPO_ROOT / "data/brainsets/ibl_bwm")
    parser.add_argument("--csh-results", type=Path, default=REPO_ROOT / "docs/lso_csh_zad_019_shared_parent_shuffle_results.md")
    parser.add_argument("--two-holdout-results", type=Path, default=REPO_ROOT / "docs/lso_two_holdout_shared_parent_shuffle_results.md")
    parser.add_argument("--nr0019-results", type=Path, default=REPO_ROOT / "docs/lso_nr0019_shared_parent_shuffle_results.md")
    parser.add_argument("--nyu12-results", type=Path, default=REPO_ROOT / "docs/lso_nyu12_parent_slice_results.md")
    parser.add_argument("--out", type=Path, default=REPO_ROOT / "docs/transfer_success_mode_audit.md")
    parser.add_argument("--target-mode", default="stimulus_side", choices=["choice", "stimulus_side", "feedback", "prior_side"])
    parser.add_argument("--window-len", type=float, default=1.0)
    parser.add_argument("--reference-subject", default="CSH_ZAD_019")
    parser.add_argument("--holdouts", nargs="+", default=list(DEFAULT_HOLDOUTS))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    write_report(
        manifest_path=args.manifest,
        data_dir=args.data_dir,
        result_paths=[args.csh_results, args.two_holdout_results, args.nr0019_results, args.nyu12_results],
        out_path=args.out,
        target_mode=args.target_mode,
        window_len=args.window_len,
        reference_subject=args.reference_subject,
        holdouts=args.holdouts,
    )
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
