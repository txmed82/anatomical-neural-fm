# Manifest Target/Anatomy Feasibility Audit

No-spend prerequisite audit for benchmark redesign. It checks whether candidate manifests have balanced within-recording trials for each target mode and enough shared anatomical family support across subjects.

- min class trials per eligible recording: `40`
- min eligible recordings per subject: `2`
- min family units per recording: `25`
- min family recordings per subject: `1`

## support80_hdf5_scored

- recordings: `28`
- subjects: `7`
- promotable targets by balance floor: `choice, stimulus_side, feedback, prior_side`
- shared families passing floor: `4`
- decision: `manifest_has_target_and_family_feasibility`

| target | eligible recordings | subjects passing floor | all subjects pass |
|---|---:|---:|---|
| choice | 28/28 | 7/7 | True |
| stimulus_side | 28/28 | 7/7 | True |
| feedback | 28/28 | 7/7 | True |
| prior_side | 28/28 | 7/7 | True |

| family | all subjects pass | subjects passing | min subject units | total units |
|---|---|---:|---:|---:|
| broad_named_anatomy | True | 7 | 2447 | 22796 |
| thalamic | True | 7 | 121 | 4170 |
| hippocampal_formation | True | 7 | 86 | 4299 |
| fiber_tracts | True | 7 | 56 | 1408 |
| brainstem_interbrain | False | 6 | 0 | 1555 |
| midbrain | False | 5 | 0 | 5625 |
| cortical_sensorimotor | False | 4 | 0 | 3385 |
| cortical_visual | False | 4 | 0 | 651 |

## support80_hdf5_iterative_pass

- recordings: `8`
- subjects: `2`
- promotable targets by balance floor: `choice, stimulus_side, feedback, prior_side`
- shared families passing floor: `7`
- decision: `manifest_has_target_and_family_feasibility`

| target | eligible recordings | subjects passing floor | all subjects pass |
|---|---:|---:|---|
| choice | 8/8 | 2/2 | True |
| stimulus_side | 8/8 | 2/2 | True |
| feedback | 8/8 | 2/2 | True |
| prior_side | 8/8 | 2/2 | True |

| family | all subjects pass | subjects passing | min subject units | total units |
|---|---|---:|---:|---:|
| broad_named_anatomy | True | 2 | 2516 | 6254 |
| midbrain | True | 2 | 914 | 2927 |
| hippocampal_formation | True | 2 | 913 | 2557 |
| brainstem_interbrain | True | 2 | 381 | 920 |
| thalamic | True | 2 | 310 | 816 |
| fiber_tracts | True | 2 | 106 | 226 |
| cortical_visual | True | 2 | 91 | 491 |

## Decision

At least one manifest has basic target balance and shared family support. Use its strongest target/family combinations for the next local model-free control redesign before any GPU launch.
