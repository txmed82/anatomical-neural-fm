# Anatomy Transfer Evidence Summary

Decision: `redesign_before_more_spend`

Do not run more same-setup GPU sweeps. Redesign the anatomy-specific objective or gate, then rerun a bounded two-holdout confirmation.

| holdout | gate | passing_seeds | paired_true_vs_shuffle | shuffle_vs_shared | specificity_gap | centered_delta_vs_shuffle | full_delta_vs_shuffle | recording_support |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| CSH_ZAD_019 | False | 1/3 | 0.536 | 0.552 | -0.016 | +0.006 | +0.005 | 4/4 |
| NR_0019 | False | 0/3 | 0.493 | 0.493 | +0.000 | +0.012 | +0.014 | 1/4 |

A holdout is not considered demo-ready unless the executable gate passes,
the paired true-vs-shuffle improvement is specific against shuffle-vs-shared,
and the recording-level AUC support is not localized to a single recording.

## Anatomy-Specific Permutation Gate

`scripts/analyze_anatomy_specific_permutation.py` tests the seed-ensemble
region-only vs region-shuffle contrast with recording-level sign flips. This is
deliberately stricter than trial-level pairing because the current holdouts have
only four recordings each.

| holdout | pass | centered_delta_vs_shuffle | specificity_gap | recording_support | sign_flip_p |
|---|---|---:|---:|---:|---:|
| CSH_ZAD_019 | False | +0.006 | -0.016 | 4/4 | 0.0625 |
| NR_0019 | False | +0.012 | +0.000 | 1/4 | 0.5000 |

CSH has broad recording support but the effect is too small, not specific
against shuffle-vs-shared, and misses the recording-level sign-flip threshold.
NR_0019 has a larger ensemble AUC delta but it is localized to one recording and
has no paired specificity. Neither result is demo-ready.

## Next Training Variant

The next implementation change is target-balanced training, not another
same-setup sweep. `scripts/train.py` accepts `--batch-sampling target_balanced`,
and the held-out RunPod wrappers expose the same control through
`BATCH_SAMPLING=target_balanced`. This balances accepted training batches across
left/right targets while keeping sampled eval uniform. Use it first on a bounded
single CSH_ZAD_019 pilot with full held-out-trial diagnostics; broaden only if
the anatomy-specific permutation gate improves.

Target-balanced pilot result: partial CSH_ZAD_019 artifacts are enough to rule
out this exact variant. Seeds 0 and 1 both fail centered-AUC true-vs-shared, so
seed 2 cannot rescue the three-seed gate. The two-complete-seed ensemble has
positive true-vs-shuffle centered delta (`+0.009`) and specificity gap
(`+0.051`), but still fails the strict anatomy-specific gate because the
centered delta is below `+0.010` and the recording sign-flip p-value is `0.125`.
Do not spend more on the same target-balanced run.

Next variant: recording-centered BCE. The trainer now has
`--loss-mode recording_centered_bce` plus
`--batch-sampling recording_target_balanced`, which draws left/right pairs from
the same recording and removes each recording's mean logit inside the training
loss. This directly targets the recording-offset failure mode that centered AUC
penalizes. Run only a one-seed CSH pilot first; broaden only if centered-AUC and
specificity improve.

Recording-centered BCE pilot result: the one-seed CSH pilot failed strongly.
`region_only` centered AUC was `0.480`, below shared `0.501` and shuffled
regions `0.530`; paired true-vs-shuffle was `0.451`; recording support was
`0/4`. This rules out broadening the recording-centered-loss variant. The next
no-spend analysis should explain why shuffled parent labels win under this
objective before another training run.

Shuffle-win audit result: `docs/csh_shuffle_win_mode_audit.md` shows the
recording-centered loss failure is specifically a shuffled-label separation
win. In that run, true-minus-shuffle centered target separation is `-0.0096`,
with the biggest negative recording at
`49e0ab27-827a-4c91-bcaa-97eea27a1b8d_probe01`. The original centered and
target-balanced runs have small positive true-minus-shuffle centered separation,
so this is not just a reporting artifact. Before another GPU run, redesign the
negative control or region vocabulary so shuffled labels cannot create an
easier target-correlated partition than true labels.
