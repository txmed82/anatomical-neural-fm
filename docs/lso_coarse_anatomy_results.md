# Cloud Phase 3-5 Results

Date: 2026-06-04T08:53:17Z

RunPod target: A100 pilot.

Exit status: 0

Configuration:

- branch: runpod-pilot-phases-3-5
- build recordings: 20
- max steps: 600
- eval batches: 50
- target mode: stimulus_side
- sweep script: scripts/run_lso_coarse_anatomy_a100.sh
- max runtime seconds: 10800
- output root: `runs/lso_coarse_anatomy_a100`

## Summary

# Leave-subject-out analysis

root: `runs/lso_coarse_anatomy_a100`

## Per-Holdout AUC and Delta vs Shared Null

| holdout | arm | n_seeds | mean_AUC | mean_delta_vs_shared | seed_deltas |
|---|---|---|---|---|---|
| CSHL045 | pure_anatomy | 3 | 0.551 | +0.033 | +0.039,+0.050,+0.008 |
| CSHL045 | region_only | 3 | 0.516 | -0.003 | +0.052,+0.005,-0.066 |
| DY_008 | pure_anatomy | 3 | 0.545 | +0.024 | +0.041,+0.000,+0.032 |
| DY_008 | region_only | 3 | 0.533 | +0.012 | +0.000,+0.005,+0.030 |
| KS014 | pure_anatomy | 3 | 0.457 | -0.049 | -0.028,-0.028,-0.092 |
| KS014 | region_only | 3 | 0.522 | +0.016 | -0.027,+0.103,-0.028 |
| MFD_05 | pure_anatomy | 3 | 0.511 | -0.009 | -0.014,-0.003,-0.009 |
| MFD_05 | region_only | 3 | 0.515 | -0.004 | -0.012,+0.008,-0.008 |

## Aggregate Delta vs Shared Null

| arm | n_pairs | mean_delta | positive_pairs |
|---|---|---|---|
| pure_anatomy | 12 | -0.000 | 6/12 |
| region_only | 12 | +0.005 | 7/12 |
