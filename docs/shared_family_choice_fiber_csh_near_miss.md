# Shared-Family Near-Miss Audit

Decomposes the strongest shared-family target/control row by recording to decide whether it is a plausible training trigger or a one-sided recording-local artifact.

- target: `choice`
- family: `fiber_tracts`
- holdout: `CSH_ZAD_019`
- bidirectional recordings: `1/4`
- target0-positive recordings: `1/4`
- target1-positive recordings: `4/4`
- decision: `one_sided_target1_recording_effect`

| recording | interpretation | target0 | target1 | true-shuffle AUC | true-total AUC | feature contrast delta | trials |
|---|---|---:|---:|---:|---:|---:|---:|
| 49e0ab27-827a-4c91-bcaa-97eea27a1b8d_probe01 | bidirectional | 0.663 | 0.630 | +0.283 | +0.305 | -2.898 | 882 |
| 5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe01 | target1_only | 0.532 | 0.604 | +0.170 | +0.167 | -4.258 | 667 |
| edd22318-216c-44ff-bc24-49ce8be78374_probe00 | target1_only | 0.506 | 0.608 | +0.229 | +0.225 | -1.017 | 890 |
| 5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe00 | target1_only | 0.503 | 0.611 | +0.188 | +0.205 | +5.909 | 667 |

## Decision

Do not promote this near miss to GPU training unless the failure is recording-local and bidirectional. Here the effect is mostly target1-only: the anatomical family helps the target1 true-class score in every held-out recording, but target0 clears the gate in only one recording.
