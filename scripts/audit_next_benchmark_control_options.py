"""Rank remaining benchmark/control options after local negative audits."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


ARTIFACTS = {
    "shared_family": "docs/shared_family_target_control_gate.json",
    "shared_broad_repair": "docs/shared_broad_anatomy_repair_sweep.json",
    "iterative_manifest": "docs/shared_family_iterative_manifest_gate.json",
    "symmetric_strict": "docs/symmetric_strict_failure_modes.json",
    "symmetric_threshold": "docs/symmetric_threshold_sensitivity_audit.json",
    "recording_replication": "docs/model_free_recording_replication_audit.json",
    "derived_target_family": "docs/derived_target_family_gate.json",
    "contextual_target_family": "docs/contextual_target_family_gate.json",
    "family_alt_prior": "docs/model_free_family_bidirectional_gate_prior_side_recording_centered.json",
    "family_alt_feedback": "docs/model_free_family_bidirectional_gate_feedback_recording_centered.json",
    "source_target_families": "docs/model_free_source_target_pair_gate_families_recording_centered.json",
}


def read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text())


def summary_value(payload: dict | None, key: str, default=None):
    if payload is None:
        return default
    return payload.get("summary", {}).get(key, default)


def branch(
    *,
    name: str,
    status: str,
    priority: int,
    evidence: list[str],
    next_action: str,
    gpu_trigger: str,
) -> dict:
    return {
        "name": name,
        "status": status,
        "priority": priority,
        "evidence": evidence,
        "next_action": next_action,
        "gpu_trigger": gpu_trigger,
    }


def build_report() -> dict:
    artifacts = {name: read_json(REPO_ROOT / rel_path) for name, rel_path in ARTIFACTS.items()}
    shared_family = artifacts["shared_family"]
    shared_broad = artifacts["shared_broad_repair"]
    iterative = artifacts["iterative_manifest"]
    strict = artifacts["symmetric_strict"]
    threshold = artifacts["symmetric_threshold"]
    replication = artifacts["recording_replication"]
    derived = artifacts["derived_target_family"]
    contextual = artifacts["contextual_target_family"]
    default_candidate_setting = summary_value(threshold, "strongest_default_target_candidate_setting", {}) or {}
    default_candidate_bidir = default_candidate_setting.get("min_bidirectional_recording_fraction")
    default_candidate_count = default_candidate_setting.get("n_candidates")

    branches = [
        branch(
            name="behavior-cache rebuild or external target preflight",
            status="recommended_next",
            priority=1,
            evidence=[
                "current cached trial targets and shared-family controls all fail strict same-recording bidirectionality",
                (
                    "direct derived cached-field target gate has "
                    f"{summary_value(derived, 'n_candidates', 'n/a')} candidates and max bidir "
                    f"{summary_value(derived, 'max_bidirectional_recording_fraction', 0.0):.3f}"
                ),
                (
                    "contextual trial-state target gate has "
                    f"{summary_value(contextual, 'n_candidates', 'n/a')} candidates and max bidir "
                    f"{summary_value(contextual, 'max_bidirectional_recording_fraction', 0.0):.3f}"
                ),
                (
                    "strict symmetric gate has "
                    f"{summary_value(strict, 'strict_candidates', 'n/a')} candidates and "
                    f"{summary_value(strict, 'one_recording_short_and_global_clear_rows', 'n/a')} "
                    "one-recording-short global-clear rows"
                ),
                (
                    "threshold sensitivity only finds default-target candidates when "
                    f"bidirectional support is relaxed to {default_candidate_bidir} "
                    f"({default_candidate_count} candidates)"
                ),
            ],
            next_action=(
                "Fetch or rebuild a richer behavior cache, or attach externally defined "
                "state labels, then define a prospectively balanced target/control and "
                "run the same model-free true-vs-shuffle, total-baseline, global target, "
                "and same-recording bidirectional gate before training."
            ),
            gpu_trigger=(
                "At least one local row must clear delta_vs_shuffle>=0, delta_vs_total>=0, "
                "target0>=0.55, target1>=0.55, and bidirectional_recording_fraction>=0.75."
            ),
        ),
        branch(
            name="new manifest with prospective bidirectional support",
            status="secondary_after_new_target",
            priority=2,
            evidence=[
                "current 28-recording manifest is feasible but not clean enough to pass the local gate",
                (
                    "strict iterative 8-recording manifest has "
                    f"{summary_value(iterative, 'n_candidates', 'n/a')} candidates and max bidir "
                    f"{summary_value(iterative, 'max_bidirectional_recording_fraction', 0.0):.3f}"
                ),
                "recording-subset replication selected zero stable validation rows",
            ],
            next_action=(
                "Only build or fetch more recordings after a target/control proposal defines "
                "which recordings should prospectively contain target0+target1 evidence."
            ),
            gpu_trigger="Same local gate as above, measured on the proposed manifest before training.",
        ),
        branch(
            name="direct cached-field derived targets",
            status="closed",
            priority=88,
            evidence=[
                (
                    "derived target family gate has "
                    f"{summary_value(derived, 'n_candidates', 'n/a')} candidates across "
                    f"{summary_value(derived, 'n_rows', 'n/a')} rows"
                ),
                "nearest response_latency row reaches 3/4 bidirectional recordings but fails true-vs-shuffle",
            ],
            next_action="Do not launch GPU training from contrast_strength, response_latency, or prior_engaged.",
            gpu_trigger="none",
        ),
        branch(
            name="contextual cached trial-state targets",
            status="closed",
            priority=89,
            evidence=[
                (
                    "contextual target family gate has "
                    f"{summary_value(contextual, 'n_candidates', 'n/a')} candidates across "
                    f"{summary_value(contextual, 'n_rows', 'n/a')} rows and max bidir "
                    f"{summary_value(contextual, 'max_bidirectional_recording_fraction', 0.0):.3f}"
                ),
                "post_error, prior_block_switch, and prior_block_late do not clear the local gate",
            ],
            next_action="Do not spend on contextual trial-sequence targets from the compact cache.",
            gpu_trigger="none",
        ),
        branch(
            name="more feature-mode or l2 sweeps on shared broad anatomy",
            status="closed",
            priority=90,
            evidence=[
                (
                    "shared broad-anatomy repair sweep has "
                    f"{summary_value(shared_broad, 'n_candidates', 'n/a')} candidates, max bidir "
                    f"{summary_value(shared_broad, 'max_bidirectional_recordings', 'n/a')}, and max min target margin "
                    f"{summary_value(shared_broad, 'max_min_target_margin', 0.0):+.3f}"
                ),
            ],
            next_action="Do not spend more local or GPU time on simple broad-anatomy feature/regularization repair.",
            gpu_trigger="none",
        ),
        branch(
            name="narrow existing manifest further",
            status="closed",
            priority=91,
            evidence=[
                (
                    "iterative manifest gate has "
                    f"{summary_value(iterative, 'n_candidates', 'n/a')} candidates and max bidir recordings "
                    f"{summary_value(iterative, 'max_bidirectional_recordings', 'n/a')}"
                ),
                "2-subject manifest is too narrow for the intended cross-animal demo",
            ],
            next_action="Do not keep shrinking the existing cache as the primary rescue path.",
            gpu_trigger="none",
        ),
        branch(
            name="recording-subset selection from current artifacts",
            status="closed",
            priority=92,
            evidence=[
                (
                    "recording replication audit selected "
                    f"{summary_value(replication, 'n_selected_by_discovery_rule', 'n/a')} rows and replicated "
                    f"{summary_value(replication, 'n_replicated_in_validation', 'n/a')}"
                ),
            ],
            next_action="Do not train on selected current recordings unless a new target/control first passes locally.",
            gpu_trigger="none",
        ),
        branch(
            name="current shared-family target/control grid",
            status="closed",
            priority=93,
            evidence=[
                (
                    "shared-family gate has "
                    f"{summary_value(shared_family, 'n_candidates', 'n/a')} candidates across "
                    f"{summary_value(shared_family, 'n_rows', 'n/a')} rows"
                ),
                "top rows are one-sided or fail baseline controls",
            ],
            next_action="Do not rerun the same target/family grid without a new target/control definition.",
            gpu_trigger="none",
        ),
        branch(
            name="alternative cached targets plus family aggregation",
            status="closed",
            priority=94,
            evidence=[
                (
                    "prior_side family gate candidates="
                    f"{summary_value(artifacts['family_alt_prior'], 'n_candidates', 'n/a')}; "
                    "feedback family gate candidates="
                    f"{summary_value(artifacts['family_alt_feedback'], 'n_candidates', 'n/a')}"
                ),
            ],
            next_action="Do not expect prior_side or feedback alone to rescue the signal under current controls.",
            gpu_trigger="none",
        ),
        branch(
            name="source-target pair narrowing",
            status="closed",
            priority=95,
            evidence=[
                (
                    "family source-target pair gate candidates="
                    f"{summary_value(artifacts['source_target_families'], 'n_candidates', 'n/a')}"
                ),
            ],
            next_action="Do not run a paid source-target pair sweep without a new local gate pass.",
            gpu_trigger="none",
        ),
    ]
    branches = sorted(branches, key=lambda row: row["priority"])
    return {
        "summary": {
            "recommended_next": branches[0]["name"],
            "closed_branches": sum(1 for row in branches if row["status"] == "closed"),
            "gpu_training_trigger": branches[0]["gpu_trigger"],
            "decision": "behavior_cache_or_external_target_required",
        },
        "artifacts": ARTIFACTS,
        "branches": branches,
    }


def render_markdown(report: dict) -> str:
    summary = report["summary"]
    lines = [
        "# Next Benchmark/Control Options Audit",
        "",
        (
            "Ranks remaining no-spend branches after the current local audits. This is "
            "the planning gate before any new RunPod training."
        ),
        "",
        f"- recommended next: `{summary['recommended_next']}`",
        f"- closed branches: `{summary['closed_branches']}`",
        f"- decision: `{summary['decision']}`",
        f"- GPU trigger: {summary['gpu_training_trigger']}",
        "",
        "| priority | branch | status | next action |",
        "|---:|---|---|---|",
    ]
    for row in report["branches"]:
        lines.append(f"| {row['priority']} | {row['name']} | `{row['status']}` | {row['next_action']} |")
    lines += [
        "",
        "## Evidence",
        "",
    ]
    for row in report["branches"]:
        lines.append(f"### {row['name']}")
        for item in row["evidence"]:
            lines.append(f"- {item}")
        lines.append(f"- GPU trigger: {row['gpu_trigger']}")
        lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-json", type=Path, default=REPO_ROOT / "docs/next_benchmark_control_options.json")
    parser.add_argument("--out-md", type=Path, default=REPO_ROOT / "docs/next_benchmark_control_options.md")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report()
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text(render_markdown(report))
    print(f"wrote {args.out_json}")
    print(f"wrote {args.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
