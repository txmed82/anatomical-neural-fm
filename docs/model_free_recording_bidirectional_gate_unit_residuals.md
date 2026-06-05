# Model-Free Recording-Bidirectional Gate

Closed-form parent-region ridge audit with a stricter support rule: a recording counts only when true region labels beat the within-recording shuffle for target0 and target1 in that same recording.

- holdouts: `7`
- candidates: `0`
- positive centered-delta holdouts: `6`
- mean bidirectional recording fraction: `0.000`
- decision: `no_recording_bidirectional_model_free_signal`

| holdout | centered delta | target0 | target1 | positive recs | bidirectional recs | decision |
|---|---:|---:|---:|---:|---:|---|
| CSH_ZAD_019 | +0.011 | 0.120 | 0.903 | 3/4 | 0/4 | reject: global target0 |
| KS014 | +0.035 | 0.305 | 0.753 | 2/4 | 0/4 | reject: global target0 |
| MFD_06 | -0.037 | 0.387 | 0.570 | 0/4 | 0/4 | reject: centered delta |
| NR_0019 | +0.035 | 0.334 | 0.645 | 3/4 | 0/4 | reject: global target0 |
| NYU-12 | +0.026 | 0.694 | 0.341 | 3/4 | 0/4 | reject: global target1 |
| SWC_038 | +0.038 | 0.400 | 0.623 | 3/4 | 0/4 | reject: global target0 |
| SWC_043 | +0.017 | 0.372 | 0.605 | 2/4 | 0/4 | reject: global target0 |

## Decision

Do not promote a model-free or neural training run unless at least one holdout clears this recording-local bidirectional gate. Positive centered deltas that split target0 and target1 wins across different recordings are not evidence for a cross-animal anatomical transfer mechanism.
