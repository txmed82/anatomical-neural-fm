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
is below the cap. With the current 5400-second guard and a conservative
`$1.50/hr` assumption, the estimated maximum is `$2.25`.

Latest status: a later short-alias cloud attempt wrote `d.md` using `t.sh` and
output root `r`, but it also produced `Missing Sweep Summary`; treat it as
another aborted/non-evidence run. Do not count `d.md` toward the evidence
ladder. The next paid attempt should use only the canonical preflight command
above and should not start if any unexpected RunPod pod already exists.
