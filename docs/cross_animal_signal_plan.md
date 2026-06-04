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

## Budget Guard

Hard cap from user: do not spend more than $100.

The targeted multi-seed confirmation and full-dataset coverage audits completed
under the cap and left zero pods and zero network volumes. The next paid run
should be a narrow region-balanced LSO check, not a broad exploratory sweep.
