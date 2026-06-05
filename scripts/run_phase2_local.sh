#!/bin/bash
# Apple Silicon phase-2 sweep: quick sanity runs before RunPod scaling.
set -e

cd "$(dirname "$0")/.."

COMMON_ARGS=(
  --device mps
  --output-query-mode shared
  --batch-size 4
  --dim 64 --depth 2 --num-latents 16
  --max-steps 300
  --eval-every 100 --eval-batches 30
  --log-every 50 --warmup-steps 50
)

run_block() {
  local split_mode="$1"
  local sweep_dir="$2"
  shift 2
  local arms=("$@")
  local seeds=(0 1)

  mkdir -p "$sweep_dir"
  for seed in "${seeds[@]}"; do
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

run_block trial runs/phase2_local_within baseline pure_anatomy waveform_only
run_block animal runs/phase2_local_cross pure_anatomy waveform_only

echo ""
echo "Analyze with:"
echo "  uv run python scripts/analyze_sweep.py runs/phase2_local_within"
echo "  uv run python scripts/analyze_sweep.py runs/phase2_local_cross"
