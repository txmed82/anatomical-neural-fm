# Model-Free Recording Directionality Audit

Classifies each per-recording target-support observation as bidirectional, target0-only, target1-only, or neither across current model-free artifacts.

- observations: `1120`
- bidirectional: `80`
- target0-only: `302`
- target1-only: `311`
- neither: `427`
- one-sided fraction: `0.547`
- decision: `one_sided_recording_effects_are_common`

## By Report

| report | observations | bidir | target0-only | target1-only | neither | mean target0 | mean target1 |
|---|---:|---:|---:|---:|---:|---:|---:|
| shared family target/control | 448 | 27 | 135 | 133 | 153 | 0.517 | 0.475 |
| source-target families | 168 | 16 | 35 | 31 | 86 | 0.500 | 0.503 |
| source-target centered | 168 | 11 | 35 | 41 | 81 | 0.493 | 0.510 |
| family centered | 28 | 5 | 3 | 7 | 13 | 0.491 | 0.511 |
| family centered l2=1 | 28 | 5 | 3 | 7 | 13 | 0.491 | 0.511 |
| family centered l2=100 | 28 | 5 | 3 | 7 | 13 | 0.489 | 0.515 |
| family prior side | 28 | 3 | 4 | 9 | 12 | 0.500 | 0.518 |
| family feedback | 28 | 3 | 7 | 2 | 16 | 0.433 | 0.471 |
| panel recording centered | 28 | 2 | 1 | 3 | 22 | 0.480 | 0.508 |
| panel grandparent centered | 28 | 2 | 4 | 6 | 16 | 0.493 | 0.509 |
| panel counts | 28 | 1 | 15 | 11 | 1 | 0.566 | 0.437 |
| panel feedback | 28 | 0 | 10 | 18 | 0 | 0.375 | 0.623 |
| panel unit residuals | 28 | 0 | 11 | 16 | 1 | 0.408 | 0.607 |
| panel prior side | 28 | 0 | 16 | 12 | 0 | 0.566 | 0.431 |
| panel fractions | 28 | 0 | 20 | 8 | 0 | 0.698 | 0.307 |

## By Subject

| subject | observations | bidir | target0-only | target1-only | neither | target1-target0 one-sided |
|---|---:|---:|---:|---:|---:|---:|
| MFD_06 | 160 | 20 | 51 | 46 | 43 | -5 |
| KS014 | 160 | 16 | 39 | 47 | 58 | 8 |
| SWC_038 | 160 | 14 | 52 | 38 | 56 | -14 |
| SWC_043 | 160 | 10 | 44 | 37 | 69 | -7 |
| CSH_ZAD_019 | 160 | 8 | 30 | 37 | 85 | 7 |
| NR_0019 | 160 | 6 | 38 | 53 | 63 | 15 |
| NYU-12 | 160 | 6 | 48 | 53 | 53 | 5 |

## Strongest One-Sided Observations

| report | context | recording | class | target0 | target1 | trials |
|---|---|---|---|---:|---:|---:|
| panel counts | stimulus_side / CSH_ZAD_019 | 49e0ab27-827a-4c91-bcaa-97eea27a1b8d_probe01 | target1_only | 0.000 | 1.000 | 777 |
| panel counts | stimulus_side / CSH_ZAD_019 | 5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe00 | target0_only | 1.000 | 0.000 | 590 |
| panel counts | stimulus_side / CSH_ZAD_019 | edd22318-216c-44ff-bc24-49ce8be78374_probe00 | target1_only | 0.000 | 1.000 | 769 |
| panel counts | stimulus_side / KS014 | 16693458-0801-4d35-a3f1-9115c7e5acfd_probe00 | target1_only | 0.000 | 1.000 | 470 |
| panel counts | stimulus_side / KS014 | 16693458-0801-4d35-a3f1-9115c7e5acfd_probe01 | target0_only | 1.000 | 0.000 | 470 |
| panel counts | stimulus_side / KS014 | b9c205c3-feac-485b-a89d-afc96d9cb280_probe00 | target1_only | 0.000 | 1.000 | 582 |
| panel counts | stimulus_side / MFD_06 | 35eeb752-8f4f-4040-9714-ba0f5b7ccdfe_probe00 | target0_only | 1.000 | 0.000 | 660 |
| panel counts | stimulus_side / MFD_06 | 3f71aa98-08c6-4e79-b4c8-00eae4f03eff_probe00 | target0_only | 1.000 | 0.000 | 590 |
| panel counts | stimulus_side / MFD_06 | a1782f4f-86b0-480c-a7f2-3d8f1ab482ab_probe00 | target1_only | 0.000 | 1.000 | 651 |
| panel counts | stimulus_side / NR_0019 | b887df2c-bb9c-44c9-a9c0-538da87b2cab_probe00 | target0_only | 1.000 | 0.000 | 422 |
| panel counts | stimulus_side / NYU-12 | a8a8af78-16de-4841-ab07-fde4b5281a03_probe00 | target0_only | 1.000 | 0.000 | 484 |
| panel counts | stimulus_side / NYU-12 | b182b754-3c3e-4942-8144-6ee790926b58_probe01 | target1_only | 0.000 | 1.000 | 397 |
| panel counts | stimulus_side / SWC_038 | 1e45d992-c356-40e1-9be1-a506d944896f_probe01 | target0_only | 1.000 | 0.000 | 549 |
| panel counts | stimulus_side / SWC_038 | 4d8c7767-981c-4347-8e5e-5d5fffe38534_probe01 | target0_only | 1.000 | 0.000 | 673 |
| panel counts | stimulus_side / SWC_043 | 4ecb5d24-f5cc-402c-be28-9d0f7cb14b3a_probe00 | target0_only | 1.000 | 0.000 | 470 |
| panel counts | stimulus_side / SWC_043 | 6fb1e12c-883b-46d1-a745-473cde3232c8_probe00 | target0_only | 1.000 | 0.000 | 451 |

## Decision

Do not promote rows with positive global deltas unless target support is bidirectional inside recordings. Current artifacts contain substantial one-sided support, so future local gates should report target-direction classification before considering any GPU training trigger.
