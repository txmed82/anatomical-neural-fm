# CSH Batch Sampling Contrast Audit

No-spend sampler audit for recording-local objectives. A recording-local ranking loss needs batches that contain at least one same-recording target-0/target-1 pair.

Holdout: `CSH_ZAD_019`
Train trials: `13015` across `24` recordings
Eligible recordings with both targets: `24/24`

| sampler | batch_size | target1_fraction | rankable_batch_fraction | mean_rankable_pairs | same_recording_adjacent_pairs | sampled_recordings |
|---|---:|---:|---:|---:|---:|---:|
| uniform | 2 | 0.477 | 0.022 | 0.022 | 0.022 | 24 |
| target_balanced | 2 | 0.500 | 0.040 | 0.040 | 0.040 | 24 |
| recording_target_balanced | 2 | 0.500 | 1.000 | 1.000 | 1.000 | 24 |

Decision rule:

Promote only samplers that make the recording-local loss active in almost every batch, then require the local probe matrix to pass centered AUC, bidirectional target-class improvement, and recording support before any RunPod launch.
