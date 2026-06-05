# CSH Model-Free Region Candidate Scan

Single-parent-region ridge scans against within-recording shuffled labels and total-spike baseline. This is a no-spend feature/control redesign gate.

Holdout: `CSH_ZAD_019`
Regions scanned: `79`
Candidates: `0`

| region | outcome | eval_centered_AUC | delta_vs_shuffle | delta_vs_total | target0 | target1 | recordings | eval_nonzero |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| IB | reject: target0 | 0.728 | +0.300 | +0.175 | 0.275 | 0.703 | 1/4 | 0.285 |
| MBmot | reject: target1 | 0.645 | +0.226 | +0.092 | 0.820 | 0.219 | 1/4 | 0.285 |
| BS | reject: target0 | 0.672 | +0.225 | +0.119 | 0.015 | 0.991 | 1/4 | 0.285 |
| LZ | reject: target0 | 0.612 | +0.174 | +0.059 | 0.114 | 0.913 | 0/4 | 0.216 |
| RSPd | reject: target1 | 0.637 | +0.173 | +0.084 | 0.951 | 0.070 | 1/4 | 0.282 |
| CA | reject: target0 | 0.680 | +0.157 | +0.127 | 0.320 | 0.721 | 2/4 | 0.501 |
| DG | reject: target0 | 0.700 | +0.126 | +0.147 | 0.285 | 0.718 | 2/4 | 0.501 |
| VENT | reject: target0 | 0.578 | +0.119 | +0.025 | 0.230 | 0.800 | 0/4 | 0.216 |
| hc | reject: target0 | 0.753 | +0.088 | +0.200 | 0.033 | 0.957 | 0/4 | 0.282 |
| VS | reject: target0 | 0.578 | +0.070 | +0.025 | 0.505 | 0.503 | 0/4 | 0.499 |
| VP | reject: target1 | 0.585 | +0.061 | +0.032 | 0.796 | 0.177 | 1/4 | 0.216 |
| cc | reject: target1 | 0.570 | +0.013 | +0.017 | 0.686 | 0.345 | 1/4 | 0.784 |
| root | reject: shuffle | 0.530 | +0.009 | -0.023 | 0.810 | 0.236 | 1/4 | 0.999 |
| ATN | reject: shuffle | 0.616 | +0.000 | +0.063 | 0.000 | 0.000 | 0/4 | 0.216 |
| CTXpl | reject: shuffle | 0.616 | +0.000 | +0.063 | 0.000 | 0.000 | 0/4 | 0.282 |
| EPI | reject: shuffle | 0.616 | +0.000 | +0.063 | 0.000 | 0.000 | 0/4 | 0.216 |
| HIP | reject: shuffle | 0.616 | +0.000 | +0.063 | 0.000 | 0.000 | 0/4 | 0.282 |
| IIIn | reject: shuffle | 0.616 | +0.000 | +0.063 | 0.000 | 0.000 | 0/4 | 0.282 |
| MED | reject: shuffle | 0.616 | +0.000 | +0.063 | 0.000 | 0.000 | 0/4 | 0.216 |
| epsc | reject: shuffle | 0.616 | +0.000 | +0.063 | 0.000 | 0.000 | 0/4 | 0.216 |
| mfbse | reject: shuffle | 0.616 | +0.000 | +0.063 | 0.000 | 0.000 | 0/4 | 0.216 |
| PRT | reject: shuffle | 0.593 | -0.003 | +0.040 | 0.709 | 0.329 | 1/4 | 0.567 |
| VL | reject: shuffle | 0.497 | -0.013 | -0.056 | 0.505 | 0.503 | 1/4 | 0.499 |
| fxs | reject: shuffle | 0.556 | -0.015 | +0.003 | 0.412 | 0.640 | 1/4 | 0.545 |
| mfbc | reject: shuffle | 0.450 | -0.020 | -0.103 | 0.073 | 0.916 | 1/4 | 1.000 |

Decision:

No single parent region passed the model-free promotion gate. The next no-spend step should test predefined region-family aggregates or alternative targets, not a GPU model run.
