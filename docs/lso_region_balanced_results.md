# Cloud Phase 3-5 Results

Date: 2026-06-04T07:58:21Z

RunPod target: A100 pilot.

Exit status: 0

Configuration:

- branch: runpod-pilot-phases-3-5
- build recordings: 20
- max steps: 600
- eval batches: 50
- target mode: stimulus_side
- sweep script: scripts/run_lso_region_balanced_a100.sh
- max runtime seconds: 10800
- output root: `runs/lso_region_balanced_a100`

## Summary

# Leave-subject-out analysis

root: `runs/lso_region_balanced_a100`

## Per-Holdout AUC and Delta vs Shared Null

| holdout | arm | n_seeds | mean_AUC | mean_delta_vs_shared | seed_deltas |
|---|---|---|---|---|---|
| CSHL045 | pure_anatomy | 3 | 0.475 | -0.014 | -0.016,-0.050,+0.024 |
| CSHL045 | region_only | 3 | 0.474 | -0.015 | -0.005,-0.044,+0.003 |
| DY_008 | pure_anatomy | 3 | 0.542 | +0.022 | +0.050,+0.014,+0.002 |
| DY_008 | region_only | 3 | 0.544 | +0.023 | +0.045,-0.001,+0.025 |
| KS014 | pure_anatomy | 3 | 0.491 | +0.009 | +0.044,+0.096,-0.111 |
| KS014 | region_only | 3 | 0.525 | +0.043 | +0.087,+0.102,-0.060 |
| MFD_05 | pure_anatomy | 3 | 0.515 | +0.006 | +0.025,-0.019,+0.011 |
| MFD_05 | region_only | 3 | 0.516 | +0.007 | +0.028,-0.034,+0.026 |

## Aggregate Delta vs Shared Null

| arm | n_pairs | mean_delta | positive_pairs |
|---|---|---|---|
| pure_anatomy | 12 | +0.006 | 8/12 |
| region_only | 12 | +0.014 | 7/12 |
