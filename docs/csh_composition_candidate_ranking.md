# CSH_ZAD_019 Composition Candidate Ranking

Manifest: `manifests/ibl_bwm_region_matched_support80_best6.json`
Data cache: `data/brainsets/ibl_bwm`
Reference holdout: `CSH_ZAD_019`
Target: `stimulus_side` over 1.0s stimulus-aligned windows

## Reference Composition

`CSH_ZAD_019` has 3564 units across 29 parent regions.

| parent | units | unit_mass |
|---|---:|---:|
| CA | 480 | 13.5% |
| MOp | 477 | 13.4% |
| PRT | 439 | 12.3% |
| VP | 335 | 9.4% |
| VENT | 224 | 6.3% |
| RSPd | 208 | 5.8% |
| MED | 178 | 5.0% |
| cc | 168 | 4.7% |
| DG | 159 | 4.5% |
| mfbc | 152 | 4.3% |
| ATN | 144 | 4.0% |
| EPI | 99 | 2.8% |

## Ranked Candidate Holdouts

The ranking compares each possible held-out subject with `CSH_ZAD_019` using parent-region unit-count vectors from the matched 28-recording cache. Weighted Jaccard is the primary score because it penalizes both missing CSH regions and large extra-region mass; cosine is a secondary shape-similarity check.

| rank | subject | units | parents | weighted_jaccard | cosine | CSH_unit_mass_present | CSH_top12_mass_present | CSH_top12_overlap | weighted_abs_spike_delta |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | NR_0019 | 2549 | 30 | 0.162 | 0.393 | 49.5% | 48.2% | 6/12 | 0.396 |
| 2 | NYU-12 | 4255 | 31 | 0.127 | 0.255 | 47.4% | 44.6% | 5/12 | 0.167 |
| 3 | SWC_043 | 4827 | 27 | 0.101 | 0.203 | 47.7% | 49.2% | 5/12 | 0.109 |
| 4 | SWC_038 | 3842 | 16 | 0.094 | 0.134 | 49.9% | 56.3% | 5/12 | 0.138 |
| 5 | KS014 | 3121 | 18 | 0.055 | 0.090 | 27.7% | 26.6% | 3/12 | 0.290 |
| 6 | MFD_06 | 5207 | 27 | 0.049 | 0.077 | 37.5% | 37.3% | 4/12 | 0.196 |

## Recommendation

`NR_0019` is the best next paid holdout if the goal is to test whether the strong CSH_ZAD_019 result generalizes to another animal with similar parent-region composition.

`KS014` and `MFD_06` were useful broadening controls, but this ranking explains why rerunning them unchanged is unlikely to be the cheapest next step: they are among the least CSH-like subjects by parent-region composition.

Next paid gate under the budget cap: run one shared-parent true-vs-shuffled control on the top-ranked candidate first. Continue to a second candidate only if the true arm beats the shuffled arm and the shared null by a meaningful margin on the first candidate. This keeps the next cloud spend small and evidence-driven.
