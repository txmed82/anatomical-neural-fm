"""Summarize the current anatomy-transfer experiment state.

The project has accumulated several generations of controls. This script keeps
the decision logic explicit so the next action follows current artifacts rather
than the last promising-looking partial result.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from audit_csh_zad_019_signal import parse_lso_rows  # noqa: E402


@dataclass(frozen=True)
class StrictGateRow:
    label: str
    holdout: str
    pass_gate: bool
    centered_delta: float | None
    paired_true_vs_shuffle: float | None
    specificity_gap: float | None
    target0_true_class_improved: float | None
    target1_true_class_improved: float | None
    sign_flip_p: float | None
    source: Path


@dataclass(frozen=True)
class SliceRow:
    label: str
    holdout: str
    true_delta: float | None
    shuffle_delta: float | None
    true_minus_shuffle: float | None
    true_positive: str
    shuffle_positive: str
    source: Path


STRICT_GATE_FILES = (
    ("CSH centered original", "docs/lso_csh_full_eval_centered_anatomy_specific_gate.json"),
    ("NR_0019 centered replication", "docs/lso_nr0019_full_eval_centered_anatomy_specific_gate.json"),
    ("CSH target-balanced", "docs/lso_csh_target_balanced_anatomy_specific_gate.json"),
    ("CSH recording-centered loss", "docs/lso_csh_recording_centered_loss_anatomy_specific_gate.json"),
    ("CSH within-recording shuffle", "docs/lso_csh_within_recording_shuffle_anatomy_specific_gate.json"),
    ("CSH recording-centered gate pilot", "docs/lso_csh_recording_centered_gate_pilot_anatomy_specific_gate.json"),
    ("CSH pairwise-rank objective pilot", "docs/lso_csh_pairwise_rank_pilot_anatomy_specific_gate.json"),
    (
        "CSH pairwise-rank centered-BCE pilot",
        "docs/lso_csh_pairwise_rank_centered_bce_pilot_anatomy_specific_gate.json",
    ),
)

SLICE_RESULT_FILES = (
    ("NYU-12 fixed carrier slice", "docs/lso_nyu12_parent_slice_results.md", "NYU-12"),
    ("SWC_038 stricter carrier slice", "docs/lso_swc038_parent_slice_results.md", "SWC_038"),
)
MECHANISM_AUDIT_FILE = "docs/csh_mechanism_audit.json"
PAIRWISE_MECHANISM_AUDIT_FILE = "docs/lso_csh_pairwise_rank_pilot_mechanism.json"
PAIRWISE_MISMATCH_AUDIT_FILE = "docs/lso_csh_pairwise_rank_pilot_mismatch.json"
CENTERED_BCE_MISMATCH_AUDIT_FILE = "docs/lso_csh_pairwise_rank_centered_bce_pilot_mismatch.json"
CENTERED_BCE_MECHANISM_AUDIT_FILE = "docs/lso_csh_pairwise_rank_centered_bce_pilot_mechanism.json"
LOCAL_AUC_SURROGATE_GATE_FILE = "docs/local_csh_auc_surrogate_probe_anatomy_specific_gate.json"
LOCAL_AUC_SURROGATE_MISMATCH_FILE = "docs/local_csh_auc_surrogate_probe_mismatch.json"


def display_path(path: Path) -> str:
    path = path.expanduser()
    if not path.is_absolute():
        return str(path)
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def read_strict_gate(label: str, path: Path) -> StrictGateRow | None:
    if not path.exists():
        return None
    data = json.loads(path.read_text())
    metrics = data.get("metrics", {})
    sign_flip = metrics.get("recording_sign_flip") or {}
    return StrictGateRow(
        label=label,
        holdout=str(data.get("holdout", "")),
        pass_gate=bool(data.get("pass", False)),
        centered_delta=_as_float(metrics.get("centered_auc_delta_vs_shuffle")),
        paired_true_vs_shuffle=_as_float(metrics.get("paired_true_vs_shuffle")),
        specificity_gap=_as_float(metrics.get("paired_specificity_gap")),
        target0_true_class_improved=_as_float(metrics.get("target0_true_class_improved")),
        target1_true_class_improved=_as_float(metrics.get("target1_true_class_improved")),
        sign_flip_p=_as_float(sign_flip.get("one_sided_p")),
        source=path,
    )


def _as_float(value) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _positive_seed_count(seed_deltas: tuple[float, ...]) -> str:
    if not seed_deltas:
        return "0/0"
    return f"{sum(delta > 0 for delta in seed_deltas)}/{len(seed_deltas)}"


def read_slice_result(label: str, path: Path, holdout: str) -> SliceRow | None:
    if not path.exists():
        return None
    rows = parse_lso_rows(path, display_path(path))
    by_arm = {(row.holdout, row.arm): row for row in rows}
    true_row = by_arm.get((holdout, "region_only"))
    shuffle_row = by_arm.get((holdout, "region_shuffle"))
    true_delta = None if true_row is None else true_row.mean_delta
    shuffle_delta = None if shuffle_row is None else shuffle_row.mean_delta
    return SliceRow(
        label=label,
        holdout=holdout,
        true_delta=true_delta,
        shuffle_delta=shuffle_delta,
        true_minus_shuffle=None if true_delta is None or shuffle_delta is None else true_delta - shuffle_delta,
        true_positive="n/a" if true_row is None else _positive_seed_count(true_row.seed_deltas),
        shuffle_positive="n/a" if shuffle_row is None else _positive_seed_count(shuffle_row.seed_deltas),
        source=path,
    )


def fmt_float(value: float | None, digits: int = 3) -> str:
    return "n/a" if value is None else f"{value:.{digits}f}"


def fmt_signed(value: float | None, digits: int = 3) -> str:
    return "n/a" if value is None else f"{value:+.{digits}f}"


def strict_gate_outcome(row: StrictGateRow) -> str:
    if row.pass_gate:
        return "pass"
    failures = []
    if row.centered_delta is not None and row.centered_delta < 0.01:
        failures.append("small centered delta")
    if row.paired_true_vs_shuffle is not None and row.paired_true_vs_shuffle < 0.55:
        failures.append("paired gate")
    if row.specificity_gap is not None and row.specificity_gap <= 0.0:
        failures.append("specificity")
    if row.target0_true_class_improved is not None and row.target0_true_class_improved < 0.55:
        failures.append("target0")
    if row.target1_true_class_improved is not None and row.target1_true_class_improved < 0.55:
        failures.append("target1")
    if row.sign_flip_p is not None and row.sign_flip_p > 0.05:
        failures.append("sign-flip")
    return "fail: " + ", ".join(failures or ["gate"])


def slice_outcome(row: SliceRow) -> str:
    if row.true_minus_shuffle is None:
        return "missing"
    if row.true_minus_shuffle > 0.02 and row.true_delta is not None and row.true_delta > 0:
        return "promising"
    if row.true_delta is not None and row.shuffle_delta is not None and row.shuffle_delta >= row.true_delta:
        return "shuffle >= true"
    return "weak"


def summarize(strict_rows: list[StrictGateRow], slice_rows: list[SliceRow]) -> dict:
    strict_passes = [row for row in strict_rows if row.pass_gate]
    promising_slices = [row for row in slice_rows if slice_outcome(row) == "promising"]
    return {
        "strict_pass_count": len(strict_passes),
        "slice_promising_count": len(promising_slices),
        "decision": "no_paid_broadening_without_new_mechanism",
        "next_mechanism": (
            "The bidirectional target-class gate and explicit recording-local AUC surrogate "
            "are now implemented. The next no-spend task is local objective debugging that "
            "can satisfy target0, target1, and recording-local AUC checks before any more "
            "paid broadening."
        ),
    }


def read_mechanism_audit(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text())


def render_markdown(
    strict_rows: list[StrictGateRow],
    slice_rows: list[SliceRow],
    mechanism: dict | None = None,
    pairwise_mechanism: dict | None = None,
    pairwise_mismatch: dict | None = None,
    centered_bce_mechanism: dict | None = None,
    centered_bce_mismatch: dict | None = None,
    local_auc_gate: dict | None = None,
    local_auc_mismatch: dict | None = None,
) -> str:
    summary = summarize(strict_rows, slice_rows)
    lines = [
        "# Current Anatomy-Transfer Experiment State",
        "",
        f"Decision: `{summary['decision']}`",
        "",
        "## Strict Gate Runs",
        "",
        "| experiment | holdout | gate | centered_delta | paired_true_vs_shuffle | specificity_gap | target0 | target1 | sign_flip_p | outcome | source |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in strict_rows:
        lines.append(
            "| "
            f"{row.label} | {row.holdout} | {row.pass_gate} | "
            f"{fmt_signed(row.centered_delta)} | {fmt_float(row.paired_true_vs_shuffle)} | "
            f"{fmt_signed(row.specificity_gap)} | "
            f"{fmt_float(row.target0_true_class_improved)} | "
            f"{fmt_float(row.target1_true_class_improved)} | "
            f"{fmt_float(row.sign_flip_p)} | "
            f"{strict_gate_outcome(row)} | `{display_path(row.source)}` |"
        )

    lines += [
        "",
        "## Fixed-Slice Runs",
        "",
        "| experiment | holdout | true_delta | shuffle_delta | true_minus_shuffle | true_positive | shuffle_positive | outcome | source |",
        "|---|---|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in slice_rows:
        lines.append(
            "| "
            f"{row.label} | {row.holdout} | {fmt_signed(row.true_delta)} | "
            f"{fmt_signed(row.shuffle_delta)} | {fmt_signed(row.true_minus_shuffle)} | "
            f"{row.true_positive} | {row.shuffle_positive} | {slice_outcome(row)} | "
            f"`{display_path(row.source)}` |"
        )

    lines += [
        "",
        "## Decision",
        "",
        (
            "No current strict-gate artifact supports paid broadening. The later "
            "recording-matched controls show the CSH true-region advantage is much "
            "smaller than the original sampled-eval signal, and both fixed carrier "
            "slice attempts let shuffled labels match or beat true labels."
        ),
        "",
        (
            "Next mechanism: "
            + summary["next_mechanism"]
        ),
        "",
    ]
    if mechanism is not None:
        global_metrics = mechanism.get("global", {})
        emb = mechanism.get("embedding_summary", {})
        interp = mechanism.get("interpretation", {})
        true_vs_shuffle = global_metrics.get("paired_true_vs_shuffle", {})
        lines += [
            "## Mechanism Audit Follow-Up",
            "",
            "`docs/csh_mechanism_audit.md` performs that saved-artifact audit on the",
            "recording-centered gate pilot. It does not find a transferable anatomical",
            "mechanism:",
            "",
            f"- global paired true-vs-shuffle remains `{fmt_float(true_vs_shuffle.get('improved_fraction'))}`",
            f"- specificity gap is `{fmt_signed(global_metrics.get('specificity_gap'))}`",
            f"- carrier-parent embeddings are nearly identical between true and shuffled controls, with mean carrier cosine `{fmt_float(emb.get('mean_carrier_cosine'))}`",
            f"- carrier-rich negative recordings: `{len(interp.get('carrier_rich_negative_recordings', []))}`",
            "",
            (
                "Updated mechanism decision: no paid run is justified until the objective "
                "itself forces target-aware true-vs-shuffle separation. Region/subject "
                "selection and embedding inspection did not reveal a mechanism that the "
                "current controls can validate."
            ),
            "",
        ]
    if pairwise_mechanism is not None:
        global_metrics = pairwise_mechanism.get("global", {})
        true_vs_shuffle = global_metrics.get("paired_true_vs_shuffle", {})
        mismatch_summary = {} if pairwise_mismatch is None else pairwise_mismatch.get("summary", {})
        gate_row = next((row for row in strict_rows if "pairwise-rank" in row.label), None)
        lines += [
            "## Pairwise-Rank Objective Pilot",
            "",
            "`docs/lso_csh_pairwise_rank_pilot_results.md` ran the implemented",
            "`recording_pairwise_rank` objective on a one-seed L4 RunPod pilot. It improved",
            f"the global paired true-vs-shuffle check to `{fmt_float(true_vs_shuffle.get('improved_fraction'))}`",
            f"and the specificity gap to `{fmt_signed(global_metrics.get('specificity_gap'))}`,",
            "so the objective change did move the right target-aware paired metric.",
            "",
            "The strict anatomy-specific gate still failed:",
            "",
        ]
        if gate_row is not None:
            lines += [
                f"- centered true-minus-shuffle delta: `{fmt_signed(gate_row.centered_delta)}`",
                f"- paired true-vs-shuffle: `{fmt_float(gate_row.paired_true_vs_shuffle)}`",
                f"- specificity gap: `{fmt_signed(gate_row.specificity_gap)}`",
                f"- recording sign-flip p-value: `{fmt_float(gate_row.sign_flip_p)}`",
            ]
        lines += [
            "",
            (
                "Updated decision before the mismatch audit: possible mechanism candidate, "
                "not demo evidence. Do not broaden yet; require a diagnostic that separates "
                "bidirectional target-aware ranking from one-direction probability shifts."
            ),
            "",
        ]
        if pairwise_mismatch is not None:
            lines += [
                "Pairwise mismatch audit: `docs/lso_csh_pairwise_rank_pilot_mismatch.md`",
                f"classifies the paired improvement as `{pairwise_mismatch.get('decision')}`.",
                f"Raw probabilities moved downward on `{fmt_float(mismatch_summary.get('raw_prob_delta_negative_fraction'))}`",
                "of paired trials; target-0 true-class probability improved on",
                f"`{fmt_float(mismatch_summary.get('target0_true_class_improved_fraction'))}`",
                "of trials while target-1 improved on",
                f"`{fmt_float(mismatch_summary.get('target1_true_class_improved_fraction'))}`.",
                "",
                (
                    "Next candidate objective: `recording_pairwise_rank_centered_bce`, "
                    "which keeps the recording-local pairwise rank term but adds "
                    "recording-centered BCE so a one-direction probability shift is not "
                    "mistaken for anatomical ranking evidence."
                ),
                "",
                (
                    "Updated decision after mismatch audit: the scalar paired metric should "
                    "not be used as a success gate. Require bidirectional target-class "
                    "improvement and positive recording-local AUC against the shuffled control."
                ),
                "",
            ]
    if centered_bce_mechanism is not None and centered_bce_mismatch is not None:
        centered_gate = next((row for row in strict_rows if "centered-BCE" in row.label), None)
        mismatch_summary = centered_bce_mismatch.get("summary", {})
        mechanism_global = centered_bce_mechanism.get("global", {})
        true_vs_shuffle = mechanism_global.get("paired_true_vs_shuffle", {})
        lines += [
            "## Pairwise-Rank Centered-BCE Pilot",
            "",
            "`docs/lso_csh_pairwise_rank_centered_bce_pilot_results.md` tested the",
            "`recording_pairwise_rank_centered_bce` objective. It removed the previous",
            "all-trial downward probability shift but did not produce anatomical transfer.",
            "",
        ]
        if centered_gate is not None:
            lines += [
                f"- centered true-minus-shuffle delta: `{fmt_signed(centered_gate.centered_delta)}`",
                f"- paired true-vs-shuffle: `{fmt_float(centered_gate.paired_true_vs_shuffle)}`",
                f"- specificity gap: `{fmt_signed(centered_gate.specificity_gap)}`",
                f"- recording sign-flip p-value: `{fmt_float(centered_gate.sign_flip_p)}`",
            ]
        lines += [
            f"- mechanism decision: `{centered_bce_mechanism.get('interpretation', {}).get('decision')}`",
            f"- mismatch decision: `{centered_bce_mismatch.get('decision')}`",
            f"- target0 true-class improved: `{fmt_float(mismatch_summary.get('target0_true_class_improved_fraction'))}`",
            f"- target1 true-class improved: `{fmt_float(mismatch_summary.get('target1_true_class_improved_fraction'))}`",
            f"- mechanism paired true-vs-shuffle: `{fmt_float(true_vs_shuffle.get('improved_fraction'))}`",
            "",
            (
                "Updated decision: stop paid one-off objective variants for now. Use the "
                "implemented bidirectional gate and `recording_local_auc_surrogate` only for "
                "local objective debugging until a candidate satisfies target0, target1, and "
                "recording-local AUC checks."
            ),
            "",
        ]
    if local_auc_gate is not None and local_auc_mismatch is not None:
        metrics = local_auc_gate.get("metrics", {})
        mismatch = local_auc_mismatch.get("summary", {})
        lines += [
            "## Local AUC-Surrogate Probe",
            "",
            "`scripts/run_local_objective_probe.py` runs a no-spend tiny CPU probe with",
            "deterministic held-out predictions and immediate strict-gate/mismatch audits.",
            "The first probe used `recording_local_auc_surrogate` for two CPU steps.",
            "",
            f"- gate pass: `{local_auc_gate.get('pass')}`",
            f"- centered true-minus-shuffle delta: `{fmt_signed(metrics.get('centered_auc_delta_vs_shuffle'))}`",
            f"- paired true-vs-shuffle: `{fmt_float(metrics.get('paired_true_vs_shuffle'))}`",
            f"- target0 true-class improved: `{fmt_float(metrics.get('target0_true_class_improved'))}`",
            f"- target1 true-class improved: `{fmt_float(metrics.get('target1_true_class_improved'))}`",
            f"- positive recordings: `{metrics.get('recordings_positive')}/{metrics.get('n_recordings')}`",
            f"- mismatch decision: `{local_auc_mismatch.get('decision')}`",
            f"- true-minus-shuffle AUC: `{fmt_signed(mismatch.get('true_minus_shuffle_auc'))}`",
            "",
            (
                "Decision: reject this objective configuration locally. It does not justify "
                "a RunPod launch because it fails target1, centered AUC, and recording support."
            ),
            "",
        ]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-md", type=Path, default=REPO_ROOT / "docs/current_experiment_state.md")
    parser.add_argument("--out-json", type=Path, default=REPO_ROOT / "docs/current_experiment_state.json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    strict_rows = [
        row for label, rel_path in STRICT_GATE_FILES
        if (row := read_strict_gate(label, REPO_ROOT / rel_path)) is not None
    ]
    slice_rows = [
        row for label, rel_path, holdout in SLICE_RESULT_FILES
        if (row := read_slice_result(label, REPO_ROOT / rel_path, holdout)) is not None
    ]
    mechanism = read_mechanism_audit(REPO_ROOT / MECHANISM_AUDIT_FILE)
    pairwise_mechanism = read_mechanism_audit(REPO_ROOT / PAIRWISE_MECHANISM_AUDIT_FILE)
    pairwise_mismatch = read_mechanism_audit(REPO_ROOT / PAIRWISE_MISMATCH_AUDIT_FILE)
    centered_bce_mechanism = read_mechanism_audit(REPO_ROOT / CENTERED_BCE_MECHANISM_AUDIT_FILE)
    centered_bce_mismatch = read_mechanism_audit(REPO_ROOT / CENTERED_BCE_MISMATCH_AUDIT_FILE)
    local_auc_gate = read_mechanism_audit(REPO_ROOT / LOCAL_AUC_SURROGATE_GATE_FILE)
    local_auc_mismatch = read_mechanism_audit(REPO_ROOT / LOCAL_AUC_SURROGATE_MISMATCH_FILE)
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text(render_markdown(
        strict_rows,
        slice_rows,
        mechanism,
        pairwise_mechanism,
        pairwise_mismatch,
        centered_bce_mechanism,
        centered_bce_mismatch,
        local_auc_gate,
        local_auc_mismatch,
    ))
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps({
        "summary": summarize(strict_rows, slice_rows),
        "strict_gates": [row.__dict__ | {"source": display_path(row.source)} for row in strict_rows],
        "fixed_slices": [row.__dict__ | {"source": display_path(row.source)} for row in slice_rows],
        "mechanism": mechanism,
        "pairwise_mechanism": pairwise_mechanism,
        "pairwise_mismatch": pairwise_mismatch,
        "centered_bce_mechanism": centered_bce_mechanism,
        "centered_bce_mismatch": centered_bce_mismatch,
        "local_auc_surrogate_gate": local_auc_gate,
        "local_auc_surrogate_mismatch": local_auc_mismatch,
    }, indent=2, sort_keys=True) + "\n")
    print(f"wrote {args.out_md}")
    print(f"wrote {args.out_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
