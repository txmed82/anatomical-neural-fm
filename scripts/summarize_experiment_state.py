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
MANIFEST_TARGET_ANATOMY_FEASIBILITY_FILE = "docs/manifest_target_anatomy_feasibility.json"
SHARED_FAMILY_TARGET_CONTROL_GATE_FILE = "docs/shared_family_target_control_gate.json"
SHARED_FAMILY_CHOICE_FIBER_CSH_NEAR_MISS_FILE = "docs/shared_family_choice_fiber_csh_near_miss.json"
SHARED_BROAD_ANATOMY_REPAIR_SWEEP_FILE = "docs/shared_broad_anatomy_repair_sweep.json"
SHARED_FAMILY_ITERATIVE_MANIFEST_GATE_FILE = "docs/shared_family_iterative_manifest_gate.json"
NEXT_BENCHMARK_CONTROL_OPTIONS_FILE = "docs/next_benchmark_control_options.json"
DERIVED_TARGET_FAMILY_GATE_FILE = "docs/derived_target_family_gate.json"
CONTEXTUAL_TARGET_FAMILY_GATE_FILE = "docs/contextual_target_family_gate.json"
WHEEL_TARGET_FAMILY_GATE_FILE = "docs/wheel_target_family_gate.json"
EXTREME_QUANTILE_TARGET_FAMILY_GATE_FILE = "docs/extreme_quantile_target_family_gate.json"
EXTREME_QUANTILE_SEED_SENSITIVITY_FILE = "docs/extreme_quantile_seed_sensitivity.json"
LOCAL_CACHED_MANIFEST_CANDIDATES_FILE = "docs/local_cached_manifest_candidates.json"
EXTERNAL_MANIFEST_ACQUISITION_GAP_FILE = "docs/external_manifest_acquisition_gap.json"
BEHAVIOR_CACHE_PREFLIGHT_FILE = "docs/behavior_cache_preflight.json"
MODEL_FREE_MATCHED_SUPPORT80_PANEL_FILE = "docs/model_free_matched_support80_hdf5_panel.json"
MODEL_FREE_POSITIVE_HOLDOUTS_MECHANISM_FILE = "docs/model_free_positive_holdouts_mechanism.json"
MODEL_FREE_RECORDING_BIDIRECTIONAL_GATE_FILE = "docs/model_free_recording_bidirectional_gate.json"
MODEL_FREE_RECORDING_BIDIRECTIONAL_FRACTIONS_FILE = "docs/model_free_recording_bidirectional_gate_fractions.json"
MODEL_FREE_RECORDING_BIDIRECTIONAL_RECORDING_CENTERED_FILE = (
    "docs/model_free_recording_bidirectional_gate_recording_centered.json"
)
MODEL_FREE_RECORDING_BIDIRECTIONAL_GRANDPARENT_RECORDING_CENTERED_FILE = (
    "docs/model_free_recording_bidirectional_gate_grandparent_recording_centered.json"
)
MODEL_FREE_RECORDING_BIDIRECTIONAL_UNIT_RESIDUALS_FILE = (
    "docs/model_free_recording_bidirectional_gate_unit_residuals.json"
)
MODEL_FREE_RECORDING_BIDIRECTIONAL_PRIOR_FILE = "docs/model_free_recording_bidirectional_gate_prior_side.json"
MODEL_FREE_RECORDING_BIDIRECTIONAL_FEEDBACK_FILE = "docs/model_free_recording_bidirectional_gate_feedback.json"
MODEL_FREE_SOURCE_TARGET_PAIR_RECORDING_CENTERED_FILE = (
    "docs/model_free_source_target_pair_gate_recording_centered.json"
)
MODEL_FREE_SOURCE_TARGET_PAIR_FAMILIES_RECORDING_CENTERED_FILE = (
    "docs/model_free_source_target_pair_gate_families_recording_centered.json"
)
MODEL_FREE_GATE_BLOCKER_AUDIT_FILE = "docs/model_free_gate_blocker_audit.json"
MODEL_FREE_RECORDING_SUPPORT_AUDIT_FILE = "docs/model_free_recording_support_audit.json"
RECORDING_BIDIRECTIONALITY_PROSPECTUS_FILE = "docs/recording_bidirectionality_prospectus.json"
DERIVED_TARGET_FAMILY_PROSPECT_LEADS_FILE = "docs/derived_target_family_gate_prospect_leads.json"
PROSPECT_LEAD_CANDIDATE_VALIDATION_FILE = "docs/prospect_lead_candidate_validation.json"
PROSPECT_LEAD_FEATURE_MODE_VALIDATION_FILE = "docs/prospect_lead_feature_mode_validation.json"
PROSPECT_LEAD_SUBJECT_STABILITY_FILE = "docs/prospect_lead_subject_stability.json"
SUBJECT_STABLE_LOCAL_GATE_PROSPECTUS_FILE = "docs/subject_stable_local_gate_prospectus.json"
SUBJECT_STABLE_SHUFFLE_SEED_SENSITIVITY_FILE = "docs/subject_stable_shuffle_seed_sensitivity.json"
SUBJECT_STABLE_BROAD_ANATOMY_MECHANISM_FILE = "docs/subject_stable_broad_anatomy_mechanism.json"
MODEL_FREE_RECORDING_DIRECTIONALITY_AUDIT_FILE = "docs/model_free_recording_directionality_audit.json"
SYMMETRIC_RECORDING_SUPPORT_AUDIT_FILE = "docs/symmetric_recording_support_audit.json"
SYMMETRIC_THRESHOLD_SENSITIVITY_AUDIT_FILE = "docs/symmetric_threshold_sensitivity_audit.json"
SYMMETRIC_STRICT_FAILURE_MODES_FILE = "docs/symmetric_strict_failure_modes.json"
MODEL_FREE_RECORDING_REPLICATION_AUDIT_FILE = "docs/model_free_recording_replication_audit.json"
MODEL_FREE_FAMILY_BIDIRECTIONAL_RECORDING_CENTERED_FILE = (
    "docs/model_free_family_bidirectional_gate_recording_centered.json"
)
MODEL_FREE_FAMILY_BIDIRECTIONAL_RECORDING_CENTERED_L2_1_FILE = (
    "docs/model_free_family_bidirectional_gate_recording_centered_l2_1.json"
)
MODEL_FREE_FAMILY_BIDIRECTIONAL_RECORDING_CENTERED_L2_100_FILE = (
    "docs/model_free_family_bidirectional_gate_recording_centered_l2_100.json"
)
MODEL_FREE_FAMILY_BIDIRECTIONAL_PRIOR_RECORDING_CENTERED_FILE = (
    "docs/model_free_family_bidirectional_gate_prior_side_recording_centered.json"
)
MODEL_FREE_FAMILY_BIDIRECTIONAL_FEEDBACK_RECORDING_CENTERED_FILE = (
    "docs/model_free_family_bidirectional_gate_feedback_recording_centered.json"
)
MODEL_FREE_FAMILY_KS014_NEAR_MISS_FILE = "docs/model_free_family_ks014_near_miss_mechanism.json"
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
    manifest_target_anatomy_feasibility: dict | None = None,
    shared_family_target_control_gate: dict | None = None,
    shared_family_choice_fiber_csh_near_miss: dict | None = None,
    shared_broad_anatomy_repair_sweep: dict | None = None,
    shared_family_iterative_manifest_gate: dict | None = None,
    next_benchmark_control_options: dict | None = None,
    derived_target_family_gate: dict | None = None,
    contextual_target_family_gate: dict | None = None,
    wheel_target_family_gate: dict | None = None,
    extreme_quantile_target_family_gate: dict | None = None,
    extreme_quantile_seed_sensitivity: dict | None = None,
    local_cached_manifest_candidates: dict | None = None,
    external_manifest_acquisition_gap: dict | None = None,
    behavior_cache_preflight: dict | None = None,
    model_free_matched_panel: dict | None = None,
    model_free_positive_holdouts: dict | None = None,
    model_free_recording_bidirectional_gate: dict | None = None,
    model_free_recording_bidirectional_fractions: dict | None = None,
    model_free_recording_bidirectional_recording_centered: dict | None = None,
    model_free_recording_bidirectional_grandparent_recording_centered: dict | None = None,
    model_free_recording_bidirectional_unit_residuals: dict | None = None,
    model_free_recording_bidirectional_prior: dict | None = None,
    model_free_recording_bidirectional_feedback: dict | None = None,
    model_free_source_target_pair_recording_centered: dict | None = None,
    model_free_source_target_pair_families_recording_centered: dict | None = None,
    model_free_gate_blocker_audit: dict | None = None,
    model_free_recording_support_audit: dict | None = None,
    recording_bidirectionality_prospectus: dict | None = None,
    derived_target_family_prospect_leads: dict | None = None,
    prospect_lead_candidate_validation: dict | None = None,
    prospect_lead_feature_mode_validation: dict | None = None,
    prospect_lead_subject_stability: dict | None = None,
    subject_stable_local_gate_prospectus: dict | None = None,
    subject_stable_shuffle_seed_sensitivity: dict | None = None,
    subject_stable_broad_anatomy_mechanism: dict | None = None,
    model_free_recording_directionality_audit: dict | None = None,
    symmetric_recording_support_audit: dict | None = None,
    symmetric_threshold_sensitivity_audit: dict | None = None,
    symmetric_strict_failure_modes: dict | None = None,
    model_free_recording_replication_audit: dict | None = None,
    model_free_family_bidirectional_recording_centered: dict | None = None,
    model_free_family_bidirectional_recording_centered_l2_1: dict | None = None,
    model_free_family_bidirectional_recording_centered_l2_100: dict | None = None,
    model_free_family_bidirectional_prior_recording_centered: dict | None = None,
    model_free_family_bidirectional_feedback_recording_centered: dict | None = None,
    model_free_family_ks014_near_miss: dict | None = None,
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
    if manifest_target_anatomy_feasibility is not None:
        lines += [
            "## Manifest Target/Anatomy Feasibility Audit",
            "",
            "`docs/manifest_target_anatomy_feasibility.md` checks whether current",
            "HDF5-backed manifests have balanced within-recording trials for each",
            "target mode and enough shared anatomical family support for a benchmark",
            "redesign.",
            "",
            "| manifest | recordings | subjects | promotable targets | shared families | decision |",
            "|---|---:|---:|---|---:|---|",
        ]
        for manifest in manifest_target_anatomy_feasibility.get("manifests", []):
            lines.append(
                f"| {manifest['label']} | {manifest['n_recordings']} | "
                f"{manifest['n_subjects']} | "
                f"{', '.join(manifest['promotable_targets']) or 'none'} | "
                f"{manifest['anatomy']['n_families_all_subjects_pass']} | "
                f"`{manifest['decision']}` |"
            )
        lines += [
            "",
            (
                "Decision: the current full matched manifest is feasible enough for "
                "another local target/control redesign. The next branch should focus on "
                "specific shared families such as thalamic, hippocampal formation, and "
                "fiber tracts under the same recording-bidirectional gate, not on GPU "
                "training or recording-subset narrowing."
            ),
            "",
        ]
    if local_cached_manifest_candidates is not None:
        summary = local_cached_manifest_candidates["summary"]
        lines += [
            "## Local Cached Manifest Candidate Audit",
            "",
            "`docs/local_cached_manifest_candidates.md` tests whether the extra",
            "locally cached recordings create a better prospective manifest before",
            "any new data fetch or GPU launch.",
            "",
            f"- local recordings: `{summary['n_local_recordings']}`",
            f"- local subjects: `{summary['n_local_subjects']}`",
            f"- candidate panels: `{summary['n_candidate_panels']}`",
            f"- new candidate panels: `{summary['n_new_candidate_panels']}`",
            f"- best panel: `{summary['best_panel']}`",
            f"- decision: `{summary['decision']}`",
            "",
            "| panel | recordings | subjects | passing target/family rows | decision |",
            "|---|---:|---:|---:|---|",
        ]
        for panel in local_cached_manifest_candidates["panels"]:
            lines.append(
                f"| {panel['label']} | {panel['n_recordings']} | {panel['n_subjects']} | "
                f"{panel['n_passing_target_family_rows']} | `{panel['decision']}` |"
            )
        lines += [
            "",
            (
                "Decision: the extra local recordings add MFD_08/MFD_09 coverage, but "
                "the expanded panels fail the prospective per-subject target/family "
                "support floor. The next manifest branch needs a broader external "
                "selection rule or a different target/control definition, not a GPU "
                "run on the local expansion."
            ),
            "",
        ]
    if external_manifest_acquisition_gap is not None:
        summary = external_manifest_acquisition_gap["summary"]
        lines += [
            "## External Manifest Acquisition Gap Audit",
            "",
            "`docs/external_manifest_acquisition_gap.md` compares the broader",
            "S3-present metadata-scored manifest against local HDF5 coverage.",
            "",
            f"- broad manifest recordings: `{summary['n_broad_recordings']}`",
            f"- broad manifest subjects: `{summary['n_broad_subjects']}`",
            f"- local HDF5 recordings in broad manifest: `{summary['n_local_hdf5_recordings_in_broad_manifest']}`",
            f"- support-qualified subjects: `{summary['support_qualified_subjects']}`",
            f"- support-qualified subjects missing HDF5: `{summary['support_qualified_subjects_missing_hdf5']}`",
            f"- missing HDF5 recordings for qualified subjects: `{summary['missing_hdf5_recordings_for_qualified_subjects']}`",
            f"- projected manifest: `{summary['projected_manifest_recordings']}` recordings, `{summary['projected_manifest_subjects']}` subjects",
            f"- decision: `{summary['decision']}`",
            "",
            "| subject | support | broad recs | local HDF5 | missing HDF5 | qualified |",
            "|---|---:|---:|---:|---:|---|",
        ]
        for row in external_manifest_acquisition_gap["subject_rows"][:8]:
            support = "n/a" if row["unit_support_frac"] is None else f"{row['unit_support_frac']:.3f}"
            lines.append(
                f"| {row['subject']} | {support} | {row['n_recordings']} | "
                f"{row['local_hdf5_recordings']} | {row['missing_hdf5_recordings']} | "
                f"{row['support_qualified']} |"
            )
        lines += [
            "",
            (
                "Decision: this is a data-acquisition trigger, not a training trigger. "
                "The concrete next set is seven missing HDF5 recordings for CSHL045 "
                "and ZFM-01577; after acquiring them, rerun the local manifest and "
                "model-free gates before any GPU run."
            ),
            "",
        ]
    if shared_family_target_control_gate is not None:
        summary = shared_family_target_control_gate["summary"]
        top = summary["top_rows"][:4]
        lines += [
            "## Shared-Family Target/Control Gate",
            "",
            "`docs/shared_family_target_control_gate.md` tests the feasible shared",
            "families across all four target modes with the same model-free",
            "true-vs-shuffled and recording-bidirectional promotion gate.",
            "",
            f"- rows: `{summary['n_rows']}`",
            f"- candidates: `{summary['n_candidates']}`",
            f"- positive centered-delta rows: `{summary['n_positive_centered_delta']}`",
            f"- max bidirectional recordings: `{summary['max_bidirectional_recordings']}`",
            f"- max bidirectional recording fraction: `{summary['max_bidirectional_recording_fraction']:.3f}`",
            f"- decision: `{summary['decision']}`",
            "",
            "| target | family | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs |",
            "|---|---|---|---|---:|---:|---:|---:|---:|",
        ]
        for row in top:
            lines.append(
                f"| {row['target_mode']} | {row['family']} | {row['holdout']} | "
                f"{row['decision']} | {row['centered_delta_vs_shuffle']:+.3f} | "
                f"{row['centered_delta_vs_total']:+.3f} | "
                f"{row['target0_improved_vs_shuffle']:.3f} | "
                f"{row['target1_improved_vs_shuffle']:.3f} | "
                f"{row['n_bidirectional_recordings']}/{row['n_recordings']} |"
            )
        lines += [
            "",
            (
                "Decision: shared-family target/control narrowing does not yet produce "
                "a promotable local signal. The best row has real centered deltas and "
                "global bidirectional target support, but fails same-recording support "
                "at `1/4`; do not launch GPU training from this branch."
            ),
            "",
        ]
    if shared_family_choice_fiber_csh_near_miss is not None:
        summary = shared_family_choice_fiber_csh_near_miss["summary"]
        global_row = shared_family_choice_fiber_csh_near_miss["global"]
        lines += [
            "## Shared-Family Near-Miss Mechanism",
            "",
            "`docs/shared_family_choice_fiber_csh_near_miss.md` decomposes the",
            "strongest shared-family row, `choice` + `fiber_tracts` on `CSH_ZAD_019`,",
            "by held-out recording.",
            "",
            f"- centered delta vs shuffle: `{global_row['centered_delta_vs_shuffle']:+.3f}`",
            f"- centered delta vs total: `{global_row['centered_delta_vs_total']:+.3f}`",
            f"- global target0: `{global_row['target0_improved_vs_shuffle']:.3f}`",
            f"- global target1: `{global_row['target1_improved_vs_shuffle']:.3f}`",
            f"- bidirectional recordings: `{summary['n_bidirectional_recordings']}/{summary['n_recordings']}`",
            f"- target0-positive recordings: `{summary['n_target0_positive_recordings']}/{summary['n_recordings']}`",
            f"- target1-positive recordings: `{summary['n_target1_positive_recordings']}/{summary['n_recordings']}`",
            f"- decision: `{summary['decision']}`",
            "",
            (
                "Decision: this large-delta near miss is not a training trigger. It is "
                "recording-local target1 support with target0 clearing in only one "
                "recording, so a neural run would likely amplify the same one-sided "
                "artifact rather than demonstrate bidirectional anatomical transfer."
            ),
            "",
        ]
    if shared_broad_anatomy_repair_sweep is not None:
        summary = shared_broad_anatomy_repair_sweep["summary"]
        top = summary["top_rows"][:6]
        lines += [
            "## Shared Broad-Anatomy Repair Sweep",
            "",
            "`docs/shared_broad_anatomy_repair_sweep.md` reruns the two nearest",
            "shared broad-anatomy misses across local feature transforms and ridge",
            "regularization values.",
            "",
            f"- rows: `{summary['n_rows']}`",
            f"- candidates: `{summary['n_candidates']}`",
            f"- max bidirectional recordings: `{summary['max_bidirectional_recordings']}`",
            f"- max min target margin: `{summary['max_min_target_margin']:+.3f}`",
            f"- max centered delta vs shuffle: `{summary['max_centered_delta_vs_shuffle']:+.3f}`",
            f"- decision: `{summary['decision']}`",
            "",
            "| target | holdout | feature | l2 | missing | delta shuffle | delta total | targets | bidir recs |",
            "|---|---|---|---:|---|---:|---:|---|---:|",
        ]
        for row in top:
            lines.append(
                f"| {row['target_mode']} | {row['holdout']} | {row['feature_mode']} | {row['l2']:.0f} | "
                f"{', '.join(row['missing_requirements']) or 'none'} | "
                f"{row['centered_delta_vs_shuffle']:+.3f} | {row['centered_delta_vs_total']:+.3f} | "
                f"{row['target0_improved_vs_shuffle']:.3f}/{row['target1_improved_vs_shuffle']:.3f} | "
                f"{row['n_bidirectional_recordings']}/{row['required_bidirectional_recordings']} |"
            )
        lines += [
            "",
            (
                "Decision: this closes the simple shared broad-anatomy repair branch. "
                "The best comparable rows remain one bidirectional recording short and "
                "also miss target0 and/or baseline controls, so they are not a GPU trigger."
            ),
            "",
        ]
    if shared_family_iterative_manifest_gate is not None:
        summary = shared_family_iterative_manifest_gate["summary"]
        top = summary["top_rows"][:6]
        lines += [
            "## Shared-Family Iterative Manifest Gate",
            "",
            "`docs/shared_family_iterative_manifest_gate.md` reruns the shared-family",
            "target/control gate on the strict 8-recording, 2-subject iterative-pass",
            "manifest using all families that pass its feasibility floor.",
            "",
            f"- rows: `{summary['n_rows']}`",
            f"- candidates: `{summary['n_candidates']}`",
            f"- positive centered-delta rows: `{summary['n_positive_centered_delta']}`",
            f"- max bidirectional recordings: `{summary['max_bidirectional_recordings']}`",
            f"- max bidirectional recording fraction: `{summary['max_bidirectional_recording_fraction']:.3f}`",
            f"- decision: `{summary['decision']}`",
            "",
            "| target | family | holdout | decision | delta shuffle | delta total | targets | bidir recs |",
            "|---|---|---|---|---:|---:|---|---:|",
        ]
        for row in top:
            lines.append(
                f"| {row['target_mode']} | {row['family']} | {row['holdout']} | {row['decision']} | "
                f"{row['centered_delta_vs_shuffle']:+.3f} | {row['centered_delta_vs_total']:+.3f} | "
                f"{row['target0_improved_vs_shuffle']:.3f}/{row['target1_improved_vs_shuffle']:.3f} | "
                f"{row['n_bidirectional_recordings']}/{row['n_recordings']} |"
            )
        lines += [
            "",
            (
                "Decision: stricter manifest support alone does not rescue the signal. "
                "The clean 2-subject panel is too narrow for a demo and still reaches "
                "only `1/4` same-recording bidirectional support, so the next branch "
                "must change the benchmark/control definition rather than further "
                "narrow this manifest."
            ),
            "",
        ]
    if next_benchmark_control_options is not None:
        summary = next_benchmark_control_options["summary"]
        top = next_benchmark_control_options["branches"][:4]
        lines += [
            "## Next Benchmark/Control Options Audit",
            "",
            "`docs/next_benchmark_control_options.md` ranks the remaining no-spend",
            "branches after the current local negative audits.",
            "",
            f"- recommended next: `{summary['recommended_next']}`",
            f"- closed branches: `{summary['closed_branches']}`",
            f"- decision: `{summary['decision']}`",
            f"- GPU trigger: {summary['gpu_training_trigger']}",
            "",
            "| priority | branch | status | next action |",
            "|---:|---|---|---|",
        ]
        for row in top:
            lines.append(
                f"| {row['priority']} | {row['name']} | `{row['status']}` | {row['next_action']} |"
            )
        lines += [""]
        if summary["decision"] == "behavior_cache_rebuild_required":
            lines += [
                (
                    "Decision: direct cached target redesign is closed as a GPU "
                    "trigger. The next aligned work is a behavior-inclusive cache "
                    "rebuild, followed by the same local model-free gate before any "
                    "paid training."
                ),
                "",
            ]
        elif summary["decision"] == "wheel_target_audit_required":
            lines += [
                (
                    "Decision: the behavior cache is ready, but wheel-derived targets "
                    "still need the same local model-free gate before any paid training."
                ),
                "",
            ]
        else:
            lines += [
                (
                    "Decision: the current cached target, contextual target, "
                    "wheel-derived target, reaction-dynamics target, cell-type "
                    "prior target/control, waveform target/control, and meta-failure "
                    "synthesis branches are closed as GPU triggers. The next aligned "
                    "work is a prospectively supported benchmark/control redesign, "
                    "still gated locally before any paid training."
                ),
                "",
            ]
    if behavior_cache_preflight is not None:
        summary = behavior_cache_preflight["summary"]
        stream_counts = ", ".join(
            f"{stream}={count}/{summary['n_manifest_recordings']}"
            for stream, count in summary["stream_counts"].items()
        )
        cache_ready = summary["decision"] == "behavior_cache_ready"
        commands = [] if cache_ready else behavior_cache_preflight.get("build_commands", [])[:2]
        lines += [
            "## Behavior Cache Preflight",
            "",
            "`docs/behavior_cache_preflight.md` inspects whether the active matched",
            "HDF5 cache contains the richer behavior streams needed for the next",
            "target/control branch.",
            "",
            f"- manifest recordings: `{summary['n_manifest_recordings']}`",
            f"- present files: `{summary['n_present_files']}`",
            f"- required stream coverage: `{stream_counts}`",
            f"- recordings needing behavior rebuild: `{summary['n_recordings_needing_behavior_rebuild']}`",
            f"- decision: `{summary['decision']}`",
            "",
        ]
        if commands:
            lines += [
                "First rebuild commands:",
                "",
                "```bash",
                *commands,
                "```",
                "",
            ]
        if cache_ready:
            lines += [
                (
                    "Decision: the matched cache now has the required wheel stream, "
                    "so the next no-spend step is the wheel-derived target family "
                    "gate. GPU training remains blocked unless that local gate passes."
                ),
                "",
            ]
        else:
            lines += [
                (
                    "Decision: the matched cache is still missing `wheel` in at "
                    "least one recording, so the next no-spend step is a "
                    "behavior-inclusive cache rebuild. GPU training remains "
                    "blocked until a wheel or external behavior target passes "
                    "the same local gate."
                ),
                "",
            ]
    if derived_target_family_gate is not None:
        summary = derived_target_family_gate["summary"]
        balances = summary["target_balances"]
        top = summary["top_rows"][:6]
        lines += [
            "## Derived Target Family Gate",
            "",
            "`docs/derived_target_family_gate.md` tests the recommended new",
            "benchmark/control direction using three cached trial-field targets:",
            "`contrast_strength`, `response_latency`, and `prior_engaged`.",
            "",
            f"- rows: `{summary['n_rows']}`",
            f"- candidates: `{summary['n_candidates']}`",
            f"- positive centered-delta rows: `{summary['n_positive_centered_delta']}`",
            f"- max bidirectional recordings: `{summary['max_bidirectional_recordings']}`",
            f"- max bidirectional recording fraction: `{summary['max_bidirectional_recording_fraction']:.3f}`",
            f"- decision: `{summary['decision']}`",
            "",
            "| target | trials | eligible recordings | recordings |",
            "|---|---:|---:|---:|",
        ]
        for target, row in balances.items():
            lines.append(
                f"| {target} | {row['n_trials']} | {row['eligible_recordings']} | {row['n_recordings']} |"
            )
        lines += [
            "",
            "| target | family | holdout | decision | delta shuffle | delta total | targets | bidir recs |",
            "|---|---|---|---|---:|---:|---|---:|",
        ]
        for row in top:
            lines.append(
                f"| {row['target_mode']} | {row['family']} | {row['holdout']} | {row['decision']} | "
                f"{row['centered_delta_vs_shuffle']:+.3f} | {row['centered_delta_vs_total']:+.3f} | "
                f"{row['target0_improved_vs_shuffle']:.3f}/{row['target1_improved_vs_shuffle']:.3f} | "
                f"{row['n_bidirectional_recordings']}/{row['n_recordings']} |"
            )
        lines += [
            "",
            (
                "Decision: cached trial-field target redesign does not yet justify "
                "GPU training. `response_latency` gives the nearest symmetric row "
                "with `3/4` bidirectional recordings, but it still loses to the "
                "within-recording shuffle control. Other positive rows remain "
                "one-sided or fail the total-spike baseline."
            ),
            "",
        ]
    if contextual_target_family_gate is not None:
        summary = contextual_target_family_gate["summary"]
        balances = summary["target_balances"]
        top = summary["top_rows"][:6]
        lines += [
            "## Contextual Target Family Gate",
            "",
            "`docs/contextual_target_family_gate.md` tests trial-sequence target",
            "definitions that are not direct task labels: `post_error`,",
            "`prior_block_switch`, and `prior_block_late`.",
            "",
            f"- rows: `{summary['n_rows']}`",
            f"- candidates: `{summary['n_candidates']}`",
            f"- positive centered-delta rows: `{summary['n_positive_centered_delta']}`",
            f"- max bidirectional recordings: `{summary['max_bidirectional_recordings']}`",
            f"- max bidirectional recording fraction: `{summary['max_bidirectional_recording_fraction']:.3f}`",
            f"- decision: `{summary['decision']}`",
            "",
            "| target | trials | eligible recordings | recordings |",
            "|---|---:|---:|---:|",
        ]
        for target, row in balances.items():
            lines.append(
                f"| {target} | {row['n_trials']} | {row['eligible_recordings']} | {row['n_recordings']} |"
            )
        lines += [
            "",
            "| target | family | holdout | decision | delta shuffle | delta total | targets | bidir recs |",
            "|---|---|---|---|---:|---:|---|---:|",
        ]
        for row in top:
            lines.append(
                f"| {row['target_mode']} | {row['family']} | {row['holdout']} | {row['decision']} | "
                f"{row['centered_delta_vs_shuffle']:+.3f} | {row['centered_delta_vs_total']:+.3f} | "
                f"{row['target0_improved_vs_shuffle']:.3f}/{row['target1_improved_vs_shuffle']:.3f} | "
                f"{row['n_bidirectional_recordings']}/{row['n_recordings']} |"
            )
        lines += [
            "",
            (
                "Decision: trial-sequence context does not create a training trigger. "
                "The best contextual rows still fail the shuffle control, one global "
                "target direction, or the total-spike baseline, and max same-recording "
                "bidirectional support is only `2/4`."
            ),
            "",
        ]
    if wheel_target_family_gate is not None:
        summary = wheel_target_family_gate["summary"]
        balances = summary["target_balances"]
        top = summary["top_rows"][:6]
        lines += [
            "## Wheel Target Family Gate",
            "",
            "`docs/wheel_target_family_gate.md` tests target definitions derived",
            "from cached wheel position: `wheel_active`, `wheel_displacement`,",
            "and `choice_aligned_wheel`.",
            "",
            f"- rows: `{summary['n_rows']}`",
            f"- candidates: `{summary['n_candidates']}`",
            f"- positive centered-delta rows: `{summary['n_positive_centered_delta']}`",
            f"- max bidirectional recordings: `{summary['max_bidirectional_recordings']}`",
            f"- max bidirectional recording fraction: `{summary['max_bidirectional_recording_fraction']:.3f}`",
            f"- decision: `{summary['decision']}`",
            "",
            "| target | trials | eligible recordings | recordings |",
            "|---|---:|---:|---:|",
        ]
        for target, row in balances.items():
            lines.append(
                f"| {target} | {row['n_trials']} | {row['eligible_recordings']} | {row['n_recordings']} |"
            )
        lines += [
            "",
            "| target | family | holdout | decision | delta shuffle | delta total | targets | bidir recs |",
            "|---|---|---|---|---:|---:|---|---:|",
        ]
        for row in top:
            lines.append(
                f"| {row['target_mode']} | {row['family']} | {row['holdout']} | {row['decision']} | "
                f"{row['centered_delta_vs_shuffle']:+.3f} | {row['centered_delta_vs_total']:+.3f} | "
                f"{row['target0_improved_vs_shuffle']:.3f}/{row['target1_improved_vs_shuffle']:.3f} | "
                f"{row['n_bidirectional_recordings']}/{row['n_recordings']} |"
            )
        lines += [
            "",
            (
                "Decision: wheel-derived targets only justify paid training if they "
                "clear the same true-vs-shuffle, total-baseline, global target, and "
                "same-recording bidirectional gate used by the prior audits."
            ),
            "",
        ]
    if extreme_quantile_target_family_gate is not None:
        summary = extreme_quantile_target_family_gate["summary"]
        top = summary["top_rows"][:8]
        lines += [
            "## Extreme-Quantile Target Family Gate",
            "",
            "`docs/extreme_quantile_target_family_gate.md` drops middle trials and",
            "labels continuous behavioral targets by within-recording low/high",
            "quantiles before running the unchanged shared-family local gate.",
            "",
            f"- candidates: `{summary['n_candidates']}`",
            f"- positive centered-delta rows: `{summary['n_positive_centered_delta']}`",
            f"- max bidirectional recording fraction: `{summary['max_bidirectional_recording_fraction']:.3f}`",
            f"- decision: `{summary['decision']}`",
            "",
            "| target | family | holdout | decision | delta shuffle | delta total | targets | bidir recs |",
            "|---|---|---|---|---:|---:|---:|---:|",
        ]
        for row in top:
            lines.append(
                f"| {row['target_mode']} | {row['family']} | {row['holdout']} | {row['decision']} | "
                f"{row['centered_delta_vs_shuffle']:+.3f} | {row['centered_delta_vs_total']:+.3f} | "
                f"{row['target0_improved_vs_shuffle']:.3f}/{row['target1_improved_vs_shuffle']:.3f} | "
                f"{row['n_bidirectional_recordings']}/{row['n_recordings']} |"
            )
        lines += [
            "",
            (
                "Decision before seed validation: this is a local candidate only, not "
                "a GPU trigger. The margins are tiny, so require shuffle-seed stability "
                "before any paid training."
            ),
            "",
        ]
    if extreme_quantile_seed_sensitivity is not None:
        summary = extreme_quantile_seed_sensitivity["summary"]
        top = extreme_quantile_seed_sensitivity["rows"][:5]
        lines += [
            "## Extreme-Quantile Shuffle Seed Sensitivity",
            "",
            "`docs/extreme_quantile_seed_sensitivity.md` reruns the strict",
            "extreme-quantile candidate across multiple within-recording shuffle seeds.",
            "",
            f"- cases: `{summary['n_cases']}`",
            f"- robust shuffle-seed candidates: `{summary['n_robust_shuffle_seed_candidates']}`",
            f"- max positive shuffle-delta fraction: `{summary['max_positive_shuffle_delta_fraction']:.3f}`",
            f"- decision: `{summary['decision']}`",
            "",
            "| target | family | holdout | positive seeds | candidate seeds | mean shuffle delta | mean total delta | mean targets | bidir range |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|",
        ]
        for row in top:
            lines.append(
                f"| {row['target_mode']} | {row['family']} | {row['holdout']} | "
                f"{row['n_positive_shuffle_delta_seeds']}/{row['n_seeds']} | "
                f"{row['n_candidate_seeds']}/{row['n_seeds']} | "
                f"{row['mean_centered_delta_vs_shuffle']:+.4f} | "
                f"{row['mean_centered_delta_vs_total']:+.4f} | "
                f"{row['mean_target0']:.3f}/{row['mean_target1']:.3f} | "
                f"{row['min_bidirectional_recordings']}-{row['max_bidirectional_recordings']} |"
            )
        lines += [
            "",
            (
                "Decision: do not train from the extreme-quantile candidate. It keeps "
                "4/4 bidirectional recording support, but true-vs-shuffle is positive "
                "in only 2/5 seeds and the mean shuffle delta is slightly negative."
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
    if model_free_recording_bidirectional_gate is not None:
        summary = model_free_recording_bidirectional_gate["summary"]
        lines += [
            "## Recording-Bidirectional Model-Free Gate",
            "",
            "`docs/model_free_recording_bidirectional_gate.md` applies the stricter",
            "same-recording rule across the full matched panel: a recording counts only",
            "when true labels beat the shuffled control for target0 and target1 inside",
            "that same recording.",
            "",
            f"- candidates: `{summary['n_candidates']}/{summary['n_holdouts']}`",
            f"- positive centered-delta holdouts: `{summary['n_positive_delta_holdouts']}/{summary['n_holdouts']}`",
            f"- mean bidirectional recording fraction: `{summary['mean_bidirectional_recording_fraction']:.3f}`",
            f"- decision: `{summary['decision']}`",
            "",
            "| holdout | centered delta | target0 | target1 | bidirectional recs | decision |",
            "|---|---:|---:|---:|---:|---|",
        ]
        for row in model_free_recording_bidirectional_gate["holdouts"]:
            paired = row["summary"]["paired_true_vs_shuffle"]
            bidir = row["recording_bidirectional"]
            lines.append(
                f"| {row['holdout']} | {row['summary']['delta_centered_auc']:+.3f} | "
                f"{paired['target0_improved_fraction']:.3f} | "
                f"{paired['target1_improved_fraction']:.3f} | "
                f"{bidir['n_bidirectional_recordings']}/{bidir['n_evaluable_recordings']} | "
                f"{row['recording_bidirectional_decision']} |"
            )
        lines += [
            "",
            (
                "Decision: this closes the weak-positive loophole for the current matched "
                "panel. Only `NYU-12` has even one bidirectional held-out recording, and "
                "it still has negative centered true-minus-shuffle AUC. Do not spend on "
                "training until a new target/control produces at least one local pass "
                "under this recording-bidirectional gate."
            ),
            "",
        ]
    if model_free_recording_bidirectional_fractions is not None:
        summary = model_free_recording_bidirectional_fractions["summary"]
        lines += [
            "## Region-Fraction Feature Gate",
            "",
            "`docs/model_free_recording_bidirectional_gate_fractions.md` reruns the",
            "same recording-bidirectional gate after normalizing each trial's parent-region",
            "spike counts to fractions of that trial's total spikes.",
            "",
            f"- candidates: `{summary['n_candidates']}/{summary['n_holdouts']}`",
            f"- positive centered-delta holdouts: `{summary['n_positive_delta_holdouts']}/{summary['n_holdouts']}`",
            f"- mean bidirectional recording fraction: `{summary['mean_bidirectional_recording_fraction']:.3f}`",
            f"- decision: `{summary['decision']}`",
            "",
            (
                "Decision: simple region-composition normalization does not rescue the "
                "anatomical feature branch. It creates three positive centered-delta "
                "holdouts, but all are one-sided and have `0/4` bidirectional recordings."
            ),
            "",
        ]
    if model_free_recording_bidirectional_recording_centered is not None:
        summary = model_free_recording_bidirectional_recording_centered["summary"]
        lines += [
            "## Recording-Centered Feature Gate",
            "",
            "`docs/model_free_recording_bidirectional_gate_recording_centered.md` subtracts",
            "each recording's own mean parent-region feature vector before ridge fitting.",
            "",
            f"- candidates: `{summary['n_candidates']}/{summary['n_holdouts']}`",
            f"- positive centered-delta holdouts: `{summary['n_positive_delta_holdouts']}/{summary['n_holdouts']}`",
            f"- mean bidirectional recording fraction: `{summary['mean_bidirectional_recording_fraction']:.3f}`",
            f"- decision: `{summary['decision']}`",
            "",
            (
                "Decision: feature-level recording centering is the least one-sided "
                "normalization so far, but it remains below the gate. `KS014` has only "
                "`1/4` bidirectional recordings and both positive-delta holdouts still "
                "miss global target0."
            ),
            "",
        ]
    if model_free_recording_bidirectional_grandparent_recording_centered is not None:
        summary = model_free_recording_bidirectional_grandparent_recording_centered["summary"]
        positives = ", ".join(summary["positive_delta_holdouts"]) or "none"
        lines += [
            "## Grandparent Recording-Centered Feature Gate",
            "",
            "`docs/model_free_recording_bidirectional_gate_grandparent_recording_centered.md`",
            "reruns the hardened local gate at coarser Allen grandparent granularity",
            "with recording-centered features.",
            "",
            f"- candidates: `{summary['n_candidates']}/{summary['n_holdouts']}`",
            f"- positive centered-delta holdouts: `{summary['n_positive_delta_holdouts']}/{summary['n_holdouts']}`",
            f"- positive holdouts: `{positives}`",
            f"- mean bidirectional recording fraction: `{summary['mean_bidirectional_recording_fraction']:.3f}`",
            f"- decision: `{summary['decision']}`",
            "",
            (
                "Decision: coarser atlas granularity increases weak positive centered "
                "deltas, but it does not produce bidirectional evidence. The positive "
                "holdouts still fail global target0 and have at most `1/4` "
                "bidirectional recordings."
            ),
            "",
        ]
    if model_free_recording_bidirectional_unit_residuals is not None:
        summary = model_free_recording_bidirectional_unit_residuals["summary"]
        positives = ", ".join(summary["positive_delta_holdouts"]) or "none"
        lines += [
            "## Unit-Residual Feature Gate",
            "",
            "`docs/model_free_recording_bidirectional_gate_unit_residuals.md` subtracts",
            "each recording's expected region counts from every trial, using total spikes",
            "times that recording's static unit-region distribution.",
            "",
            f"- candidates: `{summary['n_candidates']}/{summary['n_holdouts']}`",
            f"- positive centered-delta holdouts: `{summary['n_positive_delta_holdouts']}/{summary['n_holdouts']}`",
            f"- positive holdouts: `{positives}`",
            f"- mean bidirectional recording fraction: `{summary['mean_bidirectional_recording_fraction']:.3f}`",
            f"- decision: `{summary['decision']}`",
            "",
            (
                "Decision: residualizing static anatomical coverage increases the number "
                "of positive centered deltas, but does not create a valid transfer signal. "
                "Every positive holdout remains one target direction with `0/4` "
                "bidirectional recordings."
            ),
            "",
        ]
    if model_free_source_target_pair_recording_centered is not None:
        summary = model_free_source_target_pair_recording_centered["summary"]
        counts = ", ".join(
            f"{decision}: {count}"
            for decision, count in summary["decision_counts"].items()
        )
        lines += [
            "## Source-Target Pair Gate",
            "",
            "`docs/model_free_source_target_pair_gate_recording_centered.md` trains",
            "the same closed-form recording-centered anatomy classifier on one source",
            "subject at a time and evaluates each target subject against the",
            "within-recording shuffled-label control.",
            "",
            f"- source-target pairs: `{summary['n_pairs']}`",
            f"- candidates: `{summary['n_candidates']}`",
            f"- positive centered-delta pairs: `{summary['n_positive_delta_pairs']}`",
            f"- mean bidirectional recording fraction: `{summary['mean_bidirectional_recording_fraction']:.3f}`",
            f"- decision counts: `{counts}`",
            f"- decision: `{summary['decision']}`",
            "",
            (
                "Decision: single-source training does not reveal a hidden compatible "
                "animal pair. The best positive centered-delta pairs still fail global "
                "target0 or target1 and have at most `1/4` bidirectional target "
                "recordings."
            ),
            "",
        ]
    if model_free_source_target_pair_families_recording_centered is not None:
        summary = model_free_source_target_pair_families_recording_centered["summary"]
        counts = ", ".join(
            f"{decision}: {count}"
            for decision, count in summary["decision_counts"].items()
        )
        lines += [
            "## Family Source-Target Pair Gate",
            "",
            "`docs/model_free_source_target_pair_gate_families_recording_centered.md`",
            "combines the single-source split redesign with predefined family-aggregate",
            "features and recording centering.",
            "",
            f"- source-target pairs: `{summary['n_pairs']}`",
            f"- candidates: `{summary['n_candidates']}`",
            f"- positive centered-delta pairs: `{summary['n_positive_delta_pairs']}`",
            f"- mean bidirectional recording fraction: `{summary['mean_bidirectional_recording_fraction']:.3f}`",
            f"- decision counts: `{counts}`",
            f"- decision: `{summary['decision']}`",
            "",
            (
                "Decision: combining source-target pairing with family aggregation still "
                "does not produce a local transfer candidate. It slightly increases "
                "same-recording bidirectional support, but top pairs remain below global "
                "target0/target1 and never exceed `1/4` bidirectional recordings."
            ),
            "",
        ]
    if model_free_gate_blocker_audit is not None:
        summary = model_free_gate_blocker_audit["summary"]
        blockers = summary["blocker_counts"]
        top = summary["top_bidirectional_rows"][:4]
        lines += [
            "## Model-Free Gate Blocker Audit",
            "",
            "`docs/model_free_gate_blocker_audit.md` aggregates the current local",
            "holdout and source-target model-free gates to identify which promotion",
            "checks actually block the anatomy-transfer claim.",
            "",
            f"- rows audited: `{summary['n_rows']}`",
            f"- candidates: `{summary['n_candidates']}`",
            f"- positive centered-delta rows: `{summary['n_positive_centered_delta']}`",
            f"- max bidirectional recordings: `{summary['max_bidirectional_recordings']}`",
            f"- max bidirectional recording fraction: `{summary['max_bidirectional_fraction']:.3f}`",
            f"- blocker counts: `centered_delta={blockers['centered_delta']}, target0={blockers['target0']}, target1={blockers['target1']}, recording_bidirectionality={blockers['recording_bidirectionality']}`",
            "",
            "| report | label | centered delta | target0 | target1 | bidir recs | missing checks |",
            "|---|---|---:|---:|---:|---:|---|",
        ]
        for row in top:
            lines.append(
                f"| {row['report']} | {row['label']} | {row['centered_delta']:+.3f} | "
                f"{row['target0']:.3f} | {row['target1']:.3f} | "
                f"{row['n_bidirectional_recordings']}/{row['n_recordings']} | "
                f"{', '.join(row['missing_checks'])} |"
            )
        lines += [
            "",
            (
                "Decision: the next useful experiment should not be another small "
                "feature or regularization variant. The universal blocker is "
                "same-recording bidirectionality, so any new benchmark/control proposal "
                "must first create target0+target1 evidence inside the same recordings "
                "before GPU training."
            ),
            "",
        ]
    if model_free_recording_support_audit is not None:
        summary = model_free_recording_support_audit["summary"]
        top = summary["top_recordings"][:4]
        lines += [
            "## Model-Free Recording Support Audit",
            "",
            "`docs/model_free_recording_support_audit.md` aggregates per-recording",
            "target0/target1 support across all current model-free holdout and",
            "source-target gate artifacts.",
            "",
            f"- observations: `{summary['n_observations']}`",
            f"- recordings: `{summary['n_recordings']}`",
            f"- bidirectional observations: `{summary['n_bidirectional_observations']}`",
            f"- recordings with any bidirectional support: `{summary['recordings_with_any_bidirectional_support']}`",
            f"- max bidirectional observations/recording: `{summary['max_bidirectional_observations_per_recording']}`",
            "",
            "| recording | subjects | observations | bidir obs | mean target0 | mean target1 |",
            "|---|---|---:|---:|---:|---:|",
        ]
        for row in top:
            lines.append(
                f"| {row['recording']} | {', '.join(row['target_subjects'])} | "
                f"{row['n_observations']} | {row['n_bidirectional_observations']} | "
                f"{row['mean_target0']:.3f} | {row['mean_target1']:.3f} |"
            )
        lines += [
            "",
            (
                "Decision: rare same-recording bidirectional observations are not "
                "concentrated enough to define a stable demo subset from the current "
                "cache. The next benchmark redesign should prospectively create "
                "target0+target1 evidence inside recordings, then rerun the same "
                "model-free local gate before GPU training."
            ),
            "",
        ]
    if recording_bidirectionality_prospectus is not None:
        summary = recording_bidirectionality_prospectus["summary"]
        top = summary["top_recordings"][:4]
        lines += [
            "## Recording Bidirectionality Prospectus",
            "",
            "`docs/recording_bidirectionality_prospectus.md` aggregates per-recording",
            "target0/target1 support across the current local-gate artifacts, including",
            "the newer wheel, reaction-dynamics, cell-prior, waveform, and projected",
            "support80 sweeps.",
            "",
            f"- observations: `{summary['n_observations']}`",
            f"- recordings: `{summary['n_recordings']}`",
            f"- bidirectional observations: `{summary['n_bidirectional_observations']}`",
            f"- recordings with bidirectional support: `{summary['recordings_with_bidirectional_support']}`",
            f"- prospect recordings: `{summary['n_prospect_recordings']}`",
            f"- decision: `{summary['decision']}`",
            "",
            "| recording | holdouts | observations | bidir obs | bidir sources | bidir targets | mean sym |",
            "|---|---|---:|---:|---:|---:|---:|",
        ]
        for row in top:
            lines.append(
                f"| {row['recording']} | {', '.join(row['holdouts'])} | "
                f"{row['n_observations']} | {row['n_bidirectional_observations']} | "
                f"{row['n_bidirectional_sources']} | {row['n_bidirectional_target_modes']} | "
                f"{row['mean_symmetric_support']:.3f} |"
            )
        lines += [
            "",
            (
                "Decision: this prospectus can only inform the next prospective "
                "target/control rule. It is not a GPU trigger; the unchanged local "
                "gate must pass before training."
            ),
            "",
        ]
    if derived_target_family_prospect_leads is not None:
        summary = derived_target_family_prospect_leads["summary"]
        top = summary["top_rows"][:4]
        lines += [
            "## Prospect-Lead Derived Target Gate",
            "",
            "`docs/derived_target_family_gate_prospect_leads.md` reruns the derived",
            "cached-target local gate on the 18-recording prospect-lead manifest.",
            "",
            f"- rows: `{summary['n_rows']}`",
            f"- candidates: `{summary['n_candidates']}`",
            f"- max bidirectional recordings: `{summary['max_bidirectional_recordings']}`",
            f"- max bidirectional recording fraction: `{summary['max_bidirectional_recording_fraction']:.3f}`",
            f"- decision: `{summary['decision']}`",
            "",
            "| target | family | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs |",
            "|---|---|---|---|---:|---:|---:|---:|---:|",
        ]
        for row in top:
            lines.append(
                f"| {row['target_mode']} | {row['family']} | {row['holdout']} | "
                f"{row['decision']} | {row['centered_delta_vs_shuffle']:+.3f} | "
                f"{row['centered_delta_vs_total']:+.3f} | "
                f"{row['target0_improved_vs_shuffle']:.3f} | "
                f"{row['target1_improved_vs_shuffle']:.3f} | "
                f"{row['n_bidirectional_recordings']}/{row['n_recordings']} |"
            )
        lines.append("")
    if prospect_lead_candidate_validation is not None:
        summary = prospect_lead_candidate_validation["summary"]
        lines += [
            "## Prospect-Lead Candidate Validation",
            "",
            "`docs/prospect_lead_candidate_validation.md` compares prospect-lead",
            "candidates against the full-manifest derived target gate.",
            "",
            f"- prospect candidates: `{summary['n_prospect_candidates']}`",
            f"- validated candidates: `{summary['n_validated_candidates']}`",
            f"- single-recording candidates: `{summary['n_single_recording_candidates']}`",
            f"- subset-only candidates: `{summary['n_subset_only_candidates']}`",
            f"- decision: `{summary['decision']}`",
            "",
            (
                "Decision: prospect-lead rows remain design leads only. They do not "
                "justify GPU training until they validate outside the selected subset."
            ),
            "",
        ]
    if prospect_lead_feature_mode_validation is not None:
        summary = prospect_lead_feature_mode_validation["summary"]
        lines += [
            "## Prospect-Lead Feature-Mode Validation",
            "",
            "`docs/prospect_lead_feature_mode_validation.md` validates prospect-lead",
            "derived target candidates across recording-centered, counts, fractions,",
            "and unit-residual feature modes against the corresponding full-manifest gates.",
            "",
            f"- feature modes: `{summary['n_feature_modes']}`",
            f"- prospect candidates: `{summary['n_prospect_candidates']}`",
            f"- full-manifest candidates: `{summary['n_full_candidates']}`",
            f"- validated candidates: `{summary['n_validated_candidates']}`",
            f"- single-recording candidates: `{summary['n_single_recording_candidates']}`",
            f"- subset-only candidates: `{summary['n_subset_only_candidates']}`",
            f"- decision: `{summary['decision']}`",
            "",
            (
                "Decision: feature-mode variation does not validate the prospect-lead "
                "derived candidates. Keep the next step local and do not launch GPU "
                "training from these selected-subset rows."
            ),
            "",
        ]
    if prospect_lead_subject_stability is not None:
        summary = prospect_lead_subject_stability["summary"]
        lines += [
            "## Prospect-Lead Subject Stability Audit",
            "",
            "`docs/prospect_lead_subject_stability.md` checks whether the prospect-lead",
            "derived candidates also hold on same-subject non-lead recordings.",
            "",
            f"- prospect candidates: `{summary['n_prospect_candidates']}`",
            f"- same-subject stable candidates: `{summary['n_same_subject_stable_candidates']}`",
            f"- candidates with non-lead failure: `{summary['n_candidates_with_nonlead_failure']}`",
            f"- decision: `{summary['decision']}`",
            "",
            (
                "Decision: the prospect-lead rows are selected-recording effects, not "
                "subject-stable transfer signals. A future target/control rule must be "
                "stable across multiple recordings within the held-out subject before "
                "any GPU run."
            ),
            "",
        ]
    if subject_stable_local_gate_prospectus is not None:
        summary = subject_stable_local_gate_prospectus["summary"]
        top = subject_stable_local_gate_prospectus["subject_stable_rows"][:5]
        lines += [
            "## Subject-Stable Local Gate Prospectus",
            "",
            "`docs/subject_stable_local_gate_prospectus.md` searches all current",
            "local-gate rows for target/control definitions that are stable across",
            "multiple recordings in the held-out subject.",
            "",
            f"- rows: `{summary['n_rows']}`",
            f"- subject-stable rows: `{summary['n_subject_stable_rows']}`",
            f"- subject-stable candidates: `{summary['n_subject_stable_candidates']}`",
            f"- subject-stable one-failure rows: `{summary['n_subject_stable_one_failure_rows']}`",
            f"- subject-stable holdouts: `{', '.join(summary['subject_stable_holdouts']) or 'none'}`",
            f"- decision: `{summary['decision']}`",
            "",
            "| source | target | feature | holdout | failures | delta shuffle | delta total | targets | bidir recs |",
            "|---|---|---|---|---|---:|---:|---:|---:|",
        ]
        for row in top:
            lines.append(
                f"| {row['source']} | {row['target_mode']} | {row['feature']} | "
                f"{row['holdout']} | {', '.join(row['failures']) or 'none'} | "
                f"{row['centered_delta_vs_shuffle']:+.3f} | {row['centered_delta_vs_total']:+.3f} | "
                f"{row['target0_improved_vs_shuffle']:.3f}/{row['target1_improved_vs_shuffle']:.3f} | "
                f"{row['n_bidirectional_recordings']}/{row['n_recordings']} |"
            )
        lines += [
            "",
            (
                "Decision: the best stable local branch is now a shuffle-control "
                "problem, not just a recording-support problem. The next redesign "
                "should target anatomical information that beats within-recording "
                "shuffled anatomy while preserving KS014-like subject stability."
            ),
            "",
        ]
    if subject_stable_shuffle_seed_sensitivity is not None:
        summary = subject_stable_shuffle_seed_sensitivity["summary"]
        top = subject_stable_shuffle_seed_sensitivity["rows"][:5]
        lines += [
            "## Subject-Stable Shuffle Seed Sensitivity",
            "",
            "`docs/subject_stable_shuffle_seed_sensitivity.md` reruns the subject-stable",
            "near misses across multiple within-recording shuffle seeds.",
            "",
            f"- cases: `{summary['n_cases']}`",
            f"- robust shuffle-seed candidates: `{summary['n_robust_shuffle_seed_candidates']}`",
            f"- max positive shuffle-delta fraction: `{summary['max_positive_shuffle_delta_fraction']:.3f}`",
            f"- decision: `{summary['decision']}`",
            "",
            "| source | target | feature | holdout | positive seeds | candidate seeds | mean shuffle delta | mean total delta |",
            "|---|---|---|---|---:|---:|---:|---:|",
        ]
        for row in top:
            lines.append(
                f"| {row['source']} | {row['target_mode']} | {row['family']} | {row['holdout']} | "
                f"{row['n_positive_shuffle_delta_seeds']}/{row['n_seeds']} | "
                f"{row['n_candidate_seeds']}/{row['n_seeds']} | "
                f"{row['mean_centered_delta_vs_shuffle']:+.4f} | "
                f"{row['mean_centered_delta_vs_total']:+.4f} |"
            )
        lines += [
            "",
            (
                "Decision: the KS014 stable near misses are not robust to the "
                "within-recording shuffle seed. A future local trigger should require "
                "positive true-vs-shuffle evidence across multiple shuffle seeds before "
                "any GPU run."
            ),
            "",
        ]
    if subject_stable_broad_anatomy_mechanism is not None:
        summary = subject_stable_broad_anatomy_mechanism["summary"]
        top = subject_stable_broad_anatomy_mechanism["rows"][:5]
        lines += [
            "## Subject-Stable Broad-Anatomy Mechanism",
            "",
            "`docs/subject_stable_broad_anatomy_mechanism.md` decomposes the",
            "subject-stable broad-anatomy near misses by predefined family",
            "contribution, then checks each contribution candidate with the exact",
            "single-family promotion gate.",
            "",
            f"- subject-stable rows: `{summary['n_subject_stable_rows']}`",
            f"- contribution candidates: `{summary['n_bidirectional_family_candidates']}`",
            f"- exact family-gate candidates: `{summary['n_family_gate_candidates']}`",
            f"- decision: `{summary['decision']}`",
            "",
            "| source | target | holdout | contribution candidates | exact gate candidates |",
            "|---|---|---|---|---|",
        ]
        for row in top:
            contribution_candidates = ", ".join(row["bidirectional_family_candidates"]) or "none"
            gate_candidates = ", ".join(item["family"] for item in row["family_gate_candidates"]) or "none"
            lines.append(
                f"| {row['source']} | {row['target_mode']} | {row['holdout']} | "
                f"{contribution_candidates} | {gate_candidates} |"
            )
        lines += [
            "",
            (
                "Decision: the apparent broad-anatomy family mechanism is contribution-only. "
                "The exact single-family gates still fail shuffle and/or total baselines, "
                "so this branch does not justify GPU training."
            ),
            "",
        ]
    if model_free_recording_directionality_audit is not None:
        summary = model_free_recording_directionality_audit["summary"]
        overall = summary["overall"]
        counts = overall["class_counts"]
        lines += [
            "## Model-Free Recording Directionality Audit",
            "",
            "`docs/model_free_recording_directionality_audit.md` classifies every",
            "per-recording target-support observation as bidirectional, target0-only,",
            "target1-only, or neither across current model-free artifacts.",
            "",
            f"- observations: `{overall['n_observations']}`",
            f"- bidirectional: `{counts['bidirectional']}`",
            f"- target0-only: `{counts['target0_only']}`",
            f"- target1-only: `{counts['target1_only']}`",
            f"- neither: `{counts['neither']}`",
            f"- one-sided fraction: `{overall['one_sided_fraction']:.3f}`",
            f"- decision: `{summary['decision']}`",
            "",
            (
                "Decision: one-sided recording effects are common enough that future "
                "candidate screens must report target-direction classes before any "
                "global delta can be considered a training trigger."
            ),
            "",
        ]
    if symmetric_recording_support_audit is not None:
        summary = symmetric_recording_support_audit["summary"]
        top = summary["top_rows"][:4]
        lines += [
            "## Symmetric Recording Support Audit",
            "",
            "`docs/symmetric_recording_support_audit.md` ranks candidate rows by",
            "recording-local `min(target0_improved, target1_improved)` so one-sided",
            "effects cannot dominate the promotion order.",
            "",
            f"- rows: `{summary['n_rows']}`",
            f"- candidates: `{summary['n_candidates']}`",
            f"- max bidirectional recordings: `{summary['max_bidirectional_recordings']}`",
            f"- max bidirectional recording fraction: `{summary['max_bidirectional_fraction']:.3f}`",
            f"- max mean symmetric support: `{summary['max_mean_symmetric_support']:.3f}`",
            f"- decision: `{summary['decision']}`",
            "",
            "| report | context | bidir recs | mean sym | min sym | one-sided |",
            "|---|---|---:|---:|---:|---:|",
        ]
        for row in top:
            lines.append(
                f"| {row['report']} | {row['context']} | "
                f"{row['n_bidirectional_recordings']}/{row['n_recordings']} | "
                f"{row['mean_symmetric_support']:.3f} | "
                f"{row['min_symmetric_support']:.3f} | "
                f"{row['n_target0_only'] + row['n_target1_only']} |"
            )
        lines += [
            "",
            (
                "Decision: use this symmetric ranking before any future GPU trigger. "
                "It currently finds no candidate; even the best rows top out at `2/4` "
                "bidirectional recordings."
            ),
            "",
        ]
    if symmetric_threshold_sensitivity_audit is not None:
        summary = symmetric_threshold_sensitivity_audit["summary"]
        default_setting = summary.get("strongest_default_target_candidate_setting")
        lines += [
            "## Symmetric Threshold Sensitivity Audit",
            "",
            "`docs/symmetric_threshold_sensitivity_audit.md` sweeps the target-improvement",
            "and bidirectional-recording thresholds for the symmetric recording-support",
            "gate.",
            "",
            f"- threshold settings: `{summary['n_threshold_settings']}`",
            f"- settings with candidates: `{summary['n_settings_with_candidates']}`",
            f"- strict candidates at target>=0.55 and bidir>=0.75: `{summary['strict_candidates']}`",
            f"- strict max bidirectional recordings: `{summary['strict_max_bidirectional_recordings']}`",
            f"- decision: `{summary['decision']}`",
        ]
        if default_setting is not None:
            lines.append("")
            lines.append(
                "At the default target threshold (`0.55`), candidates only appear when "
                f"recording support is relaxed to `{default_setting['min_bidirectional_recording_fraction']:.2f}` "
                f"(`{default_setting['n_candidates']}` candidates)."
            )
        lines += [
            "",
            (
                "Decision: the current failure is not a tiny threshold miss. A candidate "
                "at the default target floor requires accepting only `1/4` bidirectional "
                "recordings, which is too weak for a cross-animal demo trigger."
            ),
            "",
        ]
    if symmetric_strict_failure_modes is not None:
        summary = symmetric_strict_failure_modes["summary"]
        blockers = ", ".join(
            f"{name}={count}" for name, count in sorted(summary["blocker_counts"].items())
        )
        top = summary["closest_rows"][:5]
        lines += [
            "## Symmetric Strict Failure Mode Audit",
            "",
            "`docs/symmetric_strict_failure_modes.md` ranks the nearest rows",
            "against the strict symmetric promotion gate and reports the exact",
            "missing requirements.",
            "",
            f"- rows: `{summary['n_rows']}`",
            f"- strict candidates: `{summary['strict_candidates']}`",
            f"- global-target-clear rows: `{summary['global_target_clear_rows']}`",
            f"- one-recording-short and global-clear rows: `{summary['one_recording_short_and_global_clear_rows']}`",
            f"- blocker counts: `{blockers}`",
            f"- decision: `{summary['decision']}`",
            "",
            "| report | context | blockers | targets | bidir recs | missing | mean sym |",
            "|---|---|---|---|---:|---:|---:|",
        ]
        for row in top:
            target0 = "n/a" if row["global_target0"] is None else f"{row['global_target0']:.3f}"
            target1 = "n/a" if row["global_target1"] is None else f"{row['global_target1']:.3f}"
            lines.append(
                f"| {row['report']} | {row['context']} | {', '.join(row['blockers']) or 'none'} | "
                f"{target0}/{target1} | "
                f"{row['n_bidirectional_recordings']}/{row['required_bidirectional_recordings']} | "
                f"{row['missing_bidirectional_recordings']} | {row['mean_symmetric_support']:.3f} |"
            )
        lines += [
            "",
            (
                "Decision: there is no clean one-recording-short row that already clears "
                "both global target floors. The nearest actionable branch is a local "
                "redesign around shared broad-anatomy rows, where target0 is marginally "
                "below threshold and recording support is one hit short."
            ),
            "",
        ]
    if model_free_recording_replication_audit is not None:
        summary = model_free_recording_replication_audit["summary"]
        top = model_free_recording_replication_audit["rows"][:4]
        lines += [
            "## Model-Free Recording Replication Audit",
            "",
            "`docs/model_free_recording_replication_audit.md` tests whether a",
            "recording subset selected from fixed discovery reports keeps bidirectional",
            "support in held-out validation report families.",
            "",
            f"- recording-subject rows: `{summary['n_recording_subject_rows']}`",
            f"- selected by discovery rule: `{summary['n_selected_by_discovery_rule']}`",
            f"- replicated in validation: `{summary['n_replicated_in_validation']}`",
            f"- decision: `{summary['decision']}`",
            "",
            "| subject | recording | selected | replicated | discovery bidir | validation bidir | validation target0 | validation target1 |",
            "|---|---|---|---|---:|---:|---:|---:|",
        ]
        for row in top:
            lines.append(
                f"| {row['target_subject']} | {row['recording']} | "
                f"{row['selected']} | {row['replicated']} | "
                f"{row['discovery_bidirectional_observations']}/{row['discovery_observations']} | "
                f"{row['validation_bidirectional_observations']}/{row['validation_observations']} | "
                f"{row['validation_mean_target0']:.3f} | {row['validation_mean_target1']:.3f} |"
            )
        lines += [
            "",
            (
                "Decision: recording-subset selection is not currently a credible demo "
                "path. The selected discovery recordings lose bidirectional target "
                "support in validation, so the next local work should redesign the "
                "target/control or matched manifest rather than narrow this cache."
            ),
            "",
        ]
    if model_free_family_bidirectional_recording_centered is not None:
        summary = model_free_family_bidirectional_recording_centered["summary"]
        lines += [
            "## Family-Aggregate Recording-Centered Gate",
            "",
            "`docs/model_free_family_bidirectional_gate_recording_centered.md` combines",
            "predefined parent-region family aggregates with feature-level recording",
            "centering and the same same-recording bidirectional gate.",
            "",
            f"- candidates: `{summary['n_candidates']}/{summary['n_holdouts']}`",
            f"- positive centered-delta holdouts: `{summary['n_positive_delta_holdouts']}/{summary['n_holdouts']}`",
            f"- mean bidirectional recording fraction: `{summary['mean_bidirectional_recording_fraction']:.3f}`",
            f"- decision: `{summary['decision']}`",
            "",
            (
                "Decision: this is the strongest local near miss so far, but still not a "
                "training trigger. `KS014` reaches centered delta `+0.080` and `2/4` "
                "bidirectional recordings, yet misses global target0 at `0.510`."
            ),
            "",
        ]
    family_l2_rows = [
        ("1", model_free_family_bidirectional_recording_centered_l2_1),
        ("10", model_free_family_bidirectional_recording_centered),
        ("100", model_free_family_bidirectional_recording_centered_l2_100),
    ]
    family_l2_rows = [(label, row) for label, row in family_l2_rows if row is not None]
    if len(family_l2_rows) >= 2:
        lines += [
            "## Family-Aggregate L2 Sensitivity",
            "",
            "The strongest family-aggregate near-miss gate was rerun across ridge",
            "regularization strengths to check whether the local decision is an",
            "artifact of the default `l2=10` setting.",
            "",
            "| l2 | candidates | positive deltas | mean bidir rec frac | decision |",
            "|---:|---:|---:|---:|---|",
        ]
        for label, row in family_l2_rows:
            summary = row["summary"]
            lines.append(
                f"| {label} | {summary['n_candidates']}/{summary['n_holdouts']} | "
                f"{summary['n_positive_delta_holdouts']}/{summary['n_holdouts']} | "
                f"{summary['mean_bidirectional_recording_fraction']:.3f} | "
                f"`{summary['decision']}` |"
            )
        lines += [
            "",
            (
                "Decision: the family near miss is not a ridge-regularization artifact. "
                "The candidate count, positive-delta count, and mean bidirectional "
                "recording fraction are unchanged across the tested l2 range."
            ),
            "",
        ]
    if model_free_family_ks014_near_miss is not None:
        top_rows = model_free_family_ks014_near_miss.get("family_rows", [])[:5]
        lines += [
            "## KS014 Family Near-Miss Mechanism",
            "",
            "`docs/model_free_family_ks014_near_miss_mechanism.md` decomposes the",
            "strongest family-aggregate near miss by family contribution.",
            "",
            f"- bidirectional family candidates: `{len(model_free_family_ks014_near_miss.get('bidirectional_family_candidates', []))}`",
            f"- decision: `{model_free_family_ks014_near_miss.get('decision')}`",
            "",
            "| family | class | mean delta | target0 | target1 | recordings |",
            "|---|---|---:|---:|---:|---:|",
        ]
        for row in top_rows:
            lines.append(
                f"| {row['family']} | {row['classification']} | "
                f"{row['mean_true_class_delta']:+.3f} | "
                f"{row['target0_improved']:.3f} | {row['target1_improved']:.3f} | "
                f"{row['positive_recordings']}/{row['n_recordings']} |"
            )
        lines += [
            "",
            (
                "Decision: the KS014 family-level near miss is a mixture of one-sided "
                "family movements, not a hidden bidirectional anatomical mechanism."
            ),
            "",
        ]
    alternative_family_target_gates = [
        row for row in [
            model_free_family_bidirectional_prior_recording_centered,
            model_free_family_bidirectional_feedback_recording_centered,
        ] if row is not None
    ]
    if alternative_family_target_gates:
        lines += [
            "## Family-Aggregate Alternative Target Gates",
            "",
            "`prior_side` and `feedback` were also tested with recording-centered",
            "family-aggregate features, using the same same-recording bidirectional gate.",
            "",
            "| target | candidates | positive deltas | mean bidir rec frac | notable positive holdouts | decision |",
            "|---|---:|---:|---:|---|---|",
        ]
        for gate in alternative_family_target_gates:
            summary = gate["summary"]
            positives = ", ".join(summary["positive_delta_holdouts"]) or "none"
            lines.append(
                f"| {gate['target_mode']} | {summary['n_candidates']}/{summary['n_holdouts']} | "
                f"{summary['n_positive_delta_holdouts']}/{summary['n_holdouts']} | "
                f"{summary['mean_bidirectional_recording_fraction']:.3f} | "
                f"{positives} | `{summary['decision']}` |"
            )
        lines += [
            "",
            (
                "Decision: family aggregation increases some positive centered deltas on "
                "alternative targets, especially `prior_side`, but still produces zero "
                "candidate holdouts. The failure remains the same: global or "
                "same-recording bidirectional target evidence does not hold."
            ),
            "",
        ]
    alternative_target_gates = [
        row for row in [
            model_free_recording_bidirectional_prior,
            model_free_recording_bidirectional_feedback,
        ] if row is not None
    ]
    if alternative_target_gates:
        lines += [
            "## Alternative Target Bidirectional Gates",
            "",
            "Two additional trial targets exposed by the cached IBL trials were tested",
            "through the same recording-bidirectional model-free gate.",
            "",
            "| target | candidates | positive deltas | mean bidir rec frac | notable positive holdouts | decision |",
            "|---|---:|---:|---:|---|---|",
        ]
        for gate in alternative_target_gates:
            summary = gate["summary"]
            positives = ", ".join(summary["positive_delta_holdouts"]) or "none"
            lines.append(
                f"| {gate['target_mode']} | {summary['n_candidates']}/{summary['n_holdouts']} | "
                f"{summary['n_positive_delta_holdouts']}/{summary['n_holdouts']} | "
                f"{summary['mean_bidirectional_recording_fraction']:.3f} | "
                f"{positives} | `{summary['decision']}` |"
            )
        lines += [
            "",
            (
                "Decision: `prior_side` and `feedback` do not rescue the matched-panel "
                "branch. Both produce zero candidate holdouts and zero mean same-recording "
                "bidirectional support. More positive global centered deltas are still "
                "class-direction artifacts under the stricter gate."
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
    manifest_target_anatomy_feasibility = read_mechanism_audit(
        REPO_ROOT / MANIFEST_TARGET_ANATOMY_FEASIBILITY_FILE
    )
    shared_family_target_control_gate = read_mechanism_audit(REPO_ROOT / SHARED_FAMILY_TARGET_CONTROL_GATE_FILE)
    shared_family_choice_fiber_csh_near_miss = read_mechanism_audit(
        REPO_ROOT / SHARED_FAMILY_CHOICE_FIBER_CSH_NEAR_MISS_FILE
    )
    shared_broad_anatomy_repair_sweep = read_mechanism_audit(REPO_ROOT / SHARED_BROAD_ANATOMY_REPAIR_SWEEP_FILE)
    shared_family_iterative_manifest_gate = read_mechanism_audit(REPO_ROOT / SHARED_FAMILY_ITERATIVE_MANIFEST_GATE_FILE)
    next_benchmark_control_options = read_mechanism_audit(REPO_ROOT / NEXT_BENCHMARK_CONTROL_OPTIONS_FILE)
    derived_target_family_gate = read_mechanism_audit(REPO_ROOT / DERIVED_TARGET_FAMILY_GATE_FILE)
    contextual_target_family_gate = read_mechanism_audit(REPO_ROOT / CONTEXTUAL_TARGET_FAMILY_GATE_FILE)
    wheel_target_family_gate = read_mechanism_audit(REPO_ROOT / WHEEL_TARGET_FAMILY_GATE_FILE)
    extreme_quantile_target_family_gate = read_mechanism_audit(REPO_ROOT / EXTREME_QUANTILE_TARGET_FAMILY_GATE_FILE)
    extreme_quantile_seed_sensitivity = read_mechanism_audit(REPO_ROOT / EXTREME_QUANTILE_SEED_SENSITIVITY_FILE)
    local_cached_manifest_candidates = read_mechanism_audit(REPO_ROOT / LOCAL_CACHED_MANIFEST_CANDIDATES_FILE)
    external_manifest_acquisition_gap = read_mechanism_audit(REPO_ROOT / EXTERNAL_MANIFEST_ACQUISITION_GAP_FILE)
    behavior_cache_preflight = read_mechanism_audit(REPO_ROOT / BEHAVIOR_CACHE_PREFLIGHT_FILE)
    model_free_matched_panel = read_mechanism_audit(REPO_ROOT / MODEL_FREE_MATCHED_SUPPORT80_PANEL_FILE)
    model_free_positive_holdouts = read_mechanism_audit(REPO_ROOT / MODEL_FREE_POSITIVE_HOLDOUTS_MECHANISM_FILE)
    model_free_recording_bidirectional_gate = read_mechanism_audit(
        REPO_ROOT / MODEL_FREE_RECORDING_BIDIRECTIONAL_GATE_FILE
    )
    model_free_recording_bidirectional_fractions = read_mechanism_audit(
        REPO_ROOT / MODEL_FREE_RECORDING_BIDIRECTIONAL_FRACTIONS_FILE
    )
    model_free_recording_bidirectional_recording_centered = read_mechanism_audit(
        REPO_ROOT / MODEL_FREE_RECORDING_BIDIRECTIONAL_RECORDING_CENTERED_FILE
    )
    model_free_recording_bidirectional_grandparent_recording_centered = read_mechanism_audit(
        REPO_ROOT / MODEL_FREE_RECORDING_BIDIRECTIONAL_GRANDPARENT_RECORDING_CENTERED_FILE
    )
    model_free_recording_bidirectional_unit_residuals = read_mechanism_audit(
        REPO_ROOT / MODEL_FREE_RECORDING_BIDIRECTIONAL_UNIT_RESIDUALS_FILE
    )
    model_free_recording_bidirectional_prior = read_mechanism_audit(
        REPO_ROOT / MODEL_FREE_RECORDING_BIDIRECTIONAL_PRIOR_FILE
    )
    model_free_recording_bidirectional_feedback = read_mechanism_audit(
        REPO_ROOT / MODEL_FREE_RECORDING_BIDIRECTIONAL_FEEDBACK_FILE
    )
    model_free_source_target_pair_recording_centered = read_mechanism_audit(
        REPO_ROOT / MODEL_FREE_SOURCE_TARGET_PAIR_RECORDING_CENTERED_FILE
    )
    model_free_source_target_pair_families_recording_centered = read_mechanism_audit(
        REPO_ROOT / MODEL_FREE_SOURCE_TARGET_PAIR_FAMILIES_RECORDING_CENTERED_FILE
    )
    model_free_gate_blocker_audit = read_mechanism_audit(REPO_ROOT / MODEL_FREE_GATE_BLOCKER_AUDIT_FILE)
    model_free_recording_support_audit = read_mechanism_audit(REPO_ROOT / MODEL_FREE_RECORDING_SUPPORT_AUDIT_FILE)
    recording_bidirectionality_prospectus = read_mechanism_audit(
        REPO_ROOT / RECORDING_BIDIRECTIONALITY_PROSPECTUS_FILE
    )
    derived_target_family_prospect_leads = read_mechanism_audit(
        REPO_ROOT / DERIVED_TARGET_FAMILY_PROSPECT_LEADS_FILE
    )
    prospect_lead_candidate_validation = read_mechanism_audit(
        REPO_ROOT / PROSPECT_LEAD_CANDIDATE_VALIDATION_FILE
    )
    prospect_lead_feature_mode_validation = read_mechanism_audit(
        REPO_ROOT / PROSPECT_LEAD_FEATURE_MODE_VALIDATION_FILE
    )
    prospect_lead_subject_stability = read_mechanism_audit(
        REPO_ROOT / PROSPECT_LEAD_SUBJECT_STABILITY_FILE
    )
    subject_stable_local_gate_prospectus = read_mechanism_audit(
        REPO_ROOT / SUBJECT_STABLE_LOCAL_GATE_PROSPECTUS_FILE
    )
    subject_stable_shuffle_seed_sensitivity = read_mechanism_audit(
        REPO_ROOT / SUBJECT_STABLE_SHUFFLE_SEED_SENSITIVITY_FILE
    )
    subject_stable_broad_anatomy_mechanism = read_mechanism_audit(
        REPO_ROOT / SUBJECT_STABLE_BROAD_ANATOMY_MECHANISM_FILE
    )
    model_free_recording_directionality_audit = read_mechanism_audit(
        REPO_ROOT / MODEL_FREE_RECORDING_DIRECTIONALITY_AUDIT_FILE
    )
    symmetric_recording_support_audit = read_mechanism_audit(REPO_ROOT / SYMMETRIC_RECORDING_SUPPORT_AUDIT_FILE)
    symmetric_threshold_sensitivity_audit = read_mechanism_audit(
        REPO_ROOT / SYMMETRIC_THRESHOLD_SENSITIVITY_AUDIT_FILE
    )
    symmetric_strict_failure_modes = read_mechanism_audit(REPO_ROOT / SYMMETRIC_STRICT_FAILURE_MODES_FILE)
    model_free_recording_replication_audit = read_mechanism_audit(
        REPO_ROOT / MODEL_FREE_RECORDING_REPLICATION_AUDIT_FILE
    )
    model_free_family_bidirectional_recording_centered = read_mechanism_audit(
        REPO_ROOT / MODEL_FREE_FAMILY_BIDIRECTIONAL_RECORDING_CENTERED_FILE
    )
    model_free_family_bidirectional_recording_centered_l2_1 = read_mechanism_audit(
        REPO_ROOT / MODEL_FREE_FAMILY_BIDIRECTIONAL_RECORDING_CENTERED_L2_1_FILE
    )
    model_free_family_bidirectional_recording_centered_l2_100 = read_mechanism_audit(
        REPO_ROOT / MODEL_FREE_FAMILY_BIDIRECTIONAL_RECORDING_CENTERED_L2_100_FILE
    )
    model_free_family_bidirectional_prior_recording_centered = read_mechanism_audit(
        REPO_ROOT / MODEL_FREE_FAMILY_BIDIRECTIONAL_PRIOR_RECORDING_CENTERED_FILE
    )
    model_free_family_bidirectional_feedback_recording_centered = read_mechanism_audit(
        REPO_ROOT / MODEL_FREE_FAMILY_BIDIRECTIONAL_FEEDBACK_RECORDING_CENTERED_FILE
    )
    model_free_family_ks014_near_miss = read_mechanism_audit(
        REPO_ROOT / MODEL_FREE_FAMILY_KS014_NEAR_MISS_FILE
    )
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
        manifest_target_anatomy_feasibility,
        shared_family_target_control_gate,
        shared_family_choice_fiber_csh_near_miss,
        shared_broad_anatomy_repair_sweep,
        shared_family_iterative_manifest_gate,
        next_benchmark_control_options,
        derived_target_family_gate,
        contextual_target_family_gate,
        wheel_target_family_gate,
        extreme_quantile_target_family_gate,
        extreme_quantile_seed_sensitivity,
        local_cached_manifest_candidates,
        external_manifest_acquisition_gap,
        behavior_cache_preflight,
        model_free_matched_panel,
        model_free_positive_holdouts,
        model_free_recording_bidirectional_gate,
        model_free_recording_bidirectional_fractions,
        model_free_recording_bidirectional_recording_centered,
        model_free_recording_bidirectional_grandparent_recording_centered,
        model_free_recording_bidirectional_unit_residuals,
        model_free_recording_bidirectional_prior,
        model_free_recording_bidirectional_feedback,
        model_free_source_target_pair_recording_centered,
        model_free_source_target_pair_families_recording_centered,
        model_free_gate_blocker_audit,
        model_free_recording_support_audit,
        recording_bidirectionality_prospectus,
        derived_target_family_prospect_leads,
        prospect_lead_candidate_validation,
        prospect_lead_feature_mode_validation,
        prospect_lead_subject_stability,
        subject_stable_local_gate_prospectus,
        subject_stable_shuffle_seed_sensitivity,
        subject_stable_broad_anatomy_mechanism,
        model_free_recording_directionality_audit,
        symmetric_recording_support_audit,
        symmetric_threshold_sensitivity_audit,
        symmetric_strict_failure_modes,
        model_free_recording_replication_audit,
        model_free_family_bidirectional_recording_centered,
        model_free_family_bidirectional_recording_centered_l2_1,
        model_free_family_bidirectional_recording_centered_l2_100,
        model_free_family_bidirectional_prior_recording_centered,
        model_free_family_bidirectional_feedback_recording_centered,
        model_free_family_ks014_near_miss,
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
        "manifest_target_anatomy_feasibility": manifest_target_anatomy_feasibility,
        "shared_family_target_control_gate": shared_family_target_control_gate,
        "shared_family_choice_fiber_csh_near_miss": shared_family_choice_fiber_csh_near_miss,
        "shared_broad_anatomy_repair_sweep": shared_broad_anatomy_repair_sweep,
        "shared_family_iterative_manifest_gate": shared_family_iterative_manifest_gate,
        "next_benchmark_control_options": next_benchmark_control_options,
        "derived_target_family_gate": derived_target_family_gate,
        "contextual_target_family_gate": contextual_target_family_gate,
        "wheel_target_family_gate": wheel_target_family_gate,
        "extreme_quantile_target_family_gate": extreme_quantile_target_family_gate,
        "extreme_quantile_seed_sensitivity": extreme_quantile_seed_sensitivity,
        "local_cached_manifest_candidates": local_cached_manifest_candidates,
        "external_manifest_acquisition_gap": external_manifest_acquisition_gap,
        "behavior_cache_preflight": behavior_cache_preflight,
        "model_free_matched_support80_panel": model_free_matched_panel,
        "model_free_positive_holdouts_mechanism": model_free_positive_holdouts,
        "model_free_recording_bidirectional_gate": model_free_recording_bidirectional_gate,
        "model_free_recording_bidirectional_fractions": model_free_recording_bidirectional_fractions,
        "model_free_recording_bidirectional_recording_centered": (
            model_free_recording_bidirectional_recording_centered
        ),
        "model_free_recording_bidirectional_grandparent_recording_centered": (
            model_free_recording_bidirectional_grandparent_recording_centered
        ),
        "model_free_recording_bidirectional_unit_residuals": model_free_recording_bidirectional_unit_residuals,
        "model_free_recording_bidirectional_prior_side": model_free_recording_bidirectional_prior,
        "model_free_recording_bidirectional_feedback": model_free_recording_bidirectional_feedback,
        "model_free_source_target_pair_recording_centered": model_free_source_target_pair_recording_centered,
        "model_free_source_target_pair_families_recording_centered": (
            model_free_source_target_pair_families_recording_centered
        ),
        "model_free_gate_blocker_audit": model_free_gate_blocker_audit,
        "model_free_recording_support_audit": model_free_recording_support_audit,
        "recording_bidirectionality_prospectus": recording_bidirectionality_prospectus,
        "derived_target_family_prospect_leads": derived_target_family_prospect_leads,
        "prospect_lead_candidate_validation": prospect_lead_candidate_validation,
        "prospect_lead_feature_mode_validation": prospect_lead_feature_mode_validation,
        "prospect_lead_subject_stability": prospect_lead_subject_stability,
        "subject_stable_local_gate_prospectus": subject_stable_local_gate_prospectus,
        "subject_stable_shuffle_seed_sensitivity": subject_stable_shuffle_seed_sensitivity,
        "subject_stable_broad_anatomy_mechanism": subject_stable_broad_anatomy_mechanism,
        "model_free_recording_directionality_audit": model_free_recording_directionality_audit,
        "symmetric_recording_support_audit": symmetric_recording_support_audit,
        "symmetric_threshold_sensitivity_audit": symmetric_threshold_sensitivity_audit,
        "symmetric_strict_failure_modes": symmetric_strict_failure_modes,
        "model_free_recording_replication_audit": model_free_recording_replication_audit,
        "model_free_family_bidirectional_recording_centered": (
            model_free_family_bidirectional_recording_centered
        ),
        "model_free_family_bidirectional_recording_centered_l2_1": (
            model_free_family_bidirectional_recording_centered_l2_1
        ),
        "model_free_family_bidirectional_recording_centered_l2_100": (
            model_free_family_bidirectional_recording_centered_l2_100
        ),
        "model_free_family_bidirectional_prior_side_recording_centered": (
            model_free_family_bidirectional_prior_recording_centered
        ),
        "model_free_family_bidirectional_feedback_recording_centered": (
            model_free_family_bidirectional_feedback_recording_centered
        ),
        "model_free_family_ks014_near_miss": model_free_family_ks014_near_miss,
    }, indent=2, sort_keys=True) + "\n")
    print(f"wrote {args.out_md}")
    print(f"wrote {args.out_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
