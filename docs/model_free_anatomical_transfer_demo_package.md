# Model-Free Anatomical Transfer Demo Package

## Claim

Supported: A narrow model-free cross-animal anatomical readout exists for post-error response-latency extremes using a fixed broad_named_anatomy aggregate.

Not supported yet: A trained neural foundation-model anatomical transfer signal is not yet supported: the A100 pilot and cloud-aligned local readout were negative.

## Status

- decision: `package_model_free_demo`
- model-free demo ready: `True`
- trained-model demo ready: `False`
- paid GPU trigger: `False`
- next action: Use this as a narrow reproducible model-free demo, with the trainable fixed-feature bridge plus local/cloud train.py fixed-family arms as intermediate checks. Treat the remaining gap as the stronger transformer/foundation-model mechanism.

## Positive Evidence

| holdout | target | family | candidate seeds | delta shuffle | delta total | targets | bidir range |
|---|---|---|---:|---:|---:|---:|---:|
| CSHL045 | post_error_response_extreme_25_75_le_1 | broad_named_anatomy | 5/5 | +0.0507 | +0.0366 | 0.700/0.800 | 3-3 |
| NR_0019 | post_error_response_extreme_33_67_le_1 | broad_named_anatomy | 5/5 | +0.0051 | +0.0042 | 0.656/0.684 | 3-4 |

## Negative Controls

- A100 training decision: `negative_training_pilot`; true-positive cases `0/2`
- cloud-aligned local readout: `no_training_aligned_true_region_advantage`
- failure audit: `local_to_training_readout_mismatch`
- blockers: `no_full_eval_or_prediction_diagnostics, shuffled_region_outperformed_true, trained_true_region_lost_to_shared`

## Reproduce

```bash
uv run python scripts/audit_composite_behavior_target_family_gate.py --manifest manifests/ibl_bwm_local_cached_external_support80_projected_hdf5.json --out-json docs/composite_behavior_response_extreme_family_gate_projected_hdf5.json --out-md docs/composite_behavior_response_extreme_family_gate_projected_hdf5.md --target post_error_response_extreme_25_75_le_1 post_error_response_extreme_33_67_le_1
uv run python scripts/audit_composite_behavior_response_extreme_seed_sensitivity.py
uv run python scripts/audit_response_extreme_training_aligned_readout.py
uv run python scripts/audit_direct_broad_family_demo_readiness.py
uv run python scripts/audit_direct_broad_family_trainable_readout.py
uv run python scripts/summarize_fixed_broad_family_train_arm_panel.py
uv run python scripts/package_model_free_demo.py
```

## Boundaries

- This is a model-free ridge/count readout demo, not a trained transformer demo.
- The positive feature is the fixed broad_named_anatomy aggregate, not the full shared parent-region feature vector.
- The local and cloud train.py fixed-family arms are positive, but this still does not establish a transformer/foundation-model anatomical mechanism.
