# Model-Free Source-Target Pair Gate

Closed-form ridge audit that trains on one source subject and evaluates on one target subject. This tests whether the leave-subject-out panel is hiding a compatible cross-animal anatomical transfer pair.

- target mode: `stimulus_side`
- feature mode: `recording_centered`
- region granularity: `parent`
- source-target pairs: `42`
- candidates: `0`
- positive centered-delta pairs: `20`
- mean bidirectional recording fraction: `0.065`
- decision: `no_source_target_model_free_signal`

## Top Pairs

| source | target | decision | centered delta | target0 | target1 | positive recs | bidirectional recs | train trials | eval trials |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| MFD_06 | SWC_038 | reject: global target1 | +0.092 | 0.705 | 0.382 | 3/4 | 1/4 | 2265 | 2436 |
| MFD_06 | CSH_ZAD_019 | reject: global target1 | +0.086 | 0.578 | 0.494 | 3/4 | 0/4 | 2265 | 2726 |
| KS014 | SWC_043 | reject: global target1 | +0.085 | 0.551 | 0.524 | 3/4 | 1/4 | 2127 | 1888 |
| SWC_043 | SWC_038 | reject: global target1 | +0.074 | 0.569 | 0.512 | 4/4 | 0/4 | 1888 | 2436 |
| MFD_06 | NR_0019 | reject: global target0 | +0.070 | 0.533 | 0.520 | 3/4 | 0/4 | 2265 | 2424 |
| MFD_06 | KS014 | reject: global target1 | +0.065 | 0.554 | 0.516 | 3/4 | 0/4 | 2265 | 2127 |
| SWC_043 | CSH_ZAD_019 | reject: global target0 | +0.058 | 0.478 | 0.540 | 3/4 | 0/4 | 1888 | 2726 |
| NR_0019 | KS014 | reject: global target1 | +0.056 | 0.558 | 0.533 | 3/4 | 0/4 | 2424 | 2127 |
| SWC_038 | CSH_ZAD_019 | reject: global target0 | +0.054 | 0.503 | 0.497 | 2/4 | 1/4 | 2436 | 2726 |
| CSH_ZAD_019 | SWC_043 | reject: global target0 | +0.053 | 0.396 | 0.595 | 2/4 | 0/4 | 2726 | 1888 |
| SWC_038 | NYU-12 | reject: global target0 | +0.049 | 0.498 | 0.545 | 1/4 | 0/4 | 2436 | 1875 |
| KS014 | MFD_06 | reject: global target0 | +0.037 | 0.421 | 0.613 | 2/4 | 1/4 | 2127 | 2265 |
| CSH_ZAD_019 | NR_0019 | reject: global target0 | +0.035 | 0.462 | 0.524 | 2/4 | 0/4 | 2726 | 2424 |
| NYU-12 | SWC_038 | reject: global target1 | +0.027 | 0.665 | 0.381 | 3/4 | 0/4 | 1875 | 2436 |
| SWC_038 | SWC_043 | reject: global target0 | +0.022 | 0.513 | 0.478 | 3/4 | 0/4 | 2436 | 1888 |
| CSH_ZAD_019 | NYU-12 | reject: global target0 | +0.020 | 0.505 | 0.555 | 3/4 | 0/4 | 2726 | 1875 |

## Decision

Do not promote source-target pair training unless at least one pair clears the same centered-delta, global target0/target1, and same-recording bidirectionality gates used by the matched-panel screens.
