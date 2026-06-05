# CSH Model-Free Region Signal Audit

Closed-form ridge classifier on trial-level parent-region spike counts. This tests whether the anatomical feature representation has a cross-animal signal before transformer training.

Holdout: `CSH_ZAD_019`
Train trials: `14680`
Eval trials: `3106`
Regions: `79`

| feature_set | train_AUC | eval_AUC | eval_centered_AUC |
|---|---:|---:|---:|
| total_spikes | 0.518 | 0.456 | 0.389 |
| region_true | 0.636 | 0.477 | 0.480 |
| region_shuffle | 0.639 | 0.540 | 0.566 |

## True vs Shuffled Region Labels

- centered AUC delta: `-0.086`
- full AUC delta: `-0.063`
- paired true-class improved: `0.507`
- target0 improved: `0.807`
- target1 improved: `0.200`
- positive recordings: `2/4`
- decision: `no_model_free_true_region_advantage`

| recording | true_AUC | shuffle_AUC | delta |
|---|---:|---:|---:|
| 49e0ab27-827a-4c91-bcaa-97eea27a1b8d_probe01 | 0.356 | 0.655 | -0.299 |
| 5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe00 | 0.543 | 0.455 | +0.088 |
| 5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe01 | 0.562 | 0.495 | +0.066 |
| edd22318-216c-44ff-bc24-49ce8be78374_probe00 | 0.483 | 0.606 | -0.124 |
