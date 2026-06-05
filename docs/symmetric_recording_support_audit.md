# Symmetric Recording Support Audit

Ranks current model-free rows by symmetric recording-local support: each recording contributes `min(target0_improved, target1_improved)`, so one-sided global wins cannot dominate the ranking.

- rows: `280`
- candidates: `0`
- max bidirectional recordings: `2`
- max bidirectional recording fraction: `0.500`
- max mean symmetric support: `0.543`
- decision: `no_symmetric_recording_candidate`

## Top Symmetric Rows

| report | context | decision | centered delta | global target0 | global target1 | bidir recs | mean sym | min sym | target imbalance | one-sided |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| shared family target/control | choice / broad_named_anatomy / SWC_043 | not_symmetric_recording_candidate | +0.008 | 0.534 | 0.610 | 2/4 | 0.531 | 0.446 | 0.083 | 2 |
| shared family target/control | feedback / broad_named_anatomy / NYU-12 | not_symmetric_recording_candidate | -0.002 | 0.540 | 0.554 | 2/4 | 0.487 | 0.347 | 0.100 | 1 |
| family centered l2=100 | stimulus_side / KS014 | not_symmetric_recording_candidate | +0.078 | 0.505 | 0.555 | 2/4 | 0.485 | 0.358 | 0.086 | 1 |
| family centered l2=1 | stimulus_side / KS014 | not_symmetric_recording_candidate | +0.081 | 0.510 | 0.549 | 2/4 | 0.485 | 0.362 | 0.088 | 1 |
| family centered | stimulus_side / KS014 | not_symmetric_recording_candidate | +0.080 | 0.510 | 0.548 | 2/4 | 0.484 | 0.362 | 0.089 | 1 |
| family feedback | feedback / NR_0019 | not_symmetric_recording_candidate | +0.011 | 0.532 | 0.500 | 2/4 | 0.432 | 0.086 | 0.131 | 0 |
| shared family target/control | choice / fiber_tracts / CSH_ZAD_019 | not_symmetric_recording_candidate | +0.199 | 0.558 | 0.614 | 1/4 | 0.543 | 0.503 | 0.079 | 3 |
| family prior side | prior_side / KS014 | not_symmetric_recording_candidate | +0.060 | 0.553 | 0.552 | 1/4 | 0.524 | 0.477 | 0.057 | 2 |
| source-target families | stimulus_side / MFD_06 -> SWC_038 | not_symmetric_recording_candidate | +0.088 | 0.601 | 0.524 | 1/4 | 0.518 | 0.467 | 0.082 | 3 |
| source-target families | stimulus_side / CSH_ZAD_019 -> SWC_038 | not_symmetric_recording_candidate | +0.029 | 0.545 | 0.552 | 1/4 | 0.510 | 0.483 | 0.071 | 2 |
| source-target centered | stimulus_side / KS014 -> SWC_043 | not_symmetric_recording_candidate | +0.085 | 0.551 | 0.524 | 1/4 | 0.509 | 0.459 | 0.057 | 1 |
| panel grandparent centered | stimulus_side / NYU-12 | not_symmetric_recording_candidate | +0.011 | 0.499 | 0.569 | 1/4 | 0.493 | 0.440 | 0.077 | 2 |
| family centered l2=1 | stimulus_side / CSH_ZAD_019 | not_symmetric_recording_candidate | +0.013 | 0.495 | 0.538 | 1/4 | 0.491 | 0.401 | 0.051 | 1 |
| family centered | stimulus_side / CSH_ZAD_019 | not_symmetric_recording_candidate | +0.013 | 0.495 | 0.539 | 1/4 | 0.491 | 0.401 | 0.052 | 1 |

## Decision

Use this ranking before any future GPU trigger. A candidate should be near the top by symmetric recording support and should not be driven by many target0-only or target1-only recordings.
