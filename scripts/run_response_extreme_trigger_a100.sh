#!/bin/bash
# Bounded A100 pilot for the first local response-extreme training trigger.
#
# Runs only the two seed-stable local candidates:
# - CSHL045: post-error 25/75 response-latency extremes
# - NR_0019: post-error 33/67 response-latency extremes
set -euo pipefail

cd "$(dirname "$0")/.."

OUT_ROOT="${OUT_ROOT:-runs/response_extreme_trigger_a100}"
SEEDS="${SEEDS:-0}"
MAX_STEPS="${MAX_STEPS:-300}"
EVAL_BATCHES="${EVAL_BATCHES:-20}"
BATCH_SIZE="${BATCH_SIZE:-16}"
BATCH_SAMPLING="${BATCH_SAMPLING:-uniform}"
LOSS_MODE="${LOSS_MODE:-bce}"
BEST_METRIC="${BEST_METRIC:-eval_loss}"
REGION_FILTER="${REGION_FILTER:-shared_regions}"
REGION_GRANULARITY="${REGION_GRANULARITY:-parent}"
REGION_SHUFFLE_CONTROL="${REGION_SHUFFLE_CONTROL:-shuffle}"
SAVE_DIAGNOSTICS="${SAVE_DIAGNOSTICS:-0}"
FULL_EVAL_ON_BEST="${FULL_EVAL_ON_BEST:-0}"
EVAL_PREDICTION_MAX_TRIALS="${EVAL_PREDICTION_MAX_TRIALS:-0}"

mkdir -p "$OUT_ROOT"

run_case() {
  local holdout="$1"
  local target="$2"
  local case_name="$3"
  local case_out="$OUT_ROOT/$case_name"

  echo ""
  echo "=== response-extreme trigger case=$case_name holdout=$holdout target=$target ==="
  SUBJECTS="$holdout" \
  TARGET_MODE="$target" \
  OUT_ROOT="$case_out" \
  SEEDS="$SEEDS" \
  MAX_STEPS="$MAX_STEPS" \
  EVAL_BATCHES="$EVAL_BATCHES" \
  BATCH_SIZE="$BATCH_SIZE" \
  BATCH_SAMPLING="$BATCH_SAMPLING" \
  LOSS_MODE="$LOSS_MODE" \
  BEST_METRIC="$BEST_METRIC" \
  REGION_FILTER="$REGION_FILTER" \
  REGION_GRANULARITY="$REGION_GRANULARITY" \
  REGION_SHUFFLE_CONTROL="$REGION_SHUFFLE_CONTROL" \
  SAVE_DIAGNOSTICS="$SAVE_DIAGNOSTICS" \
  FULL_EVAL_ON_BEST="$FULL_EVAL_ON_BEST" \
  EVAL_PREDICTION_MAX_TRIALS="$EVAL_PREDICTION_MAX_TRIALS" \
  bash scripts/run_lso_two_holdout_shared_parent_shuffle_a100.sh
}

run_case "CSHL045" "post_error_response_extreme_25_75_le_1" "cshl045_post_error_extreme_25_75"
run_case "NR_0019" "post_error_response_extreme_33_67_le_1" "nr0019_post_error_extreme_33_67"

cat > "$OUT_ROOT/summary.md" <<EOF
# Response-Extreme Trigger A100 Pilot

Cases:

- CSHL045, target \`post_error_response_extreme_25_75_le_1\`
- NR_0019, target \`post_error_response_extreme_33_67_le_1\`

Common settings:

- seeds: \`$SEEDS\`
- max steps: \`$MAX_STEPS\`
- eval batches: \`$EVAL_BATCHES\`
- region filter: \`$REGION_FILTER\`
- region granularity: \`$REGION_GRANULARITY\`
- shuffle control: \`$REGION_SHUFFLE_CONTROL\`

## CSHL045 25/75

EOF
cat "$OUT_ROOT/cshl045_post_error_extreme_25_75/summary.md" >> "$OUT_ROOT/summary.md" 2>/dev/null || true
cat >> "$OUT_ROOT/summary.md" <<EOF

## NR_0019 33/67

EOF
cat "$OUT_ROOT/nr0019_post_error_extreme_33_67/summary.md" >> "$OUT_ROOT/summary.md" 2>/dev/null || true

echo ""
echo "Wrote:"
echo "  $OUT_ROOT/summary.md"
