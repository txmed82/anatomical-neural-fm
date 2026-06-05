# Cloud Phase 3-5 Results

Date: 2026-06-04T03:45:43Z

RunPod target: A100 pilot.

Exit status: 0

Configuration:

- branch: runpod-pilot-phases-3-5
- build recordings: 20
- max steps: 600
- eval batches: 50
- target mode: stimulus_side
- max runtime seconds: 10800
- output root: `runs/phase2_cloud_a100`

## Within-Animal Summary

# Sweep analysis: within

## Per-arm AUC summary (best eval across training)

| arm | n_seeds | mean_AUC | std | min | max | seeds |
|---|---|---|---|---|---|---|
| baseline | 3 | **0.596** | 0.022 | 0.571 | 0.614 | 0.571,0.603,0.614 |
| pure_anatomy | 3 | **0.552** | 0.018 | 0.542 | 0.574 | 0.542,0.542,0.574 |
| shared_baseline | 3 | **0.508** | 0.041 | 0.463 | 0.543 | 0.517,0.463,0.543 |
| waveform_only | 3 | **0.507** | 0.030 | 0.473 | 0.529 | 0.521,0.473,0.529 |

## Paired comparison: pure_anatomy − baseline

| seed | baseline AUC | pure_anatomy AUC | Δ AUC |
|---|---|---|---|
| 0 | 0.571 | 0.542 | -0.030 |
| 1 | 0.603 | 0.542 | -0.062 |
| 2 | 0.614 | 0.574 | -0.041 |

**mean Δ AUC** = -0.0440    **paired SE** = 0.0095    **t** = -4.63 (df=2)    **positive seeds** = 0/3
→ **Significant by t but inconsistent across seeds.**

## Paired comparison: shared_baseline − baseline

| seed | baseline AUC | shared_baseline AUC | Δ AUC |
|---|---|---|---|
| 0 | 0.571 | 0.517 | -0.054 |
| 1 | 0.603 | 0.463 | -0.140 |
| 2 | 0.614 | 0.543 | -0.071 |

**mean Δ AUC** = -0.0885    **paired SE** = 0.0264    **t** = -3.35 (df=2)    **positive seeds** = 0/3
→ **Not significant at p<0.05 (two-tailed p≈0.0829). Direction consistent across seeds (all negative).**

## Paired comparison: waveform_only − baseline

| seed | baseline AUC | waveform_only AUC | Δ AUC |
|---|---|---|---|
| 0 | 0.571 | 0.521 | -0.051 |
| 1 | 0.603 | 0.473 | -0.131 |
| 2 | 0.614 | 0.529 | -0.086 |

**mean Δ AUC** = -0.0890    **paired SE** = 0.0232    **t** = -3.83 (df=2)    **positive seeds** = 0/3
→ **Not significant at p<0.05 (two-tailed p≈0.0619) but marginal at p<0.10. Direction consistent across seeds (all negative).**

## Cross-Animal Summary

# Sweep analysis: cross

## Per-arm AUC summary (best eval across training)

| arm | n_seeds | mean_AUC | std | min | max | seeds |
|---|---|---|---|---|---|---|
| cell_type_only | 3 | **0.521** | 0.008 | 0.516 | 0.530 | 0.517,0.530,0.516 |
| pure_anatomy | 3 | **0.516** | 0.009 | 0.507 | 0.524 | 0.507,0.524,0.518 |
| region_only | 3 | **0.524** | 0.005 | 0.518 | 0.529 | 0.524,0.529,0.518 |
| shared_baseline | 3 | **0.522** | 0.011 | 0.510 | 0.529 | 0.528,0.529,0.510 |
| waveform_only | 3 | **0.519** | 0.009 | 0.508 | 0.526 | 0.526,0.522,0.508 |
