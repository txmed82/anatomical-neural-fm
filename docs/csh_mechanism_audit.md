# CSH Mechanism Audit

Root: `runs/lso_csh_recording_centered_gate_pilot`
Holdout: `CSH_ZAD_019` seed `0`

## Global Paired Checks

| comparison | n | improved_fraction | mean_true_prob_delta | mean_abs_delta |
|---|---:|---:|---:|---:|
| paired_true_vs_shuffle | 2726 | 0.448 | -0.003 | 0.019 |
| paired_shuffle_vs_shared | 2726 | 0.552 | +0.003 | 0.021 |
| specificity_gap | n/a | -0.103 | n/a | n/a |

## Carrier-Parent Embeddings

| parent | present | true_norm | shuffle_norm | norm_delta | cosine | l2_distance |
|---|---|---:|---:|---:|---:|---:|
| PRT | True | 0.195 | 0.197 | -0.001 | 0.997 | 0.014 |
| CA | True | 0.174 | 0.176 | -0.002 | 0.994 | 0.020 |
| VP | True | 0.198 | 0.197 | +0.001 | 0.988 | 0.030 |
| MOp | True | 0.225 | 0.229 | -0.004 | 0.985 | 0.039 |
| DG | True | 0.202 | 0.202 | +0.000 | 0.992 | 0.025 |
| mfbc | True | 0.183 | 0.184 | -0.001 | 0.995 | 0.018 |

## Recording-Level Prediction Shifts

| recording | trials | target1_frac | carrier_units | carrier_frac | carrier_parents | true_vs_shuffle | true_delta | shuffle_vs_shared |
|---|---:|---:|---:|---:|---|---:|---:|---:|
| `49e0ab27-827a-4c91-bcaa-97eea27a1b8d_probe01` | 777 | 0.467 | 743 | 0.787 | PRT:414, CA:265, DG:56, mfbc:8 | 0.467 | -0.000 | 0.533 |
| `5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe00` | 590 | 0.414 | 805 | 0.686 | CA:215, MOp:467, DG:103, mfbc:20 | 0.414 | -0.009 | 0.586 |
| `5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe01` | 590 | 0.414 | 346 | 0.412 | VP:335, MOp:10, mfbc:1 | 0.414 | -0.003 | 0.586 |
| `edd22318-216c-44ff-bc24-49ce8be78374_probe00` | 769 | 0.482 | 148 | 0.244 | PRT:25, mfbc:123 | 0.482 | -0.000 | 0.518 |

## Interpretation

Decision: `no_mechanism_found`

The saved artifacts do not show a mechanism that justifies paid broadening yet. True labels fail the paired true-vs-shuffle gate, and carrier-rich recordings still include negative true-vs-shuffle movement.

Next implementable idea should be an objective/control that directly rewards target-aware within-recording true-vs-shuffle separation, not another subject or region-slice selection rule.
