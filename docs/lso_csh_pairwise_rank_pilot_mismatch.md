# Pairwise Rank Mismatch Audit

Root: `runs/lso_csh_pairwise_rank_pilot`
Holdout: `CSH_ZAD_019` seed `0`

## Global

| metric | value |
|---|---:|
| decision | `paired_metric_explained_by_downward_shift` |
| paired true-class improved | 0.552 |
| true-minus-shuffle AUC | -0.000 |
| mean raw probability delta | -0.247 |
| raw probability delta negative fraction | 1.000 |
| target0 true-class improved | 1.000 |
| target1 true-class improved | 0.000 |

## Recording Breakdown

| recording | n | target1_frac | true-shuffle AUC | paired improved | target0 improved | target1 improved | mean raw delta | class |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `49e0ab27-827a-4c91-bcaa-97eea27a1b8d_probe01` | 777 | 0.467 | -0.027 | 0.533 | 1.000 | 0.000 | -0.236 | `downward_probability_shift` |
| `5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe00` | 590 | 0.414 | +0.053 | 0.586 | 1.000 | 0.000 | -0.232 | `downward_probability_shift` |
| `5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe01` | 590 | 0.414 | -0.019 | 0.586 | 1.000 | 0.000 | -0.334 | `downward_probability_shift` |
| `edd22318-216c-44ff-bc24-49ce8be78374_probe00` | 769 | 0.482 | -0.021 | 0.518 | 1.000 | 0.000 | -0.204 | `downward_probability_shift` |

## Interpretation

The paired true-vs-shuffle improvement is explained by a mostly downward probability shift: target-0 trials improve, target-1 trials do not. This can pass a paired true-class-probability check in target-0-majority recordings without improving within-recording ranking.

Next objective implication: replace the scalar paired-probability gate with a balanced bidirectional criterion: true labels should beat the shuffled control for target-0 and target-1 subsets separately, and improve recording-local ranking.
