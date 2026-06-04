"""Compare controlled cross-animal transfer successes and failures."""
from __future__ import annotations

import argparse
import math
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from audit_csh_zad_019_signal import ResultRow, parse_lso_rows  # noqa: E402
from audit_shared_parent_broadening import (  # noqa: E402
    RegionSignal,
    cosine_similarity,
    display_path,
    load_recordings,
    subject_parent_signals,
    subject_parent_unit_counts,
    weighted_abs_delta,
    weighted_jaccard,
)
from train import build_trial_samples  # noqa: E402


CONTROLLED_HOLDOUTS = ("CSH_ZAD_019", "KS014", "MFD_06", "NR_0019")


@dataclass(frozen=True)
class Alignment:
    weighted_corr: float | None
    same_sign_mass_frac: float | None


def controlled_result_lookup(paths: Iterable[Path]) -> dict[tuple[str, str], ResultRow]:
    rows: list[ResultRow] = []
    for path in paths:
        rows.extend(parse_lso_rows(path, display_path(path)))
    return {(row.holdout, row.arm): row for row in rows}


def subject_trial_balance(ds, recording_ids: Iterable[str], *, window_len: float, target_mode: str) -> dict[str, Counter[str]]:
    balances: dict[str, Counter[str]] = defaultdict(Counter)
    for rid in recording_ids:
        rec = ds.get_recording(rid)
        subject = str(rec.subject.id)
        for _rid, _t0, target in build_trial_samples({rid: rec}, [rid], window_len, target_mode):
            balances[subject]["R" if target == 1.0 else "L"] += 1
    return dict(balances)


def shared_parent_panel(subject: str, counts: dict[str, Counter[str]]) -> set[str]:
    train = Counter()
    for other, row in counts.items():
        if other != subject:
            train.update(row)
    return {parent for parent in counts[subject] if train[parent] > 0}


def weighted_signal_alignment(
    reference: str,
    candidate: str,
    counts: dict[str, Counter[str]],
    signals: dict[str, dict[str, RegionSignal]],
) -> Alignment:
    common = sorted(set(signals.get(reference, {})) & set(signals.get(candidate, {})))
    weights = [min(counts[reference][parent], counts[candidate][parent]) for parent in common]
    total_weight = sum(weights)
    if total_weight == 0:
        return Alignment(None, None)
    ref_values = [signals[reference][parent].delta_rate for parent in common]
    cand_values = [signals[candidate][parent].delta_rate for parent in common]
    ref_mean = sum(weight * value for weight, value in zip(weights, ref_values)) / total_weight
    cand_mean = sum(weight * value for weight, value in zip(weights, cand_values)) / total_weight
    covariance = sum(
        weight * (ref_value - ref_mean) * (cand_value - cand_mean)
        for weight, ref_value, cand_value in zip(weights, ref_values, cand_values)
    ) / total_weight
    ref_var = sum(weight * (value - ref_mean) ** 2 for weight, value in zip(weights, ref_values)) / total_weight
    cand_var = sum(weight * (value - cand_mean) ** 2 for weight, value in zip(weights, cand_values)) / total_weight
    corr = None if ref_var == 0.0 or cand_var == 0.0 else covariance / math.sqrt(ref_var * cand_var)
    same_sign_weight = sum(
        weight
        for weight, ref_value, cand_value in zip(weights, ref_values, cand_values)
        if ref_value * cand_value > 0
    )
    return Alignment(corr, same_sign_weight / total_weight)


def baseline_auc(row: ResultRow | None) -> float | None:
    if row is None or row.mean_auc is None:
        return None
    return row.mean_auc - row.mean_delta


def fmt_float(value: float | None, digits: int = 3) -> str:
    return "n/a" if value is None else f"{value:.{digits}f}"


def fmt_signed(value: float | None, digits: int = 3) -> str:
    return "n/a" if value is None else f"{value:+.{digits}f}"


def fmt_pct(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.1%}"


def positive_seeds(row: ResultRow | None) -> str:
    if row is None:
        return "n/a"
    return f"{sum(1 for delta in row.seed_deltas if delta > 0)}/{len(row.seed_deltas)}"


def write_report(
    *,
    manifest_path: Path,
    data_dir: Path,
    result_paths: Iterable[Path],
    out_path: Path,
    target_mode: str,
    window_len: float,
    reference_subject: str = "CSH_ZAD_019",
) -> None:
    ds, recording_ids = load_recordings(data_dir, manifest_path)
    counts = subject_parent_unit_counts(ds, recording_ids)
    signals = subject_parent_signals(ds, recording_ids, window_len=window_len, target_mode=target_mode)
    balances = subject_trial_balance(ds, recording_ids, window_len=window_len, target_mode=target_mode)
    results = controlled_result_lookup(result_paths)
    reference_counts = counts[reference_subject]

    lines = [
        "# Cross-Holdout Transfer Failure-Mode Audit",
        "",
        f"Manifest: `{display_path(manifest_path)}`",
        f"Data cache: `{display_path(data_dir)}`",
        f"Target: `{target_mode}` over {window_len:.1f}s stimulus-aligned windows",
        "",
        "## Controlled Holdout Summary",
        "",
        "| holdout | true_delta | shuffle_delta | true_minus_shuffle | true_positive_seeds | baseline_auc | eval_trials | eval_R_frac | parent_regions | unit_support | wj_to_CSH | cosine_to_CSH | weighted_abs_spike_delta | shared_abs_spike_delta | CSH_delta_corr | CSH_same_sign_mass |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for subject in CONTROLLED_HOLDOUTS:
        region = results.get((subject, "region_only"))
        shuffle = results.get((subject, "region_shuffle"))
        panel = shared_parent_panel(subject, counts)
        total_units = sum(counts[subject].values())
        supported_units = sum(counts[subject][parent] for parent in panel)
        balance = balances.get(subject, Counter())
        eval_trials = sum(balance.values())
        eval_r_frac = None if eval_trials == 0 else balance["R"] / eval_trials
        alignment = Alignment(None, None) if subject == reference_subject else weighted_signal_alignment(
            reference_subject,
            subject,
            counts,
            signals,
        )
        true_delta = region.mean_delta if region else None
        shuffle_delta = shuffle.mean_delta if shuffle else None
        true_minus_shuffle = None if true_delta is None or shuffle_delta is None else true_delta - shuffle_delta
        lines.append(
            "| "
            f"{subject} | {fmt_signed(true_delta)} | {fmt_signed(shuffle_delta)} | "
            f"{fmt_signed(true_minus_shuffle)} | {positive_seeds(region)} | "
            f"{fmt_float(baseline_auc(region))} | {eval_trials} | {fmt_pct(eval_r_frac)} | "
            f"{len(counts[subject])} | {fmt_pct(0.0 if total_units == 0 else supported_units / total_units)} | "
            f"{fmt_float(1.0 if subject == reference_subject else weighted_jaccard(reference_counts, counts[subject]))} | "
            f"{fmt_float(1.0 if subject == reference_subject else cosine_similarity(reference_counts, counts[subject]))} | "
            f"{weighted_abs_delta(signals[subject]):.3f} | {weighted_abs_delta(signals[subject], panel):.3f} | "
            f"{fmt_float(alignment.weighted_corr)} | {fmt_pct(alignment.same_sign_mass_frac)} |"
        )

    lines += [
        "",
        "## Top Parent-Level Stimulus Contrasts",
        "",
        (
            "Rows are ranked by `units * abs(right_minus_left_hz)`. These are not model "
            "attribution scores; they identify where simple parent-level stimulus-side "
            "spike-rate contrast is concentrated in the held-out animal."
        ),
        "",
    ]
    for subject in CONTROLLED_HOLDOUTS:
        panel = shared_parent_panel(subject, counts)
        total_units = sum(counts[subject].values())
        ranked = sorted(
            counts[subject],
            key=lambda parent: counts[subject][parent] * signals[subject][parent].abs_delta_rate,
            reverse=True,
        )
        lines += [
            f"### {subject}",
            "",
            "| parent | units | unit_mass | right_minus_left_hz | in_train_panel |",
            "|---|---:|---:|---:|---|",
        ]
        for parent in ranked[:10]:
            row = signals[subject][parent]
            lines.append(
                "| "
                f"{parent} | {counts[subject][parent]} | {counts[subject][parent] / total_units:.1%} | "
                f"{row.delta_rate:+.3f} | {'yes' if parent in panel else 'no'} |"
            )
        lines.append("")

    lines += [
        "## Interpretation",
        "",
        (
            "`CSH_ZAD_019` remains the only controlled holdout with a strong true-label "
            "effect over both the shared null and shuffled-label control. The three "
            "follow-ups do not fail for one simple reason: `KS014` and `MFD_06` have very "
            "high parent-region support, while `NR_0019` is the most CSH-like by composition "
            "and has the largest raw parent-level spike-rate contrast."
        ),
        "",
        (
            "This argues against spending on another broad leave-subject-out sweep. Parent "
            "composition, global support fraction, trial count, class balance, and raw "
            "parent-level spike contrast are all insufficient as single gates. The next "
            "defensible target is a narrower mechanistic slice: identify which CSH parent "
            "regions carry transferable signal and test only held-out subjects/sessions where "
            "those same parents have enough units and aligned stimulus-side contrast."
        ),
        "",
        (
            "No additional GPU rental is justified until that slice is specified as an "
            "explicit inclusion rule with a pre-registered true-vs-shuffled control."
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
    parser.add_argument("--out", type=Path, default=REPO_ROOT / "docs/cross_holdout_failure_mode_audit.md")
    parser.add_argument("--target-mode", default="stimulus_side", choices=["choice", "stimulus_side"])
    parser.add_argument("--window-len", type=float, default=1.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    write_report(
        manifest_path=args.manifest,
        data_dir=args.data_dir,
        result_paths=[args.csh_results, args.two_holdout_results, args.nr0019_results],
        out_path=args.out,
        target_mode=args.target_mode,
        window_len=args.window_len,
    )
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
