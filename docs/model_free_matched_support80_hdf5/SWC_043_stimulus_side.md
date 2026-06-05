# CSH Model-Free Region Signal Audit

Closed-form ridge classifier on trial-level parent-region spike counts. This tests whether the anatomical feature representation has a cross-animal signal before transformer training.

Holdout: `SWC_043`
Train trials: `13853`
Eval trials: `1888`
Regions: `79`

| feature_set | train_AUC | eval_AUC | eval_centered_AUC |
|---|---:|---:|---:|
| total_spikes | 0.513 | 0.488 | 0.445 |
| region_true | 0.614 | 0.466 | 0.470 |
| region_shuffle | 0.590 | 0.471 | 0.483 |

## True vs Shuffled Region Labels

- centered AUC delta: `-0.014`
- full AUC delta: `-0.005`
- paired true-class improved: `0.486`
- target0 improved: `0.738`
- target1 improved: `0.212`
- positive recordings: `2/4`
- decision: `no_model_free_true_region_advantage`

| recording | true_AUC | shuffle_AUC | delta |
|---|---:|---:|---:|
| 4ecb5d24-f5cc-402c-be28-9d0f7cb14b3a_probe00 | 0.469 | 0.499 | -0.030 |
| 6f09ba7e-e3ce-44b0-932b-c003fb44fb89_probe01 | 0.512 | 0.496 | +0.017 |
| 6fb1e12c-883b-46d1-a745-473cde3232c8_probe00 | 0.469 | 0.468 | +0.001 |
| 88d24c31-52e4-49cc-9f32-6adbeb9eba87_probe00 | 0.422 | 0.482 | -0.060 |
