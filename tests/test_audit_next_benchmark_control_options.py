from scripts.audit_next_benchmark_control_options import build_report, render_markdown


def test_build_report_recommends_behavior_cache_preflight() -> None:
    report = build_report()

    assert report["summary"]["decision"] == "behavior_cache_or_external_target_required"
    assert report["summary"]["recommended_next"] == "behavior-cache rebuild or external target preflight"
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
    assert "behavior-cache rebuild or external target preflight" in markdown
    assert "contextual cached trial-state targets" in markdown
    assert "narrow existing manifest further" in markdown
    assert "`closed`" in markdown
