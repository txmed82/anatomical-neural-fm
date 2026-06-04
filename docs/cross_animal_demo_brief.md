# Cross-Animal Anatomy Transfer Demo Brief

## Current Claim

The project has a controlled, subject-specific cross-animal anatomical transfer
signal on the matched 28-recording IBL subset:

> For held-out `CSH_ZAD_019`, anatomical region identity improves
> stimulus-side decoding relative to a shared null, and the lift collapses when
> region labels are shuffled.

This is not yet a general cross-animal result across IBL animals. It is a
credible demo nucleus. The first completed broadening experiment is directionally
consistent but too weak to claim generality.

## Evidence Table

| result | setting | true anatomy delta | shuffled anatomy delta | seed support |
|---|---|---:|---:|---:|
| matched confirmation | fine regions, seeds 0-2 | +0.042 | n/a | 3/3 true positive |
| fine shuffle control | fine regions, seeds 0-2 | +0.042 | -0.012 | true 3/3, shuffled 1/3 |
| shared-parent shuffle control | shared parent regions, seeds 0-2 | +0.038 | -0.012 | true 3/3, shuffled 1/3 |
| two-holdout broadening | shared parent regions, `KS014` + `MFD_06` | +0.016 | -0.006 | true 4/6, shuffled 2/6 |

Canonical source: `docs/csh_zad_019_signal_audit.md`. Machine-readable
metrics: `docs/csh_zad_019_demo_metrics.json`.
Broadening source: `docs/lso_two_holdout_shared_parent_shuffle_results.md`.
Broadening audit: `docs/shared_parent_broadening_audit.md`.
Parent-region support audit: `docs/parent_region_support_signal_audit.md`.
Candidate ranking: `docs/csh_composition_candidate_ranking.md`.

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
- The claim should not be phrased as broad anatomical transfer across IBL until
  more held-out animals reproduce the stronger CSH_ZAD_019-sized effect.

## Next Experimental Gate

Do not rerun the same two-holdout sweep unchanged. The next paid experiment
should either preselect holdouts whose parent-region composition resembles
CSH_ZAD_019 or force all compared holdouts onto a common parent-region panel
before training.

The current cheapest paid gate is a single `NR_0019` shared-parent
true-vs-shuffled control. `NR_0019` is the closest remaining matched-cache
subject to `CSH_ZAD_019` by parent-region composition; continue to another
holdout only if that run produces a meaningful true-label lift over both the
shared null and shuffled-label control.
