from scripts.audit_next_benchmark_control_options import build_report, render_markdown


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


def test_render_markdown_lists_closed_branches() -> None:
    markdown = render_markdown(build_report())

    assert "# Next Benchmark/Control Options Audit" in markdown
    assert "behavior-inclusive cache rebuild" in markdown
    assert "wheel-derived target family gate" in markdown
    assert "wheel in" in markdown
    assert "contextual cached trial-state targets" in markdown
    assert "narrow existing manifest further" in markdown
    assert "`closed`" in markdown
