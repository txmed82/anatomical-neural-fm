# Current Anatomy-Transfer Experiment State

Decision: `no_paid_broadening_without_new_mechanism`

## Strict Gate Runs

| experiment | holdout | gate | centered_delta | paired_true_vs_shuffle | specificity_gap | sign_flip_p | outcome | source |
|---|---|---|---:|---:|---:|---:|---|---|
| CSH centered original | CSH_ZAD_019 | False | +0.006 | 0.536 | -0.016 | 0.062 | fail: small centered delta, paired gate, specificity, sign-flip | `docs/lso_csh_full_eval_centered_anatomy_specific_gate.json` |
| NR_0019 centered replication | NR_0019 | False | +0.012 | 0.493 | +0.000 | 0.500 | fail: paired gate, specificity, sign-flip | `docs/lso_nr0019_full_eval_centered_anatomy_specific_gate.json` |
| CSH target-balanced | CSH_ZAD_019 | False | +0.009 | 0.516 | +0.051 | 0.125 | fail: small centered delta, paired gate, sign-flip | `docs/lso_csh_target_balanced_anatomy_specific_gate.json` |
| CSH recording-centered loss | CSH_ZAD_019 | False | -0.050 | 0.451 | -0.092 | 1.000 | fail: small centered delta, paired gate, specificity, sign-flip | `docs/lso_csh_recording_centered_loss_anatomy_specific_gate.json` |
| CSH within-recording shuffle | CSH_ZAD_019 | False | +0.001 | 0.448 | -0.103 | 0.250 | fail: small centered delta, paired gate, specificity, sign-flip | `docs/lso_csh_within_recording_shuffle_anatomy_specific_gate.json` |
| CSH recording-centered gate pilot | CSH_ZAD_019 | False | +0.001 | 0.448 | -0.103 | 0.250 | fail: small centered delta, paired gate, specificity, sign-flip | `docs/lso_csh_recording_centered_gate_pilot_anatomy_specific_gate.json` |

## Fixed-Slice Runs

| experiment | holdout | true_delta | shuffle_delta | true_minus_shuffle | true_positive | shuffle_positive | outcome | source |
|---|---|---:|---:|---:|---:|---:|---|---|
| NYU-12 fixed carrier slice | NYU-12 | +0.013 | +0.020 | -0.007 | 2/3 | 3/3 | shuffle >= true | `docs/lso_nyu12_parent_slice_results.md` |
| SWC_038 stricter carrier slice | SWC_038 | -0.004 | +0.019 | -0.023 | 0/2 | 2/2 | shuffle >= true | `docs/lso_swc038_parent_slice_results.md` |

## Decision

No current strict-gate artifact supports paid broadening. The later recording-matched controls show the CSH true-region advantage is much smaller than the original sampled-eval signal, and both fixed carrier slice attempts let shuffled labels match or beat true labels.

Next mechanism: Define a mechanism-level analysis of the CSH success itself: compare true vs within-recording-shuffled region embeddings and prediction shifts by carrier parent and recording, then implement a training objective/control that requires true anatomical labels to improve target-aware within-recording ranking.

A useful next artifact would be a CSH mechanism audit over saved predictions and region embeddings, not another RunPod launch.

## Mechanism Audit Follow-Up

`docs/csh_mechanism_audit.md` performs that saved-artifact audit on the
recording-centered gate pilot. It does not find a transferable anatomical
mechanism:

- global paired true-vs-shuffle remains `0.448`
- specificity gap is `-0.103`
- carrier-parent embeddings are nearly identical between true and shuffled controls, with mean carrier cosine `0.992`
- carrier-rich negative recordings: `4`

Updated mechanism decision: no paid run is justified until the objective itself forces target-aware true-vs-shuffle separation. Region/subject selection and embedding inspection did not reveal a mechanism that the current controls can validate.
