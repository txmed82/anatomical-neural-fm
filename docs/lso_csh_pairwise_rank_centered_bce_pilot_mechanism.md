# CSH Mechanism Audit

Root: `runs/lso_csh_pairwise_rank_centered_bce_pilot`
Holdout: `CSH_ZAD_019` seed `0`

## Global Paired Checks

| comparison | n | improved_fraction | mean_true_prob_delta | mean_abs_delta |
|---|---:|---:|---:|---:|
| paired_true_vs_shuffle | 2726 | 0.486 | +0.000 | 0.042 |
| paired_shuffle_vs_shared | 2726 | 0.473 | -0.002 | 0.030 |
| specificity_gap | n/a | +0.013 | n/a | n/a |

## Carrier-Parent Embeddings

| parent | present | true_norm | shuffle_norm | norm_delta | cosine | l2_distance |
|---|---|---:|---:|---:|---:|---:|
| PRT | True | 0.201 | 0.195 | +0.006 | 0.989 | 0.030 |
| CA | True | 0.173 | 0.177 | -0.004 | 0.988 | 0.027 |
| VP | True | 0.204 | 0.195 | +0.009 | 0.979 | 0.042 |
| MOp | True | 0.230 | 0.230 | +0.000 | 0.970 | 0.056 |
| DG | True | 0.204 | 0.205 | -0.001 | 0.995 | 0.021 |
| mfbc | True | 0.186 | 0.187 | -0.001 | 0.992 | 0.023 |

## Recording-Level Prediction Shifts

| recording | trials | target1_frac | carrier_units | carrier_frac | carrier_parents | true_vs_shuffle | true_delta | shuffle_vs_shared |
|---|---:|---:|---:|---:|---|---:|---:|---:|
| `49e0ab27-827a-4c91-bcaa-97eea27a1b8d_probe01` | 777 | 0.467 | 743 | 0.787 | PRT:414, CA:265, DG:56, mfbc:8 | 0.467 | -0.003 | 0.467 |
| `5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe00` | 590 | 0.414 | 805 | 0.686 | CA:215, MOp:467, DG:103, mfbc:20 | 0.575 | +0.012 | 0.529 |
| `5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe01` | 590 | 0.414 | 346 | 0.412 | VP:335, MOp:10, mfbc:1 | 0.414 | -0.008 | 0.414 |
| `edd22318-216c-44ff-bc24-49ce8be78374_probe00` | 769 | 0.482 | 148 | 0.244 | PRT:25, mfbc:123 | 0.494 | -0.000 | 0.482 |

## Interpretation

Decision: `no_mechanism_found`

The saved artifacts do not show a mechanism that justifies paid broadening yet. True labels fail the paired true-vs-shuffle gate, and carrier-rich recordings still include negative true-vs-shuffle movement.

Next implementable idea should be an objective/control that directly rewards target-aware within-recording true-vs-shuffle separation, not another subject or region-slice selection rule.
