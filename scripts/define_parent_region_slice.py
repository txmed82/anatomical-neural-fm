"""Define a parent-region slice for the next anatomical-transfer test."""
from __future__ import annotations

import argparse
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from audit_shared_parent_broadening import (  # noqa: E402
    RegionSignal,
    _safe_rate,
    display_path,
    load_recordings,
    recording_parent_spike_counts,
    subject_parent_signals,
    subject_parent_unit_counts,
)
from audit_transfer_failure_modes import shared_parent_panel  # noqa: E402


@dataclass(frozen=True)
class CarrierRegion:
    parent: str
    units: int
    unit_mass: float
    delta_rate: float
    weighted_abs_delta: float


@dataclass(frozen=True)
class SliceScore:
    label: str
    subject: str
    slice_units: int
    present_carriers: int
    carriers_with_min_units: int
    aligned_unit_mass_frac: float
    present_parent_names: tuple[str, ...]
    aligned_parent_names: tuple[str, ...]
    passes_gate: bool


def select_carriers(
    counts: Counter[str],
    signals: dict[str, RegionSignal],
    *,
    train_panel: set[str],
    min_units: int,
    min_unit_mass: float,
    min_abs_delta: float,
) -> list[CarrierRegion]:
    total_units = sum(counts.values())
    carriers = []
    for parent, units in counts.items():
        if parent not in train_panel:
            continue
        unit_mass = 0.0 if total_units == 0 else units / total_units
        delta = signals[parent].delta_rate
        if units < min_units or unit_mass < min_unit_mass or abs(delta) < min_abs_delta:
            continue
        carriers.append(CarrierRegion(
            parent=parent,
            units=units,
            unit_mass=unit_mass,
            delta_rate=delta,
            weighted_abs_delta=units * abs(delta),
        ))
    return sorted(carriers, key=lambda row: row.weighted_abs_delta, reverse=True)


def score_slice(
    *,
    label: str,
    subject: str,
    candidate_counts: Counter[str],
    candidate_signals: dict[str, RegionSignal],
    carriers: list[CarrierRegion],
    min_units_per_parent: int,
    min_slice_units: int,
    min_aligned_unit_mass_frac: float,
    min_carriers_with_units: int,
) -> SliceScore:
    carrier_by_parent = {carrier.parent: carrier for carrier in carriers}
    present = [parent for parent in carrier_by_parent if candidate_counts[parent] > 0 and parent in candidate_signals]
    slice_units = sum(candidate_counts[parent] for parent in present)
    aligned = [
        parent for parent in present
        if carrier_by_parent[parent].delta_rate * candidate_signals[parent].delta_rate > 0
    ]
    aligned_units = sum(candidate_counts[parent] for parent in aligned)
    enough = [parent for parent in present if candidate_counts[parent] >= min_units_per_parent]
    aligned_frac = 0.0 if slice_units == 0 else aligned_units / slice_units
    passes = (
        slice_units >= min_slice_units
        and len(enough) >= min_carriers_with_units
        and aligned_frac >= min_aligned_unit_mass_frac
    )
    return SliceScore(
        label=label,
        subject=subject,
        slice_units=slice_units,
        present_carriers=len(present),
        carriers_with_min_units=len(enough),
        aligned_unit_mass_frac=aligned_frac,
        present_parent_names=tuple(present),
        aligned_parent_names=tuple(aligned),
        passes_gate=passes,
    )


def recording_signal_rows(rec, *, window_len: float, target_mode: str) -> dict[str, RegionSignal]:
    raw = recording_parent_spike_counts(rec, window_len, target_mode)
    rows = {}
    for parent, row in raw.items():
        units = row["units"]
        rows[parent] = RegionSignal(
            units=units,
            left_trials=row["left_trials"],
            right_trials=row["right_trials"],
            left_rate=_safe_rate(row["left_spikes"], units, row["left_trials"], window_len),
            right_rate=_safe_rate(row["right_spikes"], units, row["right_trials"], window_len),
        )
    return rows


def fmt_pct(value: float) -> str:
    return f"{value:.1%}"


def write_report(
    *,
    manifest_path: Path,
    data_dir: Path,
    out_path: Path,
    reference_subject: str,
    target_mode: str,
    window_len: float,
    min_reference_units: int,
    min_reference_unit_mass: float,
    min_reference_abs_delta: float,
    min_candidate_units_per_parent: int,
    min_candidate_slice_units: int,
    min_candidate_aligned_mass: float,
    min_candidate_carriers: int,
) -> None:
    ds, recording_ids = load_recordings(data_dir, manifest_path)
    counts = subject_parent_unit_counts(ds, recording_ids)
    signals = subject_parent_signals(ds, recording_ids, window_len=window_len, target_mode=target_mode)
    carriers = select_carriers(
        counts[reference_subject],
        signals[reference_subject],
        train_panel=shared_parent_panel(reference_subject, counts),
        min_units=min_reference_units,
        min_unit_mass=min_reference_unit_mass,
        min_abs_delta=min_reference_abs_delta,
    )

    subject_scores = []
    for subject in sorted(counts):
        if subject == reference_subject:
            continue
        subject_scores.append(score_slice(
            label=subject,
            subject=subject,
            candidate_counts=counts[subject],
            candidate_signals=signals[subject],
            carriers=carriers,
            min_units_per_parent=min_candidate_units_per_parent,
            min_slice_units=min_candidate_slice_units,
            min_aligned_unit_mass_frac=min_candidate_aligned_mass,
            min_carriers_with_units=min_candidate_carriers,
        ))
    subject_scores.sort(key=lambda row: (row.passes_gate, row.aligned_unit_mass_frac, row.slice_units), reverse=True)

    recording_scores = []
    for rid in recording_ids:
        rec = ds.get_recording(rid)
        subject = str(rec.subject.id)
        if subject == reference_subject:
            continue
        rec_signals = recording_signal_rows(rec, window_len=window_len, target_mode=target_mode)
        rec_counts = Counter({parent: row.units for parent, row in rec_signals.items()})
        recording_scores.append(score_slice(
            label=rid,
            subject=subject,
            candidate_counts=rec_counts,
            candidate_signals=rec_signals,
            carriers=carriers,
            min_units_per_parent=min_candidate_units_per_parent,
            min_slice_units=min_candidate_slice_units,
            min_aligned_unit_mass_frac=min_candidate_aligned_mass,
            min_carriers_with_units=min_candidate_carriers,
        ))
    recording_scores.sort(key=lambda row: (row.passes_gate, row.aligned_unit_mass_frac, row.slice_units), reverse=True)

    lines = [
        "# Parent-Region Slice Plan",
        "",
        f"Manifest: `{display_path(manifest_path)}`",
        f"Data cache: `{display_path(data_dir)}`",
        f"Reference holdout: `{reference_subject}`",
        f"Target: `{target_mode}` over {window_len:.1f}s stimulus-aligned windows",
        "",
        "## Slice Definition",
        "",
        "Reference carrier criteria:",
        "",
        f"- parent is present in both train and `{reference_subject}` held-out split",
        f"- at least {min_reference_units} `{reference_subject}` units",
        f"- at least {fmt_pct(min_reference_unit_mass)} of `{reference_subject}` units",
        f"- absolute right-minus-left spike-rate contrast at least {min_reference_abs_delta:.3f} Hz",
        "",
        "Candidate inclusion gate:",
        "",
        f"- at least {min_candidate_slice_units} units in the carrier-region slice",
        f"- at least {min_candidate_carriers} carrier parents with >= {min_candidate_units_per_parent} units",
        f"- at least {fmt_pct(min_candidate_aligned_mass)} of carrier-slice units have the same stimulus-side contrast sign as `{reference_subject}`",
        "",
        "## CSH Carrier Parents",
        "",
        "| parent | CSH_units | CSH_unit_mass | CSH_right_minus_left_hz | units_x_abs_delta |",
        "|---|---:|---:|---:|---:|",
    ]
    for carrier in carriers:
        lines.append(
            "| "
            f"{carrier.parent} | {carrier.units} | {fmt_pct(carrier.unit_mass)} | "
            f"{carrier.delta_rate:+.3f} | {carrier.weighted_abs_delta:.1f} |"
        )

    lines += [
        "",
        "## Subject-Level Candidate Scores",
        "",
        "| subject | pass | slice_units | present_carriers | carriers_with_min_units | aligned_unit_mass | present_parents | aligned_parents |",
        "|---|---|---:|---:|---:|---:|---|---|",
    ]
    for row in subject_scores:
        lines.append(
            "| "
            f"{row.subject} | {'yes' if row.passes_gate else 'no'} | {row.slice_units} | "
            f"{row.present_carriers}/{len(carriers)} | {row.carriers_with_min_units} | "
            f"{fmt_pct(row.aligned_unit_mass_frac)} | "
            f"{', '.join(row.present_parent_names) or 'none'} | "
            f"{', '.join(row.aligned_parent_names) or 'none'} |"
        )

    lines += [
        "",
        "## Recording-Level Candidate Scores",
        "",
        "| recording | subject | pass | slice_units | present_carriers | carriers_with_min_units | aligned_unit_mass | present_parents | aligned_parents |",
        "|---|---|---|---:|---:|---:|---:|---|---|",
    ]
    for row in recording_scores[:12]:
        lines.append(
            "| "
            f"{row.label} | {row.subject} | {'yes' if row.passes_gate else 'no'} | "
            f"{row.slice_units} | {row.present_carriers}/{len(carriers)} | "
            f"{row.carriers_with_min_units} | {fmt_pct(row.aligned_unit_mass_frac)} | "
            f"{', '.join(row.present_parent_names) or 'none'} | "
            f"{', '.join(row.aligned_parent_names) or 'none'} |"
        )

    passing_subjects = [row.subject for row in subject_scores if row.passes_gate]
    passing_recordings = [row for row in recording_scores if row.passes_gate]
    lines += [
        "",
        "## Decision",
        "",
    ]
    if passing_subjects:
        lines += [
            (
                f"The current matched cache contains subject-level slice candidates: "
                f"{', '.join(passing_subjects)}. The cleanest next paid test is not a broad "
                "matched-cache sweep; it is a fixed carrier-parent true-vs-shuffled control "
                "on the top passing subject using the explicit parent-region include filter."
            ),
            "",
        ]
    else:
        lines += [
            (
                "No subject in the current matched cache passes the slice gate. The next step "
                "would be a metadata/cache search for subjects with these carrier parents, not "
                "a GPU training run."
            ),
            "",
        ]
    if passing_recordings:
        lines += [
            (
                "At recording level, the strongest slice candidate is "
                f"`{passing_recordings[0].label}` from `{passing_recordings[0].subject}`. "
                "This supports using the slice as an inclusion rule, but a subject-level "
                "cross-animal claim still needs whole-subject held-out evaluation."
            ),
            "",
        ]
    lines += [
        (
            "Next implementation gate before GPU spend: run local/preflight checks for the "
            "fixed carrier-parent include list using `--region-filter include_regions` and "
            f"`--region-include \"{', '.join(carrier.parent for carrier in carriers)}\"`, "
            "then launch only if the RunPod cost guard remains below the $100 cap."
        ),
        "",
    ]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=REPO_ROOT / "manifests/ibl_bwm_region_matched_support80_best6.json")
    parser.add_argument("--data-dir", type=Path, default=REPO_ROOT / "data/brainsets/ibl_bwm")
    parser.add_argument("--out", type=Path, default=REPO_ROOT / "docs/parent_region_slice_plan.md")
    parser.add_argument("--reference-subject", default="CSH_ZAD_019")
    parser.add_argument("--target-mode", default="stimulus_side", choices=["choice", "stimulus_side"])
    parser.add_argument("--window-len", type=float, default=1.0)
    parser.add_argument("--min-reference-units", type=int, default=100)
    parser.add_argument("--min-reference-unit-mass", type=float, default=0.03)
    parser.add_argument("--min-reference-abs-delta", type=float, default=0.10)
    parser.add_argument("--min-candidate-units-per-parent", type=int, default=50)
    parser.add_argument("--min-candidate-slice-units", type=int, default=500)
    parser.add_argument("--min-candidate-aligned-mass", type=float, default=0.75)
    parser.add_argument("--min-candidate-carriers", type=int, default=2)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    write_report(
        manifest_path=args.manifest,
        data_dir=args.data_dir,
        out_path=args.out,
        reference_subject=args.reference_subject,
        target_mode=args.target_mode,
        window_len=args.window_len,
        min_reference_units=args.min_reference_units,
        min_reference_unit_mass=args.min_reference_unit_mass,
        min_reference_abs_delta=args.min_reference_abs_delta,
        min_candidate_units_per_parent=args.min_candidate_units_per_parent,
        min_candidate_slice_units=args.min_candidate_slice_units,
        min_candidate_aligned_mass=args.min_candidate_aligned_mass,
        min_candidate_carriers=args.min_candidate_carriers,
    )
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
