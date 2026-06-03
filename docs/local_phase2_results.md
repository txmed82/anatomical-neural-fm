# Local Phase 2 Results

Date: 2026-06-03

Machine target: Apple Silicon MPS

Dataset:

- IBL BWM local batch: 3 recordings
- Subjects: 2
- Units: 3,953
- Trials: 2,098
- Cross-animal split: train `MFD_08`, evaluate `MFD_09`

Configuration:

- `scripts/run_phase2_local.sh`
- `--output-query-mode shared`
- `--dim 64 --depth 2 --num-latents 16`
- `--max-steps 300`
- `--eval-batches 30`
- seeds: `0, 1`

## Within-Animal Sanity

| arm | n_seeds | mean_AUC | std | min | max | seeds |
|---|---:|---:|---:|---:|---:|---|
| baseline | 2 | 0.596 | 0.066 | 0.549 | 0.642 | 0.642, 0.549 |
| pure_anatomy | 2 | 0.589 | 0.079 | 0.533 | 0.644 | 0.644, 0.533 |
| waveform_only | 2 | 0.570 | 0.093 | 0.504 | 0.636 | 0.636, 0.504 |

Paired deltas vs baseline:

| arm | mean_delta_auc | paired_se | t | positive_seeds |
|---|---:|---:|---:|---:|
| pure_anatomy | -0.0066 | 0.0086 | -0.77 | 1/2 |
| waveform_only | -0.0255 | 0.0192 | -1.33 | 0/2 |

Interpretation: no reliable local within-animal advantage for anatomy or
waveform-only arms in this tiny pilot.

## Cross-Animal Sanity

| arm | n_seeds | mean_AUC | std | min | max | seeds |
|---|---:|---:|---:|---:|---:|---|
| pure_anatomy | 2 | 0.537 | 0.044 | 0.506 | 0.568 | 0.506, 0.568 |
| waveform_only | 2 | 0.537 | 0.038 | 0.510 | 0.564 | 0.510, 0.564 |

Interpretation: the fixed cross-animal path runs end-to-end with train/eval
subject separation and shared output query mode. Results are near chance on this
small local dataset, which is acceptable for the phase-2 gate; the next useful
test is scaling subjects/seeds on RunPod.
