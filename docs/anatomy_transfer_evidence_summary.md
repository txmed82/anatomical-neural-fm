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

Pairwise-rank pilot result: `docs/lso_csh_pairwise_rank_pilot_results.md`
completed on a one-seed L4 run. It improved the paired true-vs-shuffle metric
to `0.552` and the specificity gap to `+0.103`, but failed the strict
anatomy-specific gate because centered AUC still favored shuffle (`0.480` true
vs `0.494` shuffle) and only `1/4` held-out recordings had positive
true-minus-shuffle AUC. This is a useful mechanism lead, not yet a demo-quality
cross-animal anatomical transfer result.

Pairwise mismatch audit: `docs/lso_csh_pairwise_rank_pilot_mismatch.md` shows
that the apparent paired improvement was not target-aware. Raw probabilities
moved downward on every paired trial; target-0 true-class probability improved
on `1.000` of trials while target-1 improved on `0.000`. That explains how the
paired metric reached `0.552` in a target-0-majority held-out set while
recording-centered AUC still failed. The next candidate objective is
`recording_pairwise_rank_centered_bce`, tested first with no-spend CPU smoke and
only then with the bounded L4 preflight
`uv run python scripts/preflight_pairwise_rank_centered_bce_pilot_runpod.py`.

Pairwise-rank centered-BCE pilot result:
`docs/lso_csh_pairwise_rank_centered_bce_pilot_results.md` completed on the
same bounded L4 setup. The added centered-BCE anchor removed the all-trial
downward-shift artifact, but it did not create anatomical transfer. The strict
gate still failed with centered AUC `0.485` true vs `0.500` shuffle,
paired true-vs-shuffle `0.486`, and `0/4` positive recordings. The mechanism
audit decision is `no_mechanism_found`; the mismatch audit decision is
`paired_metric_not_recording_rank_stable`. Do not spend on another one-off
objective variant until a direct recording-local AUC/ranking surrogate and
bidirectional target-class gate are implemented and locally checked.

Bidirectional gate implemented: `scripts/analyze_anatomy_specific_permutation.py`
now records and requires target-0 and target-1 true-class improvement separately
against the shuffled control. This closes the false-positive path where a
one-direction probability shift can pass the scalar paired metric. The two
latest pilots fail this stricter check: pairwise-rank has target0 `1.000` and
target1 `0.000`; centered-BCE has target0 `0.354` and target1 `0.650`.
Training also exposes `--loss-mode recording_local_auc_surrogate` as the direct
recording-local AUC/ranking surrogate alias for local experiments.

Local objective probe: `scripts/run_local_objective_probe.py` now runs a tiny
CPU-only three-arm probe and immediately applies the strict bidirectional gate,
mismatch audit, and failure-mode audit. The first `recording_local_auc_surrogate`
probe failed locally, so it should not be promoted to RunPod as-is:
centered true-minus-shuffle delta `-0.005`, paired true-vs-shuffle `0.494`,
target0 `0.556`, target1 `0.419`, and positive recordings `2/4`.

Local probe matrix update: four no-spend CPU variants now fail the promotion
gate: `recording_local_auc_surrogate`, `recording_centered_bce`,
`recording_pairwise_rank_centered_bce`, and
`recording_local_auc_surrogate` with target-balanced sampling. They all lose
centered true-vs-shuffle AUC by about `-0.005`, remain around paired
true-vs-shuffle `0.494` to `0.502`, keep only `2/4` positive recordings, and
fail bidirectional target-class improvement because target1 remains around
`0.406` to `0.419`. Decision: do not launch another RunPod objective variant
from this family. The next step is no-spend sampler/objective redesign that
demonstrably improves both target classes within recordings before any paid
run.

Batch sampling contrast audit: `docs/csh_batch_sampling_contrast_audit.md`
confirms that pair availability is not the limiting issue for the current
recording-local objective. All 24 CSH training recordings have both target
classes. With batch size 2, uniform sampling creates a rankable same-recording
target pair in only `0.023` of batches, target-balanced sampling in `0.040`,
but `recording_target_balanced` creates one in `1.000` of batches. Since the
local probe matrix still fails under `recording_target_balanced`, the remaining
failure is the anatomical signal/control/objective, not inactive pairwise loss.

Model-free region signal audit:
`docs/csh_model_free_region_signal_audit.md` removes the transformer and fits a
closed-form ridge classifier on trial-level parent-region spike counts. This is
a strong negative for the current parent-region feature representation. A
total-spike-count baseline reaches centered AUC `0.553` on held-out
CSH_ZAD_019, true parent-region features reach only `0.487`, and
within-recording shuffled parent labels reach `0.538`. True-minus-shuffle
centered AUC is `-0.052`, target0 improvement is `0.338`, target1 improvement
is `0.703`, and only `1/4` recordings are positive. Decision: the next
no-spend work should redesign the anatomical feature/control target rather
than spend on another neural model run.

Single-region candidate scan:
`docs/csh_model_free_region_candidate_scan.md` tests each parent region as its
own one-feature ridge model against within-recording shuffled labels and the
total-spike baseline. No region passes the local promotion gate. The strongest
evaluable rows are one-sided or low-support: `IB` has centered AUC `0.728` and
true-minus-shuffle `+0.300` but target0 improvement is only `0.275` with
`1/4` positive recordings; `CA` and `DG` have `2/4` positive recordings but
target0 remains around `0.320` and `0.285`. Decision: do not promote any
single parent region. Next no-spend step is predefined region-family
aggregates or an alternative conserved behavioral target.

Region-family aggregate scan:
`docs/csh_model_free_region_family_scan.md` tests predefined aggregate anatomy
families. It also finds zero candidates. `basal_ganglia` beats shuffle by
`+0.100` centered AUC and total-spike by `+0.157`, but it is purely
target0-sided (`target1=0.000`) and positive in only `1/4` recordings.
`hippocampal_formation` has `2/4` positive recordings but target0 is only
`0.305`. Decision: the CSH parent-region path is exhausted for now under
model-free gates. The next branch should test an alternative conserved target
or audit a larger matched-region manifest before spending.

Alternative target check: the same model-free gates were rerun with
`--target-mode choice` in `docs/csh_choice_model_free_region_signal_audit.md`,
`docs/csh_choice_model_free_region_candidate_scan.md`, and
`docs/csh_choice_model_free_region_family_scan.md`. Choice also fails:
true parent regions have centered AUC `0.480`, shuffled parent labels have
`0.566`, true-minus-shuffle centered AUC is `-0.086`, and both the
single-region and region-family scans have zero candidates. Decision: choice
does not rescue the current CSH parent-region branch.

Matched-region cache readiness: `docs/matched_region_cache_audit.md` now shows
the larger 48-recording candidate cache is `47/48` present on S3. The
incremental CPU cache build in
`docs/matched_region_missing_incremental_results.md` uploaded `18/19` missing
HDF5s and left one dataset-specific failure:
`de588204-8fd6-4ce3-92da-7a6d1dcae238_probe00.h5`, where OpenAlyx could not
find a required ALF trials object. Decision: do not launch a matched-region
seed sweep yet. Replace or drop that single failed recording, rerun the
matched-region support scorer, and require the 80% held-out unit-support gate
before spending on GPU confirmation.

Metadata-only support scoring on the S3-present cache panel is now complete:
the 47-recording panel has `8/12` subjects above 80% held-out unit support.
The optimized cached subset in
`manifests/ibl_bwm_region_matched_candidates_s3_present_support80.json` has
28 recordings across 7 subjects, with `6/7` subjects above 80%. Decision:
the actual HDF5 cache confirms the same `6/7` support80 result. `SWC_043`
remains below gate at `65.8%`; enforcing an iterative all-pass filter collapses
to only 2 subjects (`MFD_06`, `NYU-12`). Do not call this a clean broad
benchmark. Any paid next step should either be a no-spend/model-free screen on
the 28-recording panel or a bounded training gate that treats `SWC_043` as a
predeclared weak-support holdout.

Matched-panel model-free screen:
`docs/model_free_matched_support80_hdf5_panel.md` runs the closed-form
parent-region ridge audit leave-subject-out across the HDF5-confirmed
28-recording panel. It finds zero model-free anatomy candidates. `KS014`
(`+0.030` centered true-minus-shuffle AUC) and `NR_0019` (`+0.079`) are the
only positive-delta holdouts, but both miss the bidirectional target-class and
recording-support gates. Mean centered true-minus-shuffle delta across the
seven holdouts is `-0.003`. Decision: do not spend on a broad matched-panel
training sweep from this evidence.

Positive-holdout mechanism audit:
`docs/model_free_positive_holdouts_mechanism.md` breaks those two weak
positive holdouts down by target class and recording. `KS014` remains below
the bidirectional gate with target0 `0.547`, target1 `0.538`, and only `2/4`
positive recordings; individual probes flip between target0-only and
target1-only improvement. `NR_0019` is strongly one-sided, with target0
`0.776` but target1 only `0.249`. Decision: these positive centered deltas are
not promotable. The next step should be no-spend target/control redesign or a
new local model-free gate that produces bidirectional recording-supported
signal before any RunPod training.

Recording-bidirectional panel gate:
`docs/model_free_recording_bidirectional_gate.md` formalizes that next local
gate across all seven HDF5-confirmed matched-panel holdouts. A held-out
recording counts only if true labels beat the within-recording shuffle for
target0 and target1 inside that same recording. The panel has zero candidates:
mean bidirectional recording fraction is `0.036`, `KS014` and `NR_0019` have
`0/4` bidirectional recordings despite positive centered deltas, and only
`NYU-12` has even `1/4` bidirectional recordings while its centered delta is
negative. Decision: stop before GPU training. A future target/control redesign
must pass this same-recording bidirectional gate locally before any paid
confirmation run.

Alternative target sweep:
`feedback` and `prior_side` were added as binary trial targets from the cached
IBL trial fields and run through the same recording-bidirectional model-free
gate. Both are available in all 28 matched-panel recordings. `prior_side` has
zero candidates, three positive centered-delta holdouts, and mean
bidirectional recording fraction `0.000`; `KS014` has global target0 `0.582`
and target1 `0.566` but still `0/4` bidirectional recordings. `feedback` also
has zero candidates and mean bidirectional recording fraction `0.000`; its
positive deltas are strongly class-directional, for example `SWC_043` target0
`0.000` and target1 `1.000`. Decision: these alternative behavioral targets
do not justify GPU training either.

Region-fraction feature check:
`docs/model_free_recording_bidirectional_gate_fractions.md` reruns the
stimulus-side matched-panel gate after normalizing each trial's parent-region
spike counts to fractions of total spikes. This tests whether raw rate/total
spike scale was masking an anatomical composition signal. It still finds zero
candidates and mean bidirectional recording fraction `0.000`. `KS014`,
`NR_0019`, and `SWC_043` have positive centered deltas, but each has `0/4`
bidirectional recordings and the gains remain one target direction. Decision:
simple region-composition normalization is not enough; the next local branch
needs a different anatomical control or feature family, not GPU training.

Unit-residual feature check:
`docs/model_free_recording_bidirectional_gate_unit_residuals.md` subtracts
each recording's expected region counts from each trial, using total spikes
times that recording's static unit-region distribution. This controls both
total spike scale and static anatomical coverage. It increases positive
centered-delta holdouts to `6/7`, but still yields zero candidates and mean
bidirectional recording fraction `0.000`. The positive deltas are still
target-direction artifacts: `CSH_ZAD_019` has target0 `0.120` and target1
`0.903`, while `NYU-12` flips to target0 `0.694` and target1 `0.341`.
Decision: residualized region deviations are not enough to trigger GPU
training.

Source-target pair redesign check:
`docs/model_free_source_target_pair_gate_recording_centered.md` tests whether
the leave-subject-out panel is hiding a compatible single-source animal by
training the model-free recording-centered anatomy classifier on one source
subject and evaluating one target subject at a time. It finds zero candidates
across 42 source-target pairs. Twenty pairs have positive centered deltas, but
all fail global target0/target1 or same-recording bidirectionality; the mean
bidirectional recording fraction is only `0.065`. Decision: source-target
pairing does not provide a local promotion path to GPU training.

Family source-target pair check:
`docs/model_free_source_target_pair_gate_families_recording_centered.md`
combines single-source animal pairing with predefined family aggregates. It
also finds zero candidates across 42 source-target pairs. Family aggregation
raises mean bidirectional recording fraction to `0.095`, but all positive
pairs still fail global target0/target1 or same-recording bidirectionality, and
no top pair exceeds `1/4` bidirectional recordings. Decision: the best
remaining no-spend combination still does not justify A100 training.

Gate blocker audit:
`docs/model_free_gate_blocker_audit.md` aggregates 168 rows from the current
local model-free holdout and source-target gates. It finds zero candidates,
86 rows with positive centered deltas, and a hard ceiling of `2/4`
bidirectional recordings. Every audited row misses the same-recording
bidirectionality gate, while target0 and target1 are also missing in 130 and
136 rows respectively. Decision: the next experiment should change the
benchmark/control definition enough to create target0+target1 evidence inside
the same recordings before any GPU run.

Recording support audit:
`docs/model_free_recording_support_audit.md` aggregates the per-recording
target0/target1 rows behind those gates. Across 672 observations, 53 are
bidirectional and 19 of 28 recordings have at least one bidirectional
observation, but the support is not stable: the strongest recording has only
12/24 bidirectional observations and mean target1 below gate (`0.524`), while
the next strongest recordings remain class-imbalanced. Decision: do not define
a demo by cherry-picking current recordings. The next benchmark must
prospectively select or construct recordings with bidirectional target evidence
and then rerun the same true-vs-shuffled local gate before GPU training.

Recording replication audit:
`docs/model_free_recording_replication_audit.md` turns that warning into a
discovery/validation test. Fixed discovery reports select three recordings
(`KS014` probe00, `MFD_06` probe00, and `KS014` probe01), but zero replicate
in held-out validation report families. The best validation case (`MFD_06`
probe00) keeps 9/14 bidirectional observations but drops target1 to `0.530`;
the KS014 selections drop both validation targets below gate. Decision:
recording-subset narrowing is not a credible demo path under the current cache.

Manifest feasibility audit:
`docs/manifest_target_anatomy_feasibility.md` checks whether the current
HDF5-backed manifests are at least capable of supporting a redesigned local
benchmark. The 28-recording support80 HDF5 manifest passes basic target balance
for all four target modes (`choice`, `stimulus_side`, `feedback`, and
`prior_side`) with 28/28 eligible recordings, and has four anatomical families
passing the shared-support floor across all seven subjects: broad named
anatomy, thalamic, hippocampal formation, and fiber tracts. Decision: the
current manifest is not the immediate bottleneck. The next no-spend branch
should test specific shared-family target/control designs under the
recording-bidirectional gate.

Shared-family target/control gate:
`docs/shared_family_target_control_gate.md` tests those feasible families
directly across all four target modes and seven holdouts. It finds zero
candidates across 112 rows. Fifty-five rows have positive centered true-vs-
shuffle deltas, but the maximum same-recording bidirectional support is only
`2/4`. The closest mechanistic row is `choice` + `fiber_tracts` on
`CSH_ZAD_019`: centered delta vs shuffle `+0.199`, delta vs total `+0.221`,
target0 `0.558`, target1 `0.614`, but only `1/4` bidirectional recordings.
Decision: shared-family single-feature narrowing is not a GPU trigger.

Shared-family near-miss mechanism:
`docs/shared_family_choice_fiber_csh_near_miss.md` decomposes that strongest
row by recording. The global effect is not noise, but it is one-sided:
target1 improves in `4/4` recordings while target0 clears the recording gate
in only `1/4`. The decision is `one_sided_target1_recording_effect`.
Decision: do not promote this to neural training; a model run would likely
learn the same target1-local artifact rather than bidirectional anatomical
transfer.

Recording directionality audit:
`docs/model_free_recording_directionality_audit.md` checks whether this
one-sided behavior is isolated. It is not. Across 1120 per-recording
observations from the current model-free artifacts, only 80 are bidirectional;
302 are target0-only, 311 are target1-only, and 427 are neither. One-sided
observations make up `0.547` of all observations. Decision: every future local
promotion gate must report target-direction classes before global centered
deltas are treated as evidence.

Symmetric recording support audit:
`docs/symmetric_recording_support_audit.md` converts that lesson into a ranking
criterion: each recording contributes `min(target0_improved, target1_improved)`
so one-sided wins cannot dominate. It ranks 280 current rows and finds zero
symmetric recording candidates. The best rows still top out at `2/4`
bidirectional recordings; the high-delta `choice` + `fiber_tracts` CSH row has
mean symmetric support `0.543` but only `1/4` bidirectional recordings and
three one-sided recordings. Decision: this symmetric ranking should be the
first local promotion screen before any future GPU trigger.

Symmetric threshold sensitivity audit:
`docs/symmetric_threshold_sensitivity_audit.md` sweeps the target-improvement
and bidirectional-recording thresholds to check whether the miss is just a
hard threshold artifact. It is not a credible GPU trigger: strict
target>=`0.55` and bidirectional fraction>=`0.75` produces zero candidates,
and at the default target threshold candidates appear only when the recording
support floor is relaxed to `0.25` (`1/4` recordings). Decision: do not spend
on training until a local row clears symmetric recording support without that
relaxation.

Symmetric strict failure mode audit:
`docs/symmetric_strict_failure_modes.md` ranks the closest rows against the
strict symmetric gate. Every current row fails recording bidirectionality; only
four clear both global target floors, and none of those is just one
bidirectional recording short. The closest actionable rows are shared
broad-anatomy target/control rows that are one recording short but still miss
global target0 by `0.010` to `0.016`. Decision: the next no-spend branch should
try to repair those marginal target0 plus recording-support misses locally, not
launch training.

Shared broad-anatomy repair sweep:
`docs/shared_broad_anatomy_repair_sweep.md` reruns those two closest
broad-anatomy rows across `counts`, `fractions`, `recording_centered`, and
`unit_residuals` features with `l2` in `{1,10,100}`. It finds zero candidates.
The best comparable rows remain at `2/3` required bidirectional recordings and
still miss target0 and/or baseline controls. Decision: this closes the simple
feature/regularization repair path for shared broad anatomy; do not launch GPU
training from it.

Shared-family iterative-manifest gate:
`docs/shared_family_iterative_manifest_gate.md` tests whether the stricter
8-recording, 2-subject iterative-pass manifest rescues the shared-family
target/control screen. It does not: zero candidates, 20 positive centered-delta
rows, and max same-recording bidirectional support only `1/4`. Decision:
manifest narrowing alone is not enough, and the 2-subject panel is too narrow
for a demo anyway. The next branch should change the benchmark/control
definition rather than keep shrinking this cache.

Next benchmark/control options audit:
`docs/next_benchmark_control_options.md` ranks the remaining branches. It marks
simple feature/L2 sweeps, further manifest narrowing, recording-subset
selection, the current shared-family grid, cached alternative targets, and
source-target narrowing as closed GPU triggers. The recommended next branch is
a new benchmark/control target definition, with the same local promotion gate:
delta vs shuffle and total baseline nonnegative, target0 and target1 >=`0.55`,
and same-recording bidirectional fraction >=`0.75`.

Derived target family gate:
`docs/derived_target_family_gate.md` tests the first concrete version of that
branch using cached trial fields: `contrast_strength`, `response_latency`, and
`prior_engaged`. All three targets are trial-balanced across the full
28-recording panel, but none pass the shared-family gate: zero candidates
across 84 rows. The nearest symmetric row is `response_latency` +
`broad_named_anatomy` on `KS014`, with target0 `0.714`, target1 `0.745`, and
`3/4` bidirectional recordings, but it fails the within-recording shuffle
control with centered delta `-0.004`. Other high-delta rows are one-sided or
lose to the total-spike baseline. Decision: cached-derived trial targets do
not justify GPU training; the next target/control redesign needs either
external behavioral/neural structure or a genuinely different benchmark, not
another direct transform of these cached fields.

Recording-centered feature check:
`docs/model_free_recording_bidirectional_gate_recording_centered.md` subtracts
each recording's own mean parent-region feature vector before ridge fitting.
This is the least one-sided feature normalization so far, but it still does not
pass: zero candidates, two positive centered-delta holdouts, and mean
bidirectional recording fraction `0.071`. `KS014` has centered delta `+0.042`
but target0 `0.520`, target1 `0.540`, and only `1/4` bidirectional recordings;
`NR_0019` has centered delta `+0.047` but target0 `0.482`. Decision: keep this
as a near-miss diagnostic, not a GPU trigger.

Grandparent recording-centered feature check:
`docs/model_free_recording_bidirectional_gate_grandparent_recording_centered.md`
tests whether coarser Allen atlas granularity rescues the local gate. It
does not. Grandparent features yield zero candidates, five positive
centered-delta holdouts, and mean bidirectional recording fraction `0.071`.
Every positive holdout still fails global target0, and the best recording
support is only `1/4` bidirectional recordings. Decision: atlas coarsening
creates more weak positive deltas but no promotable cross-animal anatomical
transfer signal.

Family-aggregate recording-centered check:
`docs/model_free_family_bidirectional_gate_recording_centered.md` combines
predefined parent-region family aggregates with recording-centered features.
This is the strongest no-spend near miss so far: positive centered-delta
holdouts increase to `4/7`, mean bidirectional recording fraction rises to
`0.179`, and `KS014` reaches centered delta `+0.080` with `2/4` bidirectional
recordings. It still has zero candidates because the global bidirectional
target-class gate fails (`KS014` target0 `0.510`, target1 `0.548`; `MFD_06`
target0 `0.565`, target1 `0.489`). Decision: this suggests a weak family-level
signal worth diagnosing locally, but not a RunPod training trigger.

Family-aggregate regularization sensitivity:
`docs/model_free_family_bidirectional_gate_recording_centered_l2_1.md` and
`docs/model_free_family_bidirectional_gate_recording_centered_l2_100.md` rerun
the strongest near-miss gate around the default `l2=10`. The decision is
unchanged at `l2=1`, `10`, and `100`: zero candidates, four positive
centered-delta holdouts, and mean bidirectional recording fraction `0.179`.
Decision: the family near miss is not explained by a poor ridge regularization
choice.

KS014 family near-miss mechanism:
`docs/model_free_family_ks014_near_miss_mechanism.md` decomposes the strongest
near miss by family contribution. It finds zero bidirectional family
candidates. The apparent KS014 family signal is split across one-sided
families: `broad_named_anatomy` is target0-only (`0.589` target0, `0.456`
target1), `fiber_tracts` is also target0-only (`0.657`, `0.465`), while
`cortical_retrosplenial` (`0.130`, `0.898`), `thalamic` (`0.122`, `0.874`),
and `hippocampal_formation` (`0.206`, `0.724`) are target1-only. Decision:
the KS014 near miss is not hiding a bidirectional anatomical mechanism.

Family-aggregate alternative target check:
`docs/model_free_family_bidirectional_gate_prior_side_recording_centered.md`
and `docs/model_free_family_bidirectional_gate_feedback_recording_centered.md`
rerun the strongest family-aggregate feature path on `prior_side` and
`feedback`. Both produce zero candidates. `prior_side` has six positive
centered-delta holdouts and mean bidirectional recording fraction `0.107`, but
still fails global or same-recording bidirectionality. `feedback` has four
positive centered-delta holdouts, the same `0.107` mean bidirectional recording
fraction, and zero candidates. Decision: alternative targets plus family
aggregation do not create a local promotion signal; do not launch GPU training
from this branch.
