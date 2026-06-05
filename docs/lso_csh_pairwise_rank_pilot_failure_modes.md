# Prediction Failure-Mode Audit

Root: `runs/lso_csh_pairwise_rank_pilot`
Holdout: `CSH_ZAD_019`
Region granularity: `parent`

## Offset Contribution

| arm | full_AUC | recording_centered_AUC | full_minus_centered | mean_prob | prob_std |
|---|---:|---:|---:|---:|---:|
| shared_baseline | 0.500 | 0.501 | -0.000 | 0.374 | 0.007 |
| region_only | 0.474 | 0.480 | -0.006 | 0.243 | 0.012 |
| region_shuffle | 0.474 | 0.494 | -0.020 | 0.490 | 0.060 |

## Per-Recording Prediction Behavior

| recording | n | target1_frac | imbalance | true_auc | shuffle_auc | true-shuffle_auc | true_mean_delta_vs_shared | shuffle_mean_delta_vs_shared | true_vs_shuffle_paired | parent_support | missing_top_parent_regions |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `49e0ab27-827a-4c91-bcaa-97eea27a1b8d_probe01` | 777 | 0.467 | 0.033 | 0.497 | 0.525 | -0.027 | -0.130 | +0.105 | 0.533 | 1.000 | none |
| `5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe00` | 590 | 0.414 | 0.086 | 0.533 | 0.480 | +0.053 | -0.132 | +0.100 | 0.586 | 0.752 | MED, EPI, mfbse |
| `5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe01` | 590 | 0.414 | 0.086 | 0.439 | 0.459 | -0.019 | -0.115 | +0.220 | 0.586 | 0.808 | ATN, epsc |
| `edd22318-216c-44ff-bc24-49ce8be78374_probe00` | 769 | 0.482 | 0.018 | 0.479 | 0.500 | -0.021 | -0.146 | +0.058 | 0.518 | 0.850 | HIP, CTXpl |

## Recording Offset Correlations

| measure | correlation |
|---|---:|
| `shared_baseline_mean_prob_vs_target1_fraction` | -0.941 |
| `region_only_mean_prob_vs_target1_fraction` | -0.749 |
| `region_shuffle_mean_prob_vs_target1_fraction` | -0.691 |

## Paired Trial Checks

| comparison | n | improved_fraction | mean_true_prob_delta |
|---|---:|---:|---:|
| `region_only_vs_shuffle` | 2726 | 0.552 | +0.028 |
| `region_only_vs_shared` | 2726 | 0.552 | +0.013 |
| `region_shuffle_vs_shared` | 2726 | 0.448 | -0.015 |

## Interpretation

The current failure is not explained by missing held-out parent-region coverage alone: the minimum held-out recording support is 0.752.

The stronger signal is calibration/offset behavior. `region_shuffle` gains -0.020 AUC from recording-level offsets, while `region_only` gets -0.006. After removing those offsets, the true-label advantage is too small to support a demo claim.

The paired true-vs-shuffle fraction is 0.552, so true anatomical labels are not moving trial probabilities toward the correct class more reliably than the recording-matched shuffled control.

Next experiment design should therefore make recording-matched negatives and recording-centered evaluation primary, and should avoid selecting on raw AUC.
