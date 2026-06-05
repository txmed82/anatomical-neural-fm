# CSH Model-Free Region Signal Audit

Closed-form ridge classifier on trial-level parent-region spike counts. This tests whether the anatomical feature representation has a cross-animal signal before transformer training.

Holdout: `NR_0019`
Train trials: `13317`
Eval trials: `2424`
Regions: `79`

| feature_set | train_AUC | eval_AUC | eval_centered_AUC |
|---|---:|---:|---:|
| total_spikes | 0.513 | 0.528 | 0.573 |
| region_true | 0.599 | 0.515 | 0.561 |
| region_shuffle | 0.590 | 0.486 | 0.482 |

## True vs Shuffled Region Labels

- centered AUC delta: `+0.079`
- full AUC delta: `+0.029`
- paired true-class improved: `0.508`
- target0 improved: `0.776`
- target1 improved: `0.249`
- positive recordings: `3/4`
- decision: `weak_model_free_true_region_advantage`

| recording | true_AUC | shuffle_AUC | delta |
|---|---:|---:|---:|
| 63c70ae8-4dfb-418b-b21b-f0b1e5fba6c9_probe00 | 0.500 | 0.428 | +0.072 |
| 63c70ae8-4dfb-418b-b21b-f0b1e5fba6c9_probe01 | 0.644 | 0.392 | +0.252 |
| b887df2c-bb9c-44c9-a9c0-538da87b2cab_probe00 | 0.509 | 0.543 | -0.034 |
| b887df2c-bb9c-44c9-a9c0-538da87b2cab_probe01 | 0.651 | 0.618 | +0.034 |
