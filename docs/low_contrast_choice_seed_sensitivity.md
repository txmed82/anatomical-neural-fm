# Low-Contrast Choice Seed Sensitivity

Reruns the projected-panel low-contrast choice candidate across shuffle seeds.

- cases: `1`
- robust low-contrast choice seed candidates: `0`
- max positive shuffle-delta fraction: `0.800`
- decision: `no_low_contrast_choice_seed_candidate`
- gpu training ready: `False`

| target | family | holdout | positive seeds | candidate seeds | mean delta shuffle | min/max delta shuffle | mean delta total | mean targets | bidir range |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| low_contrast_choice_le_0.125 | fiber_tracts | CSH_ZAD_019 | 4/5 | 1/5 | +0.0186 | -0.0119/+0.0354 | +0.2152 | 0.527/0.560 | 0-3 |

## Decision

Do not train: the low-contrast choice candidate does not remain a strict candidate across shuffle seeds.
