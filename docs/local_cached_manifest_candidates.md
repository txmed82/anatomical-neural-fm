# Local Cached Manifest Candidate Audit

No-spend audit for the next manifest-redesign branch. It scores local cached recordings for within-recording target balance and anatomical family support before any new data fetch or GPU launch.

- local recordings: `38`
- local subjects: `11`
- panels scored: `4`
- candidate panels: `2`
- new candidate panels: `1`
- best panel: `external_support80_projected_hdf5`
- decision: `local_expanded_candidate_ready_for_model_free_gate`

## Panels

| panel | recordings | subjects | passing target/family rows | decision |
|---|---:|---:|---:|---|
| external_support80_projected_hdf5 | 31 | 8 | 4 | `candidate_panel_has_prospective_support` |
| current_support80_hdf5 | 28 | 7 | 4 | `candidate_panel_has_prospective_support` |
| all_local_cached | 38 | 11 | 0 | `candidate_panel_support_gap` |
| local_cached_min2_recordings_per_subject | 37 | 10 | 0 | `candidate_panel_support_gap` |

## Top Prospective Rows

| panel | target | family | passing subjects | min eligible recs/subject | all subjects pass |
|---|---|---|---:|---:|---|
| external_support80_projected_hdf5 | stimulus_side | broad_named_anatomy | 8/8 | 3 | True |
| external_support80_projected_hdf5 | prior_side | broad_named_anatomy | 8/8 | 3 | True |
| external_support80_projected_hdf5 | feedback | broad_named_anatomy | 8/8 | 3 | True |
| external_support80_projected_hdf5 | choice | broad_named_anatomy | 8/8 | 3 | True |
| external_support80_projected_hdf5 | stimulus_side | hippocampal_formation | 5/8 | 0 | False |
| external_support80_projected_hdf5 | prior_side | hippocampal_formation | 5/8 | 0 | False |
| external_support80_projected_hdf5 | feedback | hippocampal_formation | 5/8 | 0 | False |
| external_support80_projected_hdf5 | choice | hippocampal_formation | 5/8 | 0 | False |
| current_support80_hdf5 | stimulus_side | broad_named_anatomy | 7/7 | 4 | True |
| current_support80_hdf5 | prior_side | broad_named_anatomy | 7/7 | 4 | True |
| current_support80_hdf5 | feedback | broad_named_anatomy | 7/7 | 4 | True |
| current_support80_hdf5 | choice | broad_named_anatomy | 7/7 | 4 | True |
| current_support80_hdf5 | stimulus_side | hippocampal_formation | 4/7 | 1 | False |
| current_support80_hdf5 | stimulus_side | fiber_tracts | 4/7 | 1 | False |
| current_support80_hdf5 | prior_side | hippocampal_formation | 4/7 | 1 | False |
| current_support80_hdf5 | prior_side | fiber_tracts | 4/7 | 1 | False |
| all_local_cached | stimulus_side | broad_named_anatomy | 9/11 | 1 | False |
| all_local_cached | prior_side | broad_named_anatomy | 9/11 | 1 | False |
| all_local_cached | feedback | broad_named_anatomy | 9/11 | 1 | False |
| all_local_cached | choice | broad_named_anatomy | 9/11 | 1 | False |
| all_local_cached | stimulus_side | fiber_tracts | 5/11 | 1 | False |
| all_local_cached | prior_side | fiber_tracts | 5/11 | 1 | False |
| all_local_cached | feedback | fiber_tracts | 5/11 | 1 | False |
| all_local_cached | choice | fiber_tracts | 5/11 | 1 | False |
| local_cached_min2_recordings_per_subject | stimulus_side | broad_named_anatomy | 9/10 | 1 | False |
| local_cached_min2_recordings_per_subject | prior_side | broad_named_anatomy | 9/10 | 1 | False |
| local_cached_min2_recordings_per_subject | feedback | broad_named_anatomy | 9/10 | 1 | False |
| local_cached_min2_recordings_per_subject | choice | broad_named_anatomy | 9/10 | 1 | False |
| local_cached_min2_recordings_per_subject | stimulus_side | fiber_tracts | 5/10 | 1 | False |
| local_cached_min2_recordings_per_subject | prior_side | fiber_tracts | 5/10 | 1 | False |
| local_cached_min2_recordings_per_subject | feedback | fiber_tracts | 5/10 | 1 | False |
| local_cached_min2_recordings_per_subject | choice | fiber_tracts | 5/10 | 1 | False |

## Written Manifests

- `external_support80_projected_hdf5`: `manifests/ibl_bwm_local_cached_external_support80_projected_hdf5.json`
- `all_local_cached`: `manifests/ibl_bwm_local_cached_all.json`
- `local_cached_min2_recordings_per_subject`: `manifests/ibl_bwm_local_cached_min2_subjects.json`

## Decision

A panel passing this audit is not a training trigger. It only means the panel has enough per-subject target and family coverage to run the same local model-free true-vs-shuffle, total-baseline, target0/target1, and same-recording bidirectional gate.
