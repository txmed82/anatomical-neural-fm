# Model-Free Family Recording-Bidirectional Gate

Closed-form ridge audit on predefined parent-region family aggregates, using the same recording-local bidirectional promotion rule.

- target mode: `feedback`
- feature mode: `recording_centered`
- holdouts: `7`
- candidates: `0`
- positive centered-delta holdouts: `4`
- mean bidirectional recording fraction: `0.107`
- decision: `no_recording_bidirectional_model_free_signal`

| holdout | centered delta | target0 | target1 | positive recs | bidirectional recs | decision |
|---|---:|---:|---:|---:|---:|---|
| CSH_ZAD_019 | +0.007 | 0.477 | 0.487 | 2/4 | 0/4 | reject: centered delta |
| KS014 | -0.004 | 0.204 | 0.445 | 1/4 | 0/4 | reject: centered delta |
| MFD_06 | +0.002 | 0.535 | 0.473 | 3/4 | 1/4 | reject: centered delta |
| NR_0019 | +0.011 | 0.532 | 0.500 | 3/4 | 2/4 | reject: global target0 |
| NYU-12 | -0.071 | 0.412 | 0.443 | 1/4 | 0/4 | reject: centered delta |
| SWC_038 | -0.024 | 0.421 | 0.458 | 1/4 | 0/4 | reject: centered delta |
| SWC_043 | +0.004 | 0.469 | 0.470 | 2/4 | 0/4 | reject: centered delta |

## Decision

Do not promote to GPU training unless this family aggregate gate produces at least one candidate holdout. The family aggregate path is meant to reduce parent-region sparsity, not relax the same-recording target0+target1 rule.
