# Lateralized Family Target Gate

No-spend model-free screen for left/right anatomical family count channels. Each family contributes two features, left and right hemisphere, and is tested against within-recording shuffled anatomy and total-spike controls.

- rows: `240`
- candidates: `0`
- positive centered-delta rows: `127`
- max bidirectional recordings: `2`
- max bidirectional recording fraction: `0.500`
- decision: `no_lateralized_family_target_candidate`
- gpu training ready: `False`

## Top Rows

| target | family | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs | left/right auc |
|---|---|---|---|---:|---:|---:|---:|---:|---:|
| signed_wheel_direction | basal_ganglia | CSHL045 | reject: shuffle | -0.140 | +0.066 | 0.204 | 0.860 | 2/4 | 0.520/0.525 |
| signed_wheel_direction | midbrain | ZFM-01577 | reject: target1 | +0.226 | +0.265 | 0.907 | 0.151 | 1/3 | 0.505/0.542 |
| choice | midbrain | ZFM-01577 | reject: target1 | +0.162 | +0.198 | 0.894 | 0.131 | 1/3 | 0.529/0.529 |
| stimulus_side | midbrain | ZFM-01577 | reject: total baseline | +0.060 | -0.002 | 0.912 | 0.160 | 1/3 | 0.775/0.964 |
| choice | basal_ganglia | ZFM-01577 | reject: total baseline | +0.045 | -0.019 | 0.887 | 0.138 | 1/3 | 0.537/0.953 |
| stimulus_side | cortical_visual | MFD_06 | reject: target1 | +0.259 | +0.187 | 0.819 | 0.221 | 1/4 | 0.491/0.949 |
| stimulus_side | cortical_visual | NR_0019 | reject: target0 | +0.187 | +0.248 | 0.100 | 0.920 | 1/4 | 0.822/0.989 |
| signed_wheel_direction | brainstem_interbrain | NR_0019 | reject: target0 | +0.153 | +0.090 | 0.460 | 0.743 | 1/4 | 0.644/0.623 |
| choice | basal_ganglia | NR_0019 | reject: total baseline | +0.136 | -0.045 | 0.357 | 0.755 | 1/4 | 0.570/0.905 |
| choice | brainstem_interbrain | NR_0019 | reject: target1 | +0.123 | +0.059 | 0.741 | 0.425 | 1/4 | 0.673/0.759 |
| stimulus_side | brainstem_interbrain | NR_0019 | reject: target0 | +0.117 | +0.060 | 0.401 | 0.753 | 1/4 | 0.635/0.989 |
| choice | basal_ganglia | CSHL045 | reject: target0 | +0.081 | +0.187 | 0.176 | 0.863 | 1/4 | 0.641/0.671 |
| stimulus_side | brainstem_interbrain | KS014 | reject: total baseline | +0.068 | -0.010 | 0.433 | 0.679 | 1/4 | 0.423/0.522 |
| signed_wheel_direction | brainstem_interbrain | KS014 | reject: target0 | +0.049 | +0.079 | 0.404 | 0.586 | 1/4 | 0.623/0.515 |

## Decision

Do not train: lateralized family features do not pass the strict local gate.
