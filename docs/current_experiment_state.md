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
