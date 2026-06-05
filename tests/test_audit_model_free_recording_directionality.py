from scripts.audit_model_free_recording_directionality import (
    DirectionalObservation,
    classify_target_direction,
    summarize_group,
)


def obs(classification: str, target0: float, target1: float) -> DirectionalObservation:
    return DirectionalObservation(
        report="r",
        context="c",
        target_subject="s",
        recording="rec",
        target0=target0,
        target1=target1,
        improved_fraction=0.5,
        mean_true_class_delta=0.0,
        n_trials=10,
        classification=classification,
    )


def test_classify_target_direction_uses_both_targets() -> None:
    assert classify_target_direction(0.60, 0.60, min_target_improvement=0.55) == "bidirectional"
    assert classify_target_direction(0.60, 0.40, min_target_improvement=0.55) == "target0_only"
    assert classify_target_direction(0.40, 0.60, min_target_improvement=0.55) == "target1_only"
    assert classify_target_direction(0.40, 0.40, min_target_improvement=0.55) == "neither"


def test_summarize_group_counts_one_sided_skew() -> None:
    summary = summarize_group([
        obs("bidirectional", 0.6, 0.6),
        obs("target1_only", 0.4, 0.7),
        obs("target1_only", 0.5, 0.8),
        obs("target0_only", 0.7, 0.4),
    ])

    assert summary["class_counts"]["bidirectional"] == 1
    assert summary["class_counts"]["target1_only"] == 2
    assert summary["one_sided_fraction"] == 0.75
    assert summary["target1_minus_target0_one_sided"] == 1
