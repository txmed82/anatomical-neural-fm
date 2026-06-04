# Cloud Phase 3-5 Results

Date: 2026-06-04T02:29:25Z

RunPod target: A100 pilot.

Exit status: 0

Configuration:

- branch: runpod-pilot-phases-3-5
- build recordings: 20
- max steps: 600
- eval batches: 50
- max runtime seconds: 10800
- output root: `runs/phase2_cloud_a100`

## Within-Animal Summary

# Sweep analysis: within

## Per-arm AUC summary (best eval across training)

| arm | n_seeds | mean_AUC | std | min | max | seeds |
|---|---|---|---|---|---|---|
| baseline | 3 | **0.751** | 0.090 | 0.647 | 0.804 | 0.804,0.647,0.802 |
| pure_anatomy | 3 | **0.625** | 0.007 | 0.617 | 0.630 | 0.627,0.630,0.617 |
| shared_baseline | 3 | **0.511** | 0.037 | 0.469 | 0.540 | 0.523,0.469,0.540 |
| waveform_only | 3 | **0.517** | 0.028 | 0.488 | 0.543 | 0.519,0.488,0.543 |

## Paired comparison: pure_anatomy − baseline

| seed | baseline AUC | pure_anatomy AUC | Δ AUC |
|---|---|---|---|
| 0 | 0.804 | 0.627 | -0.177 |
| 1 | 0.647 | 0.630 | -0.017 |
| 2 | 0.802 | 0.617 | -0.185 |

**mean Δ AUC** = -0.1262    **paired SE** = 0.0545    **t** = -2.32 (df=2)    **positive seeds** = 0/3
→ **Significant by t but inconsistent across seeds.**

## Paired comparison: shared_baseline − baseline

| seed | baseline AUC | shared_baseline AUC | Δ AUC |
|---|---|---|---|
| 0 | 0.804 | 0.523 | -0.281 |
| 1 | 0.647 | 0.469 | -0.178 |
| 2 | 0.802 | 0.540 | -0.262 |

**mean Δ AUC** = -0.2399    **paired SE** = 0.0317    **t** = -7.57 (df=2)    **positive seeds** = 0/3
→ **Significant by t but inconsistent across seeds.**

## Paired comparison: waveform_only − baseline

| seed | baseline AUC | waveform_only AUC | Δ AUC |
|---|---|---|---|
| 0 | 0.804 | 0.519 | -0.285 |
| 1 | 0.647 | 0.488 | -0.159 |
| 2 | 0.802 | 0.543 | -0.259 |

**mean Δ AUC** = -0.2340    **paired SE** = 0.0383    **t** = -6.11 (df=2)    **positive seeds** = 0/3
→ **Significant by t but inconsistent across seeds.**

## Cross-Animal Summary

# Sweep analysis: cross

## Per-arm AUC summary (best eval across training)

| arm | n_seeds | mean_AUC | std | min | max | seeds |
|---|---|---|---|---|---|---|
| pure_anatomy | 3 | **0.503** | 0.035 | 0.464 | 0.531 | 0.531,0.513,0.464 |
| shared_baseline | 3 | **0.502** | 0.010 | 0.492 | 0.512 | 0.512,0.500,0.492 |
| waveform_only | 3 | **0.494** | 0.028 | 0.462 | 0.513 | 0.513,0.509,0.462 |
