# Cross-Animal Anatomical Transfer Plan

Current status: the 20-recording choice-decoding benchmark is real, but the
cross-animal signal is effectively null. Scoring by max eval AUC gives a small
pure-anatomy lift over the shared null baseline, but not enough to claim a
transfer result.

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

## Next Experiment: Targeted Multi-Seed Confirmation

Run only the candidate held-out subjects with three seeds:

- subjects: `CSHL045 DY_008 MFD_05 KS014`
- arms: `shared_baseline region_only pure_anatomy waveform_only`
- seeds: `0 1 2`
- output root: `runs/lso_promising_a100`
- report: `docs/lso_promising_results.md`

Success criterion:

- Any anatomy arm beats `shared_baseline` by at least +0.03 mean AUC across the
  four candidate holdouts, with at least 8/12 positive subject-seed pairs.

## Budget Guard

Hard cap from user: do not spend more than $100.

The targeted multi-seed confirmation should use the existing 3-hour timeout and
is expected to cost roughly $2-$4 at the observed $1.39/hr rate. Always verify
zero pods and zero network volumes after the run.
