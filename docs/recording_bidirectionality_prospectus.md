# Recording Bidirectionality Prospectus

Aggregates per-recording target0/target1 support across the current local gate artifacts to see whether any recordings can anchor the next prospective manifest rule. This is a design prospectus, not a training trigger.

- observations: `8544`
- recordings: `35`
- bidirectional observations: `262`
- recordings with bidirectional support: `32`
- max bidirectional observations/recording: `33`
- prospect recordings: `18`
- decision: `prospective_recording_leads_present_not_training_ready`

## Top Recordings

| recording | holdouts | obs | bidir obs | bidir sources | bidir targets | bidir families | mean target0 | mean target1 | mean sym |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 6899a67d-2e53-4215-a52a-c7021b5da5d4_probe00 | MFD_06 | 288 | 33 | 9 | 11 | 11 | 0.510 | 0.506 | 0.228 |
| b887df2c-bb9c-44c9-a9c0-538da87b2cab_probe01 | NR_0019 | 288 | 23 | 9 | 9 | 7 | 0.524 | 0.483 | 0.222 |
| e1931de1-cf7b-49af-af33-2ade15e8abe7_probe00 | KS014 | 288 | 19 | 9 | 9 | 7 | 0.485 | 0.490 | 0.239 |
| b9c205c3-feac-485b-a89d-afc96d9cb280_probe00 | KS014 | 288 | 19 | 6 | 11 | 5 | 0.515 | 0.475 | 0.215 |
| a8a8af78-16de-4841-ab07-fde4b5281a03_probe01 | NYU-12 | 288 | 16 | 6 | 5 | 9 | 0.534 | 0.467 | 0.112 |
| 4d8c7767-981c-4347-8e5e-5d5fffe38534_probe01 | SWC_038 | 288 | 12 | 7 | 7 | 6 | 0.586 | 0.423 | 0.105 |
| 03063955-2523-47bd-ae57-f7489dd40f15_probe01 | SWC_038 | 288 | 12 | 5 | 7 | 5 | 0.553 | 0.439 | 0.151 |
| 41872d7f-75cb-4445-bb1a-132b354c44f0_probe01 | SWC_038 | 288 | 11 | 6 | 7 | 4 | 0.523 | 0.473 | 0.209 |
| 032ffcdf-7692-40b3-b9ff-8def1fc18b2e_probe00 | NYU-12 | 288 | 10 | 7 | 9 | 5 | 0.521 | 0.470 | 0.180 |
| 16693458-0801-4d35-a3f1-9115c7e5acfd_probe01 | KS014 | 288 | 10 | 6 | 6 | 3 | 0.532 | 0.479 | 0.127 |
| 88d24c31-52e4-49cc-9f32-6adbeb9eba87_probe00 | SWC_043 | 128 | 10 | 5 | 9 | 3 | 0.566 | 0.414 | 0.228 |
| 5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe01 | CSH_ZAD_019 | 288 | 8 | 5 | 4 | 5 | 0.521 | 0.472 | 0.186 |

## Source Coverage

| source | observations | bidir obs | recordings with bidir | targets with bidir | families with bidir |
|---|---:|---:|---:|---:|---:|
| projected_support80_recording_centered | 1240 | 43 | 18 | 4 | 9 |
| derived_targets | 336 | 34 | 20 | 3 | 4 |
| waveform | 336 | 34 | 15 | 4 | 3 |
| wheel_targets | 336 | 33 | 17 | 3 | 4 |
| reaction_dynamics_recording_centered | 336 | 30 | 15 | 3 | 4 |
| cell_type_priors | 448 | 30 | 14 | 4 | 4 |
| shared_family | 448 | 27 | 13 | 4 | 4 |
| contextual_targets | 336 | 11 | 8 | 2 | 4 |
| projected_support80_unit_residuals | 1240 | 9 | 5 | 4 | 5 |
| projected_support80_counts | 1240 | 6 | 5 | 4 | 4 |
| reaction_dynamics_counts | 336 | 3 | 3 | 2 | 2 |
| projected_support80_fractions | 1240 | 2 | 2 | 1 | 2 |
| reaction_dynamics_fractions | 336 | 0 | 0 | 0 | 0 |
| reaction_dynamics_unit_residuals | 336 | 0 | 0 | 0 | 0 |

## Next Action

Define a prospective target/control manifest from the lead recordings, then rerun the unchanged local gate.

GPU training remains blocked until a prospectively defined local row clears delta_vs_shuffle>=0, delta_vs_total>=0, target0>=0.55, target1>=0.55, and bidirectional_recording_fraction>=0.75.
