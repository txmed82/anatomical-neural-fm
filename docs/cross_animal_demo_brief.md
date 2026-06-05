# Cross-Animal Anatomy Transfer Demo Brief

## Current Claim

The project has a controlled, subject-specific cross-animal anatomical transfer
signal on the matched 28-recording IBL subset:

> For held-out `CSH_ZAD_019`, anatomical region identity improves
> stimulus-side decoding relative to a shared null, and the lift collapses when
> region labels are shuffled.

This is not yet a general cross-animal result across IBL animals. It is a
credible demo nucleus. The first completed broadening experiment is directionally
consistent but too weak to claim generality, and subsequent targeted
broadening attempts have not reproduced the CSH-sized controlled effect.

## Evidence Table

| result | setting | true anatomy delta | shuffled anatomy delta | seed support |
|---|---|---:|---:|---:|
| matched confirmation | fine regions, seeds 0-2 | +0.042 | n/a | 3/3 true positive |
| fine shuffle control | fine regions, seeds 0-2 | +0.042 | -0.012 | true 3/3, shuffled 1/3 |
| shared-parent shuffle control | shared parent regions, seeds 0-2 | +0.038 | -0.012 | true 3/3, shuffled 1/3 |
| two-holdout broadening | shared parent regions, `KS014` + `MFD_06` | +0.016 | -0.006 | true 4/6, shuffled 2/6 |
| CSH-like candidate broadening | shared parent regions, `NR_0019` | -0.008 | +0.003 | true 1/3, shuffled 2/3 |
| fixed carrier-parent slice | `NYU-12`, parents `PRT,CA,VP,MOp,DG,mfbc` | +0.013 | +0.020 | true 2/3, shuffled 3/3 |
| stricter fixed-slice candidate | `SWC_038`, same parents | -0.004 | +0.019 | true 0/2, shuffled 2/2 |

Canonical source: `docs/csh_zad_019_signal_audit.md`. Machine-readable
metrics: `docs/csh_zad_019_demo_metrics.json`.
Broadening source: `docs/lso_two_holdout_shared_parent_shuffle_results.md`.
CSH-like candidate source: `docs/lso_nr0019_shared_parent_shuffle_results.md`.
Broadening audit: `docs/shared_parent_broadening_audit.md`.
Parent-region support audit: `docs/parent_region_support_signal_audit.md`.
Candidate ranking: `docs/csh_composition_candidate_ranking.md`.
Failure-mode audit: `docs/cross_holdout_failure_mode_audit.md`.
Parent-region slice plan: `docs/parent_region_slice_plan.md`.
Fixed-slice run: `docs/lso_nyu12_parent_slice_results.md`.
Success-mode audit: `docs/transfer_success_mode_audit.md`.
CSH diagnostic output audit: `docs/csh_diagnostic_output_audit.md`.
Recovered full-trial summary source:
`docs/lso_csh_diagnostic_outputs_results.md`.
Full-eval launch attempt:
`docs/lso_csh_full_eval_shared_parent_shuffle_results.md`.

## Why This Is Real Enough To Demo

- The effect replicated for `CSH_ZAD_019` across three matched-cache seeds.
- It survived a stricter shared-region mask and Allen parent-region coarsening.
- Shuffling region identity preserved the marginal region-label distribution
  but removed the lift.
- The held-out split is explicitly cross-animal: six training subjects and one
  held-out subject.

## Limits

- The signal is currently heldout-specific.
- The completed two-holdout broadening result is positive for true labels and
  negative for shuffled labels in aggregate, but the true-label lift is only
  +0.016 and positive in 4/6 subject-seed pairs.
- The weak broadening subjects are not weak because of low global parent-region
  support; they have higher support than CSH_ZAD_019. The unresolved issue is
  anatomical composition.
- The top-ranked CSH-like follow-up, `NR_0019`, did not reproduce the signal:
  true parent-region labels were slightly below the shared null and below the
  shuffled-label control.
- The fixed carrier-parent slice on `NYU-12` also did not reproduce the
  controlled effect: true labels were weakly positive, but shuffled labels were
  larger and positive in all seeds.
- A follow-up success-mode audit found that `NYU-12` matched the
  leave-subject-out training aggregate sign, but represented only 44.9% of the
  CSH carrier-weighted signal and lacked the strongest CSH carrier parent
  (`PRT`) plus `MOp`.
- The stricter `SWC_038` fixed-slice run also failed: true labels were below
  the shared null in both completed seeds, while shuffled labels were positive
  in both.
- A partial CSH diagnostic rerun exported full held-out predictions for seed 0,
  and the analyzer now reports those full-trial metrics directly. On those
  artifacts, `region_only` and `region_shuffle` were nearly indistinguishable
  relative to the exported baseline (+0.008 vs +0.009 AUC). This weakens
  confidence that sampled eval summaries alone are sufficient for a demo-grade
  claim.
- Paired trial analysis of those seed-0 artifacts shows both anatomy arms mostly
  shifted probabilities upward rather than toward the true class. `region_only`
  improved true-class probability on only 45.5% of paired trials, while
  `region_shuffle` improved 44.8%.
- The failure-mode audit rules out several simple gates on their own:
  parent-region support, CSH-like composition, trial count, class balance, and
  raw parent-level stimulus contrast.
- The claim should not be phrased as broad anatomical transfer across IBL until
  more held-out animals reproduce the stronger CSH_ZAD_019-sized effect.

## Next Experimental Gate

Do not launch another paid broadening run unchanged. Both the initial
fixed-slice candidate (`NYU-12`) and the stricter follow-up (`SWC_038`) failed
the true-vs-shuffled control. The next step should be no-spend analysis of the
actual CSH model outputs or a redesign of the anatomical objective, not another
matched-cache A100 sweep.

Instrumentation is now available for that diagnostic: `scripts/train.py` can
export held-out trial predictions, learned region embeddings, and official
`full_eval` log metrics over every valid held-out trial. The analyzer now
reports those deterministic full held-out-trial metrics directly. If spending
again, rerun only the canonical `CSH_ZAD_019` control with
`FULL_EVAL_ON_BEST=1`; do not broaden to more held-out animals unless CSH
survives that full-trial true-vs-shuffled gate across seeds.

The first paid attempt to run that gate failed at RunPod provisioning and
produced no training metrics, so it does not change the evidence table.

Before another paid retry, tighten the gate so the model has to beat the
shuffled control on target-aware paired-trial behavior or per-recording
calibrated ranking, not just sampled eval AUC.

Current stricter-gate status from the seed-0 diagnostic: recording-centered AUC
is mildly positive for true labels (`0.521` vs shared `0.500` and shuffled
`0.510`), but the direct true-vs-shuffle paired-trial gate fails (`50.6%`
target-direction improvement, below the `55.0%` demo threshold). That is a
reason to redesign the objective/gate, not to broaden yet.

The executable gate is `scripts/check_lso_demo_gate.py`; the preserved CSH
diagnostic verdict is `docs/lso_csh_diagnostic_outputs_gate.json`.
