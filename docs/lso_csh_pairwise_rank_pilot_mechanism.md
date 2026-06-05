# CSH Mechanism Audit

Root: `runs/lso_csh_pairwise_rank_pilot`
Holdout: `CSH_ZAD_019` seed `0`

## Global Paired Checks

| comparison | n | improved_fraction | mean_true_prob_delta | mean_abs_delta |
|---|---:|---:|---:|---:|
| paired_true_vs_shuffle | 2726 | 0.552 | +0.028 | 0.247 |
| paired_shuffle_vs_shared | 2726 | 0.448 | -0.015 | 0.116 |
| specificity_gap | n/a | +0.103 | n/a | n/a |

## Carrier-Parent Embeddings

| parent | present | true_norm | shuffle_norm | norm_delta | cosine | l2_distance |
|---|---|---:|---:|---:|---:|---:|
| PRT | True | 0.198 | 0.196 | +0.002 | 0.992 | 0.025 |
| CA | True | 0.171 | 0.175 | -0.004 | 0.972 | 0.041 |
| VP | True | 0.200 | 0.199 | +0.001 | 0.976 | 0.044 |
| MOp | True | 0.225 | 0.226 | -0.001 | 0.985 | 0.039 |
| DG | True | 0.205 | 0.204 | +0.001 | 0.990 | 0.030 |
| mfbc | True | 0.186 | 0.186 | -0.001 | 0.982 | 0.035 |

## Recording-Level Prediction Shifts

| recording | trials | target1_frac | carrier_units | carrier_frac | carrier_parents | true_vs_shuffle | true_delta | shuffle_vs_shared |
|---|---:|---:|---:|---:|---|---:|---:|---:|
| `49e0ab27-827a-4c91-bcaa-97eea27a1b8d_probe01` | 777 | 0.467 | 743 | 0.787 | PRT:414, CA:265, DG:56, mfbc:8 | 0.533 | +0.015 | 0.467 |
| `5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe00` | 590 | 0.414 | 805 | 0.686 | CA:215, MOp:467, DG:103, mfbc:20 | 0.586 | +0.041 | 0.414 |
| `5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe01` | 590 | 0.414 | 346 | 0.412 | VP:335, MOp:10, mfbc:1 | 0.586 | +0.057 | 0.414 |
| `edd22318-216c-44ff-bc24-49ce8be78374_probe00` | 769 | 0.482 | 148 | 0.244 | PRT:25, mfbc:123 | 0.518 | +0.007 | 0.482 |

## Interpretation

Decision: `candidate_mechanism`

The saved artifacts do not show a mechanism that justifies paid broadening yet. True labels fail the paired true-vs-shuffle gate, and carrier-rich recordings still include negative true-vs-shuffle movement.

Next implementable idea should be an objective/control that directly rewards target-aware within-recording true-vs-shuffle separation, not another subject or region-slice selection rule.
