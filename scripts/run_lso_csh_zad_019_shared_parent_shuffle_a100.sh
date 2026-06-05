#!/bin/bash
# Stricter CSH_ZAD_019 anatomy-control check.
#
# Repeats the true-region vs shuffled-region control while restricting spikes to
# regions shared by train/eval subjects and using Allen parent acronyms by
# default. This tests whether the CSH_ZAD_019 signal survives a more defensible
# cross-animal anatomical comparison.
set -euo pipefail

cd "$(dirname "$0")/.."

DEVICE="${DEVICE:-cuda}"
MAX_STEPS="${MAX_STEPS:-300}"
EVAL_BATCHES="${EVAL_BATCHES:-20}"
BATCH_SIZE="${BATCH_SIZE:-16}"
DIM="${DIM:-96}"
DEPTH="${DEPTH:-3}"
NUM_LATENTS="${NUM_LATENTS:-24}"
SEEDS="${SEEDS:-0 1 2}"
TARGET_MODE="${TARGET_MODE:-stimulus_side}"
REGION_FILTER="${REGION_FILTER:-shared_regions}"
REGION_GRANULARITY="${REGION_GRANULARITY:-parent}"
OUT_ROOT="${OUT_ROOT:-runs/lso_csh_zad_019_shared_parent_shuffle}"
MANIFEST="${MANIFEST:-}"
SAVE_DIAGNOSTICS="${SAVE_DIAGNOSTICS:-0}"
FULL_EVAL_ON_BEST="${FULL_EVAL_ON_BEST:-0}"
EVAL_PREDICTION_MAX_TRIALS="${EVAL_PREDICTION_MAX_TRIALS:-0}"

COMMON_ARGS=(
  --device "$DEVICE"
  --output-query-mode shared
  --batch-size "$BATCH_SIZE"
  --dim "$DIM" --depth "$DEPTH" --num-latents "$NUM_LATENTS"
  --max-steps "$MAX_STEPS"
  --eval-every 150 --eval-batches "$EVAL_BATCHES"
  --log-every 50 --warmup-steps 75
  --target-mode "$TARGET_MODE"
  --split-mode animal
  --holdout CSH_ZAD_019
  --region-filter "$REGION_FILTER"
  --region-granularity "$REGION_GRANULARITY"
)
if [ -n "$MANIFEST" ]; then
  COMMON_ARGS+=(--manifest "$MANIFEST")
fi
if [ "$SAVE_DIAGNOSTICS" = "1" ]; then
  COMMON_ARGS+=(--save-eval-predictions --save-region-embeddings)
  if [ "$EVAL_PREDICTION_MAX_TRIALS" != "0" ]; then
    COMMON_ARGS+=(--eval-prediction-max-trials "$EVAL_PREDICTION_MAX_TRIALS")
  fi
fi
if [ "$FULL_EVAL_ON_BEST" = "1" ]; then
  COMMON_ARGS+=(--full-eval-on-best)
fi

mkdir -p "$OUT_ROOT/holdout_CSH_ZAD_019"
echo "subjects: CSH_ZAD_019"
echo "arms: shared_baseline region_only region_shuffle"
echo "seeds: $SEEDS"
echo "region_filter: $REGION_FILTER"
echo "region_granularity: $REGION_GRANULARITY"
echo "manifest: ${MANIFEST:-<all local recordings>}"
echo "save_diagnostics: $SAVE_DIAGNOSTICS"
echo "full_eval_on_best: $FULL_EVAL_ON_BEST"

for seed in $SEEDS; do
  for arm in shared_baseline region_only region_shuffle; do
    out="$OUT_ROOT/holdout_CSH_ZAD_019/cloud_choice_${arm}_seed${seed}"
    if [ -f "$out/log.jsonl" ] && grep -q '"event": "done"' "$out/log.jsonl" 2>/dev/null; then
      echo "skip (already done): $out"
      continue
    fi
    rm -rf "$out"
    mkdir -p "$out"
    echo ""
    echo "=== holdout=CSH_ZAD_019 arm=$arm seed=$seed region_filter=$REGION_FILTER region_granularity=$REGION_GRANULARITY ==="
    if [ "$arm" = "region_shuffle" ]; then
      uv run python -u scripts/train.py \
        "${COMMON_ARGS[@]}" \
        --seed "$seed" \
        --arm region_only \
        --region-label-control shuffle \
        --out-dir "$out"
    else
      uv run python -u scripts/train.py \
        "${COMMON_ARGS[@]}" \
        --seed "$seed" \
        --arm "$arm" \
        --out-dir "$out"
    fi
  done
done

uv run python scripts/analyze_leave_subject_out.py "$OUT_ROOT" > "$OUT_ROOT/summary.md"

echo ""
echo "Wrote:"
echo "  $OUT_ROOT/summary.md"
