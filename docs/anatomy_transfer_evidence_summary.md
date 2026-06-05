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

Within-recording shuffle pilot result: the one-seed CSH_ZAD_019 pilot also
failed the anatomy-specific gate. True labels barely beat the within-recording
shuffle on centered AUC (`+0.0014`), lost badly on full AUC (`-0.0243`), and
lost the paired true-vs-shuffle comparison (`0.448`). Recording support was
nominally 3/4 positive, but the sign-flip p-value was `0.25` and the paired
specificity gap was negative (`-0.103`). Do not broaden this control to more
seeds.

The control result is useful because it separates two failure modes. The
recording-centered loss made shuffled labels create a stronger within-recording
target separation. The within-recording shuffle removes the obvious marginal
label-count artifact, but it still does not reveal a meaningful true-region
advantage. The next step should be no-spend analysis of prediction artifacts:
quantify whether the model is using recording/probe-specific offsets, trial
count imbalance, or target-correlated region-family coverage before launching
another GPU run.

Prediction failure-mode audit result:
`docs/lso_csh_within_recording_shuffle_failure_modes.md` shows that the CSH
failure is dominated by recording-level calibration behavior, not by missing
parent-region coverage. Held-out parent-region support is at least `0.752`
across the four CSH recordings. But `region_shuffle` gains `+0.014` AUC from
raw recording offsets, while `region_only` loses `-0.011` AUC from those
offsets. The shuffled arm's recording mean probabilities also correlate
positively with each recording's target-1 fraction (`0.694`), while the paired
true-vs-shuffle fraction remains `0.448`.

Next design rule: any new demo attempt must make recording-centered evaluation
and recording-matched shuffled negatives primary gates. Raw full-trial AUC is
too easy to improve through recording/probe calibration and should not be used
as the model-selection metric for the anatomy claim.

Recording-centered gate pilot result: the executable preflight/run path in
`scripts/preflight_recording_centered_pilot_runpod.py` reproduced the same CSH
failure under the intended centered-selection settings. The anatomy-specific
gate still fails: centered true-vs-shuffle AUC delta is only `+0.0014`, paired
true-vs-shuffle is `0.448`, specificity gap is `-0.103`, and sign-flip p-value
is `0.25`. This confirms that merely making the gate and checkpoint selection
recording-centered is not sufficient; do not broaden this CSH variant.

Current experiment-state audit:
`docs/current_experiment_state.md` consolidates the strict-gate and fixed-slice
results after the later CSH recording-matched controls. No strict-gate artifact
passes. The later CSH controls fail because true labels do not beat
within-recording shuffled labels on paired target-aware trial movement, and both
fixed carrier-slice follow-ups (`NYU-12`, `SWC_038`) let shuffled labels match
or beat true labels.

Next no-spend task: inspect the CSH success mechanism directly. Compare true vs
within-recording-shuffled region embeddings and prediction shifts by carrier
parent and recording, then define an objective/control that requires true
anatomical labels to improve target-aware within-recording ranking. Do not spend
on another broadening or fixed-slice RunPod job without that new mechanism.

CSH mechanism audit result: `docs/csh_mechanism_audit.md` found no such
mechanism in the saved artifacts. Carrier-parent embeddings are nearly identical
between true and within-recording-shuffled controls (`0.992` mean cosine), and
every CSH held-out recording has true-vs-shuffle paired target movement below
`0.5`, including the carrier-rich recordings. The next useful implementation is
therefore objective redesign: train/evaluate against an explicit
within-recording true-vs-shuffle separation target, rather than choosing another
holdout subject or parent-region slice.

Objective redesign implemented: `scripts/train.py` now supports
`--loss-mode recording_pairwise_rank`, a same-recording logistic ranking loss
that pushes target-1 logits above target-0 logits within each recording and is
invariant to recording-level offsets. The intended pilot uses
`BATCH_SAMPLING=recording_target_balanced` plus the existing
within-recording-shuffle negative control. Preflight:
`uv run python scripts/preflight_pairwise_rank_pilot_runpod.py`.
