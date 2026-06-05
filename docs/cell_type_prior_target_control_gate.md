# Cell-Type Prior Target/Control Gate

No-spend model-free screen that projects fine-region trial spike counts through ABC Atlas subclass priors, then tests broad cell-class channels against within-recording shuffled region labels and the total-spike baseline.

- rows: `112`
- candidates: `0`
- positive centered-delta rows: `53`
- max bidirectional recordings: `2`
- max bidirectional recording fraction: `0.500`
- decision: `no_cell_type_prior_target_candidate`
- prior coverage: min regions with priors `52`, max missing `113`

## Target Summary

| target | rows | candidates | positive centered delta | max bidir frac |
|---|---:|---:|---:|---:|
| choice | 28 | 0 | 18 | 0.500 |
| feedback | 28 | 0 | 7 | 0.250 |
| prior_side | 28 | 0 | 14 | 0.250 |
| stimulus_side | 28 | 0 | 14 | 0.250 |

## Cell-Class Summary

| cell class | rows | candidates | positive centered delta | max bidir frac |
|---|---:|---:|---:|---:|
| gabaergic | 28 | 0 | 14 | 0.500 |
| glutamatergic | 28 | 0 | 12 | 0.250 |
| modulatory | 28 | 0 | 16 | 0.500 |
| non_neuronal | 28 | 0 | 11 | 0.250 |

## Top Rows

| target | cell class | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs |
|---|---|---|---|---:|---:|---:|---:|---:|
| choice | modulatory | SWC_038 | reject: recording bidirectionality | +0.083 | +0.081 | 0.565 | 0.566 | 2/4 |
| choice | gabaergic | NR_0019 | reject: recording bidirectionality | +0.047 | +0.047 | 0.567 | 0.589 | 2/4 |
| choice | glutamatergic | SWC_038 | reject: target0 | +0.079 | +0.086 | 0.522 | 0.547 | 1/4 |
| prior_side | modulatory | SWC_038 | reject: target0 | +0.072 | +0.056 | 0.544 | 0.510 | 1/4 |
| choice | non_neuronal | SWC_038 | reject: target0 | +0.053 | +0.063 | 0.503 | 0.525 | 1/4 |
| prior_side | modulatory | CSH_ZAD_019 | reject: target0 | +0.044 | +0.035 | 0.501 | 0.506 | 1/4 |
| feedback | gabaergic | NYU-12 | reject: target0 | +0.027 | +0.031 | 0.487 | 0.553 | 1/4 |
| stimulus_side | modulatory | SWC_043 | reject: target0 | +0.027 | +0.015 | 0.520 | 0.535 | 1/4 |
| choice | modulatory | SWC_043 | reject: total baseline | +0.026 | -0.149 | 0.565 | 0.534 | 1/4 |
| stimulus_side | glutamatergic | SWC_043 | reject: target0 | +0.019 | +0.019 | 0.535 | 0.496 | 1/4 |
| prior_side | glutamatergic | MFD_06 | reject: target1 | +0.015 | +0.023 | 0.680 | 0.392 | 1/4 |
| choice | gabaergic | CSH_ZAD_019 | reject: target0 | +0.014 | +0.011 | 0.524 | 0.588 | 1/4 |
| prior_side | glutamatergic | SWC_043 | reject: target0 | +0.013 | +0.070 | 0.525 | 0.525 | 1/4 |
| stimulus_side | gabaergic | MFD_06 | reject: target1 | +0.012 | +0.044 | 0.659 | 0.398 | 1/4 |

## Decision

A cell-type-prior feature is only a training trigger if it passes the same local gate as prior audits: nonnegative true-vs-shuffle and true-vs-total deltas, both global target classes >=0.55, and at least 3/4 same-recording bidirectional support.
