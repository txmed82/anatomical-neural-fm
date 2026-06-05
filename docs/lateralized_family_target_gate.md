# Lateralized Family Target Gate

No-spend model-free screen for left/right anatomical family count channels. Each family contributes two features, left and right hemisphere, and is tested against within-recording shuffled anatomy and total-spike controls.

- rows: `210`
- candidates: `0`
- positive centered-delta rows: `93`
- max bidirectional recordings: `2`
- max bidirectional recording fraction: `0.500`
- decision: `no_lateralized_family_target_candidate`
- gpu training ready: `False`

## Top Rows

| target | family | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs | left/right auc |
|---|---|---|---|---:|---:|---:|---:|---:|---:|
| choice | broad_named_anatomy | SWC_043 | reject: total baseline | +0.008 | -0.149 | 0.536 | 0.610 | 2/4 | 0.423/0.604 |
| stimulus_side | midbrain | KS014 | reject: target1 | +0.212 | +0.134 | 0.918 | 0.135 | 1/4 | 0.666/0.604 |
| stimulus_side | cortical_visual | NR_0019 | reject: target0 | +0.168 | +0.248 | 0.095 | 0.925 | 1/4 | 0.695/0.989 |
| choice | basal_ganglia | NR_0019 | reject: target1 | +0.136 | +0.184 | 0.714 | 0.427 | 1/4 | 0.570/0.586 |
| stimulus_side | brainstem_interbrain | NR_0019 | reject: target0 | +0.123 | +0.075 | 0.377 | 0.742 | 1/4 | 0.649/0.989 |
| signed_wheel_direction | brainstem_interbrain | NR_0019 | reject: target0 | +0.119 | +0.175 | 0.462 | 0.745 | 1/4 | 0.621/0.821 |
| signed_wheel_direction | basal_ganglia | NR_0019 | reject: target1 | +0.110 | +0.096 | 0.785 | 0.366 | 1/4 | 0.542/0.821 |
| choice | brainstem_interbrain | NR_0019 | reject: target1 | +0.104 | +0.278 | 0.741 | 0.421 | 1/4 | 0.663/0.905 |
| choice | basal_ganglia | CSH_ZAD_019 | reject: target1 | +0.092 | +0.209 | 0.786 | 0.260 | 1/4 | 0.600/0.396 |
| signed_wheel_direction | basal_ganglia | SWC_043 | reject: target0 | +0.071 | +0.088 | 0.265 | 0.739 | 1/4 | 0.651/0.745 |
| stimulus_side | hippocampal_formation | MFD_06 | reject: target0 | +0.053 | +0.049 | 0.424 | 0.675 | 1/4 | 0.541/0.949 |
| choice | brainstem_interbrain | CSH_ZAD_019 | reject: target1 | +0.046 | +0.296 | 0.793 | 0.260 | 1/4 | 0.687/0.991 |
| choice | fiber_tracts | SWC_038 | reject: target1 | +0.015 | +0.127 | 0.638 | 0.391 | 1/4 | 0.551/0.734 |
| signed_wheel_direction | broad_named_anatomy | SWC_043 | reject: total baseline | +0.009 | -0.130 | 0.604 | 0.543 | 1/4 | 0.433/0.419 |

## Decision

Do not train: lateralized family features do not pass the strict local gate.
