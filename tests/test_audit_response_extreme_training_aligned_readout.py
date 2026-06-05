from scripts.audit_response_extreme_training_aligned_readout import candidate_decision, report_decision


def summary(
    *,
    delta_shuffle: float,
    delta_total: float,
    target0: float,
    target1: float,
    recording_support: float,
) -> dict:
    return {
        "deltas": {
            "true_minus_shuffle_centered_auc": delta_shuffle,
            "true_minus_total_centered_auc": delta_total,
        },
        "paired_true_vs_shuffle": {
            "target0_improved_fraction": target0,
            "target1_improved_fraction": target1,
        },
        "recording_support_fraction": recording_support,
    }


def test_candidate_decision_requires_all_strict_gates() -> None:
    passing = summary(
        delta_shuffle=0.02,
        delta_total=0.03,
        target0=0.6,
        target1=0.7,
        recording_support=0.75,
    )
    assert candidate_decision(passing, min_centered_delta=0.01, min_target_improvement=0.55) == "candidate"

    weak_shuffle = summary(
        delta_shuffle=0.0,
        delta_total=0.03,
        target0=0.6,
        target1=0.7,
        recording_support=1.0,
    )
    assert candidate_decision(weak_shuffle, min_centered_delta=0.01, min_target_improvement=0.55) == "reject: shuffle"


def test_report_decision_only_reopens_gpu_trigger_for_candidates() -> None:
    cases = [
        {
            "feature_modes": [
                {
                    "summary": summary(
                        delta_shuffle=0.02,
                        delta_total=-0.01,
                        target0=0.7,
                        target1=0.8,
                        recording_support=1.0,
                    )
                    | {"decision": "reject: total baseline"}
                }
            ]
        }
    ]
    assert report_decision(cases) == "weak_training_aligned_true_region_advantage"

    cases[0]["feature_modes"][0]["summary"]["decision"] = "candidate"
    assert report_decision(cases) == "training_aligned_local_candidate"
