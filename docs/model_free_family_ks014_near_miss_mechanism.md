# Family Near-Miss Mechanism Audit

Contribution audit for the strongest family-aggregate recording-centered near miss. Family rows decompose true-vs-shuffle true-class movement in the held-out animal.

- holdout: `KS014`
- target mode: `stimulus_side`
- feature mode: `recording_centered`
- centered delta: `+0.080`
- target0 improved: `0.510`
- target1 improved: `0.548`
- bidirectional recordings: `2/4`

| family | class | mean delta | target0 delta | target1 delta | target0 | target1 | recs |
|---|---|---:|---:|---:|---:|---:|---:|
| midbrain | weak_or_mixed | -0.016 | -0.016 | -0.016 | 0.410 | 0.547 | 2/4 |
| broad_named_anatomy | target0_only | +0.015 | +0.015 | +0.015 | 0.589 | 0.456 | 2/4 |
| cortical_retrosplenial | target1_only | +0.016 | +0.016 | +0.016 | 0.130 | 0.898 | 3/4 |
| fiber_tracts | target0_only | +0.005 | +0.005 | +0.005 | 0.657 | 0.465 | 2/4 |
| hippocampal_formation | target1_only | -0.004 | -0.004 | -0.004 | 0.206 | 0.724 | 2/4 |
| thalamic | target1_only | -0.002 | -0.002 | -0.002 | 0.122 | 0.874 | 3/4 |
| cortical_visual | target1_only | +0.001 | +0.001 | +0.001 | 0.413 | 0.634 | 3/4 |
| brainstem_interbrain | target1_only | +0.001 | +0.001 | +0.001 | 0.394 | 0.592 | 2/4 |

## Recording-Level Largest Families

### 16693458-0801-4d35-a3f1-9115c7e5acfd_probe00

| family | mean true-class delta |
|---|---:|
| midbrain | +0.015 |
| broad_named_anatomy | -0.010 |
| fiber_tracts | -0.003 |
| brainstem_interbrain | -0.000 |
| cortical_sensorimotor | +0.000 |

### 16693458-0801-4d35-a3f1-9115c7e5acfd_probe01

| family | mean true-class delta |
|---|---:|
| cortical_retrosplenial | +0.072 |
| broad_named_anatomy | -0.030 |
| midbrain | +0.028 |
| cortical_visual | +0.000 |
| cortical_sensorimotor | +0.000 |

### b9c205c3-feac-485b-a89d-afc96d9cb280_probe00

| family | mean true-class delta |
|---|---:|
| midbrain | -0.082 |
| broad_named_anatomy | +0.066 |
| hippocampal_formation | -0.011 |
| fiber_tracts | +0.008 |
| brainstem_interbrain | +0.002 |

### e1931de1-cf7b-49af-af33-2ade15e8abe7_probe00

| family | mean true-class delta |
|---|---:|
| broad_named_anatomy | +0.020 |
| midbrain | -0.011 |
| fiber_tracts | +0.011 |
| thalamic | -0.008 |
| hippocampal_formation | -0.004 |

## Decision

No family contribution is bidirectional enough to explain a promotable signal. The KS014 near miss is still a mixture of one-sided family movements.
