# Direct Broad-Family Demo Readiness

Synthesis of the response-extreme fixed-family local trigger after the negative A100 pilot.

- decision: `model_free_demo_only`
- model-free demo ready: `True`
- trained-model demo ready: `False`
- robust local rows: `2`
- model-free demo rows: `2`
- A100 decision: `negative_training_pilot` (0/2 true-positive cases)
- training-aligned readout: `no_training_aligned_true_region_advantage`
- next action: Package the result as a narrow model-free cross-animal anatomical readout, or implement a direct fixed broad-family-count model arm before any new GPU run.

| holdout | target | family | candidate seeds | delta shuffle | delta total | targets | bidir range |
|---|---|---|---:|---:|---:|---:|---:|
| CSHL045 | post_error_response_extreme_25_75_le_1 | broad_named_anatomy | 5/5 | +0.0507 | +0.0366 | 0.700/0.800 | 3-3 |
| NR_0019 | post_error_response_extreme_33_67_le_1 | broad_named_anatomy | 5/5 | +0.0051 | +0.0042 | 0.656/0.684 | 3-4 |

## Interpretation

- The fixed broad_named_anatomy aggregate remains the only positive response-extreme evidence.
- The learned parent-region embedding pilot and the shared parent-region ridge readout are both negative.
- A demo can currently claim only a narrow model-free cross-animal anatomical readout, not a trained anatomical foundation-model transfer signal.

## Decision

Package the result as a narrow model-free cross-animal anatomical readout, or implement a direct fixed broad-family-count model arm before any new GPU run.

