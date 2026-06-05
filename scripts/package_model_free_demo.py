"""Package the current model-free anatomical transfer demo claim.

This produces a short, reproducible demo artifact from the current readiness
audits. It intentionally distinguishes what is supported now from the stronger
trained anatomical foundation-model claim that remains unresolved.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def build_package(readiness: dict, aligned_readout: dict, failure_audit: dict) -> dict:
    readiness_summary = readiness["summary"]
    aligned_summary = aligned_readout["summary"]
    failure_summary = failure_audit["summary"]
    supported_claim = (
        "A narrow model-free cross-animal anatomical readout exists for post-error "
        "response-latency extremes using a fixed broad_named_anatomy aggregate."
    )
    unsupported_claim = (
        "A trained neural foundation-model anatomical transfer signal is not yet "
        "supported: the A100 pilot and cloud-aligned local readout were negative."
    )
    rows = readiness["local_model_free_rows"]
    return {
        "summary": {
            "decision": "package_model_free_demo",
            "supported_claim": supported_claim,
            "unsupported_claim": unsupported_claim,
            "model_free_demo_ready": readiness_summary["model_free_demo_ready"],
            "trained_model_demo_ready": readiness_summary["trained_model_demo_ready"],
            "paid_gpu_trigger": False,
            "next_action": (
                "Use this as a narrow reproducible model-free demo, with the "
                "trainable fixed-feature bridge plus local/cloud train.py fixed-family "
                "arms as intermediate checks. Treat the remaining gap as the stronger "
                "transformer/foundation-model mechanism."
            ),
        },
        "evidence_rows": rows,
        "negative_controls": {
            "a100_training": readiness["negative_training_evidence"],
            "cloud_aligned_readout_decision": aligned_summary["decision"],
            "failure_audit_decision": failure_summary["decision"],
            "failure_blockers": failure_summary["blockers"],
        },
        "reproduction_commands": [
            "uv run python scripts/audit_composite_behavior_target_family_gate.py --manifest manifests/ibl_bwm_local_cached_external_support80_projected_hdf5.json --out-json docs/composite_behavior_response_extreme_family_gate_projected_hdf5.json --out-md docs/composite_behavior_response_extreme_family_gate_projected_hdf5.md --target post_error_response_extreme_25_75_le_1 post_error_response_extreme_33_67_le_1",
            "uv run python scripts/audit_composite_behavior_response_extreme_seed_sensitivity.py",
            "uv run python scripts/audit_response_extreme_training_aligned_readout.py",
            "uv run python scripts/audit_direct_broad_family_demo_readiness.py",
            "uv run python scripts/audit_direct_broad_family_trainable_readout.py",
            "uv run python scripts/summarize_fixed_broad_family_train_arm_panel.py",
            "uv run python scripts/audit_fixed_broad_family_train_arm_prediction_gate.py",
            "uv run python scripts/package_model_free_demo.py",
        ],
        "demo_boundaries": [
            "This is a model-free ridge/count readout demo, not a trained transformer demo.",
            "The positive feature is the fixed broad_named_anatomy aggregate, not the full shared parent-region feature vector.",
            "The bounded cloud fixed-feature prediction gate has one strict candidate holdout, NR_0019; CSHL045 is aggregate-positive but fails recording-local bidirectionality.",
            "The local and cloud train.py fixed-family arms are positive, but this still does not establish a transformer/foundation-model anatomical mechanism.",
        ],
    }


def render_markdown(package: dict) -> str:
    summary = package["summary"]
    lines = [
        "# Model-Free Anatomical Transfer Demo Package",
        "",
        "## Claim",
        "",
        f"Supported: {summary['supported_claim']}",
        "",
        f"Not supported yet: {summary['unsupported_claim']}",
        "",
        "## Status",
        "",
        f"- decision: `{summary['decision']}`",
        f"- model-free demo ready: `{summary['model_free_demo_ready']}`",
        f"- trained-model demo ready: `{summary['trained_model_demo_ready']}`",
        f"- paid GPU trigger: `{summary['paid_gpu_trigger']}`",
        f"- next action: {summary['next_action']}",
        "",
        "## Positive Evidence",
        "",
        "| holdout | target | family | candidate seeds | delta shuffle | delta total | targets | bidir range |",
        "|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in package["evidence_rows"]:
        lines.append(
            f"| {row['holdout']} | {row['target_mode']} | {row['family']} | "
            f"{row['candidate_seeds']}/{row['n_seeds']} | "
            f"{row['mean_delta_vs_shuffle']:+.4f} | {row['mean_delta_vs_total']:+.4f} | "
            f"{row['mean_target0']:.3f}/{row['mean_target1']:.3f} | "
            f"{row['min_bidirectional_recordings']}-{row['max_bidirectional_recordings']} |"
        )
    negative = package["negative_controls"]
    lines += [
        "",
        "## Negative Controls",
        "",
        f"- A100 training decision: `{negative['a100_training']['a100_decision']}`; true-positive cases `{negative['a100_training']['a100_true_positive']}`",
        f"- cloud-aligned local readout: `{negative['cloud_aligned_readout_decision']}`",
        f"- failure audit: `{negative['failure_audit_decision']}`",
        f"- blockers: `{', '.join(negative['failure_blockers'])}`",
        "",
        "## Reproduce",
        "",
        "```bash",
        *package["reproduction_commands"],
        "```",
        "",
        "## Boundaries",
        "",
    ]
    lines.extend(f"- {item}" for item in package["demo_boundaries"])
    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--readiness",
        type=Path,
        default=REPO_ROOT / "docs/direct_broad_family_demo_readiness.json",
    )
    parser.add_argument(
        "--aligned-readout",
        type=Path,
        default=REPO_ROOT / "docs/response_extreme_training_aligned_readout.json",
    )
    parser.add_argument(
        "--failure-audit",
        type=Path,
        default=REPO_ROOT / "docs/response_extreme_training_failure_audit.json",
    )
    parser.add_argument(
        "--out-json",
        type=Path,
        default=REPO_ROOT / "docs/model_free_anatomical_transfer_demo_package.json",
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=REPO_ROOT / "docs/model_free_anatomical_transfer_demo_package.md",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    package = build_package(
        load_json(args.readiness),
        load_json(args.aligned_readout),
        load_json(args.failure_audit),
    )
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(package, indent=2, sort_keys=True) + "\n")
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text(render_markdown(package))
    print(f"wrote {args.out_json}")
    print(f"wrote {args.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
