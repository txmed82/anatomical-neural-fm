# Shared Broad-Anatomy Repair Sweep

Focused no-spend sweep for the two shared broad-anatomy rows identified by the strict symmetric failure-mode audit.

- rows: `24`
- candidates: `0`
- max bidirectional recordings: `2`
- max min target margin: `-0.010`
- max centered delta vs shuffle: `+0.078`
- decision: `no_shared_broad_anatomy_repair_candidate`

## Top Sweep Rows

| target | holdout | feature | l2 | decision | missing | delta shuffle | delta total | target0 | target1 | bidir recs |
|---|---|---|---:|---|---|---:|---:|---:|---:|---:|
| feedback | NYU-12 | recording_centered | 1 | reject: shuffle | shuffle_delta, total_delta, target0, recording_bidirectionality | -0.002 | -0.008 | 0.540 | 0.554 | 2/3 |
| feedback | NYU-12 | recording_centered | 10 | reject: shuffle | shuffle_delta, total_delta, target0, recording_bidirectionality | -0.002 | -0.008 | 0.540 | 0.554 | 2/3 |
| feedback | NYU-12 | recording_centered | 100 | reject: shuffle | shuffle_delta, total_delta, target0, recording_bidirectionality | -0.002 | -0.008 | 0.540 | 0.554 | 2/3 |
| choice | SWC_043 | recording_centered | 1 | reject: total baseline | total_delta, target0, recording_bidirectionality | +0.008 | -0.160 | 0.534 | 0.610 | 2/3 |
| choice | SWC_043 | recording_centered | 10 | reject: total baseline | total_delta, target0, recording_bidirectionality | +0.008 | -0.160 | 0.534 | 0.610 | 2/3 |
| choice | SWC_043 | recording_centered | 100 | reject: total baseline | total_delta, target0, recording_bidirectionality | +0.008 | -0.160 | 0.534 | 0.610 | 2/3 |
| feedback | NYU-12 | unit_residuals | 1 | reject: total baseline | total_delta, target0, target1, recording_bidirectionality | +0.038 | -0.007 | 0.521 | 0.522 | 0/3 |
| feedback | NYU-12 | unit_residuals | 10 | reject: total baseline | total_delta, target0, target1, recording_bidirectionality | +0.038 | -0.007 | 0.521 | 0.522 | 0/3 |
| feedback | NYU-12 | unit_residuals | 100 | reject: total baseline | total_delta, target0, target1, recording_bidirectionality | +0.038 | -0.007 | 0.521 | 0.522 | 0/3 |
| choice | SWC_043 | counts | 1 | reject: shuffle | shuffle_delta, total_delta, target1, recording_bidirectionality | -0.008 | -0.006 | 0.625 | 0.339 | 0/3 |
| choice | SWC_043 | counts | 10 | reject: shuffle | shuffle_delta, total_delta, target1, recording_bidirectionality | -0.008 | -0.006 | 0.625 | 0.339 | 0/3 |
| choice | SWC_043 | counts | 100 | reject: shuffle | shuffle_delta, total_delta, target1, recording_bidirectionality | -0.008 | -0.006 | 0.625 | 0.339 | 0/3 |

## Decision

This sweep is a local repair attempt, not a relaxed gate. A GPU run remains unjustified unless a row clears true-vs-shuffle, total baseline, both global target floors, and at least three of four same-recording bidirectional hits.
