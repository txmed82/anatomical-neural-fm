# Pairwise Rank Mismatch Audit

Root: `runs/lso_csh_pairwise_rank_centered_bce_pilot`
Holdout: `CSH_ZAD_019` seed `0`

## Global

| metric | value |
|---|---:|
| decision | `paired_metric_not_recording_rank_stable` |
| paired true-class improved | 0.486 |
| true-minus-shuffle AUC | -0.018 |
| mean raw probability delta | +0.006 |
| raw probability delta negative fraction | 0.352 |
| target0 true-class improved | 0.354 |
| target1 true-class improved | 0.650 |

## Recording Breakdown

| recording | n | target1_frac | true-shuffle AUC | paired improved | target0 improved | target1 improved | mean raw delta | class |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `49e0ab27-827a-4c91-bcaa-97eea27a1b8d_probe01` | 777 | 0.467 | -0.006 | 0.467 | 0.000 | 1.000 | +0.042 | `upward_probability_shift` |
| `5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe00` | 590 | 0.414 | -0.004 | 0.575 | 0.971 | 0.012 | -0.069 | `downward_probability_shift` |
| `5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe01` | 590 | 0.414 | -0.034 | 0.414 | 0.000 | 1.000 | +0.043 | `upward_probability_shift` |
| `edd22318-216c-44ff-bc24-49ce8be78374_probe00` | 769 | 0.482 | -0.037 | 0.494 | 0.492 | 0.496 | -0.001 | `mixed_or_failed_ranking` |

## Interpretation

The paired true-vs-shuffle metric is not sufficient by itself. The next objective or gate should require target-0 and target-1 improvements together inside each recording, or optimize a direct recording-local AUC surrogate.

Next objective implication: replace the scalar paired-probability gate with a balanced bidirectional criterion: true labels should beat the shuffled control for target-0 and target-1 subsets separately, and improve recording-local ranking.
