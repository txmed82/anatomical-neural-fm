"""Rank remaining benchmark/control options after local negative audits."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


ARTIFACTS = {
    "shared_family": "docs/shared_family_target_control_gate.json",
    "shared_broad_repair": "docs/shared_broad_anatomy_repair_sweep.json",
    "iterative_manifest": "docs/shared_family_iterative_manifest_gate.json",
    "symmetric_strict": "docs/symmetric_strict_failure_modes.json",
    "symmetric_threshold": "docs/symmetric_threshold_sensitivity_audit.json",
    "recording_replication": "docs/model_free_recording_replication_audit.json",
    "derived_target_family": "docs/derived_target_family_gate.json",
    "contextual_target_family": "docs/contextual_target_family_gate.json",
    "wheel_target_family": "docs/wheel_target_family_gate.json",
    "extreme_quantile_target_family": "docs/extreme_quantile_target_family_gate.json",
    "extreme_quantile_seed_sensitivity": "docs/extreme_quantile_seed_sensitivity.json",
    "reaction_dynamics_target_family_recording_centered": "docs/reaction_dynamics_target_family_gate.json",
    "reaction_dynamics_target_family_counts": "docs/reaction_dynamics_target_family_gate_counts.json",
    "reaction_dynamics_target_family_fractions": "docs/reaction_dynamics_target_family_gate_fractions.json",
    "reaction_dynamics_target_family_unit_residuals": "docs/reaction_dynamics_target_family_gate_unit_residuals.json",
    "cell_type_prior_target_control": "docs/cell_type_prior_target_control_gate.json",
    "waveform_target_control": "docs/waveform_target_control_gate.json",
    "local_gate_meta_failures": "docs/local_gate_meta_failure_audit.json",
    "recording_bidirectionality_prospectus": "docs/recording_bidirectionality_prospectus.json",
    "recording_bidirectionality_prospect_manifest": (
        "manifests/ibl_bwm_recording_bidirectionality_prospect_leads.json"
    ),
    "derived_target_family_prospect_leads": "docs/derived_target_family_gate_prospect_leads.json",
    "prospect_lead_candidate_validation": "docs/prospect_lead_candidate_validation.json",
    "prospect_lead_feature_mode_validation": "docs/prospect_lead_feature_mode_validation.json",
    "prospect_lead_subject_stability": "docs/prospect_lead_subject_stability.json",
    "subject_stable_local_gate_prospectus": "docs/subject_stable_local_gate_prospectus.json",
    "subject_stable_shuffle_seed_sensitivity": "docs/subject_stable_shuffle_seed_sensitivity.json",
    "subject_stable_broad_anatomy_mechanism": "docs/subject_stable_broad_anatomy_mechanism.json",
    "local_cached_manifest_candidates": "docs/local_cached_manifest_candidates.json",
    "projected_support80_shared_family": "docs/shared_family_target_control_gate_projected_support80.json",
    "projected_support80_all_families_recording_centered": (
        "docs/shared_family_target_control_gate_projected_support80_all_families.json"
    ),
    "projected_support80_all_families_fractions": (
        "docs/shared_family_target_control_gate_projected_support80_all_families_fractions.json"
    ),
    "projected_support80_all_families_counts": (
        "docs/shared_family_target_control_gate_projected_support80_all_families_counts.json"
    ),
    "projected_support80_all_families_unit_residuals": (
        "docs/shared_family_target_control_gate_projected_support80_all_families_unit_residuals.json"
    ),
    "external_manifest_acquisition_gap": "docs/external_manifest_acquisition_gap.json",
    "behavior_cache_preflight": "docs/behavior_cache_preflight.json",
    "family_alt_prior": "docs/model_free_family_bidirectional_gate_prior_side_recording_centered.json",
    "family_alt_feedback": "docs/model_free_family_bidirectional_gate_feedback_recording_centered.json",
    "source_target_families": "docs/model_free_source_target_pair_gate_families_recording_centered.json",
}


def read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text())


def summary_value(payload: dict | None, key: str, default=None):
    if payload is None:
        return default
    return payload.get("summary", {}).get(key, default)


def feature_mode_summary(artifacts: dict[str, dict | None], keys: list[str]) -> dict:
    payloads = [(key, artifacts[key]) for key in keys if artifacts.get(key) is not None]
    return {
        "n_modes": len(payloads),
        "n_rows": sum(int(summary_value(payload, "n_rows", 0) or 0) for _key, payload in payloads),
        "n_candidates": sum(int(summary_value(payload, "n_candidates", 0) or 0) for _key, payload in payloads),
        "max_bidirectional_recording_fraction": max(
            (float(summary_value(payload, "max_bidirectional_recording_fraction", 0.0) or 0.0) for _key, payload in payloads),
            default=0.0,
        ),
    }


def projected_feature_mode_summary(artifacts: dict[str, dict | None]) -> dict:
    return feature_mode_summary(
        artifacts,
        [
            "projected_support80_all_families_recording_centered",
            "projected_support80_all_families_fractions",
            "projected_support80_all_families_counts",
            "projected_support80_all_families_unit_residuals",
        ],
    )


def reaction_feature_mode_summary(artifacts: dict[str, dict | None]) -> dict:
    return feature_mode_summary(
        artifacts,
        [
            "reaction_dynamics_target_family_recording_centered",
            "reaction_dynamics_target_family_counts",
            "reaction_dynamics_target_family_fractions",
            "reaction_dynamics_target_family_unit_residuals",
        ],
    )


def branch(
    *,
    name: str,
    status: str,
    priority: int,
    evidence: list[str],
    next_action: str,
    gpu_trigger: str,
) -> dict:
    return {
        "name": name,
        "status": status,
        "priority": priority,
        "evidence": evidence,
        "next_action": next_action,
        "gpu_trigger": gpu_trigger,
    }


def build_report() -> dict:
    artifacts = {name: read_json(REPO_ROOT / rel_path) for name, rel_path in ARTIFACTS.items()}
    shared_family = artifacts["shared_family"]
    shared_broad = artifacts["shared_broad_repair"]
    iterative = artifacts["iterative_manifest"]
    strict = artifacts["symmetric_strict"]
    threshold = artifacts["symmetric_threshold"]
    replication = artifacts["recording_replication"]
    derived = artifacts["derived_target_family"]
    contextual = artifacts["contextual_target_family"]
    wheel = artifacts["wheel_target_family"]
    local_manifest_candidates = artifacts["local_cached_manifest_candidates"]
    external_acquisition = artifacts["external_manifest_acquisition_gap"]
    behavior_cache = artifacts["behavior_cache_preflight"]
    behavior_summary = behavior_cache.get("summary", {}) if behavior_cache is not None else {}
    stream_counts = behavior_summary.get("stream_counts", {})
    wheel_count = stream_counts.get("wheel", "n/a")
    n_behavior_recordings = behavior_summary.get("n_manifest_recordings", "n/a")
    behavior_ready = behavior_summary.get("decision") == "behavior_cache_ready"
    wheel_candidates = summary_value(wheel, "n_candidates", None)
    wheel_done = wheel is not None
    extreme_quantile = artifacts["extreme_quantile_target_family"]
    extreme_quantile_done = extreme_quantile is not None
    extreme_quantile_candidates = summary_value(extreme_quantile, "n_candidates", 0)
    extreme_seed = artifacts["extreme_quantile_seed_sensitivity"]
    extreme_seed_summary = extreme_seed.get("summary", {}) if extreme_seed is not None else {}
    extreme_seed_robust = int(extreme_seed_summary.get("n_robust_shuffle_seed_candidates", 0) or 0)
    reaction_feature_modes = reaction_feature_mode_summary(artifacts)
    cell_type_prior = artifacts["cell_type_prior_target_control"]
    cell_type_prior_done = cell_type_prior is not None
    waveform = artifacts["waveform_target_control"]
    waveform_done = waveform is not None
    meta_failures = artifacts["local_gate_meta_failures"]
    meta_summary = meta_failures.get("summary", {}) if meta_failures is not None else {}
    prospectus = artifacts["recording_bidirectionality_prospectus"]
    prospectus_summary = prospectus.get("summary", {}) if prospectus is not None else {}
    prospect_manifest = artifacts["recording_bidirectionality_prospect_manifest"]
    prospect_derived_gate = artifacts["derived_target_family_prospect_leads"]
    prospect_derived_summary = prospect_derived_gate.get("summary", {}) if prospect_derived_gate is not None else {}
    prospect_validation = artifacts["prospect_lead_candidate_validation"]
    prospect_validation_summary = prospect_validation.get("summary", {}) if prospect_validation is not None else {}
    prospect_feature_validation = artifacts["prospect_lead_feature_mode_validation"]
    prospect_feature_summary = (
        prospect_feature_validation.get("summary", {}) if prospect_feature_validation is not None else {}
    )
    prospect_subject_stability = artifacts["prospect_lead_subject_stability"]
    prospect_subject_summary = (
        prospect_subject_stability.get("summary", {}) if prospect_subject_stability is not None else {}
    )
    subject_stable_prospectus = artifacts["subject_stable_local_gate_prospectus"]
    subject_stable_summary = (
        subject_stable_prospectus.get("summary", {}) if subject_stable_prospectus is not None else {}
    )
    seed_sensitivity = artifacts["subject_stable_shuffle_seed_sensitivity"]
    seed_sensitivity_summary = seed_sensitivity.get("summary", {}) if seed_sensitivity is not None else {}
    subject_stable_mechanism = artifacts["subject_stable_broad_anatomy_mechanism"]
    subject_stable_mechanism_summary = (
        subject_stable_mechanism.get("summary", {}) if subject_stable_mechanism is not None else {}
    )
    local_manifest_summary = local_manifest_candidates.get("summary", {}) if local_manifest_candidates is not None else {}
    local_manifest_decision = local_manifest_summary.get("decision")
    local_projected_panel_ready = local_manifest_decision == "local_expanded_candidate_ready_for_model_free_gate"
    projected_support80_gate = artifacts["projected_support80_shared_family"]
    projected_support80_candidates = summary_value(projected_support80_gate, "n_candidates", None)
    projected_support80_done = projected_support80_gate is not None
    projected_feature_modes = projected_feature_mode_summary(artifacts)
    external_summary = external_acquisition.get("summary", {}) if external_acquisition is not None else {}
    default_candidate_setting = summary_value(threshold, "strongest_default_target_candidate_setting", {}) or {}
    default_candidate_bidir = default_candidate_setting.get("min_bidirectional_recording_fraction")
    default_candidate_count = default_candidate_setting.get("n_candidates")

    branches = [
        branch(
            name="behavior-inclusive cache rebuild",
            status="closed" if behavior_ready else "recommended_next",
            priority=91 if behavior_ready else 1,
            evidence=[
                "current cached trial targets and shared-family controls all fail strict same-recording bidirectionality",
                (
                    "direct derived cached-field target gate has "
                    f"{summary_value(derived, 'n_candidates', 'n/a')} candidates and max bidir "
                    f"{summary_value(derived, 'max_bidirectional_recording_fraction', 0.0):.3f}"
                ),
                (
                    "contextual trial-state target gate has "
                    f"{summary_value(contextual, 'n_candidates', 'n/a')} candidates and max bidir "
                    f"{summary_value(contextual, 'max_bidirectional_recording_fraction', 0.0):.3f}"
                ),
                (
                    f"behavior-cache preflight has wheel in {wheel_count}/{n_behavior_recordings} "
                    "matched recordings"
                ),
                (
                    "strict symmetric gate has "
                    f"{summary_value(strict, 'strict_candidates', 'n/a')} candidates and "
                    f"{summary_value(strict, 'one_recording_short_and_global_clear_rows', 'n/a')} "
                    "one-recording-short global-clear rows"
                ),
                (
                    "threshold sensitivity only finds default-target candidates when "
                    f"bidirectional support is relaxed to {default_candidate_bidir} "
                    f"({default_candidate_count} candidates)"
                ),
            ],
            next_action=(
                "Cache rebuild is complete; all matched recordings now expose wheel. "
                "Use the wheel-derived local target gate before any training."
                if behavior_ready
                else (
                    "Rebuild the matched cache without --no-wheel, then define a wheel-based "
                    "prospectively balanced target/control and run the same model-free "
                    "true-vs-shuffle, total-baseline, global target, and same-recording "
                    "bidirectional gate before training."
                )
            ),
            gpu_trigger=(
                "At least one local row must clear delta_vs_shuffle>=0, delta_vs_total>=0, "
                "target0>=0.55, target1>=0.55, and bidirectional_recording_fraction>=0.75."
            ),
        ),
        branch(
            name="wheel-derived target family gate",
            status=(
                "secondary_after_cache"
                if not behavior_ready
                else "recommended_next"
                if not wheel_done or (wheel_candidates or 0) > 0
                else "closed"
            ),
            priority=2 if not behavior_ready else (1 if not wheel_done or (wheel_candidates or 0) > 0 else 86),
            evidence=[
                (
                    f"behavior-cache preflight has wheel in {wheel_count}/{n_behavior_recordings} "
                    "matched recordings"
                ),
                (
                    "wheel target family gate has not been run yet"
                    if not wheel_done
                    else (
                        "wheel target family gate has "
                        f"{summary_value(wheel, 'n_candidates', 'n/a')} candidates across "
                        f"{summary_value(wheel, 'n_rows', 'n/a')} rows and max bidir "
                        f"{summary_value(wheel, 'max_bidirectional_recording_fraction', 0.0):.3f}"
                    )
                ),
            ],
            next_action=(
                "Run scripts/audit_wheel_target_family_gate.py locally against wheel_active, "
                "wheel_displacement, and choice_aligned_wheel."
                if not wheel_done
                else (
                    "If candidates are present, launch only the bounded pilot training tied to "
                    "the passing target/family row."
                    if (wheel_candidates or 0) > 0
                    else "Do not spend on the tested wheel targets; move to a prospectively supported manifest."
                )
            ),
            gpu_trigger=(
                "At least one local wheel row must clear delta_vs_shuffle>=0, delta_vs_total>=0, "
                "target0>=0.55, target1>=0.55, and bidirectional_recording_fraction>=0.75."
            ),
        ),
        branch(
            name="extreme-quantile behavioral target gate",
            status=(
                "recommended_next"
                if extreme_quantile_done and (extreme_quantile_candidates or 0) > 0 and extreme_seed is None
                else "closed"
                if extreme_seed is not None
                else "secondary_after_cache"
            ),
            priority=85 if extreme_seed is not None else (1 if extreme_quantile_done else 3),
            evidence=[
                (
                    "extreme-quantile target family gate has not been run yet"
                    if not extreme_quantile_done
                    else (
                        "extreme-quantile target family gate found "
                        f"{summary_value(extreme_quantile, 'n_candidates', 'n/a')} candidates across "
                        f"{summary_value(extreme_quantile, 'n_rows', 'n/a')} rows and max bidir "
                        f"{summary_value(extreme_quantile, 'max_bidirectional_recording_fraction', 0.0):.3f}"
                    )
                ),
                (
                    "seed sensitivity has not validated the extreme-quantile candidate yet"
                    if extreme_seed is None
                    else (
                        "seed sensitivity found "
                        f"{extreme_seed_summary.get('n_robust_shuffle_seed_candidates', 'n/a')} robust candidates; "
                        f"max positive seed fraction={extreme_seed_summary.get('max_positive_shuffle_delta_fraction', 0.0):.3f}"
                    )
                ),
            ],
            next_action=(
                "Run scripts/audit_extreme_quantile_seed_sensitivity.py before any GPU training."
                if extreme_quantile_done and (extreme_quantile_candidates or 0) > 0 and extreme_seed is None
                else extreme_seed_summary.get("next_action", "Keep extreme-quantile redesign local.")
                if extreme_seed is not None
                else "Run scripts/audit_extreme_quantile_target_family_gate.py as a local target/control redesign."
            ),
            gpu_trigger=(
                "A candidate must pass the unchanged local gate and remain positive across multiple "
                "within-recording shuffle seeds before training."
            ),
        ),
        branch(
            name="new manifest with prospective bidirectional support",
            status="recommended_next" if behavior_ready and wheel_done and reaction_feature_modes["n_modes"] and cell_type_prior_done and waveform_done and not (wheel_candidates or 0) else "secondary_after_new_target",
            priority=1 if behavior_ready and wheel_done and reaction_feature_modes["n_modes"] and cell_type_prior_done and waveform_done and not (wheel_candidates or 0) else 2,
            evidence=[
                "current 28-recording manifest is feasible but not clean enough to pass the local gate",
                (
                    "local cached manifest candidate audit has not been run yet"
                    if local_manifest_candidates is None
                    else (
                        "local cached manifest candidate audit found "
                        f"{local_manifest_summary.get('n_new_candidate_panels', 'n/a')} new candidate panels "
                        f"across {local_manifest_summary.get('n_local_recordings', 'n/a')} local recordings "
                        f"({local_manifest_decision})"
                    )
                ),
                (
                    "external manifest acquisition gap audit has not been run yet"
                    if external_acquisition is None
                    else (
                        "external acquisition gap audit identifies "
                        f"{external_summary.get('missing_hdf5_recordings_for_qualified_subjects', 'n/a')} "
                        "missing HDF5 recordings for "
                        f"{external_summary.get('support_qualified_subjects_missing_hdf5', 'n/a')} "
                        "support-qualified subjects, projecting "
                        f"{external_summary.get('projected_manifest_recordings', 'n/a')} recordings across "
                        f"{external_summary.get('projected_manifest_subjects', 'n/a')} subjects"
                    )
                ),
                (
                    "strict iterative 8-recording manifest has "
                    f"{summary_value(iterative, 'n_candidates', 'n/a')} candidates and max bidir "
                    f"{summary_value(iterative, 'max_bidirectional_recording_fraction', 0.0):.3f}"
                ),
                (
                    "projected support80 shared-family gate has not been run yet"
                    if not projected_support80_done
                    else (
                        "projected support80 shared-family gate has "
                        f"{projected_support80_candidates} candidates across "
                        f"{summary_value(projected_support80_gate, 'n_rows', 'n/a')} rows and max bidir "
                        f"{summary_value(projected_support80_gate, 'max_bidirectional_recording_fraction', 0.0):.3f}"
                    )
                ),
                (
                    "projected support80 all-family feature-mode sweep has not been run yet"
                    if projected_feature_modes["n_modes"] == 0
                    else (
                        "projected support80 all-family feature-mode sweep has "
                        f"{projected_feature_modes['n_candidates']} candidates across "
                        f"{projected_feature_modes['n_rows']} rows, "
                        f"{projected_feature_modes['n_modes']} feature modes, and max bidir "
                        f"{projected_feature_modes['max_bidirectional_recording_fraction']:.3f}"
                    )
                ),
                (
                    "local gate meta-failure audit has not been run yet"
                    if meta_failures is None
                    else (
                        "local gate meta-failure audit has "
                        f"{meta_summary.get('n_candidates', 'n/a')} candidates across "
                        f"{meta_summary.get('n_rows', 'n/a')} rows; recording bidirectionality fails in "
                        f"{meta_summary.get('failure_counts', {}).get('recording_bidirectionality', 'n/a')} rows"
                    )
                ),
                (
                    "recording bidirectionality prospectus has not been run yet"
                    if prospectus is None
                    else (
                        "recording bidirectionality prospectus found "
                        f"{prospectus_summary.get('n_prospect_recordings', 'n/a')} prospect recordings from "
                        f"{prospectus_summary.get('n_bidirectional_observations', 'n/a')} bidirectional observations"
                    )
                ),
                (
                    "prospect-lead manifest has not been built yet"
                    if prospect_manifest is None
                    else (
                        "prospect-lead manifest has "
                        f"{prospect_manifest.get('n_recordings', 'n/a')} recordings across "
                        f"{prospect_manifest.get('n_subjects', 'n/a')} subjects with "
                        f"{len(prospect_manifest.get('missing_recording_ids', []))} missing local recordings"
                    )
                ),
                (
                    "prospect-lead candidate validation has not been run yet"
                    if seed_sensitivity is None
                    else (
                        "subject-stable shuffle-seed sensitivity found "
                        f"{seed_sensitivity_summary.get('n_robust_shuffle_seed_candidates', 'n/a')} robust candidates; "
                        "max positive seed fraction="
                        f"{seed_sensitivity_summary.get('max_positive_shuffle_delta_fraction', 'n/a')}"
                    )
                ),
                "recording-subset replication selected zero stable validation rows",
            ],
            next_action=(
                "A local projected-manifest gate passed; launch only the bounded pilot tied "
                "to the passing target/family row."
                if projected_support80_done and (projected_support80_candidates or 0) > 0
                else "Do not launch GPU training from the projected support80 panel; its "
                "model-free family and feature-mode gates have no candidates. Redesign the "
                "target/control locally."
                if projected_support80_done
                else
                "Run the model-free true-vs-shuffle, total-baseline, target0/target1, "
                "and same-recording bidirectional gate on the projected support80 local "
                "manifest before any GPU training."
                if local_projected_panel_ready
                else "The local cache expansion does not create a supported panel; build or fetch "
                "the external support80 missing-HDF5 set, then rerun the local manifest "
                "candidate audit and the same model-free gate before training."
                if external_summary.get("decision") == "external_support80_acquisition_candidate"
                else "The local cache expansion does not create a supported panel; build or fetch "
                "a broader manifest only with a prospective target/family support rule, then "
                "run the same local model-free gate before training."
                if local_manifest_decision == "local_expansion_support_gap"
                else (
                    "Only build or fetch more recordings after a target/control proposal defines "
                    "which recordings should prospectively contain target0+target1 evidence."
                )
            ),
            gpu_trigger=(
                "At least one local row on the proposed manifest must clear "
                "delta_vs_shuffle>=0, delta_vs_total>=0, target0>=0.55, "
                "target1>=0.55, and bidirectional_recording_fraction>=0.75 "
                "before training."
            ),
        ),
        branch(
            name="direct cached-field derived targets",
            status="closed",
            priority=92,
            evidence=[
                (
                    "derived target family gate has "
                    f"{summary_value(derived, 'n_candidates', 'n/a')} candidates across "
                    f"{summary_value(derived, 'n_rows', 'n/a')} rows"
                ),
                "nearest response_latency row reaches 3/4 bidirectional recordings but fails true-vs-shuffle",
            ],
            next_action="Do not launch GPU training from contrast_strength, response_latency, or prior_engaged.",
            gpu_trigger="none",
        ),
        branch(
            name="reaction-dynamics wheel targets",
            status="closed" if reaction_feature_modes["n_modes"] else "recommended_next",
            priority=87 if reaction_feature_modes["n_modes"] else 1,
            evidence=[
                (
                    "reaction-dynamics target family feature-mode sweep has not been run yet"
                    if reaction_feature_modes["n_modes"] == 0
                    else (
                        "reaction-dynamics target family feature-mode sweep has "
                        f"{reaction_feature_modes['n_candidates']} candidates across "
                        f"{reaction_feature_modes['n_rows']} rows, "
                        f"{reaction_feature_modes['n_modes']} feature modes, and max bidir "
                        f"{reaction_feature_modes['max_bidirectional_recording_fraction']:.3f}"
                    )
                ),
                (
                    "best recording-centered near miss is wheel_reaction_latency/broad_named_anatomy/KS014: "
                    "target0=0.667, target1=0.715, bidir=3/4, total delta +0.003, but shuffle delta -0.001"
                    if reaction_feature_modes["n_modes"]
                    else "reaction dynamics should test pre-stim quiescence, post-stim speed-up, and first movement latency"
                ),
            ],
            next_action=(
                "Do not spend on reaction-dynamics wheel targets; the near miss fails true-vs-shuffle and does not replicate across feature modes."
                if reaction_feature_modes["n_modes"]
                else "Run scripts/audit_reaction_dynamics_target_family_gate.py across reaction target definitions before any training."
            ),
            gpu_trigger=(
                "At least one local reaction-dynamics row must clear delta_vs_shuffle>=0, "
                "delta_vs_total>=0, target0>=0.55, target1>=0.55, and "
                "bidirectional_recording_fraction>=0.75."
                if not reaction_feature_modes["n_modes"]
                else "none"
            ),
        ),
        branch(
            name="cell-type prior target/control gate",
            status="closed" if cell_type_prior_done else "recommended_next",
            priority=88 if cell_type_prior_done else 1,
            evidence=[
                (
                    "cell-type prior target/control gate has not been run yet"
                    if not cell_type_prior_done
                    else (
                        "cell-type prior target/control gate has "
                        f"{summary_value(cell_type_prior, 'n_candidates', 'n/a')} candidates across "
                        f"{summary_value(cell_type_prior, 'n_rows', 'n/a')} rows and max bidir "
                        f"{summary_value(cell_type_prior, 'max_bidirectional_recording_fraction', 0.0):.3f}"
                    )
                ),
                (
                    "best rows clear global target fractions but reach only 2/4 same-recording bidirectional support"
                    if cell_type_prior_done
                    else "project fine-region spike counts through ABC subclass priors before any cell-type-prior GPU run"
                ),
            ],
            next_action=(
                "Do not spend on broad ABC cell-class prior channels; they do not pass the local bidirectional gate."
                if cell_type_prior_done
                else "Run scripts/audit_cell_type_prior_target_control_gate.py locally before any cell-type-prior GPU training."
            ),
            gpu_trigger=(
                "none"
                if cell_type_prior_done
                else (
                    "At least one local cell-type-prior row must clear delta_vs_shuffle>=0, "
                    "delta_vs_total>=0, target0>=0.55, target1>=0.55, and "
                    "bidirectional_recording_fraction>=0.75."
                )
            ),
        ),
        branch(
            name="waveform target/control gate",
            status="closed" if waveform_done else "recommended_next",
            priority=89 if waveform_done else 1,
            evidence=[
                (
                    "waveform target/control gate has not been run yet"
                    if not waveform_done
                    else (
                        "waveform target/control gate has "
                        f"{summary_value(waveform, 'n_candidates', 'n/a')} candidates across "
                        f"{summary_value(waveform, 'n_rows', 'n/a')} rows and max bidir "
                        f"{summary_value(waveform, 'max_bidirectional_recording_fraction', 0.0):.3f}"
                    )
                ),
                (
                    "best depth/choice near miss clears global target fractions but reaches only 2/4 same-recording bidirectional support"
                    if waveform_done
                    else "test z-scored per-unit waveform channels against a within-recording shuffled waveform assignment"
                ),
            ],
            next_action=(
                "Do not spend on simple waveform-channel controls; they do not pass the local bidirectional gate."
                if waveform_done
                else "Run scripts/audit_waveform_target_control_gate.py locally before any waveform-only GPU training."
            ),
            gpu_trigger=(
                "none"
                if waveform_done
                else (
                    "At least one local waveform row must clear delta_vs_shuffle>=0, "
                    "delta_vs_total>=0, target0>=0.55, target1>=0.55, and "
                    "bidirectional_recording_fraction>=0.75."
                )
            ),
        ),
        branch(
            name="local gate meta-failure synthesis",
            status="closed" if meta_failures is not None else "recommended_next",
            priority=90 if meta_failures is not None else 1,
            evidence=[
                (
                    "local gate meta-failure audit has not been run yet"
                    if meta_failures is None
                    else (
                        "meta-audit aggregates "
                        f"{meta_summary.get('n_rows', 'n/a')} rows from "
                        f"{meta_summary.get('n_artifacts_present', 'n/a')} artifacts with "
                        f"{meta_summary.get('n_candidates', 'n/a')} candidates and "
                        f"{meta_summary.get('n_one_failure_rows', 'n/a')} one-failure rows"
                    )
                ),
                (
                    "recording bidirectionality is the dominant blocker; it appears in "
                    f"{meta_summary.get('failure_counts', {}).get('recording_bidirectionality', 'n/a')} rows"
                    if meta_failures is not None
                    else "aggregate closed gates to identify the next target/control redesign rule"
                ),
            ],
            next_action=(
                "Use the meta-audit redesign rule: require prospectively defined same-recording target0+target1 evidence before any GPU run."
                if meta_failures is not None
                else "Run scripts/audit_local_gate_meta_failures.py and update the redesign rule."
            ),
            gpu_trigger="none",
        ),
        branch(
            name="recording bidirectionality prospectus",
            status="closed" if prospectus is not None else "recommended_next",
            priority=90 if prospectus is not None else 1,
            evidence=[
                (
                    "recording bidirectionality prospectus has not been run yet"
                    if prospectus is None
                    else (
                        "prospectus aggregates "
                        f"{prospectus_summary.get('n_observations', 'n/a')} per-recording observations "
                        f"with {prospectus_summary.get('n_bidirectional_observations', 'n/a')} bidirectional "
                        f"observations across {prospectus_summary.get('recordings_with_bidirectional_support', 'n/a')} "
                        "recordings"
                    )
                ),
                (
                    "candidate recordings are only design leads, not a GPU trigger"
                    if prospectus is not None
                    else "aggregate current local-gate recording rows to see whether bidirectionality is concentrated"
                ),
                (
                    "prospect-lead manifest has not been built yet"
                    if prospect_manifest is None
                    else (
                        "prospect-lead manifest materializes "
                        f"{prospect_manifest.get('n_recordings', 'n/a')} recordings across "
                        f"{prospect_manifest.get('n_subjects', 'n/a')} subjects"
                    )
                ),
            ],
            next_action=(
                "Run the unchanged local gate on manifests/ibl_bwm_recording_bidirectionality_prospect_leads.json; treat any pass as a local redesign candidate, not a training trigger."
                if prospect_manifest is not None
                else prospectus_summary.get("next_action", "Use the prospectus to define the next prospective manifest rule.")
                if prospectus is not None
                else "Run scripts/audit_recording_bidirectionality_prospectus.py before more manifest or GPU work."
            ),
            gpu_trigger="none",
        ),
        branch(
            name="prospect-lead derived target validation",
            status="closed" if prospect_feature_validation is not None else "recommended_next",
            priority=90 if prospect_feature_validation is not None else 1,
            evidence=[
                (
                    "prospect-lead derived gate has not been run yet"
                    if prospect_derived_gate is None
                    else (
                        "prospect-lead derived gate found "
                        f"{prospect_derived_summary.get('n_candidates', 'n/a')} candidates across "
                        f"{prospect_derived_summary.get('n_rows', 'n/a')} rows"
                    )
                ),
                (
                    "single-mode prospect-lead validation has not been run yet"
                    if prospect_validation is None
                    else (
                        "recording-centered validation found "
                        f"{prospect_validation_summary.get('n_validated_candidates', 'n/a')} validated candidates; "
                        f"{prospect_validation_summary.get('n_single_recording_candidates', 'n/a')} prospect candidates "
                        "were single-recording and "
                        f"{prospect_validation_summary.get('n_subset_only_candidates', 'n/a')} were subset-only"
                    )
                ),
                (
                    "feature-mode prospect-lead validation has not been run yet"
                    if prospect_feature_validation is None
                    else (
                        "feature-mode validation found "
                        f"{prospect_feature_summary.get('n_validated_candidates', 'n/a')} validated candidates from "
                        f"{prospect_feature_summary.get('n_prospect_candidates', 'n/a')} prospect candidates across "
                        f"{prospect_feature_summary.get('n_feature_modes', 'n/a')} feature modes"
                    )
                ),
                (
                    "prospect-lead subject-stability audit has not been run yet"
                    if prospect_subject_stability is None
                    else (
                        "subject-stability audit found "
                        f"{prospect_subject_summary.get('n_same_subject_stable_candidates', 'n/a')} same-subject "
                        "stable candidates and "
                        f"{prospect_subject_summary.get('n_candidates_with_nonlead_failure', 'n/a')} candidates with "
                        "same-subject non-lead failure"
                    )
                ),
            ],
            next_action=(
                prospect_subject_summary.get("next_action", "Keep validation no-spend.")
                if prospect_subject_stability is not None
                else prospect_feature_summary.get("next_action", "Keep validation no-spend.")
                if prospect_feature_validation is not None
                else "Run scripts/audit_prospect_lead_feature_mode_validation.py before any training decision."
            ),
            gpu_trigger="none",
        ),
        branch(
            name="subject-stable local gate prospectus",
            status="closed" if subject_stable_prospectus is not None else "recommended_next",
            priority=90 if subject_stable_prospectus is not None else 1,
            evidence=[
                (
                    "subject-stable local-gate prospectus has not been run yet"
                    if subject_stable_prospectus is None
                    else (
                        "prospectus found "
                        f"{subject_stable_summary.get('n_subject_stable_rows', 'n/a')} subject-stable rows, "
                        f"{subject_stable_summary.get('n_subject_stable_candidates', 'n/a')} candidates, and "
                        f"{subject_stable_summary.get('n_subject_stable_one_failure_rows', 'n/a')} one-failure rows"
                    )
                ),
                (
                    "subject-stable failure counts unavailable"
                    if subject_stable_prospectus is None
                    else (
                        "subject-stable failures are "
                        + ", ".join(
                            f"{name}={count}"
                            for name, count in sorted(subject_stable_summary.get("failure_counts", {}).items())
                        )
                    )
                ),
                (
                    "subject-stable shuffle-seed sensitivity has not been run yet"
                    if seed_sensitivity is None
                    else (
                        "shuffle-seed sensitivity found "
                        f"{seed_sensitivity_summary.get('n_robust_shuffle_seed_candidates', 'n/a')} robust candidates "
                        "across "
                        f"{seed_sensitivity_summary.get('n_cases', 'n/a')} subject-stable near misses"
                    )
                ),
                (
                    "subject-stable broad-anatomy mechanism audit has not been run yet"
                    if subject_stable_mechanism is None
                    else (
                        "broad-anatomy mechanism audit found "
                        f"{subject_stable_mechanism_summary.get('n_bidirectional_family_candidates', 'n/a')} "
                        "contribution candidates but "
                        f"{subject_stable_mechanism_summary.get('n_family_gate_candidates', 'n/a')} "
                        "exact family-gate candidates"
                    )
                ),
            ],
            next_action=(
                "Do not train from the current subject-stable broad-anatomy branch; exact family gates remain negative."
                if subject_stable_mechanism is not None
                else seed_sensitivity_summary.get("next_action", "Keep subject-stable redesign local.")
                if seed_sensitivity is not None
                else subject_stable_summary.get("next_action", "Keep subject-stable redesign local.")
                if subject_stable_prospectus is not None
                else "Run scripts/audit_subject_stable_local_gate_prospectus.py before another target/control branch."
            ),
            gpu_trigger="none",
        ),
        branch(
            name="contextual cached trial-state targets",
            status="closed",
            priority=93,
            evidence=[
                (
                    "contextual target family gate has "
                    f"{summary_value(contextual, 'n_candidates', 'n/a')} candidates across "
                    f"{summary_value(contextual, 'n_rows', 'n/a')} rows and max bidir "
                    f"{summary_value(contextual, 'max_bidirectional_recording_fraction', 0.0):.3f}"
                ),
                "post_error, prior_block_switch, and prior_block_late do not clear the local gate",
            ],
            next_action="Do not spend on contextual trial-sequence targets from the compact cache.",
            gpu_trigger="none",
        ),
        branch(
            name="more feature-mode or l2 sweeps on shared broad anatomy",
            status="closed",
            priority=94,
            evidence=[
                (
                    "shared broad-anatomy repair sweep has "
                    f"{summary_value(shared_broad, 'n_candidates', 'n/a')} candidates, max bidir "
                    f"{summary_value(shared_broad, 'max_bidirectional_recordings', 'n/a')}, and max min target margin "
                    f"{summary_value(shared_broad, 'max_min_target_margin', 0.0):+.3f}"
                ),
            ],
            next_action="Do not spend more local or GPU time on simple broad-anatomy feature/regularization repair.",
            gpu_trigger="none",
        ),
        branch(
            name="narrow existing manifest further",
            status="closed",
            priority=95,
            evidence=[
                (
                    "iterative manifest gate has "
                    f"{summary_value(iterative, 'n_candidates', 'n/a')} candidates and max bidir recordings "
                    f"{summary_value(iterative, 'max_bidirectional_recordings', 'n/a')}"
                ),
                "2-subject manifest is too narrow for the intended cross-animal demo",
            ],
            next_action="Do not keep shrinking the existing cache as the primary rescue path.",
            gpu_trigger="none",
        ),
        branch(
            name="recording-subset selection from current artifacts",
            status="closed",
            priority=96,
            evidence=[
                (
                    "recording replication audit selected "
                    f"{summary_value(replication, 'n_selected_by_discovery_rule', 'n/a')} rows and replicated "
                    f"{summary_value(replication, 'n_replicated_in_validation', 'n/a')}"
                ),
            ],
            next_action="Do not train on selected current recordings unless a new target/control first passes locally.",
            gpu_trigger="none",
        ),
        branch(
            name="current shared-family target/control grid",
            status="closed",
            priority=97,
            evidence=[
                (
                    "shared-family gate has "
                    f"{summary_value(shared_family, 'n_candidates', 'n/a')} candidates across "
                    f"{summary_value(shared_family, 'n_rows', 'n/a')} rows"
                ),
                "top rows are one-sided or fail baseline controls",
            ],
            next_action="Do not rerun the same target/family grid without a new target/control definition.",
            gpu_trigger="none",
        ),
        branch(
            name="alternative cached targets plus family aggregation",
            status="closed",
            priority=98,
            evidence=[
                (
                    "prior_side family gate candidates="
                    f"{summary_value(artifacts['family_alt_prior'], 'n_candidates', 'n/a')}; "
                    "feedback family gate candidates="
                    f"{summary_value(artifacts['family_alt_feedback'], 'n_candidates', 'n/a')}"
                ),
            ],
            next_action="Do not expect prior_side or feedback alone to rescue the signal under current controls.",
            gpu_trigger="none",
        ),
        branch(
            name="source-target pair narrowing",
            status="closed",
            priority=99,
            evidence=[
                (
                    "family source-target pair gate candidates="
                    f"{summary_value(artifacts['source_target_families'], 'n_candidates', 'n/a')}"
                ),
            ],
            next_action="Do not run a paid source-target pair sweep without a new local gate pass.",
            gpu_trigger="none",
        ),
    ]
    branches = sorted(branches, key=lambda row: row["priority"])
    decision = (
        "behavior_cache_rebuild_required"
        if not behavior_ready
        else "wheel_target_audit_required"
        if not wheel_done
        else "extreme_quantile_seed_validation_required"
        if extreme_quantile_done and (extreme_quantile_candidates or 0) > 0 and extreme_seed is None
        else "local_training_trigger_available"
        if (wheel_candidates or 0) > 0 or (projected_support80_candidates or 0) > 0 or extreme_seed_robust > 0
        else "no_local_training_trigger"
    )
    return {
        "summary": {
            "recommended_next": branches[0]["name"],
            "closed_branches": sum(1 for row in branches if row["status"] == "closed"),
            "gpu_training_trigger": branches[0]["gpu_trigger"],
            "decision": decision,
        },
        "artifacts": ARTIFACTS,
        "branches": branches,
    }


def render_markdown(report: dict) -> str:
    summary = report["summary"]
    lines = [
        "# Next Benchmark/Control Options Audit",
        "",
        (
            "Ranks remaining no-spend branches after the current local audits. This is "
            "the planning gate before any new RunPod training."
        ),
        "",
        f"- recommended next: `{summary['recommended_next']}`",
        f"- closed branches: `{summary['closed_branches']}`",
        f"- decision: `{summary['decision']}`",
        f"- GPU trigger: {summary['gpu_training_trigger']}",
        "",
        "| priority | branch | status | next action |",
        "|---:|---|---|---|",
    ]
    for row in report["branches"]:
        lines.append(f"| {row['priority']} | {row['name']} | `{row['status']}` | {row['next_action']} |")
    lines += [
        "",
        "## Evidence",
        "",
    ]
    for row in report["branches"]:
        lines.append(f"### {row['name']}")
        for item in row["evidence"]:
            lines.append(f"- {item}")
        lines.append(f"- GPU trigger: {row['gpu_trigger']}")
        lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-json", type=Path, default=REPO_ROOT / "docs/next_benchmark_control_options.json")
    parser.add_argument("--out-md", type=Path, default=REPO_ROOT / "docs/next_benchmark_control_options.md")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report()
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text(render_markdown(report))
    print(f"wrote {args.out_json}")
    print(f"wrote {args.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
