from scripts.package_model_free_demo import build_package


def test_model_free_package_keeps_trained_claim_unsupported() -> None:
    package = build_package(
        readiness={
            "summary": {
                "model_free_demo_ready": True,
                "trained_model_demo_ready": False,
            },
            "local_model_free_rows": [
                {
                    "holdout": "CSHL045",
                    "target_mode": "post_error_response_extreme_25_75_le_1",
                    "family": "broad_named_anatomy",
                    "candidate_seeds": 5,
                    "n_seeds": 5,
                    "mean_delta_vs_shuffle": 0.05,
                    "mean_delta_vs_total": 0.03,
                    "mean_target0": 0.7,
                    "mean_target1": 0.8,
                    "min_bidirectional_recordings": 3,
                    "max_bidirectional_recordings": 3,
                }
            ],
            "negative_training_evidence": {"a100_decision": "negative_training_pilot", "a100_true_positive": "0/2"},
        },
        aligned_readout={"summary": {"decision": "no_training_aligned_true_region_advantage"}},
        failure_audit={
            "summary": {
                "decision": "local_to_training_readout_mismatch",
                "blockers": ["trained_true_region_lost_to_shared"],
            }
        },
    )

    assert package["summary"]["model_free_demo_ready"]
    assert not package["summary"]["trained_model_demo_ready"]
    assert not package["summary"]["paid_gpu_trigger"]
    assert "model-free" in package["summary"]["supported_claim"]
    assert "not yet supported" in package["summary"]["unsupported_claim"]
