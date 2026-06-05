# CSH Model-Free Region Signal Audit

Closed-form ridge classifier on trial-level parent-region spike counts. This tests whether the anatomical feature representation has a cross-animal signal before transformer training.

Holdout: `CSH_ZAD_019`
Train trials: `13015`
Eval trials: `2726`
Regions: `79`

| feature_set | train_AUC | eval_AUC | eval_centered_AUC |
|---|---:|---:|---:|
| total_spikes | 0.503 | 0.555 | 0.553 |
| region_true | 0.597 | 0.499 | 0.487 |
| region_shuffle | 0.601 | 0.479 | 0.538 |

## True vs Shuffled Region Labels

- centered AUC delta: `-0.052`
- full AUC delta: `+0.020`
- paired true-class improved: `0.502`
- target0 improved: `0.338`
- target1 improved: `0.703`
- positive recordings: `1/4`
- decision: `no_model_free_true_region_advantage`

| recording | true_AUC | shuffle_AUC | delta |
|---|---:|---:|---:|
| 49e0ab27-827a-4c91-bcaa-97eea27a1b8d_probe01 | 0.427 | 0.582 | -0.155 |
| 5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe00 | 0.534 | 0.444 | +0.091 |
| 5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe01 | 0.501 | 0.516 | -0.016 |
| edd22318-216c-44ff-bc24-49ce8be78374_probe00 | 0.499 | 0.571 | -0.072 |
