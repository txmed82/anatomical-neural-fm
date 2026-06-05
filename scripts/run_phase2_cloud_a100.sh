#!/bin/bash
# First A100 pilot sweep. Tuned to stay cheap while checking the cross-animal signal.
set -e

cd "$(dirname "$0")/.."

DEVICE="${DEVICE:-cuda}"
MAX_STEPS="${MAX_STEPS:-600}"
EVAL_BATCHES="${EVAL_BATCHES:-50}"
BATCH_SIZE="${BATCH_SIZE:-16}"
DIM="${DIM:-96}"
DEPTH="${DEPTH:-3}"
NUM_LATENTS="${NUM_LATENTS:-24}"
SEEDS="${SEEDS:-0 1 2}"
TARGET_MODE="${TARGET_MODE:-choice}"
OUT_ROOT="${OUT_ROOT:-runs/phase2_cloud_a100}"

COMMON_ARGS=(
  --device "$DEVICE"
  --output-query-mode shared
  --batch-size "$BATCH_SIZE"
  --dim "$DIM" --depth "$DEPTH" --num-latents "$NUM_LATENTS"
  --max-steps "$MAX_STEPS"
  --eval-every 150 --eval-batches "$EVAL_BATCHES"
  --log-every 50 --warmup-steps 75
  --target-mode "$TARGET_MODE"
)

run_block() {
  local split_mode="$1"
  local sweep_dir="$2"
  shift 2
  local arms=("$@")

  mkdir -p "$sweep_dir"
  for seed in $SEEDS; do
    for arm in "${arms[@]}"; do
      local out="$sweep_dir/cloud_choice_${arm}_seed${seed}"
      if [ -f "$out/log.jsonl" ] && grep -q '"event": "done"' "$out/log.jsonl" 2>/dev/null; then
        echo "skip (already done): $out"
        continue
      fi
      rm -rf "$out"
      echo ""
      echo "=== split=$split_mode arm=$arm seed=$seed ==="
      uv run python -u scripts/train.py \
        "${COMMON_ARGS[@]}" \
        --split-mode "$split_mode" \
        --seed "$seed" \
        --arm "$arm" \
        --out-dir "$out"
    done
  done
}

mkdir -p "$OUT_ROOT"
run_block trial "$OUT_ROOT/within" baseline shared_baseline pure_anatomy waveform_only
run_block animal "$OUT_ROOT/cross" shared_baseline region_only cell_type_only pure_anatomy waveform_only

uv run python scripts/analyze_sweep.py "$OUT_ROOT/within" > "$OUT_ROOT/within_summary.md"
uv run python scripts/analyze_sweep.py "$OUT_ROOT/cross" > "$OUT_ROOT/cross_summary.md"

echo ""
echo "Wrote:"
echo "  $OUT_ROOT/within_summary.md"
echo "  $OUT_ROOT/cross_summary.md"
