# Transfer Success-Mode Audit

Manifest: `manifests/ibl_bwm_region_matched_support80_best6.json`
Data cache: `data/brainsets/ibl_bwm`
Reference success: `CSH_ZAD_019`
Target: `stimulus_side` over 1.0s stimulus-aligned windows

## Question

The previous failure-mode audit showed that global parent-region support, composition similarity, trial count, class balance, and raw parent-level contrast do not explain why only `CSH_ZAD_019` has a strong controlled true-vs-shuffled transfer signal. This audit asks a more model-facing question: for the CSH-derived carrier parents, does each held-out animal match the sign of the leave-subject-out training aggregate?

## CSH Carrier Parents

| parent | CSH_units | CSH_delta_hz | units_x_abs_delta |
|---|---:|---:|---:|
| PRT | 439 | -0.321 | 141.0 |
| CA | 480 | -0.145 | 69.7 |
| VP | 335 | +0.201 | 67.5 |
| MOp | 477 | -0.121 | 57.6 |
| DG | 159 | -0.239 | 37.9 |
| mfbc | 152 | +0.109 | 16.6 |

## Subject Compatibility With LSO Training Aggregate

| holdout | true_delta | shuffle_delta | true_minus_shuffle | slice_units | carriers_present | CSH_weighted_coverage | train_aligned_unit_mass | aligned_parents | opposed_parents | min_weighted_abs_train_delta | min_weighted_abs_holdout_delta |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---:|---:|
| CSH_ZAD_019 | +0.038 | -0.012 | +0.050 | 2042 | 6/6 | 100.0% | 92.6% | PRT, CA, VP, MOp, DG | mfbc | 0.226 | 0.196 |
| KS014 | +0.022 | -0.008 | +0.030 | 121 | 1/6 | 36.1% | 100.0% | PRT | none | 0.082 | 0.359 |
| MFD_06 | +0.010 | -0.003 | +0.013 | 242 | 3/6 | 44.9% | 1.2% | VP | CA, DG | 0.169 | 0.432 |
| NR_0019 | -0.008 | +0.003 | -0.011 | 749 | 4/6 | 67.4% | 20.8% | PRT, DG | VP, mfbc | 0.377 | 0.094 |
| NYU-12 | +0.013 | +0.020 | -0.007 | 750 | 3/6 | 44.9% | 100.0% | CA, VP, DG | none | 0.104 | 0.158 |
| SWC_038 | n/a | n/a | n/a | 503 | 4/6 | 78.5% | 76.7% | CA, MOp, DG | PRT | 0.143 | 0.359 |
| SWC_043 | n/a | n/a | n/a | 723 | 3/6 | 42.3% | 74.0% | MOp, DG | CA | 0.131 | 0.093 |

## Carrier Parent Details

### CSH_ZAD_019

| parent | units | train_units | holdout_delta_hz | train_delta_hz | sign_relation |
|---|---:|---:|---:|---:|---|
| PRT | 439 | 393 | -0.321 | -0.384 | aligned |
| CA | 480 | 684 | -0.145 | -0.046 | aligned |
| VP | 335 | 619 | +0.201 | +0.037 | aligned |
| MOp | 477 | 421 | -0.121 | -0.434 | aligned |
| DG | 159 | 951 | -0.239 | -0.163 | aligned |
| mfbc | 152 | 20 | +0.109 | -0.760 | opposed |

### KS014

| parent | units | train_units | holdout_delta_hz | train_delta_hz | sign_relation |
|---|---:|---:|---:|---:|---|
| PRT | 121 | 711 | -0.359 | -0.082 | aligned |

### MFD_06

| parent | units | train_units | holdout_delta_hz | train_delta_hz | sign_relation |
|---|---:|---:|---:|---:|---|
| CA | 117 | 1047 | +0.295 | -0.122 | opposed |
| VP | 3 | 951 | +4.200 | +0.198 | aligned |
| DG | 122 | 988 | +0.471 | -0.213 | opposed |

### NR_0019

| parent | units | train_units | holdout_delta_hz | train_delta_hz | sign_relation |
|---|---:|---:|---:|---:|---|
| PRT | 155 | 677 | -0.216 | -0.476 | aligned |
| VP | 573 | 381 | -0.008 | +0.351 | opposed |
| DG | 1 | 1109 | -0.284 | -0.179 | aligned |
| mfbc | 20 | 152 | -0.760 | +0.109 | opposed |

### NYU-12

| parent | units | train_units | holdout_delta_hz | train_delta_hz | sign_relation |
|---|---:|---:|---:|---:|---|
| CA | 356 | 808 | -0.104 | -0.076 | aligned |
| VP | 43 | 911 | +0.859 | +0.182 | aligned |
| DG | 351 | 759 | -0.126 | -0.124 | aligned |

### SWC_038

| parent | units | train_units | holdout_delta_hz | train_delta_hz | sign_relation |
|---|---:|---:|---:|---:|---|
| PRT | 117 | 715 | +0.075 | -0.323 | opposed |
| CA | 23 | 1141 | -0.214 | -0.112 | aligned |
| MOp | 300 | 598 | -0.512 | -0.068 | aligned |
| DG | 63 | 1047 | -0.211 | -0.179 | aligned |

### SWC_043

| parent | units | train_units | holdout_delta_hz | train_delta_hz | sign_relation |
|---|---:|---:|---:|---:|---|
| CA | 188 | 976 | +0.226 | -0.126 | opposed |
| MOp | 121 | 777 | -0.015 | -0.116 | aligned |
| DG | 414 | 696 | -0.055 | -0.139 | aligned |

## Top Recording-Level Carrier Slices

| recording | subject | slice_units | carriers_present | train_aligned_unit_mass | present_parents | aligned_parents |
|---|---|---:|---:|---:|---|---|
| 5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe00 | CSH_ZAD_019 | 805 | 4/6 | 100.0% | CA, MOp, DG, mfbc | CA, MOp, DG, mfbc |
| 49e0ab27-827a-4c91-bcaa-97eea27a1b8d_probe01 | CSH_ZAD_019 | 743 | 4/6 | 100.0% | PRT, CA, DG, mfbc | PRT, CA, DG, mfbc |
| 6f09ba7e-e3ce-44b0-932b-c003fb44fb89_probe01 | SWC_043 | 602 | 2/6 | 68.8% | CA, DG | DG |
| a8a8af78-16de-4841-ab07-fde4b5281a03_probe01 | NYU-12 | 591 | 2/6 | 100.0% | CA, DG | CA, DG |
| 63c70ae8-4dfb-418b-b21b-f0b1e5fba6c9_probe00 | NR_0019 | 573 | 1/6 | 0.0% | VP | none |
| 5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe01 | CSH_ZAD_019 | 346 | 3/6 | 96.8% | VP, MOp, mfbc | VP |
| 03063955-2523-47bd-ae57-f7489dd40f15_probe01 | SWC_038 | 300 | 1/6 | 100.0% | MOp | MOp |
| 6899a67d-2e53-4215-a52a-c7021b5da5d4_probe00 | MFD_06 | 242 | 3/6 | 1.2% | CA, VP, DG | VP |
| 41872d7f-75cb-4445-bb1a-132b354c44f0_probe01 | SWC_038 | 203 | 3/6 | 42.4% | PRT, CA, DG | CA, DG |
| a8a8af78-16de-4841-ab07-fde4b5281a03_probe00 | NYU-12 | 159 | 3/6 | 100.0% | CA, VP, DG | CA, VP, DG |
| b887df2c-bb9c-44c9-a9c0-538da87b2cab_probe00 | NR_0019 | 156 | 2/6 | 100.0% | PRT, DG | PRT, DG |
| edd22318-216c-44ff-bc24-49ce8be78374_probe00 | CSH_ZAD_019 | 148 | 2/6 | 100.0% | PRT, mfbc | PRT, mfbc |

## Interpretation

The fixed `NYU-12` slice failed even though it matched the sign of the leave-subject-out training aggregate. That rules out a simple sign-alignment fix. NYU-12 covers only the `CA`, `VP`, and `DG` part of the CSH carrier pattern and misses the strongest CSH carrier (`PRT`) plus `MOp`; its CSH-weighted carrier coverage is therefore much lower than the reference success. In contrast, `MFD_06` and `NR_0019` fail the train-aggregate alignment screen outright.

Next gate: before any further GPU spend, require a candidate to clear support, CSH carrier-weight coverage, and LSO-train compatibility: enough units in at least two carrier parents, at least 70% of the CSH carrier weighted signal represented, at least 75% carrier-slice unit mass sign-aligned to the leave-subject-out training aggregate, and a pre-registered shuffled-label control. This is stricter than the NYU-12 gate and directly addresses the paid-run failure.
