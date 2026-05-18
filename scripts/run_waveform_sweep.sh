#!/bin/bash
# Cross-animal waveform conditioning sweep on M4 MPS.
# Compares baseline vs unit+waveform vs waveform-only across 5 seeds.
set -e

cd "$(dirname "$0")/.."
SWEEP_DIR=runs/waveform_sweep
mkdir -p "$SWEEP_DIR"

ARMS=("baseline" "waveform" "waveform_only")
SEEDS=(0 1 2 3 4)

start_ts=$(date +%s)
for SEED in "${SEEDS[@]}"; do
    for ARM in "${ARMS[@]}"; do
        OUT="$SWEEP_DIR/cloud_choice_${ARM}_seed${SEED}"
        if [ -f "$OUT/log.jsonl" ] && grep -q '"event": "done"' "$OUT/log.jsonl" 2>/dev/null; then
            echo "skip (already done): $OUT"
            continue
        fi
        rm -rf "$OUT"
        echo ""
        echo "=== arm=$ARM seed=$SEED (cross-animal) ==="
        uv run python -u scripts/train.py \
            --device mps \
            --split-mode animal \
            --batch-size 8 \
            --dim 128 --depth 3 --num-latents 32 \
            --max-steps 1500 \
            --eval-every 100 --eval-batches 100 \
            --log-every 100 --warmup-steps 100 \
            --seed "$SEED" \
            --arm "$ARM" \
            --out-dir "$OUT" 2>&1 | grep -E "split|ckpt_best|eval_loss|done" | tail -5
    done
done
end_ts=$(date +%s)
echo ""
echo "=== ALL DONE in $((end_ts - start_ts))s ==="
