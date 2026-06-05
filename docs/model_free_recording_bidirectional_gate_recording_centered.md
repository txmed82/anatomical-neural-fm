# Model-Free Recording-Bidirectional Gate

Closed-form parent-region ridge audit with a stricter support rule: a recording counts only when true region labels beat the within-recording shuffle for target0 and target1 in that same recording.

- holdouts: `7`
- candidates: `0`
- positive centered-delta holdouts: `2`
- mean bidirectional recording fraction: `0.071`
- decision: `no_recording_bidirectional_model_free_signal`

| holdout | centered delta | target0 | target1 | positive recs | bidirectional recs | decision |
|---|---:|---:|---:|---:|---:|---|
| CSH_ZAD_019 | -0.043 | 0.416 | 0.534 | 1/4 | 0/4 | reject: centered delta |
| KS014 | +0.042 | 0.520 | 0.540 | 2/4 | 1/4 | reject: global target0 |
| MFD_06 | -0.024 | 0.471 | 0.510 | 2/4 | 0/4 | reject: centered delta |
| NR_0019 | +0.047 | 0.482 | 0.550 | 3/4 | 0/4 | reject: global target0 |
| NYU-12 | -0.011 | 0.514 | 0.450 | 2/4 | 0/4 | reject: centered delta |
| SWC_038 | -0.007 | 0.510 | 0.494 | 2/4 | 1/4 | reject: centered delta |
| SWC_043 | -0.012 | 0.488 | 0.481 | 1/4 | 0/4 | reject: centered delta |

## Decision

Do not promote a model-free or neural training run unless at least one holdout clears this recording-local bidirectional gate. Positive centered deltas that split target0 and target1 wins across different recordings are not evidence for a cross-animal anatomical transfer mechanism.
