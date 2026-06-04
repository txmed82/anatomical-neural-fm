# Parent-Region Support And Signal Audit

Manifest: `manifests/ibl_bwm_region_matched_support80_best6.json`
Data cache: `data/brainsets/ibl_bwm`
Target: `stimulus_side` over 1.0s stimulus-aligned windows

## Summary

| holdout | region_only_delta | shuffle_delta | parent_regions | unit_support | weighted_abs_spike_delta | shared-split_abs_spike_delta | top_missing_parent_regions |
|---|---:|---:|---:|---:|---:|---:|---|
| CSH_ZAD_019 | +0.038 | -0.012 | 29 | 84.8% | 0.182 | 0.165 | MED |
| KS014 | +0.022 | -0.008 | 18 | 96.2% | 0.290 | 0.292 | SCs |
| MFD_06 | +0.010 | -0.003 | 27 | 98.7% | 0.196 | 0.195 | none |

## Top Parent Regions

### CSH_ZAD_019

| parent | units | left_rate_hz | right_rate_hz | right_minus_left_hz | in_shared_split |
|---|---:|---:|---:|---:|---|
| CA | 480 | 2.529 | 2.384 | -0.145 | yes |
| MOp | 477 | 2.818 | 2.697 | -0.121 | yes |
| PRT | 439 | 4.557 | 4.236 | -0.321 | yes |
| VP | 335 | 10.279 | 10.481 | +0.201 | yes |
| VENT | 224 | 11.382 | 11.380 | -0.002 | yes |
| RSPd | 208 | 4.846 | 4.767 | -0.079 | yes |
| MED | 178 | 10.542 | 10.517 | -0.025 | no |
| cc | 168 | 2.014 | 1.949 | -0.065 | yes |
| DG | 159 | 2.441 | 2.202 | -0.239 | yes |
| mfbc | 152 | 1.612 | 1.721 | +0.109 | yes |
| ATN | 144 | 9.508 | 9.052 | -0.455 | no |
| EPI | 99 | 11.593 | 11.194 | -0.399 | no |

### KS014

| parent | units | left_rate_hz | right_rate_hz | right_minus_left_hz | in_shared_split |
|---|---:|---:|---:|---:|---|
| SCm | 1233 | 2.493 | 2.577 | +0.084 | yes |
| MBmot | 822 | 2.490 | 2.682 | +0.191 | yes |
| RSPv | 217 | 4.296 | 4.630 | +0.334 | yes |
| RSPagl | 155 | 6.192 | 6.829 | +0.636 | yes |
| RHP | 139 | 4.755 | 5.026 | +0.271 | yes |
| PRT | 121 | 14.293 | 13.934 | -0.359 | yes |
| SCs | 118 | 2.697 | 2.938 | +0.240 | no |
| VISp | 71 | 5.790 | 4.259 | -1.531 | yes |
| BS | 69 | 3.594 | 3.953 | +0.359 | yes |
| RSPd | 46 | 5.019 | 5.364 | +0.346 | yes |
| cc | 32 | 6.633 | 4.647 | -1.987 | yes |
| root | 19 | 8.059 | 5.733 | -2.325 | yes |

### MFD_06

| parent | units | left_rate_hz | right_rate_hz | right_minus_left_hz | in_shared_split |
|---|---:|---:|---:|---:|---|
| void | 1129 | 0.566 | 0.376 | -0.190 | yes |
| P-sen | 614 | 1.580 | 1.520 | -0.060 | yes |
| P-mot | 578 | 4.743 | 4.684 | -0.058 | yes |
| ENTm | 564 | 7.285 | 7.447 | +0.161 | yes |
| MBmot | 418 | 4.256 | 4.251 | -0.005 | yes |
| LAT | 256 | 4.649 | 5.838 | +1.189 | yes |
| cVIIIn | 243 | 1.839 | 1.794 | -0.046 | yes |
| MBsta | 229 | 3.112 | 3.130 | +0.018 | yes |
| HB | 215 | 2.670 | 2.666 | -0.004 | yes |
| SCm | 174 | 5.495 | 5.303 | -0.191 | yes |
| BS | 166 | 2.867 | 2.822 | -0.045 | yes |
| DG | 122 | 1.853 | 2.324 | +0.471 | yes |

## Interpretation

The weak broadening subjects are not missing global parent-region support. They have higher support than the strong CSH_ZAD_019 holdout, which rules out a simple 'more shared support means stronger transfer' explanation. The sharper difference is composition. Only 5 parent regions are shared by all three strict splits (BS, MBmot, cc, root, void).

This supports treating the current result as an anatomical-composition problem, not a simple data-volume failure. The next paid experiment should not rerun the same two holdouts unchanged; it should either preselect holdouts whose parent-region composition resembles CSH_ZAD_019 or restrict all compared holdouts to a common parent-region panel before training.
