# Model-Free Recording-Bidirectional Gate

Closed-form parent-region ridge audit with a stricter support rule: a recording counts only when true region labels beat the within-recording shuffle for target0 and target1 in that same recording.

- holdouts: `7`
- candidates: `0`
- positive centered-delta holdouts: `3`
- mean bidirectional recording fraction: `0.000`
- decision: `no_recording_bidirectional_model_free_signal`

| holdout | centered delta | target0 | target1 | positive recs | bidirectional recs | decision |
|---|---:|---:|---:|---:|---:|---|
| CSH_ZAD_019 | -0.029 | 0.401 | 0.635 | 0/4 | 0/4 | reject: centered delta |
| KS014 | +0.027 | 0.548 | 0.537 | 2/4 | 0/4 | reject: global target0 |
| MFD_06 | -0.006 | 0.578 | 0.443 | 1/4 | 0/4 | reject: centered delta |
| NR_0019 | +0.065 | 0.815 | 0.230 | 2/4 | 0/4 | reject: global target1 |
| NYU-12 | -0.015 | 0.813 | 0.238 | 1/4 | 0/4 | reject: centered delta |
| SWC_038 | -0.043 | 0.927 | 0.078 | 1/4 | 0/4 | reject: centered delta |
| SWC_043 | +0.080 | 0.997 | 0.009 | 4/4 | 0/4 | reject: global target1 |

## Decision

Do not promote a model-free or neural training run unless at least one holdout clears this recording-local bidirectional gate. Positive centered deltas that split target0 and target1 wins across different recordings are not evidence for a cross-animal anatomical transfer mechanism.
