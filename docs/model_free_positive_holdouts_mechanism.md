# Model-Free Positive-Holdout Mechanism Audit

Focused audit for holdouts with positive centered true-minus-shuffle AUC but failed gates.

| holdout | centered_delta | target0_improved | target1_improved | positive_recordings | interpretation |
|---|---:|---:|---:|---:|---|
| KS014 | +0.030 | 0.547 | 0.538 | 2/4 | not bidirectional |
| NR_0019 | +0.079 | 0.776 | 0.249 | 3/4 | not bidirectional |

## KS014

| recording | n_trials | target1_frac | improved | mean_delta | target0_improved | target1_improved |
|---|---:|---:|---:|---:|---:|---:|
| 16693458-0801-4d35-a3f1-9115c7e5acfd_probe00 | 470 | 0.517 | 0.517 | +0.231 | 0.000 | 1.000 |
| 16693458-0801-4d35-a3f1-9115c7e5acfd_probe01 | 470 | 0.517 | 0.483 | -0.365 | 1.000 | 0.000 |
| b9c205c3-feac-485b-a89d-afc96d9cb280_probe00 | 582 | 0.564 | 0.564 | +0.266 | 0.000 | 1.000 |
| e1931de1-cf7b-49af-af33-2ade15e8abe7_probe00 | 605 | 0.412 | 0.588 | +0.317 | 0.997 | 0.004 |

Top positive region weights:
MSC=+0.453, RSPv=+0.378, MED=+0.330, LS=+0.301, CTXpl=+0.258, LAT=+0.229, lfbst=+0.212, ZI=+0.184

Top negative region weights:
PALc=-0.508, EPI=-0.316, CNU=-0.299, LZ=-0.285, IIIn=-0.257, mfbc=-0.240, SSp-ll=-0.231, LGd=-0.224


## NR_0019

| recording | n_trials | target1_frac | improved | mean_delta | target0_improved | target1_improved |
|---|---:|---:|---:|---:|---:|---:|
| 63c70ae8-4dfb-418b-b21b-f0b1e5fba6c9_probe00 | 790 | 0.500 | 0.513 | +0.042 | 0.810 | 0.215 |
| 63c70ae8-4dfb-418b-b21b-f0b1e5fba6c9_probe01 | 790 | 0.500 | 0.535 | +0.017 | 0.911 | 0.159 |
| b887df2c-bb9c-44c9-a9c0-538da87b2cab_probe00 | 422 | 0.521 | 0.479 | -0.164 | 1.000 | 0.000 |
| b887df2c-bb9c-44c9-a9c0-538da87b2cab_probe01 | 422 | 0.521 | 0.479 | -0.006 | 0.218 | 0.718 |

Top positive region weights:
MSC=+0.428, MED=+0.396, LS=+0.292, CTXpl=+0.227, VP=+0.186, lfbst=+0.180, PVR=+0.147, VS=+0.143

Top negative region weights:
PALc=-0.554, EPI=-0.356, CNU=-0.331, IIIn=-0.256, LGd=-0.200, OLF=-0.194, mfbc=-0.171, VENT=-0.148

## Decision

These weak positive model-free deltas are not promotable. They are either below the bidirectional target-class gate or supported by too few recordings.
