# CSH Model-Free Region Signal Audit

Closed-form ridge classifier on trial-level parent-region spike counts. This tests whether the anatomical feature representation has a cross-animal signal before transformer training.

Holdout: `SWC_038`
Train trials: `13305`
Eval trials: `2436`
Regions: `79`

| feature_set | train_AUC | eval_AUC | eval_centered_AUC |
|---|---:|---:|---:|
| total_spikes | 0.510 | 0.529 | 0.522 |
| region_true | 0.612 | 0.505 | 0.489 |
| region_shuffle | 0.594 | 0.515 | 0.521 |

## True vs Shuffled Region Labels

- centered AUC delta: `-0.032`
- full AUC delta: `-0.010`
- paired true-class improved: `0.486`
- target0 improved: `0.629`
- target1 improved: `0.336`
- positive recordings: `0/4`
- decision: `no_model_free_true_region_advantage`

| recording | true_AUC | shuffle_AUC | delta |
|---|---:|---:|---:|
| 03063955-2523-47bd-ae57-f7489dd40f15_probe01 | 0.525 | 0.558 | -0.033 |
| 1e45d992-c356-40e1-9be1-a506d944896f_probe01 | 0.482 | 0.494 | -0.011 |
| 41872d7f-75cb-4445-bb1a-132b354c44f0_probe01 | 0.526 | 0.528 | -0.002 |
| 4d8c7767-981c-4347-8e5e-5d5fffe38534_probe01 | 0.466 | 0.513 | -0.048 |
