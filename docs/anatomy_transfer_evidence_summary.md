# Anatomy Transfer Evidence Summary

Decision: `redesign_before_more_spend`

Do not run more same-setup GPU sweeps. Redesign the anatomy-specific objective or gate, then rerun a bounded two-holdout confirmation.

| holdout | gate | passing_seeds | paired_true_vs_shuffle | shuffle_vs_shared | specificity_gap | centered_delta_vs_shuffle | full_delta_vs_shuffle | recording_support |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| CSH_ZAD_019 | False | 1/3 | 0.536 | 0.552 | -0.016 | +0.006 | +0.005 | 4/4 |
| NR_0019 | False | 0/3 | 0.493 | 0.493 | +0.000 | +0.012 | +0.014 | 1/4 |

A holdout is not considered demo-ready unless the executable gate passes,
the paired true-vs-shuffle improvement is specific against shuffle-vs-shared,
and the recording-level AUC support is not localized to a single recording.
