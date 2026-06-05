# CSH Model-Free Region Candidate Scan

Single-parent-region ridge scans against within-recording shuffled labels and total-spike baseline. This is a no-spend feature/control redesign gate.

Holdout: `CSH_ZAD_019`
Regions scanned: `79`
Candidates: `0`

| region | outcome | eval_centered_AUC | delta_vs_shuffle | delta_vs_total | target0 | target1 | recordings | eval_nonzero |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| VP | reject: target0 | 0.777 | +0.222 | +0.388 | 0.000 | 1.000 | 1/4 | 0.215 |
| BS | reject: target0 | 0.650 | +0.188 | +0.261 | 0.022 | 0.990 | 1/4 | 0.284 |
| MOp | reject: target0 | 0.697 | +0.167 | +0.307 | 0.373 | 0.639 | 2/4 | 0.429 |
| RSPagl | reject: target1 | 0.694 | +0.095 | +0.305 | 0.748 | 0.241 | 0/4 | 0.284 |
| DG | reject: target1 | 0.727 | +0.035 | +0.338 | 0.746 | 0.256 | 2/4 | 0.499 |
| cc | reject: target0 | 0.628 | +0.025 | +0.238 | 0.256 | 0.684 | 2/4 | 0.785 |
| MBmot | reject: target0 | 0.718 | +0.024 | +0.329 | 0.212 | 0.828 | 1/4 | 0.284 |
| fxs | reject: shuffle | 0.572 | +0.001 | +0.182 | 0.767 | 0.248 | 2/4 | 0.544 |
| VENT | reject: shuffle | 0.483 | +0.001 | +0.094 | 0.969 | 0.030 | 0/4 | 0.215 |
| ATN | reject: shuffle | 0.396 | +0.000 | +0.007 | 0.000 | 0.000 | 0/4 | 0.215 |
| CTXpl | reject: shuffle | 0.396 | +0.000 | +0.007 | 0.000 | 0.000 | 0/4 | 0.287 |
| EPI | reject: shuffle | 0.396 | +0.000 | +0.007 | 0.000 | 0.000 | 0/4 | 0.215 |
| HIP | reject: shuffle | 0.396 | +0.000 | +0.007 | 0.000 | 0.000 | 0/4 | 0.287 |
| IIIn | reject: shuffle | 0.396 | +0.000 | +0.007 | 0.000 | 0.000 | 0/4 | 0.287 |
| MED | reject: shuffle | 0.396 | +0.000 | +0.007 | 0.000 | 0.000 | 0/4 | 0.215 |
| epsc | reject: shuffle | 0.396 | +0.000 | +0.007 | 0.000 | 0.000 | 0/4 | 0.215 |
| mfbse | reject: shuffle | 0.396 | +0.000 | +0.007 | 0.000 | 0.000 | 0/4 | 0.215 |
| mfbc | reject: shuffle | 0.413 | -0.011 | +0.024 | 0.710 | 0.220 | 2/4 | 1.000 |
| CA | reject: shuffle | 0.551 | -0.014 | +0.161 | 0.399 | 0.665 | 1/4 | 0.499 |
| VS | reject: shuffle | 0.544 | -0.014 | +0.155 | 0.484 | 0.481 | 2/4 | 0.501 |
| IB | reject: shuffle | 0.683 | -0.017 | +0.293 | 0.706 | 0.268 | 0/4 | 0.284 |
| void | reject: shuffle | 0.541 | -0.024 | +0.152 | 1.000 | 0.000 | 0/4 | 0.215 |
| root | reject: shuffle | 0.539 | -0.032 | +0.150 | 0.401 | 0.653 | 1/4 | 1.000 |
| LZ | reject: shuffle | 0.728 | -0.034 | +0.339 | 0.780 | 0.209 | 1/4 | 0.215 |
| VL | reject: shuffle | 0.507 | -0.090 | +0.118 | 0.484 | 0.481 | 1/4 | 0.501 |

Decision:

No single parent region passed the model-free promotion gate. The next no-spend step should test predefined region-family aggregates or alternative targets, not a GPU model run.
