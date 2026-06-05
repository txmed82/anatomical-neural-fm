# Symmetric Threshold Sensitivity Audit

Sweeps target-improvement and bidirectional-recording thresholds for the symmetric recording-support gate. This checks whether the current failure is a tiny threshold miss or a structurally weak signal.

- threshold settings: `20`
- settings with candidates: `8`
- strict candidates at target>=0.55 and bidir>=0.75: `0`
- strict max bidirectional recordings: `2`
- decision: `threshold_relaxation_needed_for_candidates`

Highest target threshold with any candidate: `0.550` target, `0.25` bidir fraction (`3` candidates).

At the default target threshold (`0.55`), candidates only appear when the bidirectional-recording fraction is relaxed to `0.25` (`3` candidates).

| target threshold | bidir fraction | candidates | max bidir recs | top row |
|---:|---:|---:|---:|---|
| 0.500 | 0.25 | 41 | 4 | shared family target/control / choice / fiber_tracts / CSH_ZAD_019 (4/4, mean_sym=0.543) |
| 0.500 | 0.50 | 27 | 4 | shared family target/control / choice / fiber_tracts / CSH_ZAD_019 (4/4, mean_sym=0.543) |
| 0.500 | 0.75 | 11 | 4 | shared family target/control / choice / fiber_tracts / CSH_ZAD_019 (4/4, mean_sym=0.543) |
| 0.500 | 1.00 | 1 | 4 | shared family target/control / choice / fiber_tracts / CSH_ZAD_019 (4/4, mean_sym=0.543) |
| 0.525 | 0.25 | 10 | 3 | shared family target/control / choice / broad_named_anatomy / SWC_043 (3/4, mean_sym=0.531) |
| 0.525 | 0.50 | 3 | 3 | shared family target/control / choice / broad_named_anatomy / SWC_043 (3/4, mean_sym=0.531) |
| 0.525 | 0.75 | 1 | 3 | shared family target/control / choice / broad_named_anatomy / SWC_043 (3/4, mean_sym=0.531) |
| 0.525 | 1.00 | 0 | 3 | shared family target/control / choice / broad_named_anatomy / SWC_043 (3/4, mean_sym=0.531) |
| 0.550 | 0.25 | 3 | 2 | shared family target/control / choice / fiber_tracts / CSH_ZAD_019 (1/4, mean_sym=0.543) |
| 0.550 | 0.50 | 0 | 2 | shared family target/control / choice / broad_named_anatomy / SWC_043 (2/4, mean_sym=0.531) |
| 0.550 | 0.75 | 0 | 2 | shared family target/control / choice / broad_named_anatomy / SWC_043 (2/4, mean_sym=0.531) |
| 0.550 | 1.00 | 0 | 2 | shared family target/control / choice / broad_named_anatomy / SWC_043 (2/4, mean_sym=0.531) |
| 0.575 | 0.25 | 0 | 2 | family feedback / feedback / NR_0019 (2/4, mean_sym=0.432) |
| 0.575 | 0.50 | 0 | 2 | family feedback / feedback / NR_0019 (2/4, mean_sym=0.432) |
| 0.575 | 0.75 | 0 | 2 | family feedback / feedback / NR_0019 (2/4, mean_sym=0.432) |
| 0.575 | 1.00 | 0 | 2 | family feedback / feedback / NR_0019 (2/4, mean_sym=0.432) |
| 0.600 | 0.25 | 0 | 2 | family feedback / feedback / NR_0019 (2/4, mean_sym=0.432) |
| 0.600 | 0.50 | 0 | 2 | family feedback / feedback / NR_0019 (2/4, mean_sym=0.432) |
| 0.600 | 0.75 | 0 | 2 | family feedback / feedback / NR_0019 (2/4, mean_sym=0.432) |
| 0.600 | 1.00 | 0 | 2 | family feedback / feedback / NR_0019 (2/4, mean_sym=0.432) |

## Decision

A scientifically useful demo should not require relaxing the symmetric recording gate below the preregistered target and recording-support floors. Use this audit to distinguish near misses from threshold artifacts before spending on model training.
