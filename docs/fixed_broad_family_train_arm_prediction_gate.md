# Fixed Broad-Family Train Arm Prediction Gate

Trial-paired true-vs-shuffled anatomy gate for the fixed broad-family RunPod prediction files.

- decision: `fixed_broad_family_prediction_gate_candidate`
- candidates: `1/2`
- candidate holdouts: `NR_0019`
- global target pass: `2/2`
- positive centered-delta cases: `2/2`
- paid GPU trigger: `False`
- next action: Package the fixed-feature cloud demo around the candidate holdout(s), and keep the transformer/foundation-model claim separate.

| holdout | target | delta AUC | target0 | target1 | bidir recs | decision |
|---|---|---:|---:|---:|---:|---|
| CSHL045 | post_error_response_extreme_25_75_le_1 | +0.0132 | 0.645 | 0.688 | 2/4 | reject: recording bidirectionality |
| NR_0019 | post_error_response_extreme_33_67_le_1 | +0.0036 | 0.684 | 0.719 | 4/4 | candidate |

## Recording Rows

### CSHL045

| recording | trials | target0 | target1 | improved | mean true-class delta |
|---|---:|---:|---:|---:|---:|
| 034e726f-b35f-41e0-8d6c-a22cc32391fb_probe01 | 50 | 0.520 | 0.560 | 0.540 | +0.0293 |
| 7939711b-8b4d-4251-b698-b97c1eaa846e_probe01 | 84 | 0.310 | 0.357 | 0.333 | -0.0103 |
| dfd8e7df-dc51-4589-b6ca-7baccfeb94b4_probe01 | 60 | 0.967 | 0.967 | 0.967 | +0.8622 |
| fa704052-147e-46f6-b190-a65b837e605e_probe00 | 82 | 0.829 | 0.902 | 0.866 | +0.0400 |

### NR_0019

| recording | trials | target0 | target1 | improved | mean true-class delta |
|---|---:|---:|---:|---:|---:|
| 63c70ae8-4dfb-418b-b21b-f0b1e5fba6c9_probe00 | 76 | 0.711 | 0.658 | 0.684 | +0.0290 |
| 63c70ae8-4dfb-418b-b21b-f0b1e5fba6c9_probe01 | 76 | 0.658 | 0.711 | 0.684 | +0.0261 |
| b887df2c-bb9c-44c9-a9c0-538da87b2cab_probe00 | 38 | 0.579 | 0.737 | 0.658 | +0.0178 |
| b887df2c-bb9c-44c9-a9c0-538da87b2cab_probe01 | 38 | 0.789 | 0.842 | 0.816 | +0.0486 |
