# Current Anatomy-Transfer Experiment State

Decision: `no_paid_broadening_without_new_mechanism`

## Strict Gate Runs

| experiment | holdout | gate | centered_delta | paired_true_vs_shuffle | specificity_gap | target0 | target1 | sign_flip_p | outcome | source |
|---|---|---|---:|---:|---:|---:|---:|---:|---|---|
| CSH centered original | CSH_ZAD_019 | False | +0.006 | 0.536 | -0.016 | n/a | n/a | 0.062 | fail: small centered delta, paired gate, specificity, sign-flip | `docs/lso_csh_full_eval_centered_anatomy_specific_gate.json` |
| NR_0019 centered replication | NR_0019 | False | +0.012 | 0.493 | +0.000 | n/a | n/a | 0.500 | fail: paired gate, specificity, sign-flip | `docs/lso_nr0019_full_eval_centered_anatomy_specific_gate.json` |
| CSH target-balanced | CSH_ZAD_019 | False | +0.009 | 0.516 | +0.051 | n/a | n/a | 0.125 | fail: small centered delta, paired gate, sign-flip | `docs/lso_csh_target_balanced_anatomy_specific_gate.json` |
| CSH recording-centered loss | CSH_ZAD_019 | False | -0.050 | 0.451 | -0.092 | n/a | n/a | 1.000 | fail: small centered delta, paired gate, specificity, sign-flip | `docs/lso_csh_recording_centered_loss_anatomy_specific_gate.json` |
| CSH within-recording shuffle | CSH_ZAD_019 | False | +0.001 | 0.448 | -0.103 | n/a | n/a | 0.250 | fail: small centered delta, paired gate, specificity, sign-flip | `docs/lso_csh_within_recording_shuffle_anatomy_specific_gate.json` |
| CSH recording-centered gate pilot | CSH_ZAD_019 | False | +0.001 | 0.448 | -0.103 | n/a | n/a | 0.250 | fail: small centered delta, paired gate, specificity, sign-flip | `docs/lso_csh_recording_centered_gate_pilot_anatomy_specific_gate.json` |
| CSH pairwise-rank objective pilot | CSH_ZAD_019 | False | -0.014 | 0.552 | +0.103 | 1.000 | 0.000 | 0.562 | fail: small centered delta, target1, sign-flip | `docs/lso_csh_pairwise_rank_pilot_anatomy_specific_gate.json` |
| CSH pairwise-rank centered-BCE pilot | CSH_ZAD_019 | False | -0.016 | 0.486 | +0.013 | 0.354 | 0.650 | 1.000 | fail: small centered delta, paired gate, target0, sign-flip | `docs/lso_csh_pairwise_rank_centered_bce_pilot_anatomy_specific_gate.json` |

## Fixed-Slice Runs

| experiment | holdout | true_delta | shuffle_delta | true_minus_shuffle | true_positive | shuffle_positive | outcome | source |
|---|---|---:|---:|---:|---:|---:|---|---|
| NYU-12 fixed carrier slice | NYU-12 | +0.013 | +0.020 | -0.007 | 2/3 | 3/3 | shuffle >= true | `docs/lso_nyu12_parent_slice_results.md` |
| SWC_038 stricter carrier slice | SWC_038 | -0.004 | +0.019 | -0.023 | 0/2 | 2/2 | shuffle >= true | `docs/lso_swc038_parent_slice_results.md` |

## Decision

No current strict-gate artifact supports paid broadening. The later recording-matched controls show the CSH true-region advantage is much smaller than the original sampled-eval signal, and both fixed carrier slice attempts let shuffled labels match or beat true labels.

Next mechanism: The bidirectional target-class gate and explicit recording-local AUC surrogate are now implemented. The next no-spend task is local objective debugging that can satisfy target0, target1, and recording-local AUC checks before any more paid broadening.

## Mechanism Audit Follow-Up

`docs/csh_mechanism_audit.md` performs that saved-artifact audit on the
recording-centered gate pilot. It does not find a transferable anatomical
mechanism:

- global paired true-vs-shuffle remains `0.448`
- specificity gap is `-0.103`
- carrier-parent embeddings are nearly identical between true and shuffled controls, with mean carrier cosine `0.992`
- carrier-rich negative recordings: `4`

Updated mechanism decision: no paid run is justified until the objective itself forces target-aware true-vs-shuffle separation. Region/subject selection and embedding inspection did not reveal a mechanism that the current controls can validate.

## Pairwise-Rank Objective Pilot

`docs/lso_csh_pairwise_rank_pilot_results.md` ran the implemented
`recording_pairwise_rank` objective on a one-seed L4 RunPod pilot. It improved
the global paired true-vs-shuffle check to `0.552`
and the specificity gap to `+0.103`,
so the objective change did move the right target-aware paired metric.

The strict anatomy-specific gate still failed:

- centered true-minus-shuffle delta: `-0.014`
- paired true-vs-shuffle: `0.552`
- specificity gap: `+0.103`
- recording sign-flip p-value: `0.562`

Updated decision before the mismatch audit: possible mechanism candidate, not demo evidence. Do not broaden yet; require a diagnostic that separates bidirectional target-aware ranking from one-direction probability shifts.

Pairwise mismatch audit: `docs/lso_csh_pairwise_rank_pilot_mismatch.md`
classifies the paired improvement as `paired_metric_explained_by_downward_shift`.
Raw probabilities moved downward on `1.000`
of paired trials; target-0 true-class probability improved on
`1.000`
of trials while target-1 improved on
`0.000`.

Next candidate objective: `recording_pairwise_rank_centered_bce`, which keeps the recording-local pairwise rank term but adds recording-centered BCE so a one-direction probability shift is not mistaken for anatomical ranking evidence.

Updated decision after mismatch audit: the scalar paired metric should not be used as a success gate. Require bidirectional target-class improvement and positive recording-local AUC against the shuffled control.

## Pairwise-Rank Centered-BCE Pilot

`docs/lso_csh_pairwise_rank_centered_bce_pilot_results.md` tested the
`recording_pairwise_rank_centered_bce` objective. It removed the previous
all-trial downward probability shift but did not produce anatomical transfer.

- centered true-minus-shuffle delta: `-0.016`
- paired true-vs-shuffle: `0.486`
- specificity gap: `+0.013`
- recording sign-flip p-value: `1.000`
- mechanism decision: `no_mechanism_found`
- mismatch decision: `paired_metric_not_recording_rank_stable`
- target0 true-class improved: `0.354`
- target1 true-class improved: `0.650`
- mechanism paired true-vs-shuffle: `0.486`

Updated decision: stop paid one-off objective variants for now. Use the implemented bidirectional gate and `recording_local_auc_surrogate` only for local objective debugging until a candidate satisfies target0, target1, and recording-local AUC checks.

## Local AUC-Surrogate Probe

`scripts/run_local_objective_probe.py` runs a no-spend tiny CPU probe with
deterministic held-out predictions and immediate strict-gate/mismatch audits.
The first probe used `recording_local_auc_surrogate` for two CPU steps.

- gate pass: `False`
- centered true-minus-shuffle delta: `-0.005`
- paired true-vs-shuffle: `0.494`
- target0 true-class improved: `0.556`
- target1 true-class improved: `0.419`
- positive recordings: `2/4`
- mismatch decision: `paired_metric_not_recording_rank_stable`
- true-minus-shuffle AUC: `-0.009`

Decision: reject this objective configuration locally. It does not justify a RunPod launch because it fails target1, centered AUC, and recording support.

## Local Probe Matrix

These CPU-only probes are the current promotion gate for objective and sampling variants. A candidate should pass the strict gate locally before any new RunPod spend.

| probe | gate | centered_delta | paired_true_vs_shuffle | specificity_gap | target0 | target1 | recordings | mismatch | outcome |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| local AUC surrogate | False | -0.005 | 0.494 | +0.030 | 0.556 | 0.419 | 2/4 | `paired_metric_not_recording_rank_stable` | reject: centered AUC, target1, recording support, mismatch |
| local recording-centered BCE | False | -0.005 | 0.494 | +0.029 | 0.557 | 0.416 | 2/4 | `paired_metric_not_recording_rank_stable` | reject: centered AUC, target1, recording support, mismatch |
| local rank + centered BCE | False | -0.005 | 0.494 | +0.030 | 0.556 | 0.419 | 2/4 | `paired_metric_not_recording_rank_stable` | reject: centered AUC, target1, recording support, mismatch |
| local AUC surrogate target-balanced | False | -0.005 | 0.502 | +0.039 | 0.580 | 0.406 | 2/4 | `paired_metric_not_recording_rank_stable` | reject: centered AUC, target1, recording support, mismatch |

Decision: all current tiny local variants are rejected for cloud promotion. They repeatedly improve target-0 more than target-1, lose centered true-vs-shuffle AUC, or fail recording support. The next no-spend step is to redesign the sampler/objective so both target classes improve within recordings before any paid run.

## Batch Sampling Contrast Audit

`docs/csh_batch_sampling_contrast_audit.md` checks whether samplers create
same-recording target-0/target-1 pairs before training. This is the minimum
condition for recording-local ranking losses to be active.

| sampler | target1_fraction | rankable_batch_fraction | mean_rankable_pairs | same_recording_adjacent_pairs |
|---|---:|---:|---:|---:|
| uniform | 0.477 | 0.022 | 0.022 | 0.022 |
| target_balanced | 0.500 | 0.040 | 0.040 | 0.040 |
| recording_target_balanced | 0.500 | 1.000 | 1.000 | 1.000 |

Interpretation: `recording_target_balanced` makes the recording-local rank loss active in every audited batch, while uniform and target-balanced sampling rarely produce same-recording contrast. Since the local probe matrix still fails under `recording_target_balanced`, the next failure is not pair availability; it is the anatomy/control signal or objective itself.

## Model-Free Region Signal Audit

`docs/csh_model_free_region_signal_audit.md` removes the transformer and
tests closed-form ridge classifiers on trial-level parent-region spike counts.

| feature_set | train_AUC | eval_AUC | eval_centered_AUC |
|---|---:|---:|---:|
| total_spikes | 0.503 | 0.555 | 0.553 |
| region_true | 0.597 | 0.499 | 0.487 |
| region_shuffle | 0.601 | 0.479 | 0.538 |

- true-minus-shuffle centered AUC: `-0.052`
- true-minus-total centered AUC: `-0.066`
- paired target0 improved vs shuffle: `0.338`
- paired target1 improved vs shuffle: `0.703`
- positive recordings vs shuffle: `1/4`
- decision: `no_model_free_true_region_advantage`

Interpretation: the current parent-region spike-count representation does not show model-free anatomical transfer for CSH. True region labels are worse than shuffled labels on recording-centered AUC and worse than a total-spike-count baseline, so the next no-spend step should redesign the anatomical feature/control target rather than spend on another neural model run.

## Model-Free Single-Region Candidate Scan

`docs/csh_model_free_region_candidate_scan.md` scans each parent region as a
single-feature ridge model against within-recording shuffled labels and the
total-spike baseline.

Candidates passing the strict local gate: `0`

| region | outcome | centered_AUC | delta_vs_shuffle | delta_vs_total | target0 | target1 | recordings | eval_nonzero |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| IB | reject: target0 | 0.728 | +0.300 | +0.175 | 0.275 | 0.703 | 1/4 | 0.285 |
| MBmot | reject: target1 | 0.645 | +0.226 | +0.092 | 0.820 | 0.219 | 1/4 | 0.285 |
| BS | reject: target0 | 0.672 | +0.225 | +0.119 | 0.015 | 0.991 | 1/4 | 0.285 |
| LZ | reject: target0 | 0.612 | +0.174 | +0.059 | 0.114 | 0.913 | 0/4 | 0.216 |
| RSPd | reject: target1 | 0.637 | +0.173 | +0.084 | 0.951 | 0.070 | 1/4 | 0.282 |
| CA | reject: target0 | 0.680 | +0.157 | +0.127 | 0.320 | 0.721 | 2/4 | 0.501 |
| DG | reject: target0 | 0.700 | +0.126 | +0.147 | 0.285 | 0.718 | 2/4 | 0.501 |
| VENT | reject: target0 | 0.578 | +0.119 | +0.025 | 0.230 | 0.800 | 0/4 | 0.216 |

Interpretation: no individual parent region is strong enough to promote. The best evaluable regions beat shuffle and total-spike baselines only in one target direction or too few recordings. The next no-spend feature step should test predefined aggregate region families or a different conserved target, not a GPU model run.

## Model-Free Region-Family Candidate Scan

`docs/csh_model_free_region_family_scan.md` scans predefined aggregate
region families as one-feature ridge models against within-recording
shuffled labels and the total-spike baseline.

Candidates passing the strict local gate: `0`

| family | outcome | centered_AUC | delta_vs_shuffle | delta_vs_total | target0 | target1 | recordings | eval_nonzero |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| basal_ganglia | reject: target1 | 0.607 | +0.100 | +0.157 | 1.000 | 0.000 | 1/4 | 0.499 |
| brainstem_interbrain | reject: target0 | 0.572 | +0.035 | +0.122 | 0.036 | 0.972 | 1/4 | 0.501 |
| cortical_retrosplenial | reject: target1 | 0.548 | +0.015 | +0.098 | 0.890 | 0.146 | 1/4 | 0.567 |
| hippocampal_formation | reject: target0 | 0.582 | +0.010 | +0.132 | 0.305 | 0.709 | 2/4 | 0.784 |
| cortical_sensorimotor | reject: shuffle | 0.587 | +0.008 | +0.137 | 0.701 | 0.282 | 1/4 | 0.433 |
| broad_named_anatomy | reject: shuffle | 0.451 | +0.003 | +0.001 | 0.698 | 0.362 | 2/4 | 1.000 |
| fiber_tracts | reject: shuffle | 0.551 | +0.002 | +0.101 | 0.507 | 0.481 | 1/4 | 1.000 |
| thalamic | reject: shuffle | 0.530 | -0.017 | +0.080 | 0.381 | 0.581 | 0/4 | 1.000 |

Interpretation: predefined region-family aggregates also fail the model-free promotion gate. The evidence now argues against spending on another CSH parent-region model variant. The next branch should be an alternative conserved target or a larger matched-region manifest audit.

## Alternative Target: Choice

The same model-free gates were rerun with `--target-mode choice` to test
whether a different behavioral target exposes anatomical transfer.

| feature_set | train_AUC | eval_AUC | eval_centered_AUC |
|---|---:|---:|---:|
| total_spikes | 0.518 | 0.456 | 0.389 |
| region_true | 0.636 | 0.477 | 0.480 |
| region_shuffle | 0.639 | 0.540 | 0.566 |

- true-minus-shuffle centered AUC: `-0.086`
- true-minus-total centered AUC: `+0.091`
- paired target0 improved vs shuffle: `0.807`
- paired target1 improved vs shuffle: `0.200`
- positive recordings vs shuffle: `2/4`
- full-region decision: `no_model_free_true_region_advantage`
- single-region candidates: `0`
- region-family candidates: `0`

Interpretation: `choice` does not rescue the CSH parent-region branch. Shuffled parent labels still beat true labels on recording-centered AUC, and the single-region/family scans find no promotable candidate.
