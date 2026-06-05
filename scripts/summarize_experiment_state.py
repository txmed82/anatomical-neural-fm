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


@dataclass(frozen=True)
class LocalProbeRow:
    label: str
    pass_gate: bool
    centered_delta: float | None
    paired_true_vs_shuffle: float | None
    specificity_gap: float | None
    target0_true_class_improved: float | None
    target1_true_class_improved: float | None
    positive_recordings: str
    mismatch_decision: str
    true_minus_shuffle_auc: float | None
    gate_source: Path
    mismatch_source: Path


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
BATCH_SAMPLING_CONTRAST_AUDIT_FILE = "docs/csh_batch_sampling_contrast_audit.json"
MODEL_FREE_REGION_SIGNAL_AUDIT_FILE = "docs/csh_model_free_region_signal_audit.json"
MODEL_FREE_REGION_CANDIDATE_SCAN_FILE = "docs/csh_model_free_region_candidate_scan.json"
MODEL_FREE_REGION_FAMILY_SCAN_FILE = "docs/csh_model_free_region_family_scan.json"
CHOICE_MODEL_FREE_REGION_SIGNAL_AUDIT_FILE = "docs/csh_choice_model_free_region_signal_audit.json"
CHOICE_MODEL_FREE_REGION_CANDIDATE_SCAN_FILE = "docs/csh_choice_model_free_region_candidate_scan.json"
CHOICE_MODEL_FREE_REGION_FAMILY_SCAN_FILE = "docs/csh_choice_model_free_region_family_scan.json"
MATCHED_REGION_CACHE_AUDIT_FILE = "docs/matched_region_cache_audit.md"
MATCHED_REGION_MISSING_MANIFEST_FILE = "manifests/ibl_bwm_region_matched_candidates_missing_s3.json"
MATCHED_REGION_S3_PRESENT_SCORED_FILE = "manifests/ibl_bwm_region_matched_candidates_s3_present_scored.json"
MATCHED_REGION_S3_PRESENT_SUPPORT80_FILE = "manifests/ibl_bwm_region_matched_candidates_s3_present_support80.json"
MATCHED_REGION_S3_PRESENT_SUPPORT80_HDF5_FILE = (
    "manifests/ibl_bwm_region_matched_candidates_s3_present_support80_hdf5_scored.json"
)
MATCHED_REGION_S3_PRESENT_SUPPORT80_HDF5_ITERATIVE_FILE = (
    "manifests/ibl_bwm_region_matched_candidates_s3_present_support80_hdf5_iterative_pass.json"
)
MODEL_FREE_MATCHED_SUPPORT80_PANEL_FILE = "docs/model_free_matched_support80_hdf5_panel.json"
MODEL_FREE_POSITIVE_HOLDOUTS_MECHANISM_FILE = "docs/model_free_positive_holdouts_mechanism.json"
LOCAL_PROBE_FILES = (
    (
        "local AUC surrogate",
        "docs/local_csh_auc_surrogate_probe_anatomy_specific_gate.json",
        "docs/local_csh_auc_surrogate_probe_mismatch.json",
    ),
    (
        "local recording-centered BCE",
        "docs/local_csh_recording_centered_bce_probe_anatomy_specific_gate.json",
        "docs/local_csh_recording_centered_bce_probe_mismatch.json",
    ),
    (
        "local rank + centered BCE",
        "docs/local_csh_rank_centered_bce_probe_anatomy_specific_gate.json",
        "docs/local_csh_rank_centered_bce_probe_mismatch.json",
    ),
    (
        "local AUC surrogate target-balanced",
        "docs/local_csh_auc_surrogate_target_balanced_probe_anatomy_specific_gate.json",
        "docs/local_csh_auc_surrogate_target_balanced_probe_mismatch.json",
    ),
)


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


def read_local_probe_result(label: str, gate_path: Path, mismatch_path: Path) -> LocalProbeRow | None:
    if not gate_path.exists() or not mismatch_path.exists():
        return None
    gate = json.loads(gate_path.read_text())
    mismatch = json.loads(mismatch_path.read_text())
    metrics = gate.get("metrics", {})
    mismatch_summary = mismatch.get("summary", {})
    n_recordings = metrics.get("n_recordings")
    recordings_positive = metrics.get("recordings_positive")
    positive_recordings = (
        "n/a" if n_recordings is None or recordings_positive is None
        else f"{recordings_positive}/{n_recordings}"
    )
    return LocalProbeRow(
        label=label,
        pass_gate=bool(gate.get("pass", False)),
        centered_delta=_as_float(metrics.get("centered_auc_delta_vs_shuffle")),
        paired_true_vs_shuffle=_as_float(metrics.get("paired_true_vs_shuffle")),
        specificity_gap=_as_float(metrics.get("paired_specificity_gap")),
        target0_true_class_improved=_as_float(metrics.get("target0_true_class_improved")),
        target1_true_class_improved=_as_float(metrics.get("target1_true_class_improved")),
        positive_recordings=positive_recordings,
        mismatch_decision=str(mismatch.get("decision", "")),
        true_minus_shuffle_auc=_as_float(mismatch_summary.get("true_minus_shuffle_auc")),
        gate_source=gate_path,
        mismatch_source=mismatch_path,
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


def local_probe_outcome(row: LocalProbeRow) -> str:
    if row.pass_gate:
        return "candidate"
    failures = []
    if row.centered_delta is not None and row.centered_delta < 0.01:
        failures.append("centered AUC")
    if row.target0_true_class_improved is not None and row.target0_true_class_improved < 0.55:
        failures.append("target0")
    if row.target1_true_class_improved is not None and row.target1_true_class_improved < 0.55:
        failures.append("target1")
    if row.positive_recordings not in {"3/4", "4/4"}:
        failures.append("recording support")
    if row.mismatch_decision and row.mismatch_decision != "recording_rank_stable":
        failures.append("mismatch")
    return "reject: " + ", ".join(failures or ["gate"])


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


def read_cache_audit(path: Path) -> dict | None:
    if not path.exists():
        return None
    text = path.read_text()
    present_match = re.search(r"Present:\s+(\d+)/(\d+)\s+\(([^)]+)\)", text)
    missing_section = text.split("## Shard Build Plan", 1)[0].split("## Missing", 1)[-1]
    missing = re.findall(r"\| `([^`]+\.h5)` \|", missing_section)
    shard_rows = []
    for match in re.finditer(r"\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|", text):
        shard_rows.append({
            "shard": int(match.group(1)),
            "recordings": int(match.group(2)),
            "present": int(match.group(3)),
            "missing": int(match.group(4)),
        })
    return {
        "source": path,
        "present": None if present_match is None else int(present_match.group(1)),
        "total": None if present_match is None else int(present_match.group(2)),
        "percent": None if present_match is None else present_match.group(3),
        "missing_files": missing[:],
        "missing_count": len(missing),
        "shards": shard_rows,
        "shards_with_missing": [row for row in shard_rows if row["missing"] > 0],
    }


def read_manifest_summary(path: Path) -> dict | None:
    if not path.exists():
        return None
    payload = json.loads(path.read_text())
    rows = payload["recordings"] if isinstance(payload, dict) else payload
    subjects = {
        row.get("subject_id") or row.get("subject") or row.get("subject_nickname")
        for row in rows
    }
    return {
        "source": path,
        "n_recordings": len(rows),
        "n_subjects": len({subject for subject in subjects if subject}),
    }


def read_support_manifest_summary(path: Path) -> dict | None:
    if not path.exists():
        return None
    payload = json.loads(path.read_text())
    support = payload.get("region_support", {})
    fracs = [
        row.get("unit_support_frac")
        for row in support.values()
        if row.get("unit_support_frac") is not None
    ]
    pass_count = sum(1 for frac in fracs if frac >= 0.8)
    return {
        "source": path,
        "n_recordings": payload.get("n_recordings"),
        "n_subjects": payload.get("n_subjects"),
        "pass_count": pass_count,
        "subject_count": len(fracs),
        "min_support": None if not fracs else min(fracs),
        "optimized": payload.get("selection", {}).get("optimized_support_subset"),
    }


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
    local_probes: list[LocalProbeRow] | None = None,
    batch_sampling_audit: dict | None = None,
    model_free_region_audit: dict | None = None,
    model_free_region_scan: dict | None = None,
    model_free_family_scan: dict | None = None,
    choice_region_audit: dict | None = None,
    choice_region_scan: dict | None = None,
    choice_family_scan: dict | None = None,
    matched_cache_audit: dict | None = None,
    matched_missing_manifest: dict | None = None,
    matched_present_support: dict | None = None,
    matched_support80: dict | None = None,
    matched_support80_hdf5: dict | None = None,
    matched_support80_hdf5_iterative: dict | None = None,
    model_free_matched_panel: dict | None = None,
    model_free_positive_holdouts: dict | None = None,
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
    if local_probes:
        lines += [
            "## Local Probe Matrix",
            "",
            (
                "These CPU-only probes are the current promotion gate for objective and "
                "sampling variants. A candidate should pass the strict gate locally before "
                "any new RunPod spend."
            ),
            "",
            "| probe | gate | centered_delta | paired_true_vs_shuffle | specificity_gap | target0 | target1 | recordings | mismatch | outcome |",
            "|---|---|---:|---:|---:|---:|---:|---:|---|---|",
        ]
        for row in local_probes:
            lines.append(
                "| "
                f"{row.label} | {row.pass_gate} | {fmt_signed(row.centered_delta)} | "
                f"{fmt_float(row.paired_true_vs_shuffle)} | {fmt_signed(row.specificity_gap)} | "
                f"{fmt_float(row.target0_true_class_improved)} | "
                f"{fmt_float(row.target1_true_class_improved)} | "
                f"{row.positive_recordings} | `{row.mismatch_decision}` | "
                f"{local_probe_outcome(row)} |"
            )
        lines += [
            "",
            (
                "Decision: all current tiny local variants are rejected for cloud promotion. "
                "They repeatedly improve target-0 more than target-1, lose centered true-vs-shuffle "
                "AUC, or fail recording support. The next no-spend step is to redesign the "
                "sampler/objective so both target classes improve within recordings before any "
                "paid run."
            ),
            "",
        ]
    if batch_sampling_audit is not None:
        lines += [
            "## Batch Sampling Contrast Audit",
            "",
            "`docs/csh_batch_sampling_contrast_audit.md` checks whether samplers create",
            "same-recording target-0/target-1 pairs before training. This is the minimum",
            "condition for recording-local ranking losses to be active.",
            "",
            "| sampler | target1_fraction | rankable_batch_fraction | mean_rankable_pairs | same_recording_adjacent_pairs |",
            "|---|---:|---:|---:|---:|",
        ]
        for row in batch_sampling_audit.get("samplers", []):
            lines.append(
                "| "
                f"{row.get('batch_sampling')} | "
                f"{fmt_float(row.get('target1_fraction'))} | "
                f"{fmt_float(row.get('rankable_batch_fraction'))} | "
                f"{fmt_float(row.get('mean_rankable_pairs_per_batch'))} | "
                f"{fmt_float(row.get('same_recording_adjacent_pair_fraction'))} |"
            )
        lines += [
            "",
            (
                "Interpretation: `recording_target_balanced` makes the recording-local "
                "rank loss active in every audited batch, while uniform and target-balanced "
                "sampling rarely produce same-recording contrast. Since the local probe "
                "matrix still fails under `recording_target_balanced`, the next failure is "
                "not pair availability; it is the anatomy/control signal or objective itself."
            ),
            "",
        ]
    if model_free_region_audit is not None:
        summary = model_free_region_audit.get("summary", {})
        metrics = summary.get("metrics", {})
        deltas = summary.get("deltas", {})
        paired = summary.get("paired_true_vs_shuffle", {})
        lines += [
            "## Model-Free Region Signal Audit",
            "",
            "`docs/csh_model_free_region_signal_audit.md` removes the transformer and",
            "tests closed-form ridge classifiers on trial-level parent-region spike counts.",
            "",
            "| feature_set | train_AUC | eval_AUC | eval_centered_AUC |",
            "|---|---:|---:|---:|",
        ]
        for name in ("total_spikes", "region_true", "region_shuffle"):
            row = metrics.get(name, {})
            lines.append(
                "| "
                f"{name} | {fmt_float(row.get('train_auc'))} | "
                f"{fmt_float(row.get('eval_auc'))} | "
                f"{fmt_float(row.get('eval_centered_auc'))} |"
            )
        lines += [
            "",
            f"- true-minus-shuffle centered AUC: `{fmt_signed(deltas.get('true_minus_shuffle_centered_auc'))}`",
            f"- true-minus-total centered AUC: `{fmt_signed(deltas.get('true_minus_total_centered_auc'))}`",
            f"- paired target0 improved vs shuffle: `{fmt_float(paired.get('target0_improved_fraction'))}`",
            f"- paired target1 improved vs shuffle: `{fmt_float(paired.get('target1_improved_fraction'))}`",
            (
                f"- positive recordings vs shuffle: "
                f"`{summary.get('recordings_positive_true_minus_shuffle')}/{summary.get('n_recordings')}`"
            ),
            f"- decision: `{summary.get('decision')}`",
            "",
            (
                "Interpretation: the current parent-region spike-count representation does "
                "not show model-free anatomical transfer for CSH. True region labels are "
                "worse than shuffled labels on recording-centered AUC and worse than a "
                "total-spike-count baseline, so the next no-spend step should redesign the "
                "anatomical feature/control target rather than spend on another neural model run."
            ),
            "",
        ]
    if model_free_region_scan is not None:
        lines += [
            "## Model-Free Single-Region Candidate Scan",
            "",
            "`docs/csh_model_free_region_candidate_scan.md` scans each parent region as a",
            "single-feature ridge model against within-recording shuffled labels and the",
            "total-spike baseline.",
            "",
            f"Candidates passing the strict local gate: `{model_free_region_scan.get('n_candidates')}`",
            "",
            "| region | outcome | centered_AUC | delta_vs_shuffle | delta_vs_total | target0 | target1 | recordings | eval_nonzero |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
        for row in model_free_region_scan.get("top_regions", [])[:8]:
            lines.append(
                "| "
                f"{row.get('region')} | {row.get('outcome')} | "
                f"{fmt_float(row.get('eval_centered_auc'))} | "
                f"{fmt_signed(row.get('centered_delta_vs_shuffle'))} | "
                f"{fmt_signed(row.get('centered_delta_vs_total'))} | "
                f"{fmt_float(row.get('target0_improved_vs_shuffle'))} | "
                f"{fmt_float(row.get('target1_improved_vs_shuffle'))} | "
                f"{row.get('positive_recordings_vs_shuffle')}/{row.get('n_recordings')} | "
                f"{fmt_float(row.get('eval_nonzero_fraction'))} |"
            )
        lines += [
            "",
            (
                "Interpretation: no individual parent region is strong enough to promote. "
                "The best evaluable regions beat shuffle and total-spike baselines only in "
                "one target direction or too few recordings. The next no-spend feature step "
                "should test predefined aggregate region families or a different conserved "
                "target, not a GPU model run."
            ),
            "",
        ]
    if model_free_family_scan is not None:
        lines += [
            "## Model-Free Region-Family Candidate Scan",
            "",
            "`docs/csh_model_free_region_family_scan.md` scans predefined aggregate",
            "region families as one-feature ridge models against within-recording",
            "shuffled labels and the total-spike baseline.",
            "",
            f"Candidates passing the strict local gate: `{model_free_family_scan.get('n_candidates')}`",
            "",
            "| family | outcome | centered_AUC | delta_vs_shuffle | delta_vs_total | target0 | target1 | recordings | eval_nonzero |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
        for row in model_free_family_scan.get("families", [])[:8]:
            lines.append(
                "| "
                f"{row.get('region')} | {row.get('outcome')} | "
                f"{fmt_float(row.get('eval_centered_auc'))} | "
                f"{fmt_signed(row.get('centered_delta_vs_shuffle'))} | "
                f"{fmt_signed(row.get('centered_delta_vs_total'))} | "
                f"{fmt_float(row.get('target0_improved_vs_shuffle'))} | "
                f"{fmt_float(row.get('target1_improved_vs_shuffle'))} | "
                f"{row.get('positive_recordings_vs_shuffle')}/{row.get('n_recordings')} | "
                f"{fmt_float(row.get('eval_nonzero_fraction'))} |"
            )
        lines += [
            "",
            (
                "Interpretation: predefined region-family aggregates also fail the "
                "model-free promotion gate. The evidence now argues against spending on "
                "another CSH parent-region model variant. The next branch should be an "
                "alternative conserved target or a larger matched-region manifest audit."
            ),
            "",
        ]
    if choice_region_audit is not None:
        summary = choice_region_audit.get("summary", {})
        metrics = summary.get("metrics", {})
        deltas = summary.get("deltas", {})
        paired = summary.get("paired_true_vs_shuffle", {})
        lines += [
            "## Alternative Target: Choice",
            "",
            "The same model-free gates were rerun with `--target-mode choice` to test",
            "whether a different behavioral target exposes anatomical transfer.",
            "",
            "| feature_set | train_AUC | eval_AUC | eval_centered_AUC |",
            "|---|---:|---:|---:|",
        ]
        for name in ("total_spikes", "region_true", "region_shuffle"):
            row = metrics.get(name, {})
            lines.append(
                "| "
                f"{name} | {fmt_float(row.get('train_auc'))} | "
                f"{fmt_float(row.get('eval_auc'))} | "
                f"{fmt_float(row.get('eval_centered_auc'))} |"
            )
        lines += [
            "",
            f"- true-minus-shuffle centered AUC: `{fmt_signed(deltas.get('true_minus_shuffle_centered_auc'))}`",
            f"- true-minus-total centered AUC: `{fmt_signed(deltas.get('true_minus_total_centered_auc'))}`",
            f"- paired target0 improved vs shuffle: `{fmt_float(paired.get('target0_improved_fraction'))}`",
            f"- paired target1 improved vs shuffle: `{fmt_float(paired.get('target1_improved_fraction'))}`",
            (
                f"- positive recordings vs shuffle: "
                f"`{summary.get('recordings_positive_true_minus_shuffle')}/{summary.get('n_recordings')}`"
            ),
            f"- full-region decision: `{summary.get('decision')}`",
            f"- single-region candidates: `{None if choice_region_scan is None else choice_region_scan.get('n_candidates')}`",
            f"- region-family candidates: `{None if choice_family_scan is None else choice_family_scan.get('n_candidates')}`",
            "",
            (
                "Interpretation: `choice` does not rescue the CSH parent-region branch. "
                "Shuffled parent labels still beat true labels on recording-centered AUC, "
                "and the single-region/family scans find no promotable candidate."
            ),
            "",
        ]
    if matched_cache_audit is not None:
        missing_count = matched_cache_audit.get("missing_count")
        missing_label = "recording" if missing_count == 1 else "recordings"
        lines += [
            "## Matched-Region Cache Readiness",
            "",
            "`docs/matched_region_cache_audit.md` audits the persistent S3 cache for the",
            "48-recording matched-region manifest. This is the next gate before any",
            "larger matched-region training attempt.",
            "",
            (
                f"- present: `{matched_cache_audit.get('present')}/{matched_cache_audit.get('total')}` "
                f"(`{matched_cache_audit.get('percent')}`)"
            ),
            f"- missing {missing_label}: `{missing_count}`",
            f"- shards with missing recordings: `{len(matched_cache_audit.get('shards_with_missing', []))}`",
        ]
        if matched_missing_manifest is not None:
            recording_label = "recording" if matched_missing_manifest["n_recordings"] == 1 else "recordings"
            subject_label = "subject" if matched_missing_manifest["n_subjects"] == 1 else "subjects"
            lines.append(
                f"- missing-only manifest: `{display_path(matched_missing_manifest['source'])}` "
                f"({matched_missing_manifest['n_recordings']} {recording_label}, "
                f"{matched_missing_manifest['n_subjects']} {subject_label})"
            )
        lines += [
            "",
            "| shard | recordings | present | missing |",
            "|---:|---:|---:|---:|",
        ]
        for row in matched_cache_audit.get("shards_with_missing", [])[:12]:
            lines.append(
                f"| {row['shard']} | {row['recordings']} | {row['present']} | {row['missing']} |"
            )
        lines += [
            "",
            (
                "Decision: do not launch training. Finish the missing HDF5 cache shards "
                "first, then rerun the matched-region support scorer and require the "
                "80% held-out unit-support gate before any seed sweep."
            ),
            "",
        ]
        if missing_count == 1:
            lines[-2] = (
                "Decision: do not launch training. Replace or drop the single failed "
                "recording, then rerun the matched-region support scorer and require "
                "the 80% held-out unit-support gate before any seed sweep."
            )
    if matched_present_support is not None or matched_support80 is not None:
        lines += [
            "## Matched-Region Support Scoring",
            "",
            "Region support has been scored for the S3-present cache panel. Metadata-only",
            "scoring is a planning gate; HDF5 scoring is the stronger pre-training check.",
            "",
            "| manifest | recordings | subjects | support80 subjects | min support |",
            "|---|---:|---:|---:|---:|",
        ]
        for row in [
            matched_present_support,
            matched_support80,
            matched_support80_hdf5,
            matched_support80_hdf5_iterative,
        ]:
            if row is None:
                continue
            min_support = row.get("min_support")
            min_text = "n/a" if min_support is None else f"{min_support:.1%}"
            lines.append(
                f"| `{display_path(row['source'])}` | {row['n_recordings']} | "
                f"{row['n_subjects']} | {row['pass_count']}/{row['subject_count']} | {min_text} |"
            )
        lines += [
            "",
            (
                "Decision: the HDF5-confirmed 28-recording panel is close but not clean "
                "at `6/7` support80 subjects, while the strict iterative all-pass filter "
                "collapses to 2 subjects. Do not claim a clean broad benchmark from this "
                "panel. Treat `SWC_043` as a known weak-support holdout in any bounded "
                "training gate, or run another no-spend/model-free screen before spending."
            ),
            "",
        ]
    if model_free_matched_panel is not None:
        summary = model_free_matched_panel["summary"]
        lines += [
            "## Matched-Region Model-Free Panel",
            "",
            "`docs/model_free_matched_support80_hdf5_panel.md` runs the closed-form",
            "parent-region ridge audit leave-subject-out across the HDF5-confirmed",
            "28-recording matched support80 panel.",
            "",
            f"- holdouts: `{summary['n_holdouts']}`",
            f"- model-free candidates: `{summary['n_candidates']}`",
            f"- positive centered-delta holdouts: `{summary['n_positive_delta_holdouts']}/{summary['n_holdouts']}`",
            f"- mean true-minus-shuffle centered AUC: `{summary['mean_delta_centered_auc']:+.3f}`",
            f"- decision: `{summary['decision']}`",
            "",
            "| holdout | decision | centered delta | target0 | target1 | rec support |",
            "|---|---|---:|---:|---:|---:|",
        ]
        for row in model_free_matched_panel["rows"]:
            lines.append(
                f"| {row['holdout']} | {row['decision']} | "
                f"{row['delta_centered_auc']:+.3f} | {row['target0_improved']:.3f} | "
                f"{row['target1_improved']:.3f} | {row['positive_recordings']}/{row['n_recordings']} |"
            )
        lines += [
            "",
            (
                "Decision: do not promote this panel to a broad training sweep. "
                "The model-free anatomical feature screen has zero passing holdouts; "
                "`KS014` and `NR_0019` have positive centered deltas, but fail "
                "bidirectional target-class and/or recording-support gates."
            ),
            "",
        ]
    if model_free_positive_holdouts is not None:
        lines += [
            "## Positive-Holdout Mechanism Audit",
            "",
            "`docs/model_free_positive_holdouts_mechanism.md` inspects the two weak",
            "positive centered-delta holdouts from the matched-region panel at target-class",
            "and recording resolution.",
            "",
            "| holdout | centered delta | target0 | target1 | positive recordings | interpretation |",
            "|---|---:|---:|---:|---:|---|",
        ]
        for row in model_free_positive_holdouts.get("holdouts", []):
            summary = row["summary"]
            paired = summary["paired_true_vs_shuffle"]
            interpretation = (
                "not bidirectional"
                if min(paired["target0_improved_fraction"], paired["target1_improved_fraction"]) < 0.55
                else "low recording support"
            )
            lines.append(
                f"| {row['holdout']} | {summary['delta_centered_auc']:+.3f} | "
                f"{paired['target0_improved_fraction']:.3f} | "
                f"{paired['target1_improved_fraction']:.3f} | "
                f"{summary['recordings_positive_true_minus_shuffle']}/{summary['n_recordings']} | "
                f"{interpretation} |"
            )
        lines += [
            "",
            (
                "Decision: these positive deltas are not a training trigger. `KS014` is "
                "marginal and below the bidirectional gate; `NR_0019` is strongly one-sided "
                "toward target-0 and fails target-1. Keep the next step no-spend: redesign "
                "the target/control or require a cleaner local model-free pass before any "
                "RunPod training."
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
    local_probes = [
        row for label, gate_rel, mismatch_rel in LOCAL_PROBE_FILES
        if (row := read_local_probe_result(label, REPO_ROOT / gate_rel, REPO_ROOT / mismatch_rel)) is not None
    ]
    batch_sampling_audit = read_mechanism_audit(REPO_ROOT / BATCH_SAMPLING_CONTRAST_AUDIT_FILE)
    model_free_region_audit = read_mechanism_audit(REPO_ROOT / MODEL_FREE_REGION_SIGNAL_AUDIT_FILE)
    model_free_region_scan = read_mechanism_audit(REPO_ROOT / MODEL_FREE_REGION_CANDIDATE_SCAN_FILE)
    model_free_family_scan = read_mechanism_audit(REPO_ROOT / MODEL_FREE_REGION_FAMILY_SCAN_FILE)
    choice_region_audit = read_mechanism_audit(REPO_ROOT / CHOICE_MODEL_FREE_REGION_SIGNAL_AUDIT_FILE)
    choice_region_scan = read_mechanism_audit(REPO_ROOT / CHOICE_MODEL_FREE_REGION_CANDIDATE_SCAN_FILE)
    choice_family_scan = read_mechanism_audit(REPO_ROOT / CHOICE_MODEL_FREE_REGION_FAMILY_SCAN_FILE)
    matched_cache_audit = read_cache_audit(REPO_ROOT / MATCHED_REGION_CACHE_AUDIT_FILE)
    matched_missing_manifest = read_manifest_summary(REPO_ROOT / MATCHED_REGION_MISSING_MANIFEST_FILE)
    matched_present_support = read_support_manifest_summary(REPO_ROOT / MATCHED_REGION_S3_PRESENT_SCORED_FILE)
    matched_support80 = read_support_manifest_summary(REPO_ROOT / MATCHED_REGION_S3_PRESENT_SUPPORT80_FILE)
    matched_support80_hdf5 = read_support_manifest_summary(
        REPO_ROOT / MATCHED_REGION_S3_PRESENT_SUPPORT80_HDF5_FILE
    )
    matched_support80_hdf5_iterative = read_support_manifest_summary(
        REPO_ROOT / MATCHED_REGION_S3_PRESENT_SUPPORT80_HDF5_ITERATIVE_FILE
    )
    model_free_matched_panel = read_mechanism_audit(REPO_ROOT / MODEL_FREE_MATCHED_SUPPORT80_PANEL_FILE)
    model_free_positive_holdouts = read_mechanism_audit(REPO_ROOT / MODEL_FREE_POSITIVE_HOLDOUTS_MECHANISM_FILE)
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
        local_probes,
        batch_sampling_audit,
        model_free_region_audit,
        model_free_region_scan,
        model_free_family_scan,
        choice_region_audit,
        choice_region_scan,
        choice_family_scan,
        matched_cache_audit,
        matched_missing_manifest,
        matched_present_support,
        matched_support80,
        matched_support80_hdf5,
        matched_support80_hdf5_iterative,
        model_free_matched_panel,
        model_free_positive_holdouts,
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
        "local_probe_matrix": [
            row.__dict__ | {
                "gate_source": display_path(row.gate_source),
                "mismatch_source": display_path(row.mismatch_source),
                "outcome": local_probe_outcome(row),
            }
            for row in local_probes
        ],
        "batch_sampling_contrast_audit": batch_sampling_audit,
        "model_free_region_signal_audit": model_free_region_audit,
        "model_free_region_candidate_scan": model_free_region_scan,
        "model_free_region_family_scan": model_free_family_scan,
        "choice_model_free_region_signal_audit": choice_region_audit,
        "choice_model_free_region_candidate_scan": choice_region_scan,
        "choice_model_free_region_family_scan": choice_family_scan,
        "matched_region_cache_audit": (
            None if matched_cache_audit is None
            else matched_cache_audit | {"source": display_path(matched_cache_audit["source"])}
        ),
        "matched_region_missing_manifest": (
            None if matched_missing_manifest is None
            else matched_missing_manifest | {"source": display_path(matched_missing_manifest["source"])}
        ),
        "matched_region_s3_present_support": (
            None if matched_present_support is None
            else matched_present_support | {"source": display_path(matched_present_support["source"])}
        ),
        "matched_region_s3_present_support80": (
            None if matched_support80 is None
            else matched_support80 | {"source": display_path(matched_support80["source"])}
        ),
        "matched_region_s3_present_support80_hdf5": (
            None if matched_support80_hdf5 is None
            else matched_support80_hdf5 | {"source": display_path(matched_support80_hdf5["source"])}
        ),
        "matched_region_s3_present_support80_hdf5_iterative": (
            None if matched_support80_hdf5_iterative is None
            else matched_support80_hdf5_iterative | {
                "source": display_path(matched_support80_hdf5_iterative["source"])
            }
        ),
        "model_free_matched_support80_panel": model_free_matched_panel,
        "model_free_positive_holdouts_mechanism": model_free_positive_holdouts,
    }, indent=2, sort_keys=True) + "\n")
    print(f"wrote {args.out_md}")
    print(f"wrote {args.out_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
