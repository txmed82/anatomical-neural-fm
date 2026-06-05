# Composite Behavior Recording Failure Decomposition

Decomposes the projected post-error fast-response broad-anatomy near miss into per-recording target-class support across shuffle seeds.

- cases: `2`
- recordings: `8`
- stable bidirectional recordings: `3`
- unstable recordings: `5`
- min recording bidirectional seed fraction: `0.000`
- decision: `composite_behavior_recording_bidirectionality_failure`
- gpu training ready: `False`

## CSHL045

- stable bidirectional recordings: `2/4`
- mean bidirectional seed fraction: `0.650`

| recording | bidir seeds | target0 seeds | target1 seeds | mean target0 | mean target1 | min target0 | min target1 | mean delta | trials |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 7939711b-8b4d-4251-b698-b97c1eaa846e_probe01 | 0/5 | 0/5 | 3/5 | 0.371 | 0.667 | 0.265 | 0.518 | +0.0002 | 166.0 |
| 034e726f-b35f-41e0-8d6c-a22cc32391fb_probe01 | 3/5 | 4/5 | 4/5 | 0.612 | 0.649 | 0.490 | 0.531 | +0.0165 | 98.0 |
| fa704052-147e-46f6-b190-a65b837e605e_probe00 | 5/5 | 5/5 | 5/5 | 0.700 | 0.766 | 0.610 | 0.744 | +0.0080 | 164.0 |
| dfd8e7df-dc51-4589-b6ca-7baccfeb94b4_probe01 | 5/5 | 5/5 | 5/5 | 0.928 | 0.959 | 0.897 | 0.948 | +0.2309 | 116.0 |

## NR_0019

- stable bidirectional recordings: `1/4`
- mean bidirectional seed fraction: `0.750`

| recording | bidir seeds | target0 seeds | target1 seeds | mean target0 | mean target1 | min target0 | min target1 | mean delta | trials |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| b887df2c-bb9c-44c9-a9c0-538da87b2cab_probe00 | 3/5 | 3/5 | 3/5 | 0.517 | 0.614 | 0.379 | 0.517 | +0.0026 | 58.0 |
| 63c70ae8-4dfb-418b-b21b-f0b1e5fba6c9_probe01 | 3/5 | 4/5 | 4/5 | 0.568 | 0.593 | 0.509 | 0.526 | +0.0033 | 114.0 |
| b887df2c-bb9c-44c9-a9c0-538da87b2cab_probe01 | 4/5 | 4/5 | 5/5 | 0.593 | 0.738 | 0.483 | 0.690 | +0.0120 | 58.0 |
| 63c70ae8-4dfb-418b-b21b-f0b1e5fba6c9_probe00 | 5/5 | 5/5 | 5/5 | 0.604 | 0.649 | 0.579 | 0.614 | +0.0058 | 114.0 |

## Decision

Do not train: the composite near miss is limited by unstable same-recording target-class support, not by ridge regularization.
