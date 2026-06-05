import numpy as np

from scripts.audit_direct_broad_family_trainable_readout import (
    fit_logistic_scores,
    summarize,
)


def row(decision: str, *, holdout: str = "CSHL045", seed: int = 0) -> dict:
    return {
        "target_mode": "post_error_response_extreme_25_75_le_1",
        "family": "broad_named_anatomy",
        "holdout": holdout,
        "train_seed": seed,
        "train_auc": 0.9,
        "eval_auc": 0.7,
        "eval_centered_auc": 0.7,
        "shuffle_centered_auc": 0.65,
        "total_centered_auc": 0.66,
        "centered_delta_vs_shuffle": 0.05,
        "centered_delta_vs_total": 0.04,
        "paired_improved_vs_shuffle": 0.7,
        "target0_improved_vs_shuffle": 0.7,
        "target1_improved_vs_shuffle": 0.8,
        "paired_improved_vs_total": 0.6,
        "target0_improved_vs_total": 0.6,
        "target1_improved_vs_total": 0.6,
        "recordings_positive_vs_shuffle": 3,
        "n_recordings": 4,
        "n_bidirectional_recordings": 3,
        "bidirectional_recording_fraction": 0.75,
        "recording_target_rows": [],
        "decision": decision,
    }


def test_logistic_readout_learns_separable_direction() -> None:
    train_x = np.array([[-2.0], [-1.0], [1.0], [2.0]])
    train_y = np.array([0, 0, 1, 1])
    eval_x = np.array([[-1.5], [1.5]])

    _train_scores, eval_scores = fit_logistic_scores(
        train_x,
        train_y,
        eval_x,
        seed=0,
        steps=500,
        lr=0.2,
        l2=0.0,
    )

    assert eval_scores[1] > eval_scores[0]


def test_summarize_requires_every_train_seed_to_pass_for_robust_case() -> None:
    summary = summarize([row("candidate", seed=0), row("reject: shuffle", seed=1)])

    assert summary["decision"] == "no_direct_broad_family_trainable_candidate"
    assert summary["n_robust_cases"] == 0
    assert summary["case_summaries"][0]["n_candidate_seeds"] == 1
    assert summary["case_summaries"][0]["n_train_seeds"] == 2


def test_summarize_marks_robust_trainable_candidate() -> None:
    summary = summarize([row("candidate", seed=0), row("candidate", seed=1)])

    assert summary["decision"] == "direct_broad_family_trainable_candidate"
    assert summary["n_robust_cases"] == 1
    assert not summary["paid_gpu_trigger"]
