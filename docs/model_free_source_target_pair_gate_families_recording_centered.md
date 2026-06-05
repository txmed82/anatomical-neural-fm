# Model-Free Source-Target Pair Gate

Closed-form ridge audit that trains on one source subject and evaluates on one target subject. This tests whether the leave-subject-out panel is hiding a compatible cross-animal anatomical transfer pair.

- target mode: `stimulus_side`
- feature space: `families`
- feature mode: `recording_centered`
- region granularity: `parent`
- source-target pairs: `42`
- candidates: `0`
- positive centered-delta pairs: `19`
- mean bidirectional recording fraction: `0.095`
- decision: `no_source_target_model_free_signal`

## Top Pairs

| source | target | decision | centered delta | target0 | target1 | positive recs | bidirectional recs | train trials | eval trials |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| MFD_06 | SWC_038 | reject: global target1 | +0.088 | 0.601 | 0.524 | 4/4 | 1/4 | 2265 | 2436 |
| KS014 | SWC_038 | reject: global target1 | +0.082 | 0.592 | 0.497 | 3/4 | 1/4 | 2127 | 2436 |
| MFD_06 | KS014 | reject: global target0 | +0.082 | 0.538 | 0.547 | 3/4 | 1/4 | 2265 | 2127 |
| KS014 | MFD_06 | reject: global target0 | +0.077 | 0.536 | 0.542 | 3/4 | 1/4 | 2127 | 2265 |
| SWC_038 | NR_0019 | reject: global target0 | +0.047 | 0.508 | 0.520 | 2/4 | 1/4 | 2436 | 2424 |
| NR_0019 | CSH_ZAD_019 | reject: global target0 | +0.045 | 0.546 | 0.490 | 3/4 | 0/4 | 2424 | 2726 |
| NYU-12 | SWC_038 | reject: global target0 | +0.038 | 0.530 | 0.483 | 3/4 | 0/4 | 1875 | 2436 |
| SWC_038 | CSH_ZAD_019 | reject: global target0 | +0.037 | 0.501 | 0.536 | 2/4 | 1/4 | 2436 | 2726 |
| SWC_043 | NYU-12 | reject: global target0 | +0.035 | 0.466 | 0.572 | 2/4 | 0/4 | 1888 | 1875 |
| SWC_038 | NYU-12 | reject: global target0 | +0.034 | 0.489 | 0.573 | 3/4 | 1/4 | 2436 | 1875 |
| CSH_ZAD_019 | SWC_038 | reject: global target0 | +0.029 | 0.545 | 0.552 | 3/4 | 1/4 | 2726 | 2436 |
| NR_0019 | MFD_06 | reject: global target1 | +0.029 | 0.599 | 0.416 | 2/4 | 1/4 | 2424 | 2265 |
| NYU-12 | CSH_ZAD_019 | reject: global target0 | +0.028 | 0.543 | 0.516 | 3/4 | 0/4 | 1875 | 2726 |
| SWC_043 | NR_0019 | reject: centered delta | +0.010 | 0.497 | 0.556 | 2/4 | 0/4 | 1888 | 2424 |
| CSH_ZAD_019 | NYU-12 | reject: centered delta | +0.010 | 0.477 | 0.535 | 2/4 | 0/4 | 2726 | 1875 |
| SWC_043 | SWC_038 | reject: centered delta | +0.007 | 0.488 | 0.537 | 1/4 | 1/4 | 1888 | 2436 |

## Decision

Do not promote source-target pair training unless at least one pair clears the same centered-delta, global target0/target1, and same-recording bidirectionality gates used by the matched-panel screens.
