# Model-Free Recording-Bidirectional Gate

Closed-form parent-region ridge audit with a stricter support rule: a recording counts only when true region labels beat the within-recording shuffle for target0 and target1 in that same recording.

- holdouts: `7`
- candidates: `0`
- positive centered-delta holdouts: `3`
- mean bidirectional recording fraction: `0.000`
- decision: `no_recording_bidirectional_model_free_signal`

| holdout | centered delta | target0 | target1 | positive recs | bidirectional recs | decision |
|---|---:|---:|---:|---:|---:|---|
| CSH_ZAD_019 | -0.070 | 0.310 | 0.750 | 0/4 | 0/4 | reject: centered delta |
| KS014 | +0.033 | 0.582 | 0.566 | 3/4 | 0/4 | reject: recording bidirectionality |
| MFD_06 | -0.013 | 0.686 | 0.361 | 2/4 | 0/4 | reject: centered delta |
| NR_0019 | +0.088 | 0.946 | 0.069 | 3/4 | 0/4 | reject: global target1 |
| NYU-12 | -0.027 | 0.264 | 0.743 | 1/4 | 0/4 | reject: centered delta |
| SWC_038 | -0.081 | 0.650 | 0.303 | 0/4 | 0/4 | reject: centered delta |
| SWC_043 | +0.027 | 0.503 | 0.482 | 3/4 | 0/4 | reject: global target0 |

## Decision

Do not promote a model-free or neural training run unless at least one holdout clears this recording-local bidirectional gate. Positive centered deltas that split target0 and target1 wins across different recordings are not evidence for a cross-animal anatomical transfer mechanism.
