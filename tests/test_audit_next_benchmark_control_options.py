from scripts.audit_next_benchmark_control_options import (
    build_report,
    projected_feature_mode_summary,
    reaction_feature_mode_summary,
    render_markdown,
)


def test_build_report_tracks_current_no_spend_state() -> None:
    report = build_report()

    assert report["summary"]["decision"] in {
        "behavior_cache_rebuild_required",
        "wheel_target_audit_required",
        "local_training_trigger_available",
        "no_local_training_trigger",
    }
    assert report["branches"][0]["status"] == "recommended_next"
    assert report["summary"]["closed_branches"] >= 5


def test_gpu_trigger_remains_strict_local_gate() -> None:
    report = build_report()
    trigger = report["summary"]["gpu_training_trigger"]

    assert "target0>=0.55" in trigger
    assert "target1>=0.55" in trigger
    assert "bidirectional_recording_fraction>=0.75" in trigger


def test_projected_panel_ready_recommends_model_free_gate() -> None:
    report = build_report()
    if report["branches"][0]["name"] != "new manifest with prospective bidirectional support":
        return

    next_action = report["branches"][0]["next_action"]

    assert "projected support80" in next_action
    assert "model-free" in next_action or "Do not launch GPU training" in next_action


def test_projected_feature_mode_summary_aggregates_artifacts() -> None:
    payload = {"summary": {"n_rows": 10, "n_candidates": 1, "max_bidirectional_recording_fraction": 0.25}}
    summary = projected_feature_mode_summary({
        "projected_support80_all_families_recording_centered": payload,
        "projected_support80_all_families_fractions": None,
        "projected_support80_all_families_counts": {
            "summary": {"n_rows": 5, "n_candidates": 0, "max_bidirectional_recording_fraction": 0.5}
        },
        "projected_support80_all_families_unit_residuals": None,
    })

    assert summary["n_modes"] == 2
    assert summary["n_rows"] == 15
    assert summary["n_candidates"] == 1
    assert summary["max_bidirectional_recording_fraction"] == 0.5


def test_reaction_feature_mode_summary_aggregates_artifacts() -> None:
    payload = {"summary": {"n_rows": 84, "n_candidates": 0, "max_bidirectional_recording_fraction": 0.75}}
    summary = reaction_feature_mode_summary({
        "reaction_dynamics_target_family_recording_centered": payload,
        "reaction_dynamics_target_family_counts": {
            "summary": {"n_rows": 84, "n_candidates": 0, "max_bidirectional_recording_fraction": 0.25}
        },
        "reaction_dynamics_target_family_fractions": None,
        "reaction_dynamics_target_family_unit_residuals": None,
    })

    assert summary["n_modes"] == 2
    assert summary["n_rows"] == 168
    assert summary["n_candidates"] == 0
    assert summary["max_bidirectional_recording_fraction"] == 0.75


def test_render_markdown_lists_closed_branches() -> None:
    markdown = render_markdown(build_report())

    assert "# Next Benchmark/Control Options Audit" in markdown
    assert "behavior-inclusive cache rebuild" in markdown
    assert "wheel-derived target family gate" in markdown
    assert "reaction-dynamics wheel targets" in markdown
    assert "cell-type prior target/control gate" in markdown
    assert "waveform target/control gate" in markdown
    assert "local gate meta-failure synthesis" in markdown
    assert "recording bidirectionality prospectus" in markdown
    assert "prospect-lead derived target validation" in markdown
    assert "feature-mode validation" in markdown
    assert "subject-stability audit" in markdown
    assert "subject-stable local gate prospectus" in markdown
    assert "wheel in" in markdown
    assert "contextual cached trial-state targets" in markdown
    assert "narrow existing manifest further" in markdown
    assert "`closed`" in markdown
