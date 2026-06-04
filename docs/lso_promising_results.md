# Cloud Phase 3-5 Results

Date: 2026-06-04T06:00:27Z

RunPod target: A100 pilot.

Exit status: 0

Configuration:

- branch: runpod-pilot-phases-3-5
- build recordings: 20
- max steps: 600
- eval batches: 50
- target mode: stimulus_side
- sweep script: scripts/run_lso_promising_a100.sh
- max runtime seconds: 10800
- output root: `runs/lso_promising_a100`

## Summary

# Leave-subject-out analysis

root: `runs/lso_promising_a100`

## Per-Holdout AUC and Delta vs Shared Null

| holdout | arm | n_seeds | mean_AUC | mean_delta_vs_shared | seed_deltas |
|---|---|---|---|---|---|
| CSHL045 | pure_anatomy | 3 | 0.514 | -0.002 | +0.019,-0.076,+0.051 |
| CSHL045 | region_only | 3 | 0.483 | -0.033 | +0.038,-0.091,-0.045 |
| CSHL045 | waveform_only | 3 | 0.540 | +0.024 | +0.001,+0.013,+0.060 |
| DY_008 | pure_anatomy | 3 | 0.553 | +0.045 | +0.059,+0.027,+0.049 |
| DY_008 | region_only | 3 | 0.549 | +0.041 | +0.043,+0.026,+0.054 |
| DY_008 | waveform_only | 3 | 0.523 | +0.015 | +0.055,-0.002,-0.009 |
| KS014 | pure_anatomy | 3 | 0.510 | -0.017 | +0.029,-0.081,+0.001 |
| KS014 | region_only | 3 | 0.500 | -0.027 | -0.023,-0.002,-0.057 |
| KS014 | waveform_only | 3 | 0.510 | -0.017 | -0.029,-0.026,+0.004 |
| MFD_05 | pure_anatomy | 3 | 0.501 | +0.006 | +0.040,+0.017,-0.040 |
| MFD_05 | region_only | 3 | 0.498 | +0.003 | +0.044,+0.003,-0.039 |
| MFD_05 | waveform_only | 3 | 0.514 | +0.018 | -0.000,+0.052,+0.003 |

## Aggregate Delta vs Shared Null

| arm | n_pairs | mean_delta | positive_pairs |
|---|---|---|---|
| pure_anatomy | 12 | +0.008 | 9/12 |
| region_only | 12 | -0.004 | 6/12 |
| waveform_only | 12 | +0.010 | 7/12 |
