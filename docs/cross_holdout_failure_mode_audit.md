# Cross-Holdout Transfer Failure-Mode Audit

Manifest: `manifests/ibl_bwm_region_matched_support80_best6.json`
Data cache: `data/brainsets/ibl_bwm`
Target: `stimulus_side` over 1.0s stimulus-aligned windows

## Controlled Holdout Summary

| holdout | true_delta | shuffle_delta | true_minus_shuffle | true_positive_seeds | baseline_auc | eval_trials | eval_R_frac | parent_regions | unit_support | wj_to_CSH | cosine_to_CSH | weighted_abs_spike_delta | shared_abs_spike_delta | CSH_delta_corr | CSH_same_sign_mass |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| CSH_ZAD_019 | +0.038 | -0.012 | +0.050 | 3/3 | 0.506 | 2726 | 44.8% | 29 | 84.8% | 1.000 | 1.000 | 0.182 | 0.165 | n/a | n/a |
| KS014 | +0.022 | -0.008 | +0.030 | 2/3 | 0.535 | 2127 | 50.0% | 18 | 96.2% | 0.055 | 0.090 | 0.290 | 0.292 | -0.006 | 75.2% |
| MFD_06 | +0.010 | -0.003 | +0.013 | 2/3 | 0.496 | 2265 | 46.1% | 27 | 98.7% | 0.049 | 0.077 | 0.196 | 0.195 | 0.115 | 18.7% |
| NR_0019 | -0.008 | +0.003 | -0.011 | 1/3 | 0.506 | 2424 | 50.7% | 30 | 82.4% | 0.162 | 0.393 | 0.396 | 0.340 | 0.515 | 44.8% |

## Top Parent-Level Stimulus Contrasts

Rows are ranked by `units * abs(right_minus_left_hz)`. These are not model attribution scores; they identify where simple parent-level stimulus-side spike-rate contrast is concentrated in the held-out animal.

### CSH_ZAD_019

| parent | units | unit_mass | right_minus_left_hz | in_train_panel |
|---|---:|---:|---:|---|
| PRT | 439 | 12.3% | -0.321 | yes |
| CA | 480 | 13.5% | -0.145 | yes |
| VP | 335 | 9.4% | +0.201 | yes |
| ATN | 144 | 4.0% | -0.455 | no |
| MOp | 477 | 13.4% | -0.121 | yes |
| EPI | 99 | 2.8% | -0.399 | no |
| DG | 159 | 4.5% | -0.239 | yes |
| IIIn | 9 | 0.3% | -2.896 | no |
| mfbc | 152 | 4.3% | +0.109 | yes |
| RSPd | 208 | 5.8% | -0.079 | yes |

### KS014

| parent | units | unit_mass | right_minus_left_hz | in_train_panel |
|---|---:|---:|---:|---|
| MBmot | 822 | 26.3% | +0.191 | yes |
| VISp | 71 | 2.3% | -1.531 | yes |
| SCm | 1233 | 39.5% | +0.084 | yes |
| RSPagl | 155 | 5.0% | +0.636 | yes |
| RSPv | 217 | 7.0% | +0.334 | yes |
| cc | 32 | 1.0% | -1.987 | yes |
| root | 19 | 0.6% | -2.325 | yes |
| PRT | 121 | 3.9% | -0.359 | yes |
| RHP | 139 | 4.5% | +0.271 | yes |
| hc | 19 | 0.6% | -1.756 | yes |

### MFD_06

| parent | units | unit_mass | right_minus_left_hz | in_train_panel |
|---|---:|---:|---:|---|
| LAT | 256 | 4.9% | +1.189 | yes |
| void | 1129 | 21.7% | -0.190 | yes |
| RHP | 110 | 2.1% | -0.974 | yes |
| ENTm | 564 | 10.8% | +0.161 | yes |
| DG | 122 | 2.3% | +0.471 | yes |
| P-sen | 614 | 11.8% | -0.060 | yes |
| CA | 117 | 2.2% | +0.295 | yes |
| P-mot | 578 | 11.1% | -0.058 | yes |
| SCm | 174 | 3.3% | -0.191 | yes |
| scp | 39 | 0.7% | -0.509 | yes |

### NR_0019

| parent | units | unit_mass | right_minus_left_hz | in_train_panel |
|---|---:|---:|---:|---|
| RHP | 219 | 8.6% | -1.199 | yes |
| SSp-ul | 287 | 11.3% | -0.659 | no |
| SCm | 145 | 5.7% | -1.045 | yes |
| SSp-ll | 47 | 1.8% | -1.206 | no |
| LZ | 145 | 5.7% | -0.348 | yes |
| MBmot | 300 | 11.8% | -0.135 | yes |
| DORpm | 56 | 2.2% | -0.618 | no |
| PRT | 155 | 6.1% | -0.216 | yes |
| SSp-bfd | 53 | 2.1% | -0.497 | yes |
| BS | 192 | 7.5% | -0.131 | yes |

## Interpretation

`CSH_ZAD_019` remains the only controlled holdout with a strong true-label effect over both the shared null and shuffled-label control. The three follow-ups do not fail for one simple reason: `KS014` and `MFD_06` have very high parent-region support, while `NR_0019` is the most CSH-like by composition and has the largest raw parent-level spike-rate contrast.

This argues against spending on another broad leave-subject-out sweep. Parent composition, global support fraction, trial count, class balance, and raw parent-level spike contrast are all insufficient as single gates. The next defensible target is a narrower mechanistic slice: identify which CSH parent regions carry transferable signal and test only held-out subjects/sessions where those same parents have enough units and aligned stimulus-side contrast.

No additional GPU rental is justified until that slice is specified as an explicit inclusion rule with a pre-registered true-vs-shuffled control.
