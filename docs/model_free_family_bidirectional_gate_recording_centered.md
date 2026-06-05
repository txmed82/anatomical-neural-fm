# Model-Free Family Recording-Bidirectional Gate

Closed-form ridge audit on predefined parent-region family aggregates, using the same recording-local bidirectional promotion rule.

- target mode: `stimulus_side`
- feature mode: `recording_centered`
- holdouts: `7`
- candidates: `0`
- positive centered-delta holdouts: `4`
- mean bidirectional recording fraction: `0.179`
- decision: `no_recording_bidirectional_model_free_signal`

| holdout | centered delta | target0 | target1 | positive recs | bidirectional recs | decision |
|---|---:|---:|---:|---:|---:|---|
| CSH_ZAD_019 | +0.013 | 0.495 | 0.539 | 3/4 | 1/4 | reject: global target0 |
| KS014 | +0.080 | 0.510 | 0.548 | 3/4 | 2/4 | reject: global target0 |
| MFD_06 | +0.024 | 0.565 | 0.489 | 3/4 | 1/4 | reject: global target1 |
| NR_0019 | -0.051 | 0.466 | 0.464 | 0/4 | 0/4 | reject: centered delta |
| NYU-12 | +0.001 | 0.483 | 0.502 | 2/4 | 0/4 | reject: centered delta |
| SWC_038 | -0.007 | 0.503 | 0.541 | 2/4 | 1/4 | reject: centered delta |
| SWC_043 | -0.041 | 0.414 | 0.485 | 1/4 | 0/4 | reject: centered delta |

## Decision

Do not promote to GPU training unless this family aggregate gate produces at least one candidate holdout. The family aggregate path is meant to reduce parent-region sparsity, not relax the same-recording target0+target1 rule.
