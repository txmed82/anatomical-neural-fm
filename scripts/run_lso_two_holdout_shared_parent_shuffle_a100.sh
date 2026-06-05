#!/bin/bash
# Two-holdout strict anatomy-control check.
#
# Runs the CSH_ZAD_019 shared-parent true-vs-shuffled-region control on two
# additional matched-cache holdouts to test whether the signal generalizes.
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
SUBJECTS="${SUBJECTS:-KS014 MFD_06}"
TARGET_MODE="${TARGET_MODE:-stimulus_side}"
REGION_FILTER="${REGION_FILTER:-shared_regions}"
REGION_GRANULARITY="${REGION_GRANULARITY:-parent}"
REGION_INCLUDE="${REGION_INCLUDE:-}"
OUT_ROOT="${OUT_ROOT:-runs/lso_two_holdout_shared_parent_shuffle}"
MANIFEST="${MANIFEST:-}"
SAVE_DIAGNOSTICS="${SAVE_DIAGNOSTICS:-0}"
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
  --region-filter "$REGION_FILTER"
  --region-granularity "$REGION_GRANULARITY"
)
if [ -n "$REGION_INCLUDE" ]; then
  COMMON_ARGS+=(--region-include "$REGION_INCLUDE")
fi
if [ -n "$MANIFEST" ]; then
  COMMON_ARGS+=(--manifest "$MANIFEST")
fi
if [ "$SAVE_DIAGNOSTICS" = "1" ]; then
  COMMON_ARGS+=(--save-eval-predictions --save-region-embeddings)
  if [ "$EVAL_PREDICTION_MAX_TRIALS" != "0" ]; then
    COMMON_ARGS+=(--eval-prediction-max-trials "$EVAL_PREDICTION_MAX_TRIALS")
  fi
fi

mkdir -p "$OUT_ROOT"
write_incremental_summary() {
  tmp_summary="$OUT_ROOT/summary.md.tmp"
  if uv run python scripts/analyze_leave_subject_out.py "$OUT_ROOT" > "$tmp_summary"; then
    mv "$tmp_summary" "$OUT_ROOT/summary.md"
    echo "updated incremental summary: $OUT_ROOT/summary.md"
  else
    rm -f "$tmp_summary"
    echo "warning: incremental summary failed" >&2
  fi
}

echo "subjects: $SUBJECTS"
echo "arms: shared_baseline region_only region_shuffle"
echo "seeds: $SEEDS"
echo "region_filter: $REGION_FILTER"
echo "region_granularity: $REGION_GRANULARITY"
echo "region_include: ${REGION_INCLUDE:-<none>}"
echo "manifest: ${MANIFEST:-<all local recordings>}"
echo "save_diagnostics: $SAVE_DIAGNOSTICS"

for holdout in $SUBJECTS; do
  safe_holdout="$(printf '%s' "$holdout" | tr -c '[:alnum:]_.-' '_')"
  holdout_dir="$OUT_ROOT/holdout_$safe_holdout"
  mkdir -p "$holdout_dir"
  for seed in $SEEDS; do
    for arm in shared_baseline region_only region_shuffle; do
      out="$holdout_dir/cloud_choice_${arm}_seed${seed}"
      if [ -f "$out/log.jsonl" ] && grep -q '"event": "done"' "$out/log.jsonl" 2>/dev/null; then
        echo "skip (already done): $out"
        continue
      fi
      rm -rf "$out"
      mkdir -p "$out"
      echo ""
      echo "=== holdout=$holdout arm=$arm seed=$seed region_filter=$REGION_FILTER region_granularity=$REGION_GRANULARITY ==="
      if [ "$arm" = "region_shuffle" ]; then
        uv run python -u scripts/train.py \
          "${COMMON_ARGS[@]}" \
          --holdout "$holdout" \
          --seed "$seed" \
          --arm region_only \
          --region-label-control shuffle \
          --out-dir "$out"
      else
        uv run python -u scripts/train.py \
          "${COMMON_ARGS[@]}" \
          --holdout "$holdout" \
          --seed "$seed" \
          --arm "$arm" \
          --out-dir "$out"
      fi
      write_incremental_summary
    done
  done
  write_incremental_summary
done

write_incremental_summary

echo ""
echo "Wrote:"
echo "  $OUT_ROOT/summary.md"
