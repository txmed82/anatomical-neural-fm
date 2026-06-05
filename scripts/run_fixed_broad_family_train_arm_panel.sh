#!/bin/bash
# Local/cloud panel for the fixed broad-family count train.py arm.
set -euo pipefail

cd "$(dirname "$0")/.."

OUT_ROOT="${OUT_ROOT:-runs/fixed_broad_family_train_arm_panel}"
MANIFEST_PATH="${MANIFEST_PATH:-manifests/ibl_bwm_local_cached_external_support80_projected_hdf5.json}"
SEEDS="${SEEDS:-0}"
MAX_STEPS="${MAX_STEPS:-1000}"
LR="${LR:-0.1}"
WEIGHT_DECAY="${WEIGHT_DECAY:-1.0}"
BEST_METRIC="${BEST_METRIC:-full_eval_centered_auc}"
DEVICE="${DEVICE:-auto}"
REGION_GRANULARITY="${REGION_GRANULARITY:-parent}"
FIXED_FAMILY_FEATURE_MODE="${FIXED_FAMILY_FEATURE_MODE:-recording_centered}"

mkdir -p "$OUT_ROOT"

run_arm() {
  local holdout="$1"
  local target="$2"
  local control="$3"
  local seed="$4"
  local out="$OUT_ROOT/holdout_${holdout}/fixed_broad_family_count_${control}_seed${seed}"

  if [ -f "$out/log.jsonl" ] && grep -q '"event": "done"' "$out/log.jsonl" 2>/dev/null; then
    echo "skip (already done): $out"
    return
  fi

  echo "=== fixed broad-family holdout=$holdout target=$target control=$control seed=$seed ==="
  uv run python -u scripts/train.py \
    --manifest "$MANIFEST_PATH" \
    --holdout "$holdout" \
    --target-mode "$target" \
    --region-granularity "$REGION_GRANULARITY" \
    --arm fixed_broad_family_count \
    --fixed-family broad_named_anatomy \
    --fixed-family-feature-mode "$FIXED_FAMILY_FEATURE_MODE" \
    --region-label-control "$control" \
    --device "$DEVICE" \
    --seed "$seed" \
    --max-steps "$MAX_STEPS" \
    --lr "$LR" \
    --weight-decay "$WEIGHT_DECAY" \
    --best-metric "$BEST_METRIC" \
    --out-dir "$out"
}

for seed in $SEEDS; do
  run_arm "CSHL045" "post_error_response_extreme_25_75_le_1" "none" "$seed"
  run_arm "CSHL045" "post_error_response_extreme_25_75_le_1" "within_recording_shuffle" "$seed"
  run_arm "NR_0019" "post_error_response_extreme_33_67_le_1" "none" "$seed"
  run_arm "NR_0019" "post_error_response_extreme_33_67_le_1" "within_recording_shuffle" "$seed"
done

uv run python scripts/summarize_fixed_broad_family_train_arm_panel.py \
  --root "$OUT_ROOT" \
  --out-json "$OUT_ROOT/summary.json" \
  --out-md "$OUT_ROOT/summary.md"

echo ""
echo "Wrote:"
echo "  $OUT_ROOT/summary.md"
