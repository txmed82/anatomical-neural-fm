# CSH Model-Free Region Signal Audit

Closed-form ridge classifier on trial-level parent-region spike counts. This tests whether the anatomical feature representation has a cross-animal signal before transformer training.

Holdout: `MFD_06`
Train trials: `13476`
Eval trials: `2265`
Regions: `79`

| feature_set | train_AUC | eval_AUC | eval_centered_AUC |
|---|---:|---:|---:|
| total_spikes | 0.512 | 0.510 | 0.499 |
| region_true | 0.617 | 0.460 | 0.488 |
| region_shuffle | 0.596 | 0.482 | 0.505 |

## True vs Shuffled Region Labels

- centered AUC delta: `-0.016`
- full AUC delta: `-0.022`
- paired true-class improved: `0.513`
- target0 improved: `0.567`
- target1 improved: `0.451`
- positive recordings: `2/4`
- decision: `no_model_free_true_region_advantage`

| recording | true_AUC | shuffle_AUC | delta |
|---|---:|---:|---:|
| 35eeb752-8f4f-4040-9714-ba0f5b7ccdfe_probe00 | 0.507 | 0.549 | -0.042 |
| 3f71aa98-08c6-4e79-b4c8-00eae4f03eff_probe00 | 0.501 | 0.496 | +0.004 |
| 6899a67d-2e53-4215-a52a-c7021b5da5d4_probe00 | 0.523 | 0.402 | +0.121 |
| a1782f4f-86b0-480c-a7f2-3d8f1ab482ab_probe00 | 0.379 | 0.522 | -0.143 |
