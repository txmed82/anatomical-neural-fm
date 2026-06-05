#!/usr/bin/env bash
set -euo pipefail

OUT_ROOT="${OUT_ROOT:-runs/subject_conditioned_audit_a100}"
TARGET_MODE="${TARGET_MODE:-stimulus_side}"
MANIFEST_PATH="${MANIFEST_PATH:-manifests/ibl_bwm_phase4.json}"
RESULT_DOC="${RESULT_DOC:-docs/subject_conditioned_signal_audit.md}"

mkdir -p "$OUT_ROOT"

uv run python scripts/audit_subject_signal.py \
  --manifest "$MANIFEST_PATH" \
  --results docs/lso_promising_results.md \
  --data-dir data/brainsets/ibl_bwm \
  --target-mode "$TARGET_MODE" \
  --out "$OUT_ROOT/summary.md"

cp "$OUT_ROOT/summary.md" "$RESULT_DOC"
