"""Build a focused evidence audit for the CSH_ZAD_019 transfer signal."""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class ResultRow:
    source: str
    holdout: str
    arm: str
    n_seeds: int
    mean_auc: float | None
    mean_delta: float
    seed_deltas: tuple[float, ...]


@dataclass(frozen=True)
class SplitDiagnostic:
    region_filter: str
    region_granularity: str
    n_allowed_regions: int | None
    allowed_regions: tuple[str, ...]
    n_train_trials: int
    n_eval_trials: int
    train_class_balance: dict[str, int]
    eval_class_balance: dict[str, int]
    train_subjects: tuple[str, ...]
    eval_subjects: tuple[str, ...]


def display_path(path: Path) -> str:
    path = path.expanduser()
    if not path.is_absolute():
        return str(path)
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def parse_delta_list(value: str) -> tuple[float, ...]:
    return tuple(float(part) for part in value.split(",") if part.strip())


def parse_lso_rows(path: Path, source_label: str) -> list[ResultRow]:
    """Parse leave-subject-out markdown summary rows from a result document."""
    if not path.exists():
        return []
    rows: list[ResultRow] = []
    for line in path.read_text().splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 6 or cells[0] in {"holdout", "---"}:
            continue
        holdout, arm, n_seeds, mean_auc, mean_delta, seed_deltas = cells
        try:
            rows.append(ResultRow(
                source=source_label,
                holdout=holdout,
                arm=arm,
                n_seeds=int(n_seeds),
                mean_auc=None if mean_auc == "n/a" else float(mean_auc),
                mean_delta=float(mean_delta),
                seed_deltas=parse_delta_list(seed_deltas),
            ))
        except ValueError:
            continue
    return rows


def parse_manual_delta_rows(path: Path, source_label: str) -> list[ResultRow]:
    """Parse older manually recovered tables without mean_AUC columns."""
    if not path.exists():
        return []
    rows: list[ResultRow] = []
    for line in path.read_text().splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 5 or cells[0] in {"holdout", "---"}:
            continue
        holdout, arm, n_pairs, mean_delta, seed_deltas = cells
        try:
            rows.append(ResultRow(
                source=source_label,
                holdout=holdout,
                arm=arm,
                n_seeds=int(n_pairs),
                mean_auc=None,
                mean_delta=float(mean_delta),
                seed_deltas=parse_delta_list(seed_deltas),
            ))
        except ValueError:
            continue
    return rows


def rows_for(rows: Iterable[ResultRow], holdout: str, arms: set[str] | None = None) -> list[ResultRow]:
    return [
        row for row in rows
        if row.holdout == holdout and (arms is None or row.arm in arms)
    ]


def combine_rows(rows: Iterable[ResultRow], *, source: str, holdout: str, arm: str) -> ResultRow | None:
    seed_deltas: list[float] = []
    aucs: list[float] = []
    for row in rows:
        if row.holdout == holdout and row.arm == arm:
            seed_deltas.extend(row.seed_deltas)
            if row.mean_auc is not None:
                aucs.extend([row.mean_auc] * row.n_seeds)
    if not seed_deltas:
        return None
    return ResultRow(
        source=source,
        holdout=holdout,
        arm=arm,
        n_seeds=len(seed_deltas),
        mean_auc=mean(aucs) if aucs else None,
        mean_delta=mean(seed_deltas),
        seed_deltas=tuple(seed_deltas),
    )


def load_manifest_subject(manifest_path: Path, subject: str) -> dict:
    manifest = json.loads(manifest_path.read_text())
    rows = [row for row in manifest.get("recordings", []) if row.get("subject_id") == subject]
    return {
        "n_recordings": len(rows),
        "n_units_meta": sum(int(row.get("n_units_meta") or 0) for row in rows),
        "labs": sorted({str(row.get("lab")) for row in rows if row.get("lab")}),
        "probes": sorted({str(row.get("probe_name")) for row in rows if row.get("probe_name")}),
        "recordings": rows,
        "manifest_n_recordings": len(manifest.get("recordings", [])),
        "manifest_n_subjects": len({row.get("subject_id") for row in manifest.get("recordings", [])}),
    }


def parse_split_diagnostics(log_path: Path, holdout: str) -> list[SplitDiagnostic]:
    if not log_path.exists():
        return []
    diagnostics: list[SplitDiagnostic] = []
    for line in log_path.read_text(errors="replace").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("event") != "split":
            continue
        if holdout not in event.get("holdout_subjects", []):
            continue
        diagnostics.append(SplitDiagnostic(
            region_filter=str(event.get("region_filter", "none")),
            region_granularity=str(event.get("region_granularity", "fine")),
            n_allowed_regions=event.get("n_allowed_regions"),
            allowed_regions=tuple(event.get("allowed_regions", [])),
            n_train_trials=int(event.get("n_train_trials", 0)),
            n_eval_trials=int(event.get("n_eval_trials", 0)),
            train_class_balance={str(k): int(v) for k, v in event.get("train_class_balance", {}).items()},
            eval_class_balance={str(k): int(v) for k, v in event.get("eval_class_balance", {}).items()},
            train_subjects=tuple(event.get("train_subjects", [])),
            eval_subjects=tuple(event.get("eval_subjects", [])),
        ))
    return diagnostics


def fmt_delta(value: float) -> str:
    return f"{value:+.3f}"


def fmt_auc(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.3f}"


def fmt_deltas(values: Iterable[float]) -> str:
    return ",".join(fmt_delta(value) for value in values)


def write_report(
    *,
    manifest_path: Path,
    seed0_path: Path,
    confirm_path: Path,
    fine_shuffle_path: Path,
    shared_parent_path: Path,
    log_path: Path,
    out_path: Path,
    holdout: str,
) -> None:
    seed0_rows = parse_manual_delta_rows(seed0_path, "matched seed0 screen")
    confirm_rows = parse_lso_rows(confirm_path, "matched seeds1-2 confirmation")
    fine_rows = parse_lso_rows(fine_shuffle_path, "fine region shuffle control")
    parent_rows = parse_lso_rows(shared_parent_path, "shared-parent shuffle control")
    combined_region = combine_rows(
        [*seed0_rows, *confirm_rows],
        source="matched seed0 + seeds1-2",
        holdout=holdout,
        arm="region_only",
    )
    combined_pure = combine_rows(
        [*seed0_rows, *confirm_rows],
        source="matched seed0 + seeds1-2",
        holdout=holdout,
        arm="pure_anatomy",
    )
    manifest_subject = load_manifest_subject(manifest_path, holdout)
    split_diagnostics = parse_split_diagnostics(log_path, holdout)
    shared_parent_split = next(
        (
            diag for diag in split_diagnostics
            if diag.region_filter == "shared_regions" and diag.region_granularity == "parent"
        ),
        None,
    )

    evidence_rows = [
        *rows_for(seed0_rows, holdout, {"pure_anatomy", "region_only"}),
        *rows_for(confirm_rows, holdout, {"pure_anatomy", "region_only"}),
    ]
    if combined_pure is not None:
        evidence_rows.append(combined_pure)
    if combined_region is not None:
        evidence_rows.append(combined_region)
    evidence_rows.extend(rows_for(fine_rows, holdout, {"region_only", "region_shuffle"}))
    evidence_rows.extend(rows_for(parent_rows, holdout, {"region_only", "region_shuffle"}))

    lines = [
        "# CSH_ZAD_019 Cross-Animal Anatomy Signal Audit",
        "",
        f"Holdout: `{holdout}`",
        f"Manifest: `{display_path(manifest_path)}`",
        "",
        "## Data Footprint",
        "",
        (
            f"The matched manifest contains {manifest_subject['manifest_n_recordings']} recordings "
            f"from {manifest_subject['manifest_n_subjects']} subjects. `{holdout}` contributes "
            f"{manifest_subject['n_recordings']} recordings, {manifest_subject['n_units_meta']} "
            "metadata units, and probes "
            f"{', '.join(manifest_subject['probes']) or 'n/a'} from "
            f"{', '.join(manifest_subject['labs']) or 'n/a'}."
        ),
        "",
    ]
    if shared_parent_split is not None:
        lines += [
            "## Shared-Parent Split Diagnostic",
            "",
            (
                f"The stricter control used `{shared_parent_split.region_filter}` with "
                f"`{shared_parent_split.region_granularity}` region labels, leaving "
                f"{shared_parent_split.n_allowed_regions} shared parent regions."
            ),
            "",
            "| train_subjects | eval_subjects | train_trials | eval_trials | train_balance | eval_balance |",
            "|---|---|---:|---:|---|---|",
            (
                "| "
                f"{', '.join(shared_parent_split.train_subjects)} | "
                f"{', '.join(shared_parent_split.eval_subjects)} | "
                f"{shared_parent_split.n_train_trials} | {shared_parent_split.n_eval_trials} | "
                f"{shared_parent_split.train_class_balance} | {shared_parent_split.eval_class_balance} |"
            ),
            "",
            "Allowed parent regions:",
            "",
            "`" + "`, `".join(shared_parent_split.allowed_regions) + "`",
            "",
        ]

    lines += [
        "## Evidence Ladder",
        "",
        "| source | arm | n_seeds | mean_AUC | mean_delta_vs_shared | seed_deltas | positive_seeds |",
        "|---|---|---:|---:|---:|---|---:|",
    ]
    for row in evidence_rows:
        positives = sum(1 for delta in row.seed_deltas if delta > 0)
        lines.append(
            "| "
            f"{row.source} | {row.arm} | {row.n_seeds} | {fmt_auc(row.mean_auc)} | "
            f"{fmt_delta(row.mean_delta)} | {fmt_deltas(row.seed_deltas)} | "
            f"{positives}/{len(row.seed_deltas)} |"
        )

    lines += [
        "",
        "## Interpretation",
        "",
        (
            "The strongest current evidence is not a broad aggregate gain; it is a "
            "controlled single-holdout signal. `CSH_ZAD_019` is positive for "
            "`region_only` across the matched seed0 screen and the two confirmation "
            "seeds, and the effect persists under two label-identity controls."
        ),
        "",
        (
            "The fine-region control shows true labels at +0.042 mean delta while "
            "shuffled labels are -0.012. The stricter shared-parent control shows "
            "true labels at +0.038 while shuffled parent labels are also -0.012. "
            "That makes a simple model-capacity or marginal label-frequency "
            "explanation unlikely."
        ),
        "",
        (
            "The honest claim is still subject-specific: this is a credible demo "
            "nucleus for cross-animal anatomical transfer, not yet evidence that "
            "the effect is general across IBL animals. The next paid experiment "
            "should broaden the same shared-parent true-vs-shuffled control to a "
            "small number of additional matched holdouts instead of rerunning "
            "`CSH_ZAD_019` again."
        ),
        "",
        "## Source Documents",
        "",
        f"- `{display_path(seed0_path)}`",
        f"- `{display_path(confirm_path)}`",
        f"- `{display_path(fine_shuffle_path)}`",
        f"- `{display_path(shared_parent_path)}`",
        f"- `{display_path(log_path)}`",
        "",
    ]

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=REPO_ROOT / "manifests/ibl_bwm_region_matched_support80_best6.json")
    parser.add_argument("--seed0-results", type=Path, default=REPO_ROOT / "docs/lso_matched_support80_best6_seed0_results.md")
    parser.add_argument("--confirm-results", type=Path, default=REPO_ROOT / "docs/lso_matched_support80_best6_confirm_results.md")
    parser.add_argument("--fine-shuffle-results", type=Path, default=REPO_ROOT / "docs/lso_csh_zad_019_region_shuffle_results.md")
    parser.add_argument("--shared-parent-results", type=Path, default=REPO_ROOT / "docs/lso_csh_zad_019_shared_parent_shuffle_results.md")
    parser.add_argument("--log", type=Path, default=REPO_ROOT / "docs/cloud_phase3_5_runpod.log")
    parser.add_argument("--out", type=Path, default=REPO_ROOT / "docs/csh_zad_019_signal_audit.md")
    parser.add_argument("--holdout", default="CSH_ZAD_019")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    write_report(
        manifest_path=args.manifest,
        seed0_path=args.seed0_results,
        confirm_path=args.confirm_results,
        fine_shuffle_path=args.fine_shuffle_results,
        shared_parent_path=args.shared_parent_results,
        log_path=args.log,
        out_path=args.out,
        holdout=args.holdout,
    )
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
