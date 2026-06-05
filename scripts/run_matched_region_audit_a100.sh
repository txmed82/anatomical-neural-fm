#!/usr/bin/env bash
# Score the built 48-recording candidate manifest for region-family support.
#
# The RunPod launcher builds MANIFEST_PATH first. This wrapper performs no
# training; it only reruns the manifest planner against the built HDF5 cache.
set -euo pipefail

OUT_ROOT="${OUT_ROOT:-runs/matched_region_audit_a100}"
MANIFEST_PATH="${MANIFEST_PATH:-manifests/ibl_bwm_region_matched_candidates.json}"
REGION_GRANULARITY="${REGION_GRANULARITY:-parent}"
RESULT_DOC="${RESULT_DOC:-docs/matched_region_manifest_full_audit.md}"

mkdir -p "$OUT_ROOT"

uv run python scripts/plan_matched_region_manifest.py \
  --input-manifest "$MANIFEST_PATH" \
  --region-granularity "$REGION_GRANULARITY" \
  --data-dir data/brainsets/ibl_bwm \
  --out-manifest "$OUT_ROOT/manifest.json" \
  --out-report "$OUT_ROOT/summary.md"

cp "$OUT_ROOT/summary.md" "$RESULT_DOC"
