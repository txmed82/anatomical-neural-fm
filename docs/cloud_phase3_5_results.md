# Cloud Phase 3-5 Results

Date: 2026-06-03T23:58:15Z

RunPod target: A100 pilot.

Exit status: 0

Configuration:

- branch: runpod-pilot-phases-3-5
- build recordings: 6
- max steps: 600
- eval batches: 50
- max runtime seconds: 7200
- output root: `runs/phase2_cloud_a100`

## Within-Animal Summary

# Sweep analysis: within

## Per-arm AUC summary (best eval across training)

| arm | n_seeds | mean_AUC | std | min | max | seeds |
|---|---|---|---|---|---|---|
| baseline | 2 | **0.843** | 0.098 | 0.774 | 0.913 | 0.913,0.774 |
| pure_anatomy | 2 | **0.602** | 0.041 | 0.574 | 0.631 | 0.574,0.631 |
| waveform_only | 2 | **0.600** | 0.012 | 0.592 | 0.608 | 0.592,0.608 |

## Paired comparison: pure_anatomy − baseline

| seed | baseline AUC | pure_anatomy AUC | Δ AUC |
|---|---|---|---|
| 0 | 0.913 | 0.574 | -0.339 |
| 1 | 0.774 | 0.631 | -0.143 |

**mean Δ AUC** = -0.2410    **paired SE** = 0.0978    **t** = -2.46 (df=1)    **positive seeds** = 0/2
→ **Significant by t but inconsistent across seeds.**

## Paired comparison: waveform_only − baseline

| seed | baseline AUC | waveform_only AUC | Δ AUC |
|---|---|---|---|
| 0 | 0.913 | 0.592 | -0.321 |
| 1 | 0.774 | 0.608 | -0.166 |

**mean Δ AUC** = -0.2433    **paired SE** = 0.0774    **t** = -3.14 (df=1)    **positive seeds** = 0/2
→ **Significant by t but inconsistent across seeds.**

## Cross-Animal Summary

# Sweep analysis: cross

## Per-arm AUC summary (best eval across training)

| arm | n_seeds | mean_AUC | std | min | max | seeds |
|---|---|---|---|---|---|---|
| pure_anatomy | 2 | **0.482** | 0.040 | 0.453 | 0.510 | 0.453,0.510 |
| waveform_only | 2 | **0.477** | 0.019 | 0.464 | 0.491 | 0.464,0.491 |
