# Local Cached Manifest Candidate Audit

No-spend audit for the next manifest-redesign branch. It scores local cached recordings for within-recording target balance and anatomical family support before any new data fetch or GPU launch.

- local recordings: `31`
- local subjects: `9`
- panels scored: `3`
- candidate panels: `1`
- new candidate panels: `0`
- best panel: `current_support80_hdf5`
- decision: `local_expansion_support_gap`

## Panels

| panel | recordings | subjects | passing target/family rows | decision |
|---|---:|---:|---:|---|
| current_support80_hdf5 | 28 | 7 | 4 | `candidate_panel_has_prospective_support` |
| all_local_cached | 31 | 9 | 0 | `candidate_panel_support_gap` |
| local_cached_min2_recordings_per_subject | 30 | 8 | 0 | `candidate_panel_support_gap` |

## Top Prospective Rows

| panel | target | family | passing subjects | min eligible recs/subject | all subjects pass |
|---|---|---|---:|---:|---|
| current_support80_hdf5 | stimulus_side | broad_named_anatomy | 7/7 | 4 | True |
| current_support80_hdf5 | prior_side | broad_named_anatomy | 7/7 | 4 | True |
| current_support80_hdf5 | feedback | broad_named_anatomy | 7/7 | 4 | True |
| current_support80_hdf5 | choice | broad_named_anatomy | 7/7 | 4 | True |
| current_support80_hdf5 | stimulus_side | hippocampal_formation | 4/7 | 1 | False |
| current_support80_hdf5 | stimulus_side | fiber_tracts | 4/7 | 1 | False |
| current_support80_hdf5 | prior_side | hippocampal_formation | 4/7 | 1 | False |
| current_support80_hdf5 | prior_side | fiber_tracts | 4/7 | 1 | False |
| all_local_cached | stimulus_side | broad_named_anatomy | 7/9 | 1 | False |
| all_local_cached | prior_side | broad_named_anatomy | 7/9 | 1 | False |
| all_local_cached | feedback | broad_named_anatomy | 7/9 | 1 | False |
| all_local_cached | choice | broad_named_anatomy | 7/9 | 1 | False |
| all_local_cached | stimulus_side | midbrain | 5/9 | 0 | False |
| all_local_cached | prior_side | midbrain | 5/9 | 0 | False |
| all_local_cached | feedback | midbrain | 5/9 | 0 | False |
| all_local_cached | choice | midbrain | 5/9 | 0 | False |
| local_cached_min2_recordings_per_subject | stimulus_side | broad_named_anatomy | 7/8 | 1 | False |
| local_cached_min2_recordings_per_subject | prior_side | broad_named_anatomy | 7/8 | 1 | False |
| local_cached_min2_recordings_per_subject | feedback | broad_named_anatomy | 7/8 | 1 | False |
| local_cached_min2_recordings_per_subject | choice | broad_named_anatomy | 7/8 | 1 | False |
| local_cached_min2_recordings_per_subject | stimulus_side | midbrain | 5/8 | 0 | False |
| local_cached_min2_recordings_per_subject | prior_side | midbrain | 5/8 | 0 | False |
| local_cached_min2_recordings_per_subject | feedback | midbrain | 5/8 | 0 | False |
| local_cached_min2_recordings_per_subject | choice | midbrain | 5/8 | 0 | False |

## Written Manifests

- `all_local_cached`: `manifests/ibl_bwm_local_cached_all.json`
- `local_cached_min2_recordings_per_subject`: `manifests/ibl_bwm_local_cached_min2_subjects.json`

## Decision

A panel passing this audit is not a training trigger. It only means the panel has enough per-subject target and family coverage to run the same local model-free true-vs-shuffle, total-baseline, target0/target1, and same-recording bidirectional gate.
