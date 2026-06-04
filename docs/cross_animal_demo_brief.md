# Cross-Animal Anatomy Transfer Demo Brief

## Current Claim

The project has a controlled, subject-specific cross-animal anatomical transfer
signal on the matched 28-recording IBL subset:

> For held-out `CSH_ZAD_019`, anatomical region identity improves
> stimulus-side decoding relative to a shared null, and the lift collapses when
> region labels are shuffled.

This is not yet a general cross-animal result across IBL animals. It is a
credible demo nucleus that justifies one carefully gated broadening experiment.

## Evidence Table

| result | setting | true anatomy delta | shuffled anatomy delta | seed support |
|---|---|---:|---:|---:|
| matched confirmation | fine regions, seeds 0-2 | +0.042 | n/a | 3/3 true positive |
| fine shuffle control | fine regions, seeds 0-2 | +0.042 | -0.012 | true 3/3, shuffled 1/3 |
| shared-parent shuffle control | shared parent regions, seeds 0-2 | +0.038 | -0.012 | true 3/3, shuffled 1/3 |

Canonical source: `docs/csh_zad_019_signal_audit.md`.

## Why This Is Real Enough To Demo

- The effect replicated for `CSH_ZAD_019` across three matched-cache seeds.
- It survived a stricter shared-region mask and Allen parent-region coarsening.
- Shuffling region identity preserved the marginal region-label distribution
  but removed the lift.
- The held-out split is explicitly cross-animal: six training subjects and one
  held-out subject.

## Limits

- The signal is currently heldout-specific.
- Two-holdout broadening attempts so far are aborted/non-evidence; they produced
  missing-summary artifacts, not usable result tables.
- The claim should not be phrased as broad anatomical transfer across IBL until
  the same true-vs-shuffled shared-parent control succeeds on additional
  holdouts.

## Next Experimental Gate

Run only the canonical two-holdout preflight:

```bash
uv run python scripts/preflight_two_holdout_runpod.py --max-dollars 10
```

Proceed only if:

- active RunPod pods are zero;
- Git is clean and synced;
- the launch command uses `scripts/run_lso_two_holdout_shared_parent_shuffle_a100.sh`;
- the result document is `docs/lso_two_holdout_shared_parent_shuffle_results.md`;
- estimated max cost is below the cap.

If the broadening run completes, count it as progress only if
`docs/lso_two_holdout_shared_parent_shuffle_results.md` contains non-empty
leave-subject-out rows for `region_only` and `region_shuffle`.
