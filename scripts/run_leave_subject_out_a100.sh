#!/bin/bash
# Leave-subject-out cross-animal diagnostic.
#
# This asks whether any held-out animal shows an anatomical lift over the
# shared null baseline. Defaults are cheap: one seed, stimulus-side target.
set -e

cd "$(dirname "$0")/.."

DEVICE="${DEVICE:-cuda}"
MAX_STEPS="${MAX_STEPS:-600}"
EVAL_BATCHES="${EVAL_BATCHES:-50}"
BATCH_SIZE="${BATCH_SIZE:-16}"
DIM="${DIM:-96}"
DEPTH="${DEPTH:-3}"
NUM_LATENTS="${NUM_LATENTS:-24}"
SEEDS="${SEEDS:-0}"
TARGET_MODE="${TARGET_MODE:-stimulus_side}"
OUT_ROOT="${OUT_ROOT:-runs/leave_subject_out_a100}"
SUBJECTS="${SUBJECTS:-}"
ARMS="${ARMS:-shared_baseline region_only cell_type_only pure_anatomy waveform_only}"

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
)

if [ -z "$SUBJECTS" ]; then
  SUBJECTS="$(uv run python - <<'PY'
from torch_brain.dataset import Dataset
from scripts.train import build_vocab

ds = Dataset(dataset_dir="data/brainsets/ibl_bwm", keep_files_open=True)
vocab = build_vocab(ds)
print(" ".join(sorted(set(vocab["subject_by_rid"].values()))))
PY
)"
fi

mkdir -p "$OUT_ROOT"
echo "subjects: $SUBJECTS"
echo "arms: $ARMS"
echo "seeds: $SEEDS"

for holdout in $SUBJECTS; do
  safe_holdout="$(printf '%s' "$holdout" | tr -c '[:alnum:]_.-' '_')"
  sweep_dir="$OUT_ROOT/holdout_$safe_holdout"
  mkdir -p "$sweep_dir"
  for seed in $SEEDS; do
    for arm in $ARMS; do
      out="$sweep_dir/cloud_choice_${arm}_seed${seed}"
      if [ -f "$out/log.jsonl" ] && grep -q '"event": "done"' "$out/log.jsonl" 2>/dev/null; then
        echo "skip (already done): $out"
        continue
      fi
      rm -rf "$out"
      echo ""
      echo "=== holdout=$holdout arm=$arm seed=$seed ==="
      uv run python -u scripts/train.py \
        "${COMMON_ARGS[@]}" \
        --holdout "$holdout" \
        --seed "$seed" \
        --arm "$arm" \
        --out-dir "$out"
    done
  done
  uv run python scripts/analyze_sweep.py "$sweep_dir" > "$sweep_dir/summary.md"
done

uv run python scripts/analyze_leave_subject_out.py "$OUT_ROOT" > "$OUT_ROOT/summary.md"

echo ""
echo "Wrote:"
echo "  $OUT_ROOT/summary.md"
