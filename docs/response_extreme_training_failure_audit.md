# Response-Extreme Training Failure Audit

Compares the local response-extreme training trigger with the completed A100 pilot.

- cases: `2`
- decision: `local_to_training_readout_mismatch`
- paid GPU trigger: `False`
- next recommended action: `local_training_aligned_readout_diagnostic`
- blockers: `no_full_eval_or_prediction_diagnostics, shuffled_region_outperformed_true, trained_true_region_lost_to_shared`

| holdout | target | target trials | cloud train/eval | eval sample draws/trial | local delta shuffle | cloud true delta | cloud shuffle delta | failure modes |
|---|---|---:|---:|---:|---:|---:|---:|---|
| CSHL045 | post_error_response_extreme_25_75_le_1 | 1942 | 1666/276 | 320 (1.16) | +0.0507 | -0.065 | +0.041 | trained_true_region_lost_to_shared, shuffled_region_outperformed_true, sampled_eval_loss_selection, no_full_eval_or_prediction_diagnostics, local_feature_not_training_arm |
| NR_0019 | post_error_response_extreme_33_67_le_1 | 2538 | 2310/228 | 320 (1.40) | +0.0051 | -0.037 | +0.004 | trained_true_region_lost_to_shared, shuffled_region_outperformed_true, sampled_eval_loss_selection, no_full_eval_or_prediction_diagnostics, local_feature_not_training_arm |

## Interpretation

- Response-extreme target construction transferred to cloud: cloud train+eval trials match projected local trial counts.
- The local trigger was a recording-centered broad-family count feature, not the trained parent-region embedding arm.
- The cloud pilot selected by sampled eval_loss and did not save full-eval predictions, so the trained output cannot be checked with the strict recording-centered paired gate.
- True region labels underperformed the shared baseline in both tested cases while shuffled labels were non-negative, so more paid seeds are not justified before a local training-aligned diagnostic.

## Next Steps

1. Run a no-spend local readout using the exact cloud feature space: parent shared-region count vector plus true/shuffled controls, not only broad_named_anatomy aggregates.
2. If a future GPU run is justified, require SAVE_DIAGNOSTICS=1, FULL_EVAL_ON_BEST=1, and BEST_METRIC=full_eval_centered_auc so the trained outputs can be scored by the same recording-centered gate.
3. Consider a model arm that exposes the local successful feature directly, such as a fixed broad-family-count readout, before returning to learned region embeddings.
