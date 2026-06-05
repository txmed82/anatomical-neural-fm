# Model-Free Recording Support Audit

Aggregates per-recording target0/target1 support across the current model-free holdout and source-target artifacts.

- observations: `672`
- recordings: `28`
- bidirectional observations: `53`
- recordings with any bidirectional support: `19`
- max bidirectional observations for one recording: `12`

## Top Recording Support

| recording | subjects | observations | bidir obs | bidir frac | mean target0 | mean target1 | mean true-class delta |
|---|---|---:|---:|---:|---:|---:|---:|
| 6899a67d-2e53-4215-a52a-c7021b5da5d4_probe00 | MFD_06 | 24 | 12 | 0.500 | 0.566 | 0.524 | +0.045 |
| 03063955-2523-47bd-ae57-f7489dd40f15_probe01 | SWC_038 | 24 | 8 | 0.333 | 0.474 | 0.574 | +0.040 |
| e1931de1-cf7b-49af-af33-2ade15e8abe7_probe00 | KS014 | 24 | 8 | 0.333 | 0.592 | 0.444 | +0.105 |
| edd22318-216c-44ff-bc24-49ce8be78374_probe00 | CSH_ZAD_019 | 24 | 4 | 0.167 | 0.462 | 0.585 | -0.149 |
| 16693458-0801-4d35-a3f1-9115c7e5acfd_probe01 | KS014 | 24 | 4 | 0.167 | 0.607 | 0.439 | -0.042 |
| 032ffcdf-7692-40b3-b9ff-8def1fc18b2e_probe00 | NYU-12 | 24 | 2 | 0.083 | 0.505 | 0.516 | -0.091 |
| 4ecb5d24-f5cc-402c-be28-9d0f7cb14b3a_probe00 | SWC_043 | 24 | 2 | 0.083 | 0.521 | 0.459 | +0.016 |
| 49e0ab27-827a-4c91-bcaa-97eea27a1b8d_probe01 | CSH_ZAD_019 | 24 | 2 | 0.083 | 0.427 | 0.558 | -0.067 |
| 63c70ae8-4dfb-418b-b21b-f0b1e5fba6c9_probe00 | NR_0019 | 24 | 1 | 0.042 | 0.517 | 0.502 | +0.024 |
| a8a8af78-16de-4841-ab07-fde4b5281a03_probe01 | NYU-12 | 24 | 1 | 0.042 | 0.502 | 0.497 | +0.007 |
| 63c70ae8-4dfb-418b-b21b-f0b1e5fba6c9_probe01 | NR_0019 | 24 | 1 | 0.042 | 0.498 | 0.491 | -0.043 |
| 1e45d992-c356-40e1-9be1-a506d944896f_probe01 | SWC_038 | 24 | 1 | 0.042 | 0.539 | 0.460 | +0.811 |

## Subject-Level Recording Support

| subject | recordings | recordings with support | total bidir obs | max bidir obs/recording |
|---|---:|---:|---:|---:|
| NR_0019 | 4 | 4 | 4 | 1 |
| KS014 | 4 | 3 | 13 | 8 |
| SWC_038 | 4 | 3 | 10 | 8 |
| SWC_043 | 4 | 3 | 4 | 2 |
| MFD_06 | 4 | 2 | 13 | 12 |
| CSH_ZAD_019 | 4 | 2 | 6 | 4 |
| NYU-12 | 4 | 2 | 3 | 2 |

## Decision

Rare bidirectional observations are not concentrated enough to define a stable subject-level demo subset. A recording-level inclusion rule would be post hoc under the current cache; the next benchmark redesign should seek recordings with bidirectional target evidence prospectively, then rerun the same true-vs-shuffled local gate before GPU training.
