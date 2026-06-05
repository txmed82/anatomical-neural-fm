# Cross-Animal Anatomical Transfer Goal Handoff

## Goal

Demonstrate a credible cross-animal anatomical transfer signal in open
computational neuroscience using auditable IBL BrainWideMap data, explicit
held-out-animal evaluation, and true-vs-shuffled anatomical controls.

The stronger long-term goal is a trained neural foundation-model mechanism that
uses anatomical information in a way that transfers across animals. The current
verified result is narrower.

## Where We Stand

The project currently supports a narrow fixed-feature anatomical-transfer demo:

- `NR_0019` is the clean strict candidate for the fixed `broad_named_anatomy`
  feature.
- `CSHL045` is aggregate-positive, but it fails the stricter recording-local
  bidirectionality gate.
- The result is useful as an open, reproducible anatomical readout benchmark,
  but it is not yet evidence that the transformer/foundation-model path learned
  the anatomical mechanism.

Important existing artifacts:

- `docs/model_free_anatomical_transfer_demo_package.md`
- `docs/fixed_broad_family_train_arm_runpod_panel.md`
- `docs/fixed_broad_family_train_arm_prediction_gate.md`
- `docs/anatomical_transfer_demo_decision.md`

## What This Branch Adds

This checkpoint adds a no-spend mechanism bridge arm:

- New arm: `region_fixed_broad_family_auxiliary`
- Base path: identity-free `region_only` transformer conditioning
- Auxiliary path: learned scalar head over fixed `broad_named_anatomy` spike
  counts
- Auxiliary feature normalization: per-recording centered counts, z-scored using
  training-split statistics
- Prediction export remains compatible with the existing `eval_predictions.jsonl`
  schema

This is intended to test whether the proven fixed-family signal can be attached
to the trainable model path before any new paid GPU run.

## Verification So Far

Focused tests passed:

```bash
uv run pytest -q tests/test_eval_design.py tests/test_train_auxiliary_fixed_family_arm.py
```

Local CPU smoke runs completed for `NR_0019` with true and
within-recording-shuffle controls:

- `runs/local_region_fixed_broad_family_auxiliary_smoke_centered/holdout_NR_0019/region_fixed_broad_family_auxiliary_none_seed0`
- `runs/local_region_fixed_broad_family_auxiliary_smoke_centered/holdout_NR_0019/region_fixed_broad_family_auxiliary_within_recording_shuffle_seed0`

These were execution checks only, not evidence runs. They used two training
steps and truncated prediction export.

Cloud state at handoff:

- RunPod active pods: `0`
- No new cloud/GPU spend for this checkpoint

## Next Pickup Steps

1. Run a bounded local CPU mini-panel for `NR_0019` using the new auxiliary arm:
   true control plus within-recording shuffle, full held-out prediction export,
   and the same response-extreme target.
2. Audit the resulting prediction rows with the existing trial-paired
   true-vs-shuffle gate.
3. If `NR_0019` passes locally, add `CSHL045` as a diagnostic case and inspect
   recording-local failures rather than aggregate AUC alone.
4. Only if the local auxiliary arm clears the gate, prepare a low-cost RunPod
   preflight. Keep the hard budget cap below `$100`, and prefer an L4 run below
   `$8`.
5. Keep claims separated:
   - fixed-feature anatomical readout: currently supported narrowly
   - trained transformer/foundation-model mechanism: still unproven
