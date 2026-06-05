# Model-Free Recording-Bidirectional Gate

Closed-form parent-region ridge audit with a stricter support rule: a recording counts only when true region labels beat the within-recording shuffle for target0 and target1 in that same recording.

- holdouts: `7`
- candidates: `0`
- positive centered-delta holdouts: `5`
- mean bidirectional recording fraction: `0.071`
- decision: `no_recording_bidirectional_model_free_signal`

| holdout | centered delta | target0 | target1 | positive recs | bidirectional recs | decision |
|---|---:|---:|---:|---:|---:|---|
| CSH_ZAD_019 | +0.017 | 0.507 | 0.517 | 2/4 | 0/4 | reject: global target0 |
| KS014 | +0.050 | 0.500 | 0.533 | 3/4 | 1/4 | reject: global target0 |
| MFD_06 | +0.014 | 0.522 | 0.496 | 2/4 | 0/4 | reject: global target0 |
| NR_0019 | +0.061 | 0.522 | 0.511 | 3/4 | 0/4 | reject: global target0 |
| NYU-12 | +0.011 | 0.499 | 0.569 | 2/4 | 1/4 | reject: global target0 |
| SWC_038 | -0.005 | 0.470 | 0.492 | 1/4 | 0/4 | reject: centered delta |
| SWC_043 | -0.071 | 0.471 | 0.447 | 0/4 | 0/4 | reject: centered delta |

## Decision

Do not promote a model-free or neural training run unless at least one holdout clears this recording-local bidirectional gate. Positive centered deltas that split target0 and target1 wins across different recordings are not evidence for a cross-animal anatomical transfer mechanism.
