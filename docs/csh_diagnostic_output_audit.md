# CSH Diagnostic Output Audit

Root: `runs/lso_csh_diagnostic_outputs`

## Available Prediction Artifacts

| arm | seed | rows | AUC | accuracy | mean_prob_target0 | mean_prob_target1 | delta_vs_shared_same_seed | path |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| region_only | 0 | 2726 | 0.508 | 0.552 | 0.476 | 0.476 | +0.008 | `runs/lso_csh_diagnostic_outputs/holdout_CSH_ZAD_019/cloud_choice_region_only_seed0/eval_predictions.jsonl` |
| region_shuffle | 0 | 2726 | 0.509 | 0.552 | 0.477 | 0.477 | +0.009 | `runs/lso_csh_diagnostic_outputs/holdout_CSH_ZAD_019/cloud_choice_region_shuffle_seed0/eval_predictions.jsonl` |
| shared_baseline | 0 | 2726 | 0.500 | 0.552 | 0.457 | 0.457 | +0.000 | `runs/lso_csh_diagnostic_outputs/holdout_CSH_ZAD_019/cloud_choice_shared_baseline_seed0/eval_predictions.jsonl` |
| shared_baseline | 1 | 2726 | 0.515 | 0.448 | 0.527 | 0.527 | +0.000 | `runs/lso_csh_diagnostic_outputs/holdout_CSH_ZAD_019/cloud_choice_shared_baseline_seed1/eval_predictions.jsonl` |

## Per-Recording AUC

| arm | seed | recording | rows | AUC | accuracy |
|---|---:|---|---:|---:|---:|
| region_only | 0 | `49e0ab27-827a-4c91-bcaa-97eea27a1b8d_probe01` | 777 | 0.497 | 0.533 |
| region_only | 0 | `5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe00` | 590 | 0.544 | 0.590 |
| region_only | 0 | `5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe01` | 590 | 0.547 | 0.586 |
| region_only | 0 | `edd22318-216c-44ff-bc24-49ce8be78374_probe00` | 769 | 0.509 | 0.518 |
| region_shuffle | 0 | `49e0ab27-827a-4c91-bcaa-97eea27a1b8d_probe01` | 777 | 0.506 | 0.533 |
| region_shuffle | 0 | `5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe00` | 590 | 0.517 | 0.586 |
| region_shuffle | 0 | `5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe01` | 590 | 0.528 | 0.586 |
| region_shuffle | 0 | `edd22318-216c-44ff-bc24-49ce8be78374_probe00` | 769 | 0.496 | 0.518 |
| shared_baseline | 0 | `49e0ab27-827a-4c91-bcaa-97eea27a1b8d_probe01` | 777 | 0.513 | 0.533 |
| shared_baseline | 0 | `5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe00` | 590 | 0.491 | 0.586 |
| shared_baseline | 0 | `5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe01` | 590 | 0.499 | 0.586 |
| shared_baseline | 0 | `edd22318-216c-44ff-bc24-49ce8be78374_probe00` | 769 | 0.494 | 0.518 |
| shared_baseline | 1 | `49e0ab27-827a-4c91-bcaa-97eea27a1b8d_probe01` | 777 | 0.491 | 0.467 |
| shared_baseline | 1 | `5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe00` | 590 | 0.522 | 0.414 |
| shared_baseline | 1 | `5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe01` | 590 | 0.529 | 0.414 |
| shared_baseline | 1 | `edd22318-216c-44ff-bc24-49ce8be78374_probe00` | 769 | 0.525 | 0.482 |

## Seed-0 Per-Recording Delta vs Shared Baseline

| arm | recording | rows | AUC | baseline_AUC | delta_AUC | mean_prob_delta | mean_abs_prob_delta | true_prob_improved |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| region_only | `49e0ab27-827a-4c91-bcaa-97eea27a1b8d_probe01` | 777 | 0.497 | 0.513 | -0.016 | +0.007 | 0.010 | 0.490 |
| region_only | `5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe00` | 590 | 0.544 | 0.491 | +0.053 | +0.026 | 0.026 | 0.414 |
| region_only | `5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe01` | 590 | 0.547 | 0.499 | +0.048 | +0.021 | 0.021 | 0.414 |
| region_only | `edd22318-216c-44ff-bc24-49ce8be78374_probe00` | 769 | 0.509 | 0.494 | +0.015 | +0.023 | 0.023 | 0.482 |
| region_shuffle | `49e0ab27-827a-4c91-bcaa-97eea27a1b8d_probe01` | 777 | 0.506 | 0.513 | -0.007 | +0.020 | 0.020 | 0.467 |
| region_shuffle | `5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe00` | 590 | 0.517 | 0.491 | +0.026 | +0.020 | 0.020 | 0.414 |
| region_shuffle | `5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe01` | 590 | 0.528 | 0.499 | +0.029 | +0.020 | 0.020 | 0.414 |
| region_shuffle | `edd22318-216c-44ff-bc24-49ce8be78374_probe00` | 769 | 0.496 | 0.494 | +0.001 | +0.020 | 0.020 | 0.482 |

## Seed-0 Paired Trial Probability Shift vs Shared Baseline

| arm | paired_trials | mean_prob_delta | mean_abs_prob_delta | mean_delta_target0 | mean_delta_target1 | true_prob_improved |
|---|---:|---:|---:|---:|---:|---:|
| region_only | 2726 | +0.019 | 0.020 | +0.019 | +0.019 | 0.455 |
| region_shuffle | 2726 | +0.020 | 0.020 | +0.020 | +0.020 | 0.448 |

## Seed-0 Region Embedding Diagnostics

| region | true_norm | shuffled_norm | true_shuffle_cosine |
|---|---:|---:|---:|
| PRT | 0.195 | 0.194 | 0.997 |
| CA | 0.174 | 0.174 | 0.995 |
| VP | 0.198 | 0.195 | 0.990 |
| MOp | 0.226 | 0.221 | 0.996 |
| DG | 0.202 | 0.202 | 0.992 |
| mfbc | 0.185 | 0.183 | 0.994 |

## Interpretation

This is a partial diagnostic run, not a completed three-seed sweep. The pod terminated before `summary.md`, but it preserved full held-out prediction exports for seed 0 `shared_baseline`, `region_only`, and `region_shuffle`, plus seed 1 `shared_baseline`.

For seed 0, exported predictions give `region_only` delta +0.008 AUC vs the exported shared baseline and `region_shuffle` delta +0.009 AUC. Use this artifact-level result to inspect where the canonical aggregate lift comes from before launching additional candidate subjects.

Paired trial comparisons show that both seed-0 anatomy arms mostly shift probabilities upward relative to the shared baseline rather than moving probabilities toward the true class: `region_only` mean probability delta +0.019 with true-class improvement on 0.455 of paired trials, and `region_shuffle` mean probability delta +0.020 with true-class improvement on 0.448 of paired trials.

The strongest true-label per-recording gains are on the two `5adab0b7` probes, but the shuffled-label control also improves those probes. That makes the surviving seed-0 full-trial signal look more like calibration/probe-specific behavior than a clean anatomical identity code.

