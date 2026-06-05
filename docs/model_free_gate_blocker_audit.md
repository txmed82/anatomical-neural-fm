# Model-Free Gate Blocker Audit

Aggregates current model-free holdout and source-target gate artifacts to identify which promotion checks actually block the cross-animal anatomy claim.

- rows audited: `168`
- candidates: `0`
- positive centered-delta rows: `86`
- max bidirectional recordings: `2`
- max bidirectional recording fraction: `0.500`

## Blocker Counts

| blocker | rows missing check |
|---|---:|
| centered_delta | 97 |
| target0 | 130 |
| target1 | 136 |
| recording_bidirectionality | 168 |

## Top Same-Recording Bidirectional Rows

| report | label | decision | centered delta | target0 | target1 | bidir recs | positive rec frac | missing checks |
|---|---|---|---:|---:|---:|---:|---:|---|
| family centered l2=1 | KS014 | reject: global target0 | +0.081 | 0.510 | 0.549 | 2/4 | 0.750 | target0, target1, recording_bidirectionality |
| family centered | KS014 | reject: global target0 | +0.080 | 0.510 | 0.548 | 2/4 | 0.750 | target0, target1, recording_bidirectionality |
| family centered l2=100 | KS014 | reject: global target0 | +0.078 | 0.505 | 0.555 | 2/4 | 0.750 | target0, recording_bidirectionality |
| family feedback | NR_0019 | reject: global target0 | +0.011 | 0.532 | 0.500 | 2/4 | 0.750 | target0, target1, recording_bidirectionality |
| source-target centered | MFD_06 -> SWC_038 | reject: global target1 | +0.092 | 0.705 | 0.382 | 1/4 | 0.750 | target1, recording_bidirectionality |
| source-target families | MFD_06 -> SWC_038 | reject: global target1 | +0.088 | 0.601 | 0.524 | 1/4 | 1.000 | target1, recording_bidirectionality |
| source-target centered | KS014 -> SWC_043 | reject: global target1 | +0.085 | 0.551 | 0.524 | 1/4 | 0.750 | target1, recording_bidirectionality |
| source-target families | KS014 -> SWC_038 | reject: global target1 | +0.082 | 0.592 | 0.497 | 1/4 | 0.750 | target1, recording_bidirectionality |
| source-target families | MFD_06 -> KS014 | reject: global target0 | +0.082 | 0.538 | 0.547 | 1/4 | 0.750 | target0, target1, recording_bidirectionality |
| source-target families | KS014 -> MFD_06 | reject: global target0 | +0.077 | 0.536 | 0.542 | 1/4 | 0.750 | target0, target1, recording_bidirectionality |

## Closest Rows By Worst Gate Margin

| report | label | decision | worst margin | centered delta | target0 | target1 | bidir frac | missing checks |
|---|---|---|---:|---:|---:|---:|---:|---|
| family centered | KS014 | reject: global target0 | -0.250 | +0.080 | 0.510 | 0.548 | 0.500 | target0, target1, recording_bidirectionality |
| family centered l2=1 | KS014 | reject: global target0 | -0.250 | +0.081 | 0.510 | 0.549 | 0.500 | target0, target1, recording_bidirectionality |
| family centered l2=100 | KS014 | reject: global target0 | -0.250 | +0.078 | 0.505 | 0.555 | 0.500 | target0, recording_bidirectionality |
| family feedback | NR_0019 | reject: global target0 | -0.250 | +0.011 | 0.532 | 0.500 | 0.500 | target0, target1, recording_bidirectionality |
| panel counts | NYU-12 | reject: centered delta | -0.500 | -0.015 | 0.410 | 0.624 | 0.250 | centered_delta, target0, recording_bidirectionality |
| panel recording centered | KS014 | reject: global target0 | -0.500 | +0.042 | 0.520 | 0.540 | 0.250 | target0, target1, recording_bidirectionality |
| panel recording centered | SWC_038 | reject: centered delta | -0.500 | -0.007 | 0.510 | 0.494 | 0.250 | centered_delta, target0, target1, recording_bidirectionality |
| panel grandparent centered | KS014 | reject: global target0 | -0.500 | +0.050 | 0.500 | 0.533 | 0.250 | target0, target1, recording_bidirectionality |
| panel grandparent centered | NYU-12 | reject: global target0 | -0.500 | +0.011 | 0.499 | 0.569 | 0.250 | target0, recording_bidirectionality |
| family centered | CSH_ZAD_019 | reject: global target0 | -0.500 | +0.013 | 0.495 | 0.539 | 0.250 | target0, target1, recording_bidirectionality |

## Decision

The limiting condition is no longer just centered AUC or ridge tuning. Across all audited local model-free variants, no row reaches more than two bidirectional recordings, and the closest rows still miss global target0/target1 or same-recording bidirectionality. The next plan should change the benchmark/control definition enough to create same-recording bidirectional evidence before any GPU run.
