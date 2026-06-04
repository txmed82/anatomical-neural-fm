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

## Next Experiment

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

## Budget Guard

Hard cap from user: do not spend more than $100.

The next A100 run should use the existing 3-hour timeout and is expected to cost
roughly $1-$2 at the observed $1.39/hr rate. Always verify zero pods and zero
network volumes after the run.
