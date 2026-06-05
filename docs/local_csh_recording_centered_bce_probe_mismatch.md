# Pairwise Rank Mismatch Audit

Root: `runs/local_csh_recording_centered_bce_probe`
Holdout: `CSH_ZAD_019` seed `0`

## Global

| metric | value |
|---|---:|
| decision | `paired_metric_not_recording_rank_stable` |
| paired true-class improved | 0.494 |
| true-minus-shuffle AUC | -0.009 |
| mean raw probability delta | -0.001 |
| raw probability delta negative fraction | 0.569 |
| target0 true-class improved | 0.557 |
| target1 true-class improved | 0.416 |

## Recording Breakdown

| recording | n | target1_frac | true-shuffle AUC | paired improved | target0 improved | target1 improved | mean raw delta | class |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `49e0ab27-827a-4c91-bcaa-97eea27a1b8d_probe01` | 777 | 0.467 | -0.030 | 0.430 | 0.292 | 0.587 | +0.001 | `mixed_or_failed_ranking` |
| `5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe00` | 590 | 0.414 | -0.045 | 0.417 | 0.006 | 1.000 | +0.007 | `upward_probability_shift` |
| `5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe01` | 590 | 0.414 | +0.001 | 0.608 | 0.997 | 0.057 | -0.005 | `downward_probability_shift` |
| `edd22318-216c-44ff-bc24-49ce8be78374_probe00` | 769 | 0.482 | +0.015 | 0.529 | 0.930 | 0.100 | -0.005 | `downward_probability_shift` |

## Interpretation

The paired true-vs-shuffle metric is not sufficient by itself. The next objective or gate should require target-0 and target-1 improvements together inside each recording, or optimize a direct recording-local AUC surrogate.

Next objective implication: replace the scalar paired-probability gate with a balanced bidirectional criterion: true labels should beat the shuffled control for target-0 and target-1 subsets separately, and improve recording-local ranking.
