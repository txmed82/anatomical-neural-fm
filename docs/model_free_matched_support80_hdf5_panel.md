# Matched Support80 Model-Free Panel Audit

Closed-form ridge classifier on trial-level parent-region spike counts, run leave-subject-out across the HDF5-confirmed matched support80 panel.

- holdouts: `7`
- candidates: `0`
- positive centered-delta holdouts: `2/7`
- mean true-minus-shuffle centered AUC: `-0.003`
- decision: `no_model_free_panel_signal`

| holdout | decision | true_centered | shuffle_centered | delta | paired | target0 | target1 | rec_support |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| CSH_ZAD_019 | no_model_free_true_region_advantage | 0.487 | 0.538 | -0.052 | 0.502 | 0.338 | 0.703 | 1/4 |
| KS014 | weak_model_free_true_region_advantage | 0.588 | 0.558 | +0.030 | 0.543 | 0.547 | 0.538 | 2/4 |
| MFD_06 | no_model_free_true_region_advantage | 0.488 | 0.505 | -0.016 | 0.513 | 0.567 | 0.451 | 2/4 |
| NR_0019 | weak_model_free_true_region_advantage | 0.561 | 0.482 | +0.079 | 0.508 | 0.776 | 0.249 | 3/4 |
| NYU-12 | no_model_free_true_region_advantage | 0.484 | 0.500 | -0.015 | 0.513 | 0.410 | 0.624 | 2/4 |
| SWC_038 | no_model_free_true_region_advantage | 0.489 | 0.521 | -0.032 | 0.486 | 0.629 | 0.336 | 0/4 |
| SWC_043 | no_model_free_true_region_advantage | 0.470 | 0.483 | -0.014 | 0.486 | 0.738 | 0.212 | 2/4 |

Decision: do not promote this panel to a broad training sweep. Positive centered deltas are not bidirectional and not broadly supported across recordings.
