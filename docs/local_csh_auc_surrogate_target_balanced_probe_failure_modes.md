# Prediction Failure-Mode Audit

Root: `runs/local_csh_auc_surrogate_target_balanced_probe`
Holdout: `CSH_ZAD_019`
Region granularity: `parent`

## Offset Contribution

| arm | full_AUC | recording_centered_AUC | full_minus_centered | mean_prob | prob_std |
|---|---:|---:|---:|---:|---:|
| shared_baseline | 0.518 | 0.518 | -0.000 | 0.461 | 0.012 |
| region_only | 0.474 | 0.494 | -0.020 | 0.472 | 0.012 |
| region_shuffle | 0.484 | 0.500 | -0.016 | 0.472 | 0.011 |

## Per-Recording Prediction Behavior

| recording | n | target1_frac | imbalance | true_auc | shuffle_auc | true-shuffle_auc | true_mean_delta_vs_shared | shuffle_mean_delta_vs_shared | true_vs_shuffle_paired | parent_support | missing_top_parent_regions |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `49e0ab27-827a-4c91-bcaa-97eea27a1b8d_probe01` | 777 | 0.467 | 0.033 | 0.481 | 0.508 | -0.027 | +0.003 | +0.002 | 0.468 | 1.000 | none |
| `5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe00` | 590 | 0.414 | 0.086 | 0.492 | 0.535 | -0.043 | +0.025 | +0.017 | 0.414 | 0.752 | MED, EPI, mfbse |
| `5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe01` | 590 | 0.414 | 0.086 | 0.475 | 0.474 | +0.001 | +0.013 | +0.018 | 0.610 | 0.808 | ATN, epsc |
| `edd22318-216c-44ff-bc24-49ce8be78374_probe00` | 769 | 0.482 | 0.018 | 0.520 | 0.506 | +0.014 | +0.007 | +0.012 | 0.521 | 0.850 | HIP, CTXpl |

## Recording Offset Correlations

| measure | correlation |
|---|---:|
| `shared_baseline_mean_prob_vs_target1_fraction` | -0.042 |
| `region_only_mean_prob_vs_target1_fraction` | -0.796 |
| `region_shuffle_mean_prob_vs_target1_fraction` | -0.722 |

## Paired Trial Checks

| comparison | n | improved_fraction | mean_true_prob_delta |
|---|---:|---:|---:|
| `region_only_vs_shuffle` | 2726 | 0.502 | -0.000 |
| `region_only_vs_shared` | 2726 | 0.459 | -0.002 |
| `region_shuffle_vs_shared` | 2726 | 0.463 | -0.002 |

## Interpretation

The current failure is not explained by missing held-out parent-region coverage alone: the minimum held-out recording support is 0.752.

The stronger signal is calibration/offset behavior. `region_shuffle` gains -0.016 AUC from recording-level offsets, while `region_only` gets -0.020. After removing those offsets, the true-label advantage is too small to support a demo claim.

The paired true-vs-shuffle fraction is 0.502, so true anatomical labels are not moving trial probabilities toward the correct class more reliably than the recording-matched shuffled control.

Next experiment design should therefore make recording-matched negatives and recording-centered evaluation primary, and should avoid selecting on raw AUC.
