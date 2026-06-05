import json
from pathlib import Path

from scripts.summarize_experiment_state import (
    local_probe_outcome,
    read_cache_audit,
    read_slice_result,
    read_local_probe_result,
    read_strict_gate,
    render_markdown,
    slice_outcome,
    strict_gate_outcome,
    summarize,
)


def test_strict_gate_outcome_lists_failed_checks(tmp_path: Path) -> None:
    path = tmp_path / "gate.json"
    path.write_text(json.dumps({
        "holdout": "mouse",
        "pass": False,
        "metrics": {
            "centered_auc_delta_vs_shuffle": 0.001,
            "paired_true_vs_shuffle": 0.44,
            "paired_specificity_gap": -0.10,
            "recording_sign_flip": {"one_sided_p": 0.25},
        },
    }))

    row = read_strict_gate("pilot", path)

    assert row is not None
    assert row.holdout == "mouse"
    assert strict_gate_outcome(row) == "fail: small centered delta, paired gate, specificity, sign-flip"


def test_slice_result_parses_true_minus_shuffle(tmp_path: Path) -> None:
    path = tmp_path / "results.md"
    path.write_text("\n".join([
        "| holdout | arm | n_seeds | mean_AUC | mean_delta_vs_shared | seed_deltas |",
        "|---|---|---:|---:|---:|---|",
        "| NYU-12 | region_only | 3 | 0.513 | +0.013 | +0.067, +0.021, -0.048 |",
        "| NYU-12 | region_shuffle | 3 | 0.520 | +0.020 | +0.038, +0.015, +0.007 |",
    ]))

    row = read_slice_result("slice", path, "NYU-12")

    assert row is not None
    assert row.true_delta == 0.013
    assert row.shuffle_delta == 0.020
    assert row.true_positive == "2/3"
    assert row.shuffle_positive == "3/3"
    assert slice_outcome(row) == "shuffle >= true"


def test_render_markdown_keeps_no_paid_broadening_decision(tmp_path: Path) -> None:
    gate_path = tmp_path / "gate.json"
    gate_path.write_text(json.dumps({
        "holdout": "mouse",
        "pass": False,
        "metrics": {"paired_true_vs_shuffle": 0.44},
    }))
    gate = read_strict_gate("pilot", gate_path)
    summary = summarize([gate], [])
    markdown = render_markdown([gate], [])

    assert summary["decision"] == "no_paid_broadening_without_new_mechanism"
    assert "Current Anatomy-Transfer Experiment State" in markdown
    assert "No current strict-gate artifact supports paid broadening" in markdown


def test_render_markdown_includes_subject_stable_mechanism_section() -> None:
    markdown = render_markdown(
        [],
        [],
        subject_stable_broad_anatomy_mechanism={
            "summary": {
                "n_subject_stable_rows": 1,
                "n_bidirectional_family_candidates": 1,
                "n_family_gate_candidates": 0,
                "decision": "contribution_only_subject_stable_broad_family_mechanism",
            },
            "rows": [
                {
                    "source": "reaction_recording_centered",
                    "target_mode": "wheel_reaction_latency",
                    "holdout": "KS014",
                    "bidirectional_family_candidates": ["broad_named_anatomy"],
                    "family_gate_candidates": [],
                }
            ],
        },
    )

    assert "Subject-Stable Broad-Anatomy Mechanism" in markdown
    assert "exact family-gate candidates: `0`" in markdown
    assert "does not justify GPU training" in markdown


def test_render_markdown_includes_composite_behavior_seed_veto() -> None:
    markdown = render_markdown(
        [],
        [],
        composite_behavior_target_gate={
            "summary": {
                "n_rows": 8,
                "n_candidates": 1,
                "n_positive_centered_delta": 4,
                "max_bidirectional_recording_fraction": 0.75,
                "decision": "composite_behavior_target_family_candidate",
                "target_balances": {
                    "post_error_fast_response_le_1": {
                        "n_trials": 100,
                        "eligible_recordings": 4,
                        "n_recordings": 4,
                    }
                },
                "top_rows": [
                    {
                        "target_mode": "post_error_fast_response_le_1",
                        "family": "broad_named_anatomy",
                        "holdout": "NR_0019",
                        "decision": "candidate",
                        "centered_delta_vs_shuffle": 0.004,
                        "centered_delta_vs_total": 0.002,
                        "target0_improved_vs_shuffle": 0.57,
                        "target1_improved_vs_shuffle": 0.64,
                        "n_bidirectional_recordings": 3,
                        "n_recordings": 4,
                    }
                ],
            }
        },
        composite_behavior_target_projected_gate={
            "summary": {
                "n_rows": 8,
                "n_candidates": 2,
                "n_positive_centered_delta": 5,
                "max_bidirectional_recording_fraction": 0.75,
                "decision": "composite_behavior_target_family_candidate",
                "target_balances": {
                    "post_error_fast_response_le_1": {
                        "n_trials": 120,
                        "eligible_recordings": 4,
                        "n_recordings": 4,
                    }
                },
                "top_rows": [
                    {
                        "target_mode": "post_error_fast_response_le_1",
                        "family": "broad_named_anatomy",
                        "holdout": "CSHL045",
                        "decision": "candidate",
                        "centered_delta_vs_shuffle": 0.068,
                        "centered_delta_vs_total": 0.039,
                        "target0_improved_vs_shuffle": 0.62,
                        "target1_improved_vs_shuffle": 0.84,
                        "n_bidirectional_recordings": 3,
                        "n_recordings": 4,
                    }
                ],
            }
        },
        composite_behavior_target_seed_sensitivity={
            "summary": {
                "n_cases": 2,
                "n_robust_composite_behavior_seed_candidates": 0,
                "max_positive_shuffle_delta_fraction": 1.0,
                "max_candidate_seed_fraction": 0.8,
                "decision": "no_composite_behavior_seed_candidate",
            },
            "rows": [
                {
                    "target_mode": "post_error_fast_response_le_1",
                    "family": "broad_named_anatomy",
                    "holdout": "CSHL045",
                    "n_positive_shuffle_delta_seeds": 5,
                    "n_candidate_seeds": 3,
                    "n_seeds": 5,
                    "mean_centered_delta_vs_shuffle": 0.062,
                    "mean_centered_delta_vs_total": 0.039,
                    "mean_target0": 0.63,
                    "mean_target1": 0.76,
                    "min_bidirectional_recordings": 2,
                    "max_bidirectional_recordings": 3,
                }
            ],
        },
        composite_behavior_target_l2_seed_sensitivity={
            "summary": {
                "n_cases": 2,
                "n_l2_values": 3,
                "n_robust_composite_behavior_l2_seed_candidates": 0,
                "max_positive_shuffle_delta_fraction": 1.0,
                "max_candidate_seed_fraction": 0.8,
                "decision": "no_composite_behavior_l2_seed_candidate",
            },
            "rows": [
                {
                    "l2": 1.0,
                    "target_mode": "post_error_fast_response_le_1",
                    "family": "broad_named_anatomy",
                    "holdout": "CSHL045",
                    "n_positive_shuffle_delta_seeds": 5,
                    "n_candidate_seeds": 3,
                    "n_seeds": 5,
                    "mean_centered_delta_vs_shuffle": 0.062,
                    "mean_centered_delta_vs_total": 0.039,
                    "mean_target0": 0.63,
                    "mean_target1": 0.76,
                    "min_bidirectional_recordings": 2,
                    "max_bidirectional_recordings": 3,
                }
            ],
        },
        composite_behavior_recording_failure={
            "summary": {
                "n_cases": 2,
                "n_recordings": 8,
                "n_stable_bidirectional_recordings": 3,
                "n_unstable_recordings": 5,
                "min_recording_bidirectional_seed_fraction": 0.0,
                "decision": "composite_behavior_recording_bidirectionality_failure",
            },
            "rows": [
                {
                    "holdout": "CSHL045",
                    "n_stable_bidirectional_recordings": 2,
                    "n_recordings": 4,
                    "mean_bidirectional_seed_fraction": 0.65,
                    "weakest_recordings": [
                        {
                            "recording": "weak_probe",
                            "n_bidirectional_seeds": 0,
                            "n_seeds": 5,
                            "mean_target0_improved": 0.37,
                            "mean_target1_improved": 0.67,
                        }
                    ],
                }
            ],
        },
    )

    assert "Composite Behavior Seed Sensitivity" in markdown
    assert "Composite Behavior L2/Seed Sensitivity" in markdown
    assert "Composite Behavior Recording Failure Decomposition" in markdown
    assert "do not train" in markdown.lower()
    assert "strongest current near miss" in markdown
    assert "not a ridge-l2 artifact" in markdown
    assert "same-recording target0+target1 stability" in markdown


def test_render_markdown_includes_extreme_quantile_seed_veto() -> None:
    markdown = render_markdown(
        [],
        [],
        extreme_quantile_target_family_gate={
            "summary": {
                "n_candidates": 1,
                "n_positive_centered_delta": 10,
                "max_bidirectional_recording_fraction": 1.0,
                "decision": "extreme_quantile_target_family_candidate",
                "top_rows": [
                    {
                        "target_mode": "response_latency_extreme",
                        "family": "broad_named_anatomy",
                        "holdout": "NR_0019",
                        "decision": "candidate",
                        "centered_delta_vs_shuffle": 0.001,
                        "centered_delta_vs_total": 0.0004,
                        "target0_improved_vs_shuffle": 0.63,
                        "target1_improved_vs_shuffle": 0.65,
                        "n_bidirectional_recordings": 4,
                        "n_recordings": 4,
                    }
                ],
            }
        },
        extreme_quantile_seed_sensitivity={
            "summary": {
                "n_cases": 1,
                "n_robust_shuffle_seed_candidates": 0,
                "max_positive_shuffle_delta_fraction": 0.4,
                "decision": "no_extreme_quantile_shuffle_seed_candidate",
            },
            "rows": [
                {
                    "target_mode": "response_latency_extreme",
                    "family": "broad_named_anatomy",
                    "holdout": "NR_0019",
                    "n_positive_shuffle_delta_seeds": 2,
                    "n_candidate_seeds": 2,
                    "n_seeds": 5,
                    "mean_centered_delta_vs_shuffle": -0.0001,
                    "mean_centered_delta_vs_total": 0.0004,
                    "mean_target0": 0.64,
                    "mean_target1": 0.68,
                    "min_bidirectional_recordings": 4,
                    "max_bidirectional_recordings": 4,
                }
            ],
        },
        extreme_quantile_cutoff_sensitivity={
            "summary": {
                "n_cutoffs": 1,
                "n_robust_cutoff_candidates": 0,
                "best_cutoff": "20/80",
                "best_candidate_seeds": 2,
                "decision": "no_extreme_quantile_cutoff_candidate",
            },
            "rows": [
                {
                    "label": "20/80",
                    "n_positive_shuffle_delta_seeds": 2,
                    "n_candidate_seeds": 2,
                    "n_seeds": 5,
                    "mean_centered_delta_vs_shuffle": 0.0002,
                    "mean_centered_delta_vs_total": 0.0003,
                    "mean_target0": 0.68,
                    "mean_target1": 0.71,
                    "min_bidirectional_recordings": 4,
                    "max_bidirectional_recordings": 4,
                }
            ],
        },
        extreme_quantile_region_specificity={
            "summary": {
                "n_regions": 1,
                "n_candidates": 1,
                "n_positive_centered_delta": 1,
                "max_bidirectional_recording_fraction": 0.75,
                "decision": "extreme_quantile_region_candidate",
                "top_rows": [
                    {
                        "region": "root",
                        "holdout": "CSH_ZAD_019",
                        "decision": "candidate",
                        "centered_delta_vs_shuffle": 0.13,
                        "centered_delta_vs_total": 0.02,
                        "target0_improved_vs_shuffle": 0.62,
                        "target1_improved_vs_shuffle": 0.59,
                        "n_bidirectional_recordings": 3,
                        "n_recordings": 4,
                        "eval_nonzero_fraction": 0.48,
                    }
                ],
            }
        },
        extreme_quantile_region_seed_sensitivity={
            "summary": {
                "n_cases": 1,
                "n_robust_region_seed_candidates": 0,
                "max_positive_shuffle_delta_fraction": 1.0,
                "decision": "no_extreme_quantile_region_seed_candidate",
            },
            "rows": [
                {
                    "target_mode": "response_latency_extreme",
                    "region": "root",
                    "holdout": "CSH_ZAD_019",
                    "n_positive_shuffle_delta_seeds": 5,
                    "n_candidate_seeds": 1,
                    "n_seeds": 5,
                    "mean_centered_delta_vs_shuffle": 0.079,
                    "mean_centered_delta_vs_total": 0.019,
                    "mean_target0": 0.54,
                    "mean_target1": 0.56,
                    "min_bidirectional_recordings": 1,
                    "max_bidirectional_recordings": 3,
                }
            ],
        },
        extreme_quantile_interpretable_region_filter={
            "summary": {
                "excluded_regions": ["root", "void"],
                "n_regions": 1,
                "n_candidates": 0,
                "n_excluded_candidates": 1,
                "decision": "no_extreme_quantile_interpretable_region_candidate",
                "top_rows": [
                    {
                        "region": "MOp",
                        "holdout": "SWC_038",
                        "decision": "reject: shuffle",
                        "centered_delta_vs_shuffle": -0.02,
                        "centered_delta_vs_total": -0.05,
                        "target0_improved_vs_shuffle": 0.87,
                        "target1_improved_vs_shuffle": 0.30,
                        "n_bidirectional_recordings": 2,
                        "n_recordings": 4,
                        "eval_nonzero_fraction": 0.21,
                    }
                ],
            }
        },
        extreme_quantile_interpretable_region_pair_scan={
            "selected_regions": ["PRT", "VP", "cc"],
            "summary": {
                "n_region_pairs": 3,
                "n_candidates": 2,
                "n_positive_centered_delta": 4,
                "decision": "extreme_quantile_interpretable_region_pair_candidate",
                "gpu_training_ready": False,
                "top_rows": [
                    {
                        "region_pair": "PRT+VP",
                        "holdout": "CSH_ZAD_019",
                        "decision": "candidate",
                        "centered_delta_vs_shuffle": 0.099,
                        "centered_delta_vs_total": 0.083,
                        "target0_improved_vs_shuffle": 0.56,
                        "target1_improved_vs_shuffle": 0.75,
                        "n_bidirectional_recordings": 3,
                        "n_recordings": 4,
                        "eval_nonzero_fraction": 0.37,
                    }
                ],
            },
        },
        extreme_quantile_region_pair_seed_sensitivity={
            "summary": {
                "n_cases": 2,
                "n_robust_region_pair_seed_candidates": 0,
                "max_positive_shuffle_delta_fraction": 1.0,
                "decision": "no_extreme_quantile_region_pair_seed_candidate",
                "gpu_training_ready": False,
            },
            "rows": [
                {
                    "target_mode": "response_latency_extreme",
                    "region_pair": "PRT+VP",
                    "holdout": "CSH_ZAD_019",
                    "n_positive_shuffle_delta_seeds": 5,
                    "n_candidate_seeds": 2,
                    "n_seeds": 5,
                    "mean_centered_delta_vs_shuffle": 0.069,
                    "mean_centered_delta_vs_total": 0.084,
                    "mean_target0": 0.67,
                    "mean_target1": 0.59,
                    "min_bidirectional_recordings": 2,
                    "max_bidirectional_recordings": 3,
                }
            ],
        },
    )

    assert "Extreme-Quantile Target Family Gate" in markdown
    assert "Extreme-Quantile Shuffle Seed Sensitivity" in markdown
    assert "Extreme-Quantile Cutoff Sensitivity" in markdown
    assert "Extreme-Quantile Region Specificity" in markdown
    assert "Extreme-Quantile Region Seed Sensitivity" in markdown
    assert "Extreme-Quantile Interpretable Region Filter" in markdown
    assert "Extreme-Quantile Interpretable Region Pair Scan" in markdown
    assert "Extreme-Quantile Region Pair Seed Sensitivity" in markdown
    assert "do not train from the extreme-quantile candidate" in markdown
    assert "do not train from the exploratory region-pair rows" in markdown


def test_render_markdown_includes_projected_recording_zscore_gate() -> None:
    markdown = render_markdown(
        [],
        [],
        projected_support80_recording_zscore={
            "summary": {
                "n_rows": 2,
                "n_candidates": 0,
                "n_positive_centered_delta": 1,
                "max_bidirectional_recording_fraction": 0.5,
                "decision": "no_shared_family_target_candidate",
                "top_rows": [
                    {
                        "target_mode": "choice",
                        "family": "brainstem_interbrain",
                        "holdout": "NR_0019",
                        "decision": "reject_target1",
                        "centered_delta_vs_shuffle": 0.134,
                        "centered_delta_vs_total": 0.305,
                        "target0_improved_vs_shuffle": 0.721,
                        "target1_improved_vs_shuffle": 0.416,
                        "n_bidirectional_recordings": 2,
                        "n_recordings": 4,
                    }
                ],
            }
        },
    )

    assert "Projected Support80 Recording-Zscore Gate" in markdown
    assert "candidates: `0`" in markdown
    assert "do not train" in markdown


def test_render_markdown_includes_low_contrast_choice_seed_veto() -> None:
    markdown = render_markdown(
        [],
        [],
        low_contrast_choice_family_gate={
            "summary": {
                "n_rows": 84,
                "n_candidates": 0,
                "n_positive_centered_delta": 41,
                "max_bidirectional_recordings": 2,
                "max_bidirectional_recording_fraction": 0.5,
                "decision": "no_low_contrast_choice_family_candidate",
                "target_balances": {
                    "low_contrast_choice_le_0.125": {
                        "n_trials": 9786,
                        "eligible_recordings": 28,
                        "n_recordings": 28,
                    }
                },
                "top_rows": [
                    {
                        "target_mode": "low_contrast_choice_le_0.125",
                        "family": "fiber_tracts",
                        "holdout": "CSH_ZAD_019",
                        "decision": "reject: target0",
                        "centered_delta_vs_shuffle": 0.209,
                        "centered_delta_vs_total": 0.215,
                        "target0_improved_vs_shuffle": 0.545,
                        "target1_improved_vs_shuffle": 0.629,
                        "n_bidirectional_recordings": 2,
                        "n_recordings": 4,
                    }
                ],
            }
        },
        low_contrast_choice_projected_gate={
            "summary": {
                "n_rows": 96,
                "n_candidates": 1,
                "n_positive_centered_delta": 48,
                "max_bidirectional_recordings": 3,
                "max_bidirectional_recording_fraction": 0.75,
                "decision": "low_contrast_choice_family_candidate",
                "gpu_training_ready": False,
                "target_balances": {
                    "low_contrast_choice_le_0.125": {
                        "n_trials": 11384,
                        "eligible_recordings": 31,
                        "n_recordings": 31,
                    }
                },
                "top_rows": [
                    {
                        "target_mode": "low_contrast_choice_le_0.125",
                        "family": "fiber_tracts",
                        "holdout": "CSH_ZAD_019",
                        "decision": "candidate",
                        "centered_delta_vs_shuffle": 0.021,
                        "centered_delta_vs_total": 0.215,
                        "target0_improved_vs_shuffle": 0.552,
                        "target1_improved_vs_shuffle": 0.593,
                        "n_bidirectional_recordings": 3,
                        "n_recordings": 4,
                    }
                ],
            }
        },
        low_contrast_choice_seed_sensitivity={
            "summary": {
                "n_cases": 1,
                "n_robust_low_contrast_choice_seed_candidates": 0,
                "max_positive_shuffle_delta_fraction": 0.8,
                "decision": "no_low_contrast_choice_seed_candidate",
                "gpu_training_ready": False,
            },
            "rows": [
                {
                    "target_mode": "low_contrast_choice_le_0.125",
                    "family": "fiber_tracts",
                    "holdout": "CSH_ZAD_019",
                    "n_positive_shuffle_delta_seeds": 4,
                    "n_candidate_seeds": 1,
                    "n_seeds": 5,
                    "mean_centered_delta_vs_shuffle": 0.019,
                    "mean_centered_delta_vs_total": 0.215,
                    "mean_target0": 0.527,
                    "mean_target1": 0.560,
                    "min_bidirectional_recordings": 0,
                    "max_bidirectional_recordings": 3,
                }
            ],
        },
    )

    assert "Low-Contrast Choice Family Gate" in markdown
    assert "Low-Contrast Choice Projected Manifest Gate" in markdown
    assert "Low-Contrast Choice Seed Sensitivity" in markdown
    assert "do not train from the low-contrast choice row" in markdown


def test_render_markdown_includes_neutral_prior_low_contrast_choice_veto() -> None:
    gate_payload = {
        "summary": {
            "n_rows": 320,
            "n_candidates": 0,
            "n_positive_centered_delta": 133,
            "max_bidirectional_recording_fraction": 0.75,
            "decision": "no_neutral_prior_low_contrast_choice_family_candidate",
            "target_balances": {
                "neutral_prior_low_contrast_choice_le_1": {
                    "n_trials": 2790,
                    "eligible_recordings": 11,
                    "n_recordings": 31,
                }
            },
            "top_rows": [
                {
                    "target_mode": "neutral_prior_low_contrast_choice_le_1",
                    "family": "broad_named_anatomy",
                    "holdout": "CSH_ZAD_019",
                    "decision": "reject: shuffle",
                    "centered_delta_vs_shuffle": -0.003,
                    "centered_delta_vs_total": -0.006,
                    "target0_improved_vs_shuffle": 0.596,
                    "target1_improved_vs_shuffle": 0.683,
                    "n_bidirectional_recordings": 3,
                    "n_recordings": 4,
                }
            ],
        }
    }
    markdown = render_markdown(
        [],
        [],
        neutral_prior_low_contrast_choice_family_gate=gate_payload,
        neutral_prior_low_contrast_choice_projected_gate=gate_payload,
        neutral_prior_low_contrast_choice_seed_sensitivity={
            "summary": {
                "n_cases": 1,
                "n_robust_neutral_prior_low_contrast_choice_seed_candidates": 0,
                "max_positive_shuffle_delta_fraction": 1.0,
                "decision": "no_neutral_prior_low_contrast_choice_seed_candidate",
                "gpu_training_ready": False,
            },
            "rows": [
                {
                    "target_mode": "neutral_prior_low_contrast_choice_le_1",
                    "family": "fiber_tracts",
                    "holdout": "CSH_ZAD_019",
                    "n_positive_shuffle_delta_seeds": 5,
                    "n_candidate_seeds": 2,
                    "n_seeds": 5,
                    "mean_centered_delta_vs_shuffle": 0.0607,
                    "mean_centered_delta_vs_total": 0.126,
                    "mean_target0": 0.562,
                    "mean_target1": 0.637,
                    "min_bidirectional_recordings": 1,
                    "max_bidirectional_recordings": 3,
                }
            ],
        },
    )

    assert "Neutral-Prior Low-Contrast Choice Family Gate" in markdown
    assert "Neutral-Prior Low-Contrast Choice Projected Manifest Gate" in markdown
    assert "Neutral-Prior Low-Contrast Choice Seed Sensitivity" in markdown
    assert "do not train from the neutral-prior low-contrast choice row" in markdown


def test_render_markdown_includes_signed_wheel_direction_veto() -> None:
    gate_payload = {
        "summary": {
            "n_rows": 80,
            "n_candidates": 0,
            "n_positive_centered_delta": 34,
            "max_bidirectional_recordings": 2,
            "max_bidirectional_recording_fraction": 0.5,
            "decision": "no_signed_wheel_direction_family_candidate",
            "target_balances": {
                "signed_wheel_direction": {
                    "n_trials": 19287,
                    "eligible_recordings": 31,
                    "n_recordings": 31,
                }
            },
            "top_rows": [
                {
                    "target_mode": "signed_wheel_direction",
                    "family": "fiber_tracts",
                    "holdout": "CSH_ZAD_019",
                    "decision": "reject: target1",
                    "centered_delta_vs_shuffle": 0.198,
                    "centered_delta_vs_total": 0.186,
                    "target0_improved_vs_shuffle": 0.628,
                    "target1_improved_vs_shuffle": 0.533,
                    "n_bidirectional_recordings": 2,
                    "n_recordings": 4,
                }
            ],
        }
    }

    markdown = render_markdown(
        [],
        [],
        signed_wheel_direction_family_gate=gate_payload,
        signed_wheel_direction_projected_gate=gate_payload,
    )

    assert "Signed Wheel-Direction Family Gate" in markdown
    assert "Signed Wheel-Direction Projected Manifest Gate" in markdown
    assert "this motor target is closed" in markdown


def test_render_markdown_includes_lateralized_family_veto() -> None:
    gate_payload = {
        "summary": {
            "n_rows": 240,
            "n_candidates": 0,
            "n_positive_centered_delta": 127,
            "max_bidirectional_recordings": 2,
            "max_bidirectional_recording_fraction": 0.5,
            "decision": "no_lateralized_family_target_candidate",
            "top_rows": [
                {
                    "target_mode": "choice",
                    "family": "broad_named_anatomy",
                    "holdout": "SWC_043",
                    "decision": "reject: total baseline",
                    "centered_delta_vs_shuffle": 0.008,
                    "centered_delta_vs_total": -0.149,
                    "target0_improved_vs_shuffle": 0.536,
                    "target1_improved_vs_shuffle": 0.610,
                    "n_bidirectional_recordings": 2,
                    "n_recordings": 4,
                    "left_centered_auc": 0.423,
                    "right_centered_auc": 0.604,
                }
            ],
        }
    }

    markdown = render_markdown(
        [],
        [],
        lateralized_family_target_gate=gate_payload,
        lateralized_family_target_projected_gate=gate_payload,
    )

    assert "Lateralized Family Target Gate" in markdown
    assert "Lateralized Family Projected Manifest Gate" in markdown
    assert "hemisphere-split family counts" in markdown


def test_render_markdown_includes_correct_low_contrast_choice_veto() -> None:
    gate_payload = {
        "summary": {
            "n_rows": 96,
            "n_candidates": 0,
            "n_positive_centered_delta": 52,
            "max_bidirectional_recording_fraction": 1 / 3,
            "decision": "no_correct_low_contrast_choice_family_candidate",
            "target_balances": {
                "correct_low_contrast_choice_le_0.125": {
                    "n_trials": 8287,
                    "eligible_recordings": 31,
                    "n_recordings": 31,
                }
            },
            "top_rows": [
                {
                    "target_mode": "correct_low_contrast_choice_le_0.125",
                    "family": "fiber_tracts",
                    "holdout": "ZFM-01577",
                    "decision": "reject: target1",
                    "centered_delta_vs_shuffle": 0.018,
                    "centered_delta_vs_total": 0.095,
                    "target0_improved_vs_shuffle": 0.657,
                    "target1_improved_vs_shuffle": 0.426,
                    "n_bidirectional_recordings": 1,
                    "n_recordings": 3,
                }
            ],
        }
    }

    markdown = render_markdown(
        [],
        [],
        correct_low_contrast_choice_family_gate=gate_payload,
        correct_low_contrast_choice_projected_gate=gate_payload,
    )

    assert "Correct Low-Contrast Choice Family Gate" in markdown
    assert "Correct Low-Contrast Choice Projected Manifest Gate" in markdown
    assert "do not train from the correct-only low-contrast target" in markdown


def test_render_markdown_includes_prior_aligned_choice_veto() -> None:
    gate_payload = {
        "summary": {
            "n_rows": 128,
            "n_candidates": 0,
            "n_positive_centered_delta": 56,
            "max_bidirectional_recording_fraction": 0.25,
            "decision": "no_prior_aligned_choice_family_candidate",
            "target_balances": {
                "prior_aligned_choice_le_0.125": {
                    "n_trials": 9834,
                    "eligible_recordings": 31,
                    "n_recordings": 31,
                }
            },
            "top_rows": [
                {
                    "target_mode": "prior_aligned_choice_le_0.125",
                    "family": "hippocampal_formation",
                    "holdout": "CSH_ZAD_019",
                    "decision": "reject: total baseline",
                    "centered_delta_vs_shuffle": 0.044,
                    "centered_delta_vs_total": -0.052,
                    "target0_improved_vs_shuffle": 0.607,
                    "target1_improved_vs_shuffle": 0.445,
                    "n_bidirectional_recordings": 1,
                    "n_recordings": 4,
                }
            ],
        }
    }

    markdown = render_markdown(
        [],
        [],
        prior_aligned_choice_family_gate=gate_payload,
        prior_aligned_choice_projected_gate=gate_payload,
    )

    assert "Prior-Aligned Choice Family Gate" in markdown
    assert "Prior-Aligned Choice Projected Manifest Gate" in markdown
    assert "do not train from prior-aligned choice" in markdown


def test_local_probe_matrix_rejects_failed_target_class(tmp_path: Path) -> None:
    gate_path = tmp_path / "gate.json"
    mismatch_path = tmp_path / "mismatch.json"
    gate_path.write_text(json.dumps({
        "pass": False,
        "metrics": {
            "centered_auc_delta_vs_shuffle": -0.005,
            "paired_true_vs_shuffle": 0.494,
            "paired_specificity_gap": 0.010,
            "target0_true_class_improved": 0.556,
            "target1_true_class_improved": 0.419,
            "recordings_positive": 2,
            "n_recordings": 4,
        },
    }))
    mismatch_path.write_text(json.dumps({
        "decision": "paired_metric_not_recording_rank_stable",
        "summary": {"true_minus_shuffle_auc": -0.009},
    }))

    row = read_local_probe_result("probe", gate_path, mismatch_path)
    markdown = render_markdown([], [], local_probes=[row])

    assert row is not None
    assert local_probe_outcome(row) == "reject: centered AUC, target1, recording support, mismatch"
    assert "Local Probe Matrix" in markdown
    assert "paired_metric_not_recording_rank_stable" in markdown


def test_read_cache_audit_parses_missing_without_present(tmp_path: Path) -> None:
    path = tmp_path / "cache.md"
    path.write_text("\n".join([
        "# BrainSet S3 Cache Audit",
        "",
        "Present: 1/3 (33.3%)",
        "",
        "## Missing",
        "",
        "| filename |",
        "|---|",
        "| `missing-a.h5` |",
        "| `missing-b.h5` |",
        "",
        "## Shard Build Plan",
        "",
        "| shard | recordings | present | missing | build command |",
        "|---:|---:|---:|---:|---|",
        "| 0 | 2 | 1 | 1 | `build 0` |",
        "",
        "## Present",
        "",
        "| filename |",
        "|---|",
        "| `present.h5` |",
    ]))

    audit = read_cache_audit(path)

    assert audit is not None
    assert audit["present"] == 1
    assert audit["total"] == 3
    assert audit["missing_count"] == 2
    assert audit["missing_files"] == ["missing-a.h5", "missing-b.h5"]
    assert audit["shards_with_missing"] == [{"shard": 0, "recordings": 2, "present": 1, "missing": 1}]
