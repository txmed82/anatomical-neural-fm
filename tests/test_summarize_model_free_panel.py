import json

from scripts.summarize_model_free_panel import load_rows, render_markdown, summarize


def _write_audit(path, *, holdout: str, decision: str, delta: float, target1: float) -> None:
    path.write_text(json.dumps({
        "holdout": [holdout],
        "n_train_trials": 10,
        "n_eval_trials": 4,
        "n_regions": 3,
        "summary": {
            "decision": decision,
            "metrics": {
                "region_true": {"eval_centered_auc": 0.5 + delta},
                "region_shuffle": {"eval_centered_auc": 0.5},
            },
            "deltas": {"true_minus_shuffle_centered_auc": delta},
            "paired_true_vs_shuffle": {
                "improved_fraction": 0.51,
                "target0_improved_fraction": 0.60,
                "target1_improved_fraction": target1,
            },
            "recordings_positive_true_minus_shuffle": 2,
            "n_recordings": 4,
            "recording_support_fraction": 0.5,
        },
    }))


def test_summarize_panel_counts_candidates_and_positive_deltas(tmp_path):
    _write_audit(
        tmp_path / "A_stimulus_side.json",
        holdout="A",
        decision="weak_model_free_true_region_advantage",
        delta=0.02,
        target1=0.4,
    )
    _write_audit(
        tmp_path / "B_stimulus_side.json",
        holdout="B",
        decision="model_free_anatomy_candidate",
        delta=0.03,
        target1=0.7,
    )

    rows = load_rows(tmp_path, "*_stimulus_side.json")
    summary = summarize(rows)
    markdown = render_markdown({"summary": summary, "rows": rows})

    assert summary["n_holdouts"] == 2
    assert summary["n_candidates"] == 1
    assert summary["candidate_holdouts"] == ["B"]
    assert summary["n_positive_delta_holdouts"] == 2
    assert summary["decision"] == "model_free_panel_candidate"
    assert "| B | model_free_anatomy_candidate |" in markdown
