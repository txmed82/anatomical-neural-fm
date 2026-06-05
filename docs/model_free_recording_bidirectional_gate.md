# Model-Free Recording-Bidirectional Gate

Closed-form parent-region ridge audit with a stricter support rule: a recording counts only when true region labels beat the within-recording shuffle for target0 and target1 in that same recording.

- holdouts: `7`
- candidates: `0`
- positive centered-delta holdouts: `2`
- mean bidirectional recording fraction: `0.036`
- decision: `no_recording_bidirectional_model_free_signal`

| holdout | centered delta | target0 | target1 | positive recs | bidirectional recs | decision |
|---|---:|---:|---:|---:|---:|---|
| CSH_ZAD_019 | -0.052 | 0.338 | 0.703 | 1/4 | 0/4 | reject: centered delta |
| KS014 | +0.030 | 0.547 | 0.538 | 2/4 | 0/4 | reject: global target0 |
| MFD_06 | -0.016 | 0.567 | 0.451 | 2/4 | 0/4 | reject: centered delta |
| NR_0019 | +0.079 | 0.776 | 0.249 | 3/4 | 0/4 | reject: global target1 |
| NYU-12 | -0.015 | 0.410 | 0.624 | 2/4 | 1/4 | reject: centered delta |
| SWC_038 | -0.032 | 0.629 | 0.336 | 0/4 | 0/4 | reject: centered delta |
| SWC_043 | -0.014 | 0.738 | 0.212 | 2/4 | 0/4 | reject: centered delta |

## Decision

Do not promote a model-free or neural training run unless at least one holdout clears this recording-local bidirectional gate. Positive centered deltas that split target0 and target1 wins across different recordings are not evidence for a cross-animal anatomical transfer mechanism.
