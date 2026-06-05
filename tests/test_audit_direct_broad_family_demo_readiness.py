from scripts.audit_direct_broad_family_demo_readiness import summarize


def robust_seed_payload() -> dict:
    return {
        "robust_response_extreme_seed_candidates": [
            {
                "family": "broad_named_anatomy",
                "holdout": "CSHL045",
                "target_mode": "post_error_response_extreme_25_75_le_1",
                "n_candidate_seeds": 5,
                "n_seeds": 5,
                "min_bidirectional_recordings": 3,
                "max_bidirectional_recordings": 3,
                "mean_centered_delta_vs_shuffle": 0.05,
                "mean_centered_delta_vs_total": 0.03,
                "mean_target0": 0.7,
                "mean_target1": 0.8,
            }
        ]
    }


def test_demo_readiness_is_model_free_only_after_negative_training() -> None:
    summary = summarize(
        seed_sensitivity=robust_seed_payload(),
        a100_result={"summary": {"decision": "negative_training_pilot", "n_true_positive": 0}},
        training_aligned={"summary": {"decision": "no_training_aligned_true_region_advantage"}},
    )

    assert summary["decision"] == "model_free_demo_only"
    assert summary["model_free_demo_ready"]
    assert not summary["trained_model_demo_ready"]


def test_demo_readiness_requires_strict_local_seed_support() -> None:
    payload = robust_seed_payload()
    payload["robust_response_extreme_seed_candidates"][0]["n_candidate_seeds"] = 4

    summary = summarize(
        seed_sensitivity=payload,
        a100_result={"summary": {"decision": "negative_training_pilot", "n_true_positive": 0}},
        training_aligned={"summary": {"decision": "no_training_aligned_true_region_advantage"}},
    )

    assert summary["decision"] == "no_direct_broad_family_demo_candidate"
    assert not summary["model_free_demo_ready"]
