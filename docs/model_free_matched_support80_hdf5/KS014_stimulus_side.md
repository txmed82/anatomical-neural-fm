# CSH Model-Free Region Signal Audit

Closed-form ridge classifier on trial-level parent-region spike counts. This tests whether the anatomical feature representation has a cross-animal signal before transformer training.

Holdout: `KS014`
Train trials: `13614`
Eval trials: `2127`
Regions: `79`

| feature_set | train_AUC | eval_AUC | eval_centered_AUC |
|---|---:|---:|---:|
| total_spikes | 0.515 | 0.509 | 0.538 |
| region_true | 0.611 | 0.565 | 0.588 |
| region_shuffle | 0.600 | 0.502 | 0.558 |

## True vs Shuffled Region Labels

- centered AUC delta: `+0.030`
- full AUC delta: `+0.063`
- paired true-class improved: `0.543`
- target0 improved: `0.547`
- target1 improved: `0.538`
- positive recordings: `2/4`
- decision: `weak_model_free_true_region_advantage`

| recording | true_AUC | shuffle_AUC | delta |
|---|---:|---:|---:|
| 16693458-0801-4d35-a3f1-9115c7e5acfd_probe00 | 0.565 | 0.495 | +0.071 |
| 16693458-0801-4d35-a3f1-9115c7e5acfd_probe01 | 0.537 | 0.567 | -0.030 |
| b9c205c3-feac-485b-a89d-afc96d9cb280_probe00 | 0.577 | 0.672 | -0.094 |
| e1931de1-cf7b-49af-af33-2ade15e8abe7_probe00 | 0.665 | 0.562 | +0.103 |
