# CSH Model-Free Region Signal Audit

Closed-form ridge classifier on trial-level parent-region spike counts. This tests whether the anatomical feature representation has a cross-animal signal before transformer training.

Holdout: `NYU-12`
Train trials: `13866`
Eval trials: `1875`
Regions: `79`

| feature_set | train_AUC | eval_AUC | eval_centered_AUC |
|---|---:|---:|---:|
| total_spikes | 0.515 | 0.483 | 0.505 |
| region_true | 0.612 | 0.479 | 0.484 |
| region_shuffle | 0.597 | 0.460 | 0.500 |

## True vs Shuffled Region Labels

- centered AUC delta: `-0.015`
- full AUC delta: `+0.019`
- paired true-class improved: `0.513`
- target0 improved: `0.410`
- target1 improved: `0.624`
- positive recordings: `2/4`
- decision: `no_model_free_true_region_advantage`

| recording | true_AUC | shuffle_AUC | delta |
|---|---:|---:|---:|
| 032ffcdf-7692-40b3-b9ff-8def1fc18b2e_probe00 | 0.438 | 0.428 | +0.009 |
| a8a8af78-16de-4841-ab07-fde4b5281a03_probe00 | 0.483 | 0.564 | -0.081 |
| a8a8af78-16de-4841-ab07-fde4b5281a03_probe01 | 0.544 | 0.524 | +0.020 |
| b182b754-3c3e-4942-8144-6ee790926b58_probe01 | 0.454 | 0.503 | -0.049 |
