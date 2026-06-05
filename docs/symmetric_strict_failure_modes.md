# Symmetric Strict Failure Mode Audit

Ranks the closest current rows against the strict symmetric promotion gate and explains which requirement each row misses.

- rows: `280`
- strict candidates: `0`
- target threshold: `0.550`
- bidirectional fraction: `0.75`
- required recordings for four-recording rows: `3`
- global-target-clear rows: `4`
- one-recording-short and global-clear rows: `0`
- blocker counts: `global_target0=197, global_target1=215, recording_bidirectionality=280`
- decision: `strict_failure_modes_identified`

## Closest Strict-Gate Misses

| report | context | blockers | global target0 | global target1 | margins | bidir recs | missing | mean sym | one-sided |
|---|---|---|---:|---:|---|---:|---:|---:|---:|
| shared family target/control | feedback / broad_named_anatomy / NYU-12 | recording_bidirectionality, global_target0 | 0.540 | 0.554 | -0.010/+0.004 | 2/3 | 1 | 0.487 | 1 |
| shared family target/control | choice / broad_named_anatomy / SWC_043 | recording_bidirectionality, global_target0 | 0.534 | 0.610 | -0.016/+0.060 | 2/3 | 1 | 0.531 | 2 |
| family centered l2=1 | stimulus_side / KS014 | recording_bidirectionality, global_target0, global_target1 | 0.510 | 0.549 | -0.040/-0.001 | 2/3 | 1 | 0.485 | 1 |
| family centered | stimulus_side / KS014 | recording_bidirectionality, global_target0, global_target1 | 0.510 | 0.548 | -0.040/-0.002 | 2/3 | 1 | 0.484 | 1 |
| family centered l2=100 | stimulus_side / KS014 | recording_bidirectionality, global_target0 | 0.505 | 0.555 | -0.045/+0.005 | 2/3 | 1 | 0.485 | 1 |
| family feedback | feedback / NR_0019 | recording_bidirectionality, global_target0, global_target1 | 0.532 | 0.500 | -0.018/-0.050 | 2/3 | 1 | 0.432 | 0 |
| shared family target/control | choice / fiber_tracts / CSH_ZAD_019 | recording_bidirectionality | 0.558 | 0.614 | +0.008/+0.064 | 1/3 | 2 | 0.543 | 3 |
| shared family target/control | feedback / broad_named_anatomy / SWC_043 | recording_bidirectionality | 0.554 | 0.559 | +0.004/+0.009 | 1/3 | 2 | 0.469 | 3 |
| family prior side | prior_side / KS014 | recording_bidirectionality | 0.553 | 0.552 | +0.003/+0.002 | 1/3 | 2 | 0.524 | 2 |
| source-target families | stimulus_side / CSH_ZAD_019 -> SWC_038 | recording_bidirectionality, global_target0 | 0.545 | 0.552 | -0.005/+0.002 | 1/3 | 2 | 0.510 | 2 |
| source-target families | stimulus_side / MFD_06 -> KS014 | recording_bidirectionality, global_target0, global_target1 | 0.538 | 0.547 | -0.012/-0.003 | 1/3 | 2 | 0.487 | 2 |
| source-target families | stimulus_side / KS014 -> MFD_06 | recording_bidirectionality, global_target0, global_target1 | 0.536 | 0.542 | -0.014/-0.008 | 1/3 | 2 | 0.487 | 3 |

## Decision

The next no-spend experiment should target the one-recording-short rows whose remaining global miss is marginal, especially target0 misses in the shared broad-anatomy rows. If a redesign cannot turn those rows into at least three of four bidirectional recordings while clearing both global target floors locally, it should not launch a paid neural training run.
