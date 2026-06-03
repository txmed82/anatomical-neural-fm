# Cloud Phase 3-5 Results

Date: 2026-06-03T23:44:00Z

RunPod target: A100 pilot.

Exit status: 0

Configuration:

- branch: runpod-pilot-phases-3-5
- build recordings: 3
- max steps: 200
- eval batches: 20
- max runtime seconds: 7200
- output root: `runs/phase2_cloud_a100`

## Within-Animal Summary

# Sweep analysis: within

## Per-arm AUC summary (best eval across training)

| arm | n_seeds | mean_AUC | std | min | max | seeds |
|---|---|---|---|---|---|---|
| baseline | 2 | **0.611** | 0.043 | 0.581 | 0.641 | 0.641,0.581 |
| pure_anatomy | 2 | **0.545** | 0.081 | 0.488 | 0.602 | 0.602,0.488 |
| waveform_only | 2 | **0.563** | 0.059 | 0.521 | 0.604 | 0.604,0.521 |

## Paired comparison: pure_anatomy − baseline

| seed | baseline AUC | pure_anatomy AUC | Δ AUC |
|---|---|---|---|
| 0 | 0.641 | 0.602 | -0.039 |
| 1 | 0.581 | 0.488 | -0.093 |

**mean Δ AUC** = -0.0659    **paired SE** = 0.0269    **t** = -2.45 (df=1)    **positive seeds** = 0/2
→ **Significant by t but inconsistent across seeds.**

## Paired comparison: waveform_only − baseline

| seed | baseline AUC | waveform_only AUC | Δ AUC |
|---|---|---|---|
| 0 | 0.641 | 0.604 | -0.037 |
| 1 | 0.581 | 0.521 | -0.059 |

**mean Δ AUC** = -0.0479    **paired SE** = 0.0114    **t** = -4.21 (df=1)    **positive seeds** = 0/2
→ **Significant by t but inconsistent across seeds.**

## Cross-Animal Summary

# Sweep analysis: cross

## Per-arm AUC summary (best eval across training)

| arm | n_seeds | mean_AUC | std | min | max | seeds |
|---|---|---|---|---|---|---|
| pure_anatomy | 2 | **0.524** | 0.029 | 0.503 | 0.545 | 0.503,0.545 |
| waveform_only | 2 | **0.515** | 0.002 | 0.513 | 0.517 | 0.513,0.517 |
