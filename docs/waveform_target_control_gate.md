# Waveform Target/Control Gate

No-spend model-free screen for waveform-derived unit features. Per-unit amp, depth, and peak-to-trough features are z-scored within recording, summed over trial-window spikes, and compared against a within-recording shuffled waveform assignment plus a total-spike baseline.

- rows: `84`
- candidates: `0`
- positive centered-delta rows: `37`
- max bidirectional recordings: `2`
- max bidirectional recording fraction: `0.500`
- decision: `no_waveform_target_control_candidate`

## Target Summary

| target | rows | candidates | positive centered delta | max bidir frac |
|---|---:|---:|---:|---:|
| choice | 21 | 0 | 10 | 0.500 |
| feedback | 21 | 0 | 9 | 0.500 |
| prior_side | 21 | 0 | 9 | 0.500 |
| stimulus_side | 21 | 0 | 9 | 0.250 |

## Waveform Channel Summary

| channel | rows | candidates | positive centered delta | max bidir frac |
|---|---:|---:|---:|---:|
| amp | 28 | 0 | 9 | 0.500 |
| depth | 28 | 0 | 15 | 0.500 |
| peak_to_trough | 28 | 0 | 13 | 0.250 |

## Top Rows

| target | channel | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs |
|---|---|---|---|---:|---:|---:|---:|---:|
| choice | depth | CSH_ZAD_019 | reject: recording bidirectionality | +0.092 | +0.039 | 0.551 | 0.568 | 2/4 |
| feedback | amp | CSH_ZAD_019 | reject: total baseline | +0.069 | -0.141 | 0.570 | 0.527 | 2/4 |
| feedback | amp | NYU-12 | reject: target0 | +0.017 | +0.025 | 0.476 | 0.544 | 2/4 |
| choice | amp | CSH_ZAD_019 | reject: target0 | +0.014 | +0.042 | 0.517 | 0.516 | 2/4 |
| prior_side | depth | SWC_038 | reject: shuffle | -0.010 | -0.021 | 0.481 | 0.537 | 2/4 |
| prior_side | depth | MFD_06 | reject: target0 | +0.086 | +0.109 | 0.502 | 0.593 | 1/4 |
| feedback | amp | NR_0019 | reject: target0 | +0.060 | +0.030 | 0.471 | 0.513 | 1/4 |
| prior_side | peak_to_trough | NYU-12 | reject: target0 | +0.052 | +0.088 | 0.520 | 0.501 | 1/4 |
| choice | depth | SWC_038 | reject: target0 | +0.048 | +0.094 | 0.514 | 0.537 | 1/4 |
| stimulus_side | depth | CSH_ZAD_019 | reject: target0 | +0.035 | +0.010 | 0.535 | 0.490 | 1/4 |
| stimulus_side | peak_to_trough | NYU-12 | reject: target0 | +0.031 | +0.049 | 0.521 | 0.513 | 1/4 |
| feedback | peak_to_trough | NYU-12 | reject: total baseline | +0.028 | -0.014 | 0.515 | 0.503 | 1/4 |
| feedback | depth | SWC_043 | reject: target0 | +0.024 | +0.096 | 0.491 | 0.478 | 1/4 |
| stimulus_side | peak_to_trough | MFD_06 | reject: target0 | +0.020 | +0.098 | 0.474 | 0.580 | 1/4 |

## Decision

A waveform feature is only a training trigger if it passes the same local gate as prior audits: nonnegative true-vs-shuffle and true-vs-total deltas, both global target classes >=0.55, and at least 3/4 same-recording bidirectional support.
