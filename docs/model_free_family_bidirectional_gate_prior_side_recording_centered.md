# Model-Free Family Recording-Bidirectional Gate

Closed-form ridge audit on predefined parent-region family aggregates, using the same recording-local bidirectional promotion rule.

- target mode: `prior_side`
- feature mode: `recording_centered`
- holdouts: `7`
- candidates: `0`
- positive centered-delta holdouts: `6`
- mean bidirectional recording fraction: `0.107`
- decision: `no_recording_bidirectional_model_free_signal`

| holdout | centered delta | target0 | target1 | positive recs | bidirectional recs | decision |
|---|---:|---:|---:|---:|---:|---|
| CSH_ZAD_019 | +0.026 | 0.493 | 0.539 | 3/4 | 0/4 | reject: global target0 |
| KS014 | +0.060 | 0.553 | 0.552 | 3/4 | 1/4 | reject: recording bidirectionality |
| MFD_06 | +0.049 | 0.544 | 0.517 | 3/4 | 1/4 | reject: global target0 |
| NR_0019 | +0.008 | 0.494 | 0.505 | 2/4 | 0/4 | reject: centered delta |
| NYU-12 | +0.005 | 0.478 | 0.507 | 4/4 | 0/4 | reject: centered delta |
| SWC_038 | -0.016 | 0.480 | 0.523 | 1/4 | 1/4 | reject: centered delta |
| SWC_043 | +0.004 | 0.457 | 0.494 | 1/4 | 0/4 | reject: centered delta |

## Decision

Do not promote to GPU training unless this family aggregate gate produces at least one candidate holdout. The family aggregate path is meant to reduce parent-region sparsity, not relax the same-recording target0+target1 rule.
