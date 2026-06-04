# Cloud Phase 3-5 Results

Date: 2026-06-04T05:00:25Z

RunPod target: A100 pilot.

Exit status: 0

Configuration:

- branch: runpod-pilot-phases-3-5
- build recordings: 20
- max steps: 600
- eval batches: 50
- target mode: stimulus_side
- sweep script: scripts/run_leave_subject_out_a100.sh
- max runtime seconds: 10800
- output root: `runs/leave_subject_out_a100`

## Summary

# Leave-subject-out analysis

root: `runs/leave_subject_out_a100`

## Per-Holdout AUC and Delta vs Shared Null

| holdout | arm | n_seeds | mean_AUC | mean_delta_vs_shared | seed_deltas |
|---|---|---|---|---|---|
| CSHL045 | cell_type_only | 1 | 0.526 | +0.016 | +0.016 |
| CSHL045 | pure_anatomy | 1 | 0.528 | +0.019 | +0.019 |
| CSHL045 | region_only | 1 | 0.547 | +0.038 | +0.038 |
| CSHL045 | waveform_only | 1 | 0.510 | +0.001 | +0.001 |
| DY_008 | cell_type_only | 1 | 0.543 | +0.045 | +0.045 |
| DY_008 | pure_anatomy | 1 | 0.557 | +0.059 | +0.059 |
| DY_008 | region_only | 1 | 0.541 | +0.043 | +0.043 |
| DY_008 | waveform_only | 1 | 0.553 | +0.055 | +0.055 |
| KS014 | cell_type_only | 1 | 0.460 | -0.070 | -0.070 |
| KS014 | pure_anatomy | 1 | 0.559 | +0.029 | +0.029 |
| KS014 | region_only | 1 | 0.507 | -0.023 | -0.023 |
| KS014 | waveform_only | 1 | 0.501 | -0.029 | -0.029 |
| MFD_05 | cell_type_only | 1 | 0.488 | -0.004 | -0.004 |
| MFD_05 | pure_anatomy | 1 | 0.532 | +0.040 | +0.040 |
| MFD_05 | region_only | 1 | 0.536 | +0.044 | +0.044 |
| MFD_05 | waveform_only | 1 | 0.492 | -0.000 | -0.000 |
| NR_0019 | cell_type_only | 1 | 0.534 | +0.012 | +0.012 |
| NR_0019 | pure_anatomy | 1 | 0.540 | +0.019 | +0.019 |
| NR_0019 | region_only | 1 | 0.529 | +0.007 | +0.007 |
| NR_0019 | waveform_only | 1 | 0.523 | +0.001 | +0.001 |
| NYU-11 | cell_type_only | 1 | 0.525 | -0.019 | -0.019 |
| NYU-11 | pure_anatomy | 1 | 0.513 | -0.032 | -0.032 |
| NYU-11 | region_only | 1 | 0.539 | -0.006 | -0.006 |
| NYU-11 | waveform_only | 1 | 0.549 | +0.004 | +0.004 |
| PL015 | cell_type_only | 1 | 0.515 | -0.008 | -0.008 |
| PL015 | pure_anatomy | 1 | 0.521 | -0.003 | -0.003 |
| PL015 | region_only | 1 | 0.529 | +0.005 | +0.005 |
| PL015 | waveform_only | 1 | 0.522 | -0.001 | -0.001 |
| SWC_038 | cell_type_only | 1 | 0.485 | -0.045 | -0.045 |
| SWC_038 | pure_anatomy | 1 | 0.473 | -0.057 | -0.057 |
| SWC_038 | region_only | 1 | 0.471 | -0.059 | -0.059 |
| SWC_038 | waveform_only | 1 | 0.474 | -0.056 | -0.056 |
| SWC_042 | cell_type_only | 1 | 0.515 | +0.008 | +0.008 |
| SWC_042 | pure_anatomy | 1 | 0.525 | +0.017 | +0.017 |
| SWC_042 | region_only | 1 | 0.494 | -0.013 | -0.013 |
| SWC_042 | waveform_only | 1 | 0.504 | -0.003 | -0.003 |
| ZFM-01576 | cell_type_only | 1 | 0.544 | +0.012 | +0.012 |
| ZFM-01576 | pure_anatomy | 1 | 0.540 | +0.008 | +0.008 |
| ZFM-01576 | region_only | 1 | 0.543 | +0.011 | +0.011 |
| ZFM-01576 | waveform_only | 1 | 0.541 | +0.009 | +0.009 |

## Aggregate Delta vs Shared Null

| arm | n_pairs | mean_delta | positive_pairs |
|---|---|---|---|
| cell_type_only | 10 | -0.005 | 5/10 |
| pure_anatomy | 10 | +0.010 | 7/10 |
| region_only | 10 | +0.005 | 6/10 |
| waveform_only | 10 | -0.002 | 5/10 |
