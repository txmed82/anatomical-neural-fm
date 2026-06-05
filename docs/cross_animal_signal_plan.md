# Cross-Animal Anatomical Transfer Plan

Current status: the 20-recording benchmarks are real, but the cross-animal
anatomical transfer signal is not yet demo-grade. The best confirmation result
so far is a subject-specific effect for `DY_008`; the aggregate targeted
multi-seed screen did not clear the pre-registered threshold.

## Working Hypotheses

1. Choice decoding may be too animal- and session-specific for the first
   transfer demo. Stimulus side should be a more conserved sensory target.
2. The original cross split only evaluates two held-out subjects. We need
   broader held-out-subject sweeps before claiming generalization.
3. The anatomy signal may be diluted by combining region identity and
   cell-type priors. Test `region_only`, `cell_type_only`, and `pure_anatomy`
   separately against `shared_baseline`.
4. Reported AUC should be selected by max eval AUC, not by lowest eval loss.

## Completed Probe: Stimulus Side

Run the fixed 20-recording benchmark with `--target-mode stimulus_side`.

Within-animal arms:

- `baseline`
- `shared_baseline`
- `pure_anatomy`
- `waveform_only`

Cross-animal arms:

- `shared_baseline`
- `region_only`
- `cell_type_only`
- `pure_anatomy`
- `waveform_only`

Success criterion for a demo signal:

- Cross-animal `pure_anatomy` or one of its single-channel components beats
  `shared_baseline` by at least 0.03 mean AUC across three seeds, with at least
  two positive seeds.

Result: no demo-grade signal on the default held-out subjects. `region_only`
was best but only 0.002 AUC above `shared_baseline`.

## Next Experiment: Leave-Subject-Out Diagnostic

Run each subject as the held-out animal and compare identity-free anatomy arms
against the shared null baseline:

- `shared_baseline`
- `region_only`
- `cell_type_only`
- `pure_anatomy`
- `waveform_only`

Default diagnostic run:

- target: `stimulus_side`
- seeds: `0`
- max steps: `600`
- output root: `runs/leave_subject_out_a100`
- report: `docs/leave_subject_out_results.md`

This is not meant as the final claim. It is a cheap screen for whether some
held-out animals or anatomical channels show a reproducible lift worth rerunning
with more seeds.

Result: the one-seed screen found candidate lifts, but not a global effect.
Aggregate `pure_anatomy` was +0.010 AUC over `shared_baseline` across 10
held-out subjects, positive in 7/10 pairs. Strongest candidate holdouts:

- `DY_008`: `pure_anatomy` +0.059, `region_only` +0.043
- `MFD_05`: `pure_anatomy` +0.040, `region_only` +0.044
- `CSHL045`: `region_only` +0.038
- `KS014`: `pure_anatomy` +0.029, despite weaker single-channel arms

## Completed Probe: Targeted Multi-Seed Confirmation

Run only the candidate held-out subjects with three seeds:

- subjects: `CSHL045 DY_008 MFD_05 KS014`
- arms: `shared_baseline region_only pure_anatomy waveform_only`
- seeds: `0 1 2`
- output root: `runs/lso_promising_a100`
- report: `docs/lso_promising_results.md`

Success criterion:

- Any anatomy arm beats `shared_baseline` by at least +0.03 mean AUC across the
  four candidate holdouts, with at least 8/12 positive subject-seed pairs.

Result: not confirmed as a general candidate-holdout effect. `pure_anatomy`
was positive in 9/12 subject-seed pairs, but only averaged +0.008 AUC over
`shared_baseline`. `waveform_only` averaged +0.010 AUC, and `region_only`
averaged -0.004 AUC. The only clearly reproducible held-out subject was
`DY_008`:

- `DY_008`: `pure_anatomy` +0.045 mean delta, positive in 3/3 seeds
- `DY_008`: `region_only` +0.041 mean delta, positive in 3/3 seeds

This is useful evidence that the machinery can surface cross-animal signals,
but it is not yet evidence for a robust open computational neuroscience result.

## Completed Probe: Local Subject-Conditioned Signal Audit

The next cheap step is to explain why `DY_008` works and the other candidate
holdouts do not. Before spending on longer training runs, run a subject-level
audit that reports, for each held-out animal:

- trial count and class balance for `stimulus_side`
- region coverage and overlap with the training animals
- recording/session count and probe coverage
- baseline AUC variance across seeds
- anatomy-arm delta grouped by anatomical region

Then rerun only the most defensible slice: either a region-balanced
leave-subject-out benchmark, or a narrowed anatomical target where held-out and
training animals have comparable coverage.

Local result: `docs/subject_conditioned_signal_audit.md` now combines the
20-recording manifest with the targeted LSO confirmation table. It confirms
that `DY_008` is the only subject where both `pure_anatomy` and `region_only`
clear +0.03 across three seeds. The local HDF5 cache is not the 20-recording
benchmark cache, though, so local trial-balance and region-coverage rows are
partial and cannot explain the signal.

## Completed Probe: Full-Dataset Coverage Audit

Run `scripts/audit_subject_signal.py` on a fresh RunPod clone after rebuilding
the 20-recording BrainSet data, but do not train. This should be a sub-$2 job
at the observed A100 rate because it only builds data and writes the audit.

Result: `docs/subject_conditioned_signal_audit.md` now contains a full-cache
audit over all 10 subjects and 20 recordings. The `DY_008` lift is not explained
by obvious class imbalance: it has 405 left vs 376 right valid stimulus-side
trials. It has partial but meaningful anatomical support in the training
subjects: 69.0% of held-out region units are in regions seen in other subjects,
and 6/8 top regions are seen in training. Two top `DY_008` regions, `PO` and
`LP`, are missing from the other subjects' top-region support.

Decision:

- If `DY_008` has comparable region support and class balance, run a
  region-balanced LSO rerun focused on `DY_008` plus matched controls.
- If `DY_008` has unusual coverage or imbalance, treat the current lift as a
  dataset-composition artifact and redesign the benchmark before spending on
  more seeds.

The decision gate points to a region-balanced rerun, not a broad multi-seed
sweep. The rerun should downsample or mask to regions with train/eval support
and compare `DY_008` against matched controls (`MFD_05`, `CSHL045`, `KS014`) so
we can distinguish a real transfer signal from coverage effects.

## Completed Probe: Region-Balanced LSO Rerun

Run `scripts/run_lso_region_balanced_a100.sh` with:

- subjects: `DY_008 MFD_05 CSHL045 KS014`
- arms: `shared_baseline region_only pure_anatomy`
- seeds: `0 1 2`
- region filter: `shared_regions`
- report: `docs/lso_region_balanced_results.md`

Result: the `DY_008` effect weakened after masking to regions shared between
train and held-out recordings, but did not disappear.

- `DY_008` `pure_anatomy`: +0.022 mean delta, positive in 3/3 seeds
- `DY_008` `region_only`: +0.023 mean delta, positive in 2/3 seeds
- aggregate `pure_anatomy`: +0.006 mean delta, positive in 8/12 pairs
- aggregate `region_only`: +0.014 mean delta, positive in 7/12 pairs

This is not demo-grade by the earlier +0.03 threshold. It suggests that some
of the original `DY_008` lift was coverage-sensitive, but the surviving
positive direction means the idea is not dead. The stronger post-mask result
was actually `KS014` `region_only` at +0.043 mean delta, though one seed was
negative.

Next decision: do not spend on simply repeating the same fine-region mask. The
more informative next check is to compare fine acronyms against coarser atlas
ancestor groups, because the audit showed substantial ancestor resolution in
the CCF mapping and fine-region labels may be too sparse across animals.

## Completed Probe: Coarse-Anatomy LSO Rerun

Run `scripts/run_lso_coarse_anatomy_a100.sh` with Allen parent acronyms for
region embeddings and shared-region masking:

- subjects: `DY_008 MFD_05 CSHL045 KS014`
- arms: `shared_baseline region_only pure_anatomy`
- seeds: `0 1 2`
- region granularity: `parent`
- report: `docs/lso_coarse_anatomy_results.md`

Result: coarse parent regions did not create a robust aggregate effect.

- aggregate `pure_anatomy`: -0.000 mean delta, positive in 6/12 pairs
- aggregate `region_only`: +0.005 mean delta, positive in 7/12 pairs
- `DY_008` `pure_anatomy`: +0.024 mean delta, positive in 2/3 clearly and
  one seed at +0.000
- `CSHL045` `pure_anatomy`: +0.033 mean delta, positive in 3/3 seeds

This shifts the best subject-specific candidate from `DY_008` to `CSHL045`,
but it is still not a general cross-animal anatomical transfer result. The
signal is now hopping across subjects depending on anatomical encoding, which
argues against making a claim from the current 20-recording benchmark.

Next decision: stop spending on architecture/encoding sweeps until the
benchmark is redesigned. The most likely failure mode is that stimulus-side
decoding at this sample size is dominated by subject/probe/session composition.
The next constructive step is an analysis-only benchmark redesign: choose a
larger manifest with matched region families across subjects, predefine
region-family holdout strata, and only then rerun a small seed sweep.

## Completed Planning Step: Larger Matched-Region Candidate Manifest

Run `scripts/plan_matched_region_manifest.py` without GPU training to select a
larger candidate benchmark from Alyx metadata:

- candidate manifest: `manifests/ibl_bwm_region_matched_candidates.json`
- planning report: `docs/matched_region_manifest_plan.md`
- target: 48 recordings
- subjects: 12
- labs: 12
- max recordings per subject: 4
- region granularity for later scoring: `parent`

Result: the metadata-balanced candidate manifest is ready, but it is not yet a
training benchmark. The local HDF5 cache does not contain these candidate
subjects, so anatomical region-family matching cannot be scored locally yet.

Decision gate before any more training:

- Build the 48 candidate recordings only as a data/audit job.
- Rerun `scripts/plan_matched_region_manifest.py` against that built cache.
- Require at least 80% held-out unit support for most subjects at parent-region
  granularity.
- Only then launch another small seed sweep.

## Budget Guard

Hard cap from user: do not spend more than $100.

The targeted multi-seed confirmation, full-dataset coverage audits,
region-balanced LSO rerun, and coarse-anatomy rerun completed under the cap and
left zero pods and zero network volumes. The matched-region candidate manifest
was generated locally from Alyx metadata with no GPU spend. Avoid additional
paid training until the candidate manifest has been built and region-scored.

Follow-up cloud audit attempt: a 48-recording matched-region data-build/audit
job was tried twice on RunPod A100 in `CA-MTL-3`.

- first attempt: 2-hour cap, 80 GB container disk, manually stopped after the
  pod missed the cap; no artifact was pushed
- second attempt: 4-hour cap, 160 GB container disk, pod-side pytest/smoke
  verification skipped, manually stopped after the pod still had not exited
  cleanly; no artifact was pushed
- estimated combined spend: about $8.45
- final resource state: zero pods and zero network volumes

## Completed Probe: CSH Shuffle-Control Redesign

After the two-holdout gate failed, the CSH_ZAD_019 artifacts were used to test
whether the shuffled-region null was too weak or accidentally target-correlated.
Three variants were compared in `docs/csh_shuffle_win_mode_audit.md`:

- original centered full-eval run
- target-balanced training
- recording-centered BCE

The audit showed that recording-centered BCE should not be repeated: shuffled
labels beat true labels by `+0.050` centered AUC and created stronger
within-recording target separation. The more conservative control was therefore
implemented as `within_recording_shuffle`, which preserves each recording's
region-label distribution while breaking unit-to-region identity.

Result: the one-seed within-recording shuffle pilot failed. True labels beat
the within-recording shuffle by only `+0.001` centered AUC, lost full-trial AUC
by `-0.024`, and lost the paired true-vs-shuffle comparison (`0.448` vs the
`0.550` threshold). This rules out broadening the current CSH setup as a
demo-path.

Next decision: do not spend on another same-objective seed sweep. The next
useful work is analysis-only:

- measure recording/probe offset usage directly from saved predictions
- compare target balance and region-family support inside each held-out
  recording, not just per subject
- define a new objective or benchmark where anatomical identity is tested
  against recording-matched negative controls from the start

Follow-up audit: `docs/lso_csh_within_recording_shuffle_failure_modes.md`
completes the first two analysis-only checks for the CSH within-recording
shuffle pilot. It found:

- parent-region support is adequate in the held-out CSH recordings
  (`0.752` minimum support), so missing parent coverage alone does not explain
  the failure
- `region_shuffle` gains `+0.014` AUC from recording-level offsets, while
  `region_only` loses `-0.011`
- shuffled-arm recording mean probabilities correlate with recording target
  prevalence (`0.694`), consistent with a calibration shortcut
- true labels still lose the paired true-vs-shuffle trial check (`0.448`)

Next experiment shape: replace the current raw-AUC-selected training/eval loop
with a recording-centered, recording-matched objective/gate. The minimum viable
bounded test should use:

- best checkpoint selected by recording-centered AUC only
- recording-matched within-recording shuffle as the mandatory negative control
- no pass condition on full raw AUC
- a paired true-vs-shuffle gate plus recording-level sign-flip support
- one CSH seed first, then broaden only if the centered true-vs-shuffle effect
  clears the existing anatomy-specific gate

Executable preflight: run
`uv run python scripts/preflight_recording_centered_pilot_runpod.py` before any
paid launch. The preset is intentionally one seed on an L4, with
`REGION_SHUFFLE_CONTROL=within_recording_shuffle`,
`BEST_METRIC=full_eval_centered_auc`, `FULL_EVAL_ON_BEST=1`, and
`SAVE_DIAGNOSTICS=1`. It prints the exact launch command plus the required
post-run anatomy-specific gate and prediction failure-mode audit. Do not launch
if it reports dirty git state, active pods, or estimated cost above `$8`.

Pilot result: the preset ran successfully on RunPod L4 and terminated cleanly,
but it failed the anatomy-specific gate. Metrics match the prior
within-recording-shuffle pilot: centered true-vs-shuffle delta `+0.001`, paired
true-vs-shuffle `0.448`, specificity gap `-0.103`, and sign-flip p-value
`0.25`. This means the current CSH setup is not just missing the right gate; the
learned true-region effect is too small relative to a recording-matched
shuffled control.

Updated next step: do not spend on more seeds for this CSH variant. Use the
saved predictions and local HDF5 cache to define a stricter inclusion rule for a
region-family slice before the next paid run. The next benchmark should choose
held-out recordings where the candidate parent regions have:

- sufficient held-out and training unit support
- nontrivial stimulus-side spike-rate contrast
- aligned contrast direction across train and held-out subjects
- an explicit within-recording shuffle negative control

Current consolidated state: `docs/current_experiment_state.md` now summarizes
the strict gates and fixed-slice attempts in one place. The decision is
`no_paid_broadening_without_new_mechanism`: zero current strict-gate artifacts
pass, and both fixed carrier-slice attempts let shuffled labels match or beat
true labels. This supersedes older "try another slice" recommendations.

Next mechanism task: audit the CSH success itself using saved predictions and
region embeddings. The useful question is not which broadening subject to rent
next; it is whether true region labels create any carrier-parent or
recording-level target-aware shift that a within-recording shuffled control
cannot reproduce.

Completed mechanism audit: `docs/csh_mechanism_audit.md` compared the
recording-centered CSH pilot's true-label arm against the within-recording
shuffled arm using saved predictions and region embeddings.

- global paired true-vs-shuffle: `0.448`
- specificity gap: `-0.103`
- mean carrier-parent embedding cosine true vs shuffled: `0.992`
- all four held-out recordings have true-vs-shuffle paired movement below `0.5`
- carrier-rich recordings are not rescued; the largest carrier slice
  (`5adab0b7...probe00`, 805 carrier units) has paired true-vs-shuffle `0.414`

Decision: the current objective is not producing an anatomical representation
that survives the recording-matched shuffled control. Do not run another
subject/slice selection job. The next implementable experiment should change
the training objective or model comparison so that true anatomical labels must
beat a within-recording shuffled-label arm on target-aware within-recording
ranking, preferably as a contrastive or paired auxiliary criterion.

Implemented objective candidate: `--loss-mode recording_pairwise_rank` optimizes
same-recording target-1 logits above target-0 logits with a logistic pairwise
ranking loss. It should be used with `BATCH_SAMPLING=recording_target_balanced`
so batches contain left/right pairs from the same recording. This directly
targets the failure mode found in `docs/csh_mechanism_audit.md`: true labels
must improve target-aware within-recording ordering rather than recording-level
calibration.

Bounded preflight for the next paid test:
`uv run python scripts/preflight_pairwise_rank_pilot_runpod.py`. It is a
one-seed CSH_ZAD_019 L4 pilot with
`REGION_SHUFFLE_CONTROL=within_recording_shuffle`,
`BEST_METRIC=full_eval_centered_auc`, and diagnostics enabled. Broaden only if
the strict anatomy-specific gate and CSH mechanism audit improve over the
current paired true-vs-shuffle `0.448` baseline.

Paid pilot result: the one-seed L4 pairwise-rank run finished successfully and
improved the paired mechanism check (`0.552` true-vs-shuffle, `+0.103`
specificity gap), but the strict gate still failed. Recording-centered AUC
favored the shuffled control (`0.480` true vs `0.494` shuffle), positive
recording support was `1/4`, and the recording sign-flip p-value was `0.562`.
This is enough to justify no-spend mechanism analysis or a very small objective
tweak; it is not enough to justify broadening across more subjects yet.

The no-spend mismatch audit resolved that ambiguity:
`docs/lso_csh_pairwise_rank_pilot_mismatch.md` classifies the paired improvement
as `paired_metric_explained_by_downward_shift`. Region-only probabilities were
lower than shuffle on every paired trial, which helps target-0 and hurts
target-1. The next gate should therefore require bidirectional target evidence:
true labels must beat the shuffled control separately for target-0 and target-1
subsets, in addition to improving recording-local ranking. The next implemented
objective candidate is `recording_pairwise_rank_centered_bce`; its bounded
preflight is
`uv run python scripts/preflight_pairwise_rank_centered_bce_pilot_runpod.py`.

Centered-BCE pilot outcome: the bounded L4 run completed and failed the strict
gate. It removed the pure downward-shift artifact from the pairwise-rank run,
but true labels still lost to the shuffled control on centered AUC (`0.485` vs
`0.500`) and on every held-out recording (`0/4` positive recording deltas).
Paired true-vs-shuffle fell to `0.486`. Stop paid one-off variants here. The
next implementable step should be no-spend design/code for a direct
recording-local AUC surrogate plus a bidirectional target-class success gate.

Implemented no-spend gate hardening: the strict anatomy gate now requires true
labels to improve target-0 and target-1 true-class probabilities separately
against the within-recording shuffled control. The scalar paired metric is no
longer sufficient. The training CLI also has
`--loss-mode recording_local_auc_surrogate`, an explicit alias for the
recording-local pairwise AUC surrogate, verified by CPU smoke. This should be
used only for local objective debugging until a bidirectional gate result looks
plausible.

Local probe result: `uv run python scripts/run_local_objective_probe.py --force
--max-steps 2` ran the direct AUC surrogate on CPU with full deterministic
held-out predictions. It failed the hardened gate (`target0=0.556`,
`target1=0.419`, centered delta `-0.005`, positive recordings `2/4`), so this
objective should not be launched on RunPod as-is. The next no-spend iteration
should change the objective or sampling so target0 and target1 improve together
within each recording before any more cloud spend.

Conclusion: building all 48 public IBL recordings inside a throwaway A100
container is the wrong next spend. The next attempt should either split the
candidate manifest into smaller persisted build shards, use a persistent
RunPod volume/cache for ONE downloads, or run the data construction on cheaper
CPU/storage before using GPU time for training. Do not launch another training
sweep until the matched-region cache has been scored.

Implemented next step: the IBL batch builder now supports deterministic shard
selection, per-shard markdown build reports, and partial-success exits. The
RunPod clone launcher can pass shard arguments through to the builder and
include the build report in the pushed result document. A tiny 2-recording
probe launch was attempted, but no pod was created because the checked A100
datacenters had no compatible capacity. Cleanup after those create attempts
left zero pods and zero network volumes.

Persistence correction: sharded build reports do not by themselves preserve the
HDF5 data needed for later scoring. The repo now has `scripts/sync_brainset_s3.py`
and optional RunPod launcher flags (`--s3-bucket`, `--s3-prefix`,
`--s3-datacenter`/`--s3-endpoint-url`) so each shard can download an existing
cache, build missing recordings, upload `.h5` files, and then exit. The next
paid run should use that S3 cache path, not a throwaway shard-only pod.
The cache can be audited with `scripts/sync_brainset_s3.py audit`; require
`Present: 48/48` before rerunning `scripts/plan_matched_region_manifest.py`
against the rebuilt cache for the 80% held-out unit-support gate.

## Completed Data Step: Compact Matched Support80/Best6 Cache

The 48-recording plan was narrowed to a compact support80/best6 manifest that
is cheap enough to train against while still matching anatomical support better
than the original 20-recording benchmark:

- manifest: `manifests/ibl_bwm_region_matched_support80_best6.json`
- cache audit: `docs/compact_support80_best6_s3_audit.md`
- recordings: 28
- subjects: 7
- S3 cache: 28/28 present
- build mode: `--no-wheel --trial-window-only --window-len 1.0`

This clears the previous decision gate for a small training screen. It does
not prove transfer; it only makes the next training comparison legitimate.

## Partial Matched-Cache LSO Screen

Run a one-seed matched-cache leave-subject-out screen with:

- subjects: all 7 matched-cache subjects
- arms: `shared_baseline pure_anatomy region_only`
- seed: `0`
- max steps: `300`
- eval batches: `20`
- target: `stimulus_side`
- report: `docs/lso_matched_support80_best6_seed0_results.md`

Result: the cloud run was partial but useful. It completed all three arms for
`CSH_ZAD_019`, `KS014`, and `MFD_06`, plus `shared_baseline` and
`pure_anatomy` for `NR_0019`. The recovered best-AUC deltas were:

- `MFD_06`: `pure_anatomy` +0.067, `region_only` +0.067
- `KS014`: `pure_anatomy` +0.017, `region_only` +0.038
- `CSH_ZAD_019`: `pure_anatomy` +0.002, `region_only` +0.029
- `NR_0019`: `pure_anatomy` -0.005

Interpretation: this is still not demo-grade because it is one seed and
partial. It does, however, produce a cleaner candidate than the earlier
20-recording benchmark: `MFD_06` is the first matched-cache holdout where both
anatomy arms beat the shared null by more than +0.03 on the screen seed.

Confirmation run: confirm only the candidate holdouts before broadening:

- subjects: `MFD_06 KS014 CSH_ZAD_019`
- arms: `shared_baseline pure_anatomy region_only`
- seeds: `1 2`
- same 300-step/20-eval-batch budget
- report: `docs/lso_matched_support80_best6_confirm_results.md`

Result: the seed-0 `MFD_06` lift did not replicate. Across seeds 1-2,
`MFD_06` was approximately null (`pure_anatomy` -0.006, `region_only` -0.002).
`KS014` was inconsistent (`region_only` -0.061, +0.080). The strongest
remaining candidate is now `CSH_ZAD_019`:

- `CSH_ZAD_019` `region_only`: +0.049 mean delta over seeds 1-2, positive in
  2/2 seeds
- `CSH_ZAD_019` `pure_anatomy`: +0.040 mean delta over seeds 1-2, positive in
  2/2 seeds
- including seed 0, `CSH_ZAD_019` `region_only` is positive in 3/3 seeds with
  an approximate +0.044 mean delta

Interpretation: this is the best current demo candidate, but still not a
general cross-animal anatomical transfer result. The next useful step is a
CSH_ZAD_019-focused ablation, not another broad sweep: rerun `CSH_ZAD_019`
with region-shuffled labels or shared-region masking to test whether the lift
depends on anatomical identity rather than another subject/session correlate.

## Completed Control: CSH_ZAD_019 Region-Label Shuffle

Add `--region-label-control shuffle` to `scripts/train.py`. The control
permutes region labels across unit tokens after vocab construction, preserving
the marginal region-label distribution but breaking the anatomy-to-unit mapping.

Run:

- subject: `CSH_ZAD_019`
- arms: `shared_baseline region_only region_shuffle`
- seeds: `0 1 2`
- target: `stimulus_side`
- report: `docs/lso_csh_zad_019_region_shuffle_results.md`

Result:

- true `region_only`: +0.042 mean delta, positive in 3/3 seeds
- shuffled-region control: -0.012 mean delta, effectively null
- seed deltas:
  - true `region_only`: +0.029, +0.054, +0.044
  - shuffled: +0.001, -0.036, +0.000

Interpretation: this is the first controlled evidence that the CSH_ZAD_019
effect depends on anatomical region identity rather than only model capacity or
the marginal region-label distribution. It is still subject-specific, so the
current honest claim is: "on a matched 28-recording IBL subset, one held-out
animal shows a reproducible cross-animal region-identity transfer signal that
collapses under shuffled anatomical labels." The next step toward a stronger
open computational neuroscience demo is to test whether the same CSH_ZAD_019
effect survives shared-region masking or parent-region granularity.

## Completed Stricter Control: CSH_ZAD_019 Shared Parent Regions

Run `scripts/run_lso_csh_zad_019_shared_parent_shuffle_a100.sh` to repeat the
true-vs-shuffled region-label control under stricter anatomical constraints:

- subject: `CSH_ZAD_019`
- arms: `shared_baseline region_only region_shuffle`
- seeds: `0 1 2`
- target: `stimulus_side`
- region filter: `shared_regions`
- region granularity: `parent`
- report: `docs/lso_csh_zad_019_shared_parent_shuffle_results.md`
- focused evidence audit: `docs/csh_zad_019_signal_audit.md`

Result:

- true parent `region_only`: +0.038 mean delta, positive in 3/3 seeds
- shuffled parent-region control: -0.012 mean delta, positive in 1/3 seeds
- seed deltas:
  - true `region_only`: +0.014, +0.045, +0.056
  - shuffled: -0.008, -0.030, +0.003

Interpretation: the CSH_ZAD_019 signal survives both shared-region masking and
parent-region coarsening. This is stronger than the fine-region shuffle result
because it reduces the chance that the lift is driven by held-out-only regions
or brittle fine acronyms. The claim is still subject-specific, but it is now a
credible demo nucleus: a held-out animal benefits from train-animal anatomical
region identity, and the benefit disappears when region identity is shuffled.

Next decision: stop rerunning CSH_ZAD_019 in isolation. The next useful spend is
either (1) a small transfer-screen of two more matched holdouts using the same
shared-parent true-vs-shuffled control, or (2) a publication-facing audit of the
CSH_ZAD_019 runs that extracts per-region unit support, class balance, and
failure modes before broadening.

## Focused Evidence Audit

`docs/csh_zad_019_signal_audit.md` is the current canonical evidence ladder for
the CSH_ZAD_019 claim. It combines the matched seed-0 screen, seeds 1-2
confirmation, fine-region shuffle control, and shared-parent shuffle control.
`docs/cross_animal_demo_brief.md` is the concise demo-facing version of the
same evidence and limitations.

Current claim:

- `CSH_ZAD_019` `region_only` is positive in 3/3 matched-cache seeds.
- Fine-region true labels beat shuffled labels (+0.042 vs -0.012 mean delta).
- Shared-parent true labels also beat shuffled labels (+0.038 vs -0.012 mean
  delta).
- The result remains subject-specific; it is a credible demo nucleus, not yet a
  general cross-animal effect.

An initial two-holdout broadening wrapper now exists:
`scripts/run_lso_two_holdout_shared_parent_shuffle_a100.sh`. The first cloud
attempt produced `docs/lso_two_holdout_shared_parent_shuffle_results.md`, but
that result is empty and should be treated as an aborted/non-evidence run.
The wrapper now writes `summary.md` incrementally after completed arms/holdouts,
so a future interrupted run should still preserve partial evidence for cleanup
to push.

Before launching that broadening run, execute:

```bash
uv run python scripts/preflight_two_holdout_runpod.py --max-dollars 10
```

The preflight does not rent a pod. It verifies that the Git branch is clean and
synced, active RunPod pods are zero, and the estimated one-pod worst-case cost
is below the cap. The canonical launch now tries both `NVIDIA A100 80GB PCIe`
and `NVIDIA A100-SXM4-80GB` by availability. With the current 5400-second
runtime guard, 7200-second provisioning guard, and a conservative `$3.00/hr`
assumption, the estimated maximum is `$6.00`.

Latest status: a later short-alias cloud attempt wrote `d.md` using `t.sh` and
output root `r`, but it also produced `Missing Sweep Summary`; treat it as
another aborted/non-evidence run. Do not count `d.md` toward the evidence
ladder. Those short-alias root files have been removed from the branch. The
next paid attempt should use only the canonical preflight command above and
should not start if any unexpected RunPod pod already exists.

Capacity note: an `ANY` datacenter create attempt with only
`NVIDIA A100 80GB PCIe` failed before allocation because no matching instances
were available. A second attempt with both A100 variants rented a `$1.49/hr`
pod and did start training even though the RunPod status API continued to
report no public IP and `machineReady=false`. That attempt was manually
terminated after several minutes because the readiness fields looked stalled,
so it only preserved partial KS014 seed-0 evidence. Active pods returned to
zero. Do not manually terminate future polled pods based only on those
readiness fields; rely on the runtime guard unless cost or API state clearly
violates the cap.

Follow-up rerun: a clean relaunch self-terminated early and pushed another
`Missing Sweep Summary` artifact. Its log reached dependency setup and S3 cache
download, then stopped during HDF5 download before training. The launcher now
has a body-level ERR trap and optional `--dependency-diagnostic` mode so the
next paid step should first capture dependency/disk/CUDA diagnostics or a
download-only cache check before retrying the full two-holdout sweep.

Dependency diagnostic result: dependency setup is not the blocker. The pod
completed `uv sync --no-dev`, imported the required Python/GPU stack, saw one
CUDA device, and had about 67 GB free on the 80 GB container disk. The real
launcher bug found by the diagnostic was cleanup control: pod-side RunPod
DELETE returned HTTP 403 after completion, allowing diagnostic pods to remain
in desired `RUNNING` state and restart. The local poller now watches the S3
diagnostic log for a fresh completion marker and terminates diagnostic pods
from the local API.

Cache-check result: `docs/runpod_cache_download_check.md` verifies that the
same pod path can download all 28 cached HDF5 files, skip all existing build
outputs, verify `Present: 28/28`, write `manifests/ibl_bwm.local.json`, and
exit through the new body-completion marker. That clears the S3/cache path as
the immediate failure point.

Completed two-holdout broadening result:
`docs/lso_two_holdout_shared_parent_shuffle_results.md` now contains usable
rows for `KS014` and `MFD_06` under the same shared-parent true-vs-shuffled
control. The first follow-up audit is
`docs/shared_parent_broadening_audit.md`.

- `KS014` `region_only`: +0.022 mean delta, positive in 2/3 seeds
- `KS014` `region_shuffle`: -0.008 mean delta, positive in 1/3 seeds
- `MFD_06` `region_only`: +0.010 mean delta, positive in 2/3 seeds
- `MFD_06` `region_shuffle`: -0.003 mean delta, positive in 1/3 seeds
- aggregate `region_only`: +0.016 mean delta, positive in 4/6 pairs
- aggregate `region_shuffle`: -0.006 mean delta, positive in 2/6 pairs

Interpretation: this is directionally consistent with the CSH_ZAD_019 control,
because true parent-region labels beat shuffled parent labels on both added
holdouts and in aggregate. It is not a broad demo-grade anatomical transfer
result: the lift is small, noisy by seed, and far below the stronger
CSH_ZAD_019 effect. Do not rerun the same two-holdout sweep unchanged. The next
no-spend step should audit why CSH_ZAD_019 is strong while KS014 and MFD_06 are
weak, using the split diagnostics, per-parent-region support, trial balance,
and baseline AUC variance already present in the logs.

Completed no-spend audit:
`docs/parent_region_support_signal_audit.md` uses the compact 28-recording HDF5
cache to compute parent-region unit support and a simple per-parent stimulus-side
spike-rate contrast. The weak broadening subjects have higher global
parent-region support than CSH_ZAD_019 (`KS014` 96.2%, `MFD_06` 98.7%,
`CSH_ZAD_019` 84.8%), so the broadening failure is not explained by a simple
support-fraction deficit. The remaining issue is anatomical composition: only
five parent regions (`BS`, `MBmot`, `cc`, `root`, `void`) are shared by all
three strict splits. The next paid experiment should either preselect holdouts
whose parent-region composition resembles CSH_ZAD_019 or force all compared
holdouts onto a common parent-region panel before training.

Completed no-spend candidate ranking:
`docs/csh_composition_candidate_ranking.md` ranks the remaining matched-cache
subjects by parent-region unit-count similarity to the strong `CSH_ZAD_019`
holdout. `NR_0019` is the closest candidate by weighted Jaccard and cosine,
while the already-tested `KS014` and `MFD_06` are among the least CSH-like
subjects by composition.

Paid gate selected at that point under the $100 hard cap:

- run only `NR_0019` first under the same shared-parent true-vs-shuffled control
- arms: `shared_baseline region_only region_shuffle`
- seeds: `0 1 2`
- target: `stimulus_side`
- region filter: `shared_regions`
- region granularity: `parent`
- stop after `NR_0019` unless true `region_only` beats both the shared null and
  shuffled control by a meaningful margin

This is the cheapest defensible broadening step because it tests whether the
CSH_ZAD_019 effect generalizes to the most compositionally similar held-out
animal, instead of paying again for holdouts that the no-spend audit already
flags as mismatched.

Completed paid gate: `NR_0019` shared-parent control:
`docs/lso_nr0019_shared_parent_shuffle_results.md` ran the top-ranked
compositionally similar holdout under the same shared-parent true-vs-shuffled
control.

- `NR_0019` `region_only`: -0.008 mean delta, positive in 1/3 seeds
- `NR_0019` `region_shuffle`: +0.003 mean delta, positive in 2/3 seeds
- cache gate: 28/28 matched-cache HDF5 files present
- resource cleanup: zero active RunPod pods after completion

Interpretation: the most CSH-like follow-up did not reproduce the
CSH_ZAD_019 signal. This materially weakens the hypothesis that the CSH result
will broaden simply by choosing anatomically similar held-out subjects. The
current honest position is now narrower: CSH_ZAD_019 remains a controlled,
subject-specific demo nucleus, while matched-cache broadening has failed on
three additional holdouts (`KS014`, `MFD_06`, `NR_0019`) at demo-grade effect
size.

Next no-spend step before any more GPU rental: analyze why `CSH_ZAD_019`
separates from the three weak follow-ups at the parent-region level. Use the
existing logs and cache to compare per-parent unit mass, trial support,
baseline AUC, and region-wise stimulus-side spike contrast for all four
controlled holdouts. Do not launch another paid broadening run until that
failure-mode audit produces a specific falsifiable slice.

Completed no-spend failure-mode audit:
`docs/cross_holdout_failure_mode_audit.md` compares the four controlled
shared-parent true-vs-shuffled holdouts (`CSH_ZAD_019`, `KS014`, `MFD_06`,
`NR_0019`) using preserved result docs plus the local 28-recording cache.

Key findings:

- `CSH_ZAD_019` remains the only strong controlled success: true-minus-shuffle
  gap +0.050, true positive in 3/3 seeds.
- `KS014` and `MFD_06` have very high parent-region support (96.2% and 98.7%),
  so support fraction alone does not explain failure.
- `NR_0019` is the closest CSH-like candidate by composition and has the
  largest raw parent-level spike-rate contrast, but true parent labels are
  below the shared null and below shuffled labels.
- Trial counts and class balance are adequate for all four controlled holdouts.

Decision: do not spend on another broad LSO sweep or another composition-only
candidate. The next useful step is to define a parent-region-specific slice
from the successful CSH run: identify CSH parent regions that are shared,
high-mass, and stimulus-informative, then search for held-out subjects/sessions
where those same parents have enough units and aligned stimulus-side contrast.
Only after that slice is specified should we run another small true-vs-shuffled
control.

Completed no-spend parent-region slice definition:
`docs/parent_region_slice_plan.md` defines an explicit carrier-parent slice
from the successful CSH_ZAD_019 run and scores the current matched-cache
subjects/sessions against it.

Carrier parents:

- `PRT`, `CA`, `VP`, `MOp`, `DG`, `mfbc`

Candidate gate:

- at least 500 units in the carrier-region slice
- at least two carrier parents with at least 50 units
- at least 75% of carrier-slice units have the same stimulus-side contrast sign
  as CSH_ZAD_019

Current-cache candidates:

- `NYU-12`: passes cleanly; 750 slice units, 3/6 carrier parents, 100% aligned
  unit mass (`CA`, `VP`, `DG`)
- `SWC_038`: passes narrowly; 503 slice units, 4/6 carrier parents, 76.7%
  aligned unit mass
- strongest recording-level candidate:
  `a8a8af78-16de-4841-ab07-fde4b5281a03_probe01` from `NYU-12`, with 591
  slice units in `CA` and `DG`, 100% aligned

Implementation gate completed: `scripts/train.py` and the shared-parent wrapper
now support an explicit include list via `--region-filter include_regions` and
`--region-include`.

Completed paid fixed-slice gate:
`docs/lso_nyu12_parent_slice_results.md` ran the top passing candidate
(`NYU-12`) with the fixed carrier-parent include list
`PRT,CA,VP,MOp,DG,mfbc` under the same true-vs-shuffled control. The run used
the existing 28/28 matched-cache files, finished successfully, and active
RunPod pods were zero after completion.

Result:

- `NYU-12` `region_only`: +0.013 mean delta, positive in 2/3 seeds
- `NYU-12` `region_shuffle`: +0.020 mean delta, positive in 3/3 seeds
- true seed deltas: +0.067, +0.021, -0.048
- shuffled seed deltas: +0.038, +0.015, +0.007
- preflight worst-case cost envelope: $6.00; actual usage was well below the
  $100 cap because the pod ran briefly at $1.49/hr

Interpretation: the fixed carrier-parent slice did not pass the controlled
demo gate. The true-label arm is weakly positive, but the shuffled-label arm is
larger and more consistent, so this result does not support a generalizable
anatomical-transfer claim beyond the CSH_ZAD_019 nucleus. This also means the
no-spend support/alignment gate is insufficient on its own.

Next decision: pause paid GPU broadening. The next useful work is no-spend
analysis of the CSH-specific success mode: compare region-pair interactions,
session/probe contributions, and trial-conditioned behavior across CSH_ZAD_019
versus the failed follow-ups. Only launch another GPU run after defining a
stricter falsifiable slice that predicts true labels should beat shuffled
labels, not merely clear support and contrast-alignment thresholds.

Completed no-spend success-mode audit:
`docs/transfer_success_mode_audit.md` compares the CSH carrier parents against
the actual leave-subject-out training aggregate for each candidate. This is
closer to the model's transfer setting than the earlier CSH-sign-only slice.

Key findings:

- `NYU-12` failed despite 100.0% sign alignment to the LSO training aggregate,
  so sign alignment alone is not sufficient.
- `NYU-12` covers only 44.9% of the CSH carrier-weighted signal because it
  includes `CA`, `VP`, and `DG` but lacks `PRT` and `MOp`.
- `MFD_06` and `NR_0019` fail the LSO-train sign screen: 1.2% and 20.8%
  aligned unit mass.
- `SWC_038` is now the only untested subject clearing the stricter gate: 503
  slice units, 78.5% CSH carrier-weighted coverage, and 76.7% LSO-train
  aligned unit mass.
- `SWC_043` remains below gate: 42.3% CSH carrier-weighted coverage and 74.0%
  LSO-train aligned unit mass.

Completed paid stricter fixed-slice gate:
`docs/lso_swc038_parent_slice_results.md` ran `SWC_038` under the same
carrier-parent true-vs-shuffled control. The run produced two completed seeds
before termination, enough to fail the stop rule:

- `SWC_038` `region_only`: -0.004 mean delta, positive in 0/2 completed seeds
- `SWC_038` `region_shuffle`: +0.019 mean delta, positive in 2/2 completed
  seeds
- cache gate: 28/28 matched-cache HDF5 files present
- preflight envelope: $4.50-$6.00, below the $100 cap
- active pods returned to zero after completion/termination

Interpretation: the stricter support + CSH-weighted coverage + LSO-train
alignment gate also failed. This is a stronger negative result than NYU-12
because `SWC_038` was the only remaining untested subject that cleared the
stricter no-spend screen. Do not spend on another matched-cache fixed-slice
variant without a new mechanism. The next useful work is no-spend analysis of
the actual CSH success: inspect per-recording model outputs, region-embedding
behavior, and whether the apparent anatomical lift is tied to CSH-specific
session/probe structure rather than a transferable anatomical code.

Instrumentation gates completed: `scripts/train.py` can now export diagnostic
artifacts and official deterministic full held-out-trial metrics when a new
best checkpoint is selected:

- `--save-eval-predictions` writes held-out trial predictions to
  `eval_predictions.jsonl` with recording id, subject, target, logit, and
  probability.
- `--save-region-embeddings` writes learned region embedding vectors to
  `region_embeddings.jsonl` with mapped region acronym and embedding norm.
- `--full-eval-on-best` scores every valid held-out trial and logs a
  `full_eval` event with loss, accuracy, AUC, trial count, and class counts.
- `scripts/run_lso_csh_zad_019_shared_parent_shuffle_a100.sh` and
  `scripts/run_lso_two_holdout_shared_parent_shuffle_a100.sh` can enable these
  via `SAVE_DIAGNOSTICS=1` and `FULL_EVAL_ON_BEST=1`.
- `scripts/runpod_clone_a100.py` now force-adds only those diagnostic JSONL
  files from ignored `runs/` trees, not checkpoints.
- `scripts/analyze_leave_subject_out.py` now reports a separate full
  held-out-trial AUC table and aggregate delta table whenever either
  `full_eval` log events or `eval_predictions.jsonl` artifacts are available.

Local smoke check: `runs/instrumentation_smoke` verified the new exports on a
one-step CPU run with five prediction rows and 79 region-embedding rows.

Next falsifiable diagnostic run, if spending again: rerun only the canonical
`CSH_ZAD_019` shared-parent true-vs-shuffled control with `SAVE_DIAGNOSTICS=1`
and a small prediction cap first, using the already proven result doc path or a
new diagnostic result doc. The goal is not another broadening claim; it is to
answer whether the CSH lift is distributed across recordings/trials and whether
the learned region embeddings show true-vs-shuffled structure. Do not launch
another candidate-subject run until those exported artifacts have been audited.

Completed partial CSH diagnostic run:
`docs/lso_csh_diagnostic_outputs_results.md` is incomplete as a sweep because
the pod hit the 300-second unprovisioned guard before writing `summary.md`, but
it did preserve diagnostic artifacts under `runs/lso_csh_diagnostic_outputs`.
`docs/csh_diagnostic_output_audit.md` analyzes those artifacts.

Available artifacts:

- seed 0 `shared_baseline`: full held-out predictions for 2,726 trials
- seed 0 `region_only`: full held-out predictions and 79 region embeddings
- seed 0 `region_shuffle`: full held-out predictions and 79 region embeddings
- seed 1 `shared_baseline`: full held-out predictions

Artifact-level finding:

- seed 0 full held-out AUC: `shared_baseline` 0.500, `region_only` 0.508,
  `region_shuffle` 0.509
- seed 0 full held-out deltas: true `region_only` +0.008, shuffled +0.009
- carrier-region embedding norms are nearly identical between true and shuffled
  seed-0 runs; same-region true-vs-shuffle cosines are 0.990-0.997

Interpretation: this partial diagnostic materially weakens the current CSH demo
claim. The earlier CSH summaries were based on sampled eval batches, while the
new exported seed-0 full-trial predictions show no true-vs-shuffled separation.
The next engineering step should be to promote deterministic full held-out-trial
evaluation into the official sweep summary, then rerun only the canonical CSH
control under that metric. Do not spend on any additional held-out animal until
the canonical CSH result survives full-trial evaluation.

Official full-trial summary gate completed locally: the analyzer can now recover
full held-out-trial AUCs from the preserved diagnostic artifacts. For the partial
CSH diagnostic output, it reports seed-0 full-trial deltas of +0.008 for
`region_only` and +0.009 for `region_shuffle`, matching the artifact audit and
showing no true-vs-shuffled separation.

Next paid run, if any, should be only the canonical `CSH_ZAD_019` shared-parent
control with `FULL_EVAL_ON_BEST=1`, three seeds, and no new held-out subjects.
Use `SAVE_DIAGNOSTICS=0` unless embeddings or exported predictions are needed
again, because `full_eval` log events are enough for the official summary and
are cheaper to preserve. Stop immediately if the full-trial true-label arm does
not beat both the shared null and the shuffled-label arm across seeds.

First CSH full-eval launch attempt:
`docs/lso_csh_full_eval_shared_parent_shuffle_results.md` records a RunPod
provisioning failure, not an experiment. Two A100 pods landed on the same
unusable machine id without runtime access, `US-MO-1` was rejected as an invalid
current datacenter id, and `US-IL-1` had no matching A100 capacity. Cleanup
returned active pods to zero. The launcher now treats machine id alone as
unprovisioned for the billing guard; a future paid retry should wait for
healthier A100 capacity or use a different valid GPU/datacenter path.

Cheap fallback check: an `NVIDIA L4` retry also failed before training, with no
machine details or public IP, and the hardened 300-second guard terminated it.
This points to a RunPod runtime provisioning/access issue rather than an
A100-only capacity issue. Active pods returned to zero again.

No-spend paired-output audit update:
`docs/csh_diagnostic_output_audit.md` now compares seed-0 anatomy-arm
predictions against the shared baseline trial by trial. Both `region_only` and
`region_shuffle` mostly apply a uniform upward probability shift rather than a
target-aware correction: `region_only` shifts probability by +0.019 on average
and improves the true-class probability on only 45.5% of paired trials, while
`region_shuffle` shifts by +0.020 and improves 44.8%. The true-label arm has
larger per-recording AUC gains on the two `5adab0b7` probes, but the shuffled
control also improves those probes. This makes the surviving seed-0 full-trial
signal look more like calibration/probe-specific behavior than a clean
anatomical identity code.

Next no-spend modeling step: specify an objective or evaluation gate that
requires anatomy to improve target-aware ranking/calibration, not just shift
held-out probabilities. Candidate directions are per-recording calibration
before AUC comparison, paired-trial signed probability improvement as a
selection metric, or a contrastive anatomy objective that must separate true
labels from shuffled labels before another paid sweep.

Gate specification update: the diagnostic audit now reports recording-centered
AUC and a direct true-vs-shuffle paired-trial gate. On seed 0,
recording-centered AUC is mildly positive for true labels (`region_only` 0.521,
shared baseline 0.500, shuffled 0.510), but the paired true-vs-shuffle gate
fails: true labels move probability in the correct class direction over shuffled
labels on only 50.6% of paired trials, below the 55.0% demo threshold. Treat the
centered AUC as a hypothesis to preserve, not enough evidence to spend on broad
candidate subjects.

Minimum demo gate before another broadening run:

- full held-out-trial true-label AUC must beat shared and shuffled controls
  across seeds
- recording-centered true-label AUC must beat shared and shuffled controls
- true labels must improve target-direction probability over shuffled labels on
  at least 55% of paired held-out trials
- learned region embeddings should show more separation than near-identical
  true-vs-shuffle cosines

Implementation update: `scripts/analyze_leave_subject_out.py` now emits
recording-centered full-trial AUC and the paired true-vs-shuffle gate whenever
`eval_predictions.jsonl` artifacts are present. The recovered CSH diagnostic
result doc has been refreshed with these standard sections. This makes the gate
available for future canonical reruns without hand-auditing the JSONL files.

Executable gate update: `scripts/check_lso_demo_gate.py` writes a JSON pass/fail
artifact for an LSO root and holdout. Running it on the preserved CSH diagnostic
artifacts produced `docs/lso_csh_diagnostic_outputs_gate.json` with overall
`pass: false`. Seed 0 passes centered-AUC checks but fails both full true-vs-
shuffle AUC and the paired 55% threshold; seed 1 is incomplete because only the
shared baseline artifact exists. Future canonical runs should publish this JSON
next to the result doc and must pass before any broadening spend.

Training selection update: `scripts/train.py` now supports `--best-metric`
values `eval_auc`, `full_eval_auc`, and `full_eval_centered_auc`, and the
CSH/two-holdout wrappers expose this as `BEST_METRIC=...`. The next canonical
rerun should use `BEST_METRIC=full_eval_centered_auc` so checkpoint selection
uses every held-out trial and removes recording-level probability offsets before
ranking. Local CPU smoke `runs/best_metric_smoke` verified that
`full_eval_centered_auc` checkpoint selection logs `best_metric:
full_eval_centered_auc`, saves a best checkpoint, and emits `full_eval` metrics.

Next canonical command shape, once cloud runtime access is healthy:

```bash
FULL_EVAL_ON_BEST=1 SAVE_DIAGNOSTICS=1 BEST_METRIC=full_eval_centered_auc \
  uv run python scripts/runpod_clone_a100.py --poll ... \
  --sweep-script scripts/run_lso_csh_zad_019_shared_parent_shuffle_a100.sh \
  --output-root runs/lso_csh_full_eval_shared_parent_shuffle \
  --result-doc docs/lso_csh_full_eval_shared_parent_shuffle_results.md \
  --sweep-env FULL_EVAL_ON_BEST=1 \
  --sweep-env SAVE_DIAGNOSTICS=1 \
  --sweep-env BEST_METRIC=full_eval_centered_auc
```

RunPod retry update: after the launcher was hardened to preserve pods with
active S3 logs, the L4 rerun completed all three seeds for `CSH_ZAD_019` under
`runs/lso_csh_full_eval_centered_shared_parent_shuffle`. The executable gate
still failed: only seed 2 passed, with overall `n_passing_seeds=1/3`. Mean
recording-centered full-trial AUC improved for region-only (`0.517`, delta
`+0.016`) while shuffled regions stayed at chance (`0.501`, delta `-0.000`),
but paired true-vs-shuffle trial improvement was inconsistent (`0.513`,
`0.486`, `0.552` against the `0.550` threshold). Treat this as suggestive but
insufficient evidence, not a successful cross-animal anatomical-transfer demo.

Seed-ensemble diagnostic: `scripts/analyze_lso_prediction_ensemble.py` shows
that averaging the three seeds raises region-only centered AUC to `0.519` versus
shuffle `0.513`, but paired `region_only_vs_shuffle` improves only `0.536` of
trials. Because `shuffle_vs_shared` improves `0.552` of trials, the paired
true-probability statistic is not specific enough to be the primary demo
criterion. The next paid experiment should replicate the centered-AUC delta on a
second held-out animal or switch the gate to a recording-centered true-vs-shuffle
AUC/permutation test before spending on broader sweeps.

Second-holdout replication: a bounded L4 run for `NR_0019` completed under
`runs/lso_nr0019_full_eval_centered_shared_parent_shuffle`. It is negative:
the executable gate has `n_passing_seeds=0/3`, paired true-vs-shuffle
improvements are `0.500`, `0.493`, and `0.512`, and the seed ensemble has
paired `region_only_vs_shuffle=0.493`. Although the NR_0019 ensemble has a small
full/centered AUC separation from shuffled regions (`region_only` full AUC
`0.508`, centered `0.505`; shuffle full `0.494`, centered `0.493`), it does not
replicate the CSH centered-AUC pattern strongly enough for a demo. Do not spend
on more same-setup held-out sweeps until the objective/gate is redesigned around
a statistically defensible anatomy-specific contrast.

Cross-holdout evidence summary:
`scripts/summarize_anatomy_transfer_evidence.py` writes
`docs/anatomy_transfer_evidence_summary.{json,md}` from the CSH and NR_0019 gate
plus ensemble diagnostics. Current decision is
`redesign_before_more_spend`. CSH has broad recording-level AUC support
(`4/4` recordings true > shuffle), but its paired true-vs-shuffle ensemble
fraction is `0.536`, below both the `0.550` gate and the shuffle-vs-shared
fraction `0.552`. NR_0019 has positive ensemble AUC deltas but only `1/4`
recordings true > shuffle and paired true-vs-shuffle is `0.493`. This means the
existing run setup has not demonstrated a general cross-animal anatomical
transfer signal. The next milestone should be an offline gate/objective redesign
that produces an anatomy-specific statistic on these saved predictions before
any additional GPU spend.

Anatomy-specific permutation gate: `scripts/analyze_anatomy_specific_permutation.py`
now tests the seed-ensemble `region_only` vs `region_shuffle` contrast with
recording-level sign flips. CSH still fails: centered delta is only `+0.006`,
paired specificity gap is `-0.016`, and the one-sided sign-flip p-value is
`0.0625` despite `4/4` positive recordings. NR_0019 also fails: centered delta
is `+0.012`, but only `1/4` recordings are positive, specificity gap is `0.000`,
and sign-flip p-value is `0.5000`. This confirms the current architecture/gate
is not demo-ready. The next implementation step should change what is trained
or selected, not spend on more held-out animals.

Target-balanced training update: `scripts/train.py` now supports
`--batch-sampling target_balanced`, and the CSH/two-holdout RunPod wrappers
expose it as `BATCH_SAMPLING=target_balanced`. This alternates accepted
left/right targets during training while leaving sampled eval uniform, so the
next candidate run is less able to exploit target-prior imbalance without
changing the held-out metric. The next paid run should be a bounded single
CSH_ZAD_019 pilot with `BATCH_SAMPLING=target_balanced`,
`BEST_METRIC=full_eval_centered_auc`, `FULL_EVAL_ON_BEST=1`, and
`SAVE_DIAGNOSTICS=1`; only broaden to NR_0019 if the strict anatomy-specific
permutation gate improves.

Target-balanced RunPod pilot attempt: preflight passed on branch
`runpod-pilot-phases-3-5` with `active_pods: 0`, `git_ready: True`, L4
`costPerHr=$0.39`, and an estimated guarded cost of `$0.78` under an `$8`
launch cap. Pod `4zqrrhmb02mm6j` was rented but never exposed runtime details
or visible startup progress; it was manually terminated after roughly seven
minutes to avoid idle spend. Follow-up preflight again reported
`active_pods: 0`. The next attempt should use the same target-balanced command
shape but with a shorter provisioning cap or a more reliable datacenter/GPU
availability target.

Target-balanced resume state: a later cloud artifact push produced partial
prediction files for `runs/lso_csh_target_balanced_pilot`. Seed 0 has
`shared_baseline`, `region_only`, and `region_shuffle` prediction artifacts;
seed 1 has `shared_baseline` only. The current full-trial gate is still false:
seed 0 passes paired true-vs-shuffle (`0.557` over the `0.550` threshold) and
full AUC true-vs-shuffle, but fails centered-AUC true-vs-shared/shuffle
(`region_only=0.473`, `region_shuffle=0.474`, `shared=0.478`). The wrappers now
resume from prediction-only diagnostic arms so these artifacts are not wiped on
the next attempt. A second L4 placement, pod `kwsbwnvn2d6jrm`, hit the same
machine id `8mfa5qalulbd` and again failed to expose runtime details; it was
terminated with follow-up preflight showing `active_pods: 0`. The launcher guard
was fixed so stale S3 log timestamps cannot indefinitely extend the provisioning
deadline.

Target-balanced decision update: a subsequent resume completed seed 1
`region_only` and `region_shuffle`, plus seed 2 `shared_baseline`. The standard
gate remains false with `n_passing_seeds=0/3`; seeds 0 and 1 both fail
centered-AUC true-vs-shared, so finishing seed 2 cannot make this pilot pass.
The complete-seed ensemble (`seeds=[0,1]`, incomplete seed 2 omitted) is
directionally better than the original target-balanced per-seed table but still
not demo-grade: `region_only` full AUC is `0.505` vs `0.490` shuffle, centered
AUC is `0.492` vs `0.483` shuffle, paired true-vs-shuffle is `0.516`, and the
anatomy-specific gate fails on centered-delta threshold (`+0.009` vs required
`+0.010`) and recording sign-flip (`p=0.125`). Stop spending on this exact
target-balanced variant; the next implementation change should attack
recording/subject-prior leakage more directly rather than complete seed 2.

Recording-centered loss variant: `scripts/train.py` now supports
`--loss-mode recording_centered_bce` and `--batch-sampling
recording_target_balanced`. This trains on logits after subtracting each
recording's mean logit within the accepted batch, with left/right pairs drawn
from the same recording. The goal is to remove the recording-offset shortcut
that repeatedly hurts the centered-AUC gate while keeping eval and prediction
export on raw logits. CPU smoke `runs/recording_centered_loss_smoke` completed
then was removed after verifying the trainer logs `loss_mode:
recording_centered_bce`, `batch_sampling: recording_target_balanced`, and
full centered eval. The next bounded paid check should be a one-seed
CSH_ZAD_019 pilot under a low cap:

```bash
uv run python scripts/runpod_clone_a100.py --poll \
  --datacenter ANY \
  --gpu-type 'NVIDIA L4' \
  --container-disk-gb 80 \
  --max-runtime-seconds 3600 \
  --max-provision-seconds 300 \
  --skip-verification \
  --skip-cell-type-priors \
  --build-recordings 0 \
  --max-steps 300 \
  --eval-batches 20 \
  --target-mode stimulus_side \
  --manifest-path manifests/ibl_bwm_region_matched_support80_best6.json \
  --seeds '0' \
  --sweep-script scripts/run_lso_two_holdout_shared_parent_shuffle_a100.sh \
  --output-root runs/lso_csh_recording_centered_loss_pilot \
  --result-doc docs/lso_csh_recording_centered_loss_pilot_results.md \
  --s3-bucket rppfvo6ifn \
  --s3-prefix brainsets/ibl_bwm \
  --s3-datacenter US-IL-1 \
  --name-prefix anfm-csh-recording-centered \
  --sweep-env SUBJECTS=CSH_ZAD_019 \
  --sweep-env BATCH_SAMPLING=recording_target_balanced \
  --sweep-env LOSS_MODE=recording_centered_bce \
  --sweep-env BEST_METRIC=full_eval_centered_auc \
  --sweep-env FULL_EVAL_ON_BEST=1 \
  --sweep-env SAVE_DIAGNOSTICS=1
```

Recording-centered loss pilot result: the one-seed CSH_ZAD_019 run completed
under `runs/lso_csh_recording_centered_loss_pilot` and is a strong negative.
The standard gate fails with `n_passing_seeds=0/1`. True region labels are worse
than both shared and shuffled controls: full AUC `0.479` vs shared `0.501` and
shuffle `0.512`; centered AUC `0.480` vs shared `0.501` and shuffle `0.530`;
paired true-vs-shuffle is only `0.451`. The anatomy-specific gate fails every
check, with centered delta vs shuffle `-0.050`, specificity gap `-0.092`, and
`0/4` recordings positive. Do not broaden or repeat this exact
recording-centered-loss variant. The next useful implementation step should
focus on why shuffled parent labels can outperform true labels, likely by
auditing region-label distribution, per-region trial contrast, and whether the
current `region_shuffle` control is creating an easier nuisance partition under
the centered objective.

Shuffle-win audit: `scripts/audit_shuffle_win_modes.py` compares the centered,
target-balanced, and recording-centered-loss CSH prediction artifacts in
`docs/csh_shuffle_win_mode_audit.{json,md}`. The centered and target-balanced
runs do not show a shuffle separation win: true labels are slightly above
shuffle on centered AUC (`+0.006` and `+0.009`) and slightly above shuffle on
centered target separation, but the effect is tiny. The recording-centered-loss
run is different: shuffle beats true on centered AUC by `+0.050`, and shuffle
creates a much stronger within-recording target separation than true labels
(`true-minus-shuffle centered separation = -0.0096`). The largest single
recording driver is `49e0ab27-827a-4c91-bcaa-97eea27a1b8d_probe01`
(`-0.0307` true-minus-shuffle centered separation). This argues that the next
step is not another loss tweak. It is to redesign the anatomical control and/or
region vocabulary so shuffled labels cannot accidentally create an easier
target-correlated partition than the true parent labels.

Next no-spend design target: audit region-label assignments for the CSH heldout
and training recordings against target contrast, then replace simple unit-level
region shuffling with a stricter negative control that preserves recording,
region counts, and any per-recording target/region exposure structure. A
credible next GPU run should only happen after this control audit explains why
the current `region_shuffle` can win.

Stricter shuffle-control implementation: `scripts/train.py` now supports
`--region-label-control within_recording_shuffle`. Unlike the previous global
`shuffle`, this permutes region labels only among units from the same recording,
so every recording keeps its own region-label distribution while anatomy-to-unit
identity is broken. The CSH/two-holdout wrappers expose this as
`REGION_SHUFFLE_CONTROL=within_recording_shuffle` for the `region_shuffle` arm.
Local CPU smoke `runs/within_recording_shuffle_smoke` completed and was removed
after verifying the trainer logs `region_label_control:
within_recording_shuffle` and full centered eval.

Next bounded candidate: rerun only a one-seed CSH_ZAD_019 comparison with the
original BCE objective, `BEST_METRIC=full_eval_centered_auc`, diagnostics on,
and `REGION_SHUFFLE_CONTROL=within_recording_shuffle`. This tests whether the
positive true-vs-shuffle centered AUC edge survives a stricter negative control
that cannot change per-recording region marginals. Do not broaden to more
subjects unless true labels beat this stricter shuffle control on centered AUC
and paired true-probability direction.

After cleanup, run:

```bash
uv run python scripts/check_lso_demo_gate.py \
  runs/lso_csh_full_eval_centered_shared_parent_shuffle \
  --holdout CSH_ZAD_019 \
  --out docs/lso_csh_full_eval_centered_shared_parent_shuffle_gate.json
```

## Current Phase 3-5 Stop Condition

The stricter within-recording shuffle, pairwise-rank objective, centered-BCE
anchor, bidirectional target-class gate, and local objective probe are now in
place. The paid one-seed L4 pilots did not produce a demo-quality transfer
signal, and the newest no-spend CPU matrix rejects all current local variants
for cloud promotion:

- `recording_local_auc_surrogate`
- `recording_centered_bce`
- `recording_pairwise_rank_centered_bce`
- `recording_local_auc_surrogate` with target-balanced sampling

All four local probes fail centered true-vs-shuffle AUC, target1 true-class
improvement, and recording support. The next step is not another RunPod pilot.
Redesign the sampler/objective locally until target0 and target1 both improve
within recordings against the shuffled control, then spend only on a bounded
confirmation run.
