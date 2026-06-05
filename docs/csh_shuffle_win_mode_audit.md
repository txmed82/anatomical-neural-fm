# Shuffle Win Mode Audit

## centered

- complete seeds: `[0, 1, 2]`
- incomplete seeds: `[]`
- diagnosis: `true_labels_not_outperformed_by_shuffle_on_centered_separation`
- region_only centered AUC: `0.519`
- region_shuffle centered AUC: `0.513`
- true-minus-shuffle centered AUC: `+0.006`
- true-minus-shuffle centered target separation: `+0.000`
- paired true-vs-shuffle: `0.536`

| recording | true centered sep | shuffle centered sep | true-shuffle centered sep | paired true-vs-shuffle |
|---|---:|---:|---:|---:|
| 49e0ab27-827a-4c91-bcaa-97eea27a1b8d_probe01 | 0.000 | 0.000 | +0.000 | 0.533 |
| 5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe00 | 0.000 | 0.000 | +0.000 | 0.586 |
| 5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe01 | 0.000 | 0.000 | +0.000 | 0.515 |
| edd22318-216c-44ff-bc24-49ce8be78374_probe00 | 0.000 | -0.000 | +0.000 | 0.515 |

## target_balanced

- complete seeds: `[0, 1]`
- incomplete seeds: `[2]`
- diagnosis: `true_labels_not_outperformed_by_shuffle_on_centered_separation`
- region_only centered AUC: `0.492`
- region_shuffle centered AUC: `0.483`
- true-minus-shuffle centered AUC: `+0.009`
- true-minus-shuffle centered target separation: `+0.000`
- paired true-vs-shuffle: `0.516`

| recording | true centered sep | shuffle centered sep | true-shuffle centered sep | paired true-vs-shuffle |
|---|---:|---:|---:|---:|
| 49e0ab27-827a-4c91-bcaa-97eea27a1b8d_probe01 | 0.000 | 0.000 | +0.000 | 0.533 |
| 5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe00 | -0.000 | -0.001 | +0.001 | 0.585 |
| 5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe01 | -0.001 | -0.000 | -0.000 | 0.414 |
| edd22318-216c-44ff-bc24-49ce8be78374_probe00 | -0.000 | -0.001 | +0.001 | 0.525 |

## recording_centered_loss

- complete seeds: `[0]`
- incomplete seeds: `[]`
- diagnosis: `shuffle_labels_create_stronger_within_recording_target_separation`
- region_only centered AUC: `0.480`
- region_shuffle centered AUC: `0.530`
- true-minus-shuffle centered AUC: `-0.050`
- true-minus-shuffle centered target separation: `-0.010`
- paired true-vs-shuffle: `0.451`

| recording | true centered sep | shuffle centered sep | true-shuffle centered sep | paired true-vs-shuffle |
|---|---:|---:|---:|---:|
| 49e0ab27-827a-4c91-bcaa-97eea27a1b8d_probe01 | 0.000 | 0.031 | -0.031 | 0.456 |
| 5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe00 | -0.001 | 0.001 | -0.002 | 0.415 |
| 5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe01 | -0.001 | 0.003 | -0.005 | 0.442 |
| edd22318-216c-44ff-bc24-49ce8be78374_probe00 | -0.001 | -0.003 | +0.002 | 0.480 |

## within_recording_shuffle

- complete seeds: `[0]`
- incomplete seeds: `[]`
- diagnosis: `true_labels_not_outperformed_by_shuffle_on_centered_separation`
- region_only centered AUC: `0.517`
- region_shuffle centered AUC: `0.515`
- true-minus-shuffle centered AUC: `+0.001`
- true-minus-shuffle centered target separation: `-0.000`
- paired true-vs-shuffle: `0.448`

| recording | true centered sep | shuffle centered sep | true-shuffle centered sep | paired true-vs-shuffle |
|---|---:|---:|---:|---:|
| 49e0ab27-827a-4c91-bcaa-97eea27a1b8d_probe01 | 0.000 | 0.000 | -0.000 | 0.467 |
| 5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe00 | 0.001 | 0.001 | -0.000 | 0.414 |
| 5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe01 | 0.001 | 0.001 | -0.000 | 0.414 |
| edd22318-216c-44ff-bc24-49ce8be78374_probe00 | 0.000 | 0.000 | -0.000 | 0.482 |

