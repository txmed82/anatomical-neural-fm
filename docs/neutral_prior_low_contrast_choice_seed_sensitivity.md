# Neutral-Prior Low-Contrast Choice Seed Sensitivity

Reruns the current-panel neutral-prior low-contrast choice candidate across shuffle seeds.

- cases: `1`
- robust neutral-prior low-contrast choice seed candidates: `0`
- max positive shuffle-delta fraction: `1.000`
- decision: `no_neutral_prior_low_contrast_choice_seed_candidate`
- gpu training ready: `False`

| target | family | holdout | positive seeds | candidate seeds | mean delta shuffle | min/max delta shuffle | mean delta total | mean targets | bidir range |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| neutral_prior_low_contrast_choice_le_1 | fiber_tracts | CSH_ZAD_019 | 5/5 | 2/5 | +0.0607 | +0.0423/+0.0762 | +0.1260 | 0.562/0.637 | 1-3 |

## Decision

Do not train: the neutral-prior low-contrast choice candidate does not remain a strict candidate across shuffle seeds.
