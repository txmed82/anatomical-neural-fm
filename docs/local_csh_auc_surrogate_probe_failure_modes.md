# Prediction Failure-Mode Audit

Root: `runs/local_csh_auc_surrogate_probe`
Holdout: `CSH_ZAD_019`
Region granularity: `parent`

## Offset Contribution

| arm | full_AUC | recording_centered_AUC | full_minus_centered | mean_prob | prob_std |
|---|---:|---:|---:|---:|---:|
| shared_baseline | 0.517 | 0.517 | -0.000 | 0.462 | 0.010 |
| region_only | 0.474 | 0.493 | -0.019 | 0.472 | 0.011 |
| region_shuffle | 0.483 | 0.498 | -0.015 | 0.473 | 0.010 |

## Per-Recording Prediction Behavior

| recording | n | target1_frac | imbalance | true_auc | shuffle_auc | true-shuffle_auc | true_mean_delta_vs_shared | shuffle_mean_delta_vs_shared | true_vs_shuffle_paired | parent_support | missing_top_parent_regions |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `49e0ab27-827a-4c91-bcaa-97eea27a1b8d_probe01` | 777 | 0.467 | 0.033 | 0.480 | 0.510 | -0.030 | +0.003 | +0.002 | 0.434 | 1.000 | none |
| `5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe00` | 590 | 0.414 | 0.086 | 0.484 | 0.529 | -0.045 | +0.024 | +0.017 | 0.417 | 0.752 | MED, EPI, mfbse |
| `5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe01` | 590 | 0.414 | 0.086 | 0.474 | 0.473 | +0.001 | +0.012 | +0.017 | 0.607 | 0.808 | ATN, epsc |
| `edd22318-216c-44ff-bc24-49ce8be78374_probe00` | 769 | 0.482 | 0.018 | 0.521 | 0.506 | +0.015 | +0.007 | +0.011 | 0.529 | 0.850 | HIP, CTXpl |

## Recording Offset Correlations

| measure | correlation |
|---|---:|
| `shared_baseline_mean_prob_vs_target1_fraction` | -0.043 |
| `region_only_mean_prob_vs_target1_fraction` | -0.782 |
| `region_shuffle_mean_prob_vs_target1_fraction` | -0.720 |

## Paired Trial Checks

| comparison | n | improved_fraction | mean_true_prob_delta |
|---|---:|---:|---:|
| `region_only_vs_shuffle` | 2726 | 0.494 | -0.000 |
| `region_only_vs_shared` | 2726 | 0.457 | -0.002 |
| `region_shuffle_vs_shared` | 2726 | 0.464 | -0.002 |

## Interpretation

The current failure is not explained by missing held-out parent-region coverage alone: the minimum held-out recording support is 0.752.

The stronger signal is calibration/offset behavior. `region_shuffle` gains -0.015 AUC from recording-level offsets, while `region_only` gets -0.019. After removing those offsets, the true-label advantage is too small to support a demo claim.

The paired true-vs-shuffle fraction is 0.494, so true anatomical labels are not moving trial probabilities toward the correct class more reliably than the recording-matched shuffled control.

Next experiment design should therefore make recording-matched negatives and recording-centered evaluation primary, and should avoid selecting on raw AUC.
