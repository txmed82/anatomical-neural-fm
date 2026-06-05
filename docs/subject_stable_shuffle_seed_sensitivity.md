# Subject-Stable Shuffle Seed Sensitivity

Reruns the subject-stable near misses across multiple within-recording shuffle seeds.

- cases: `5`
- robust shuffle-seed candidates: `0`
- max positive shuffle-delta fraction: `0.400`
- decision: `no_subject_stable_shuffle_seed_candidate`

| source | target | feature | holdout | positive seeds | candidate seeds | mean delta shuffle | min/max delta shuffle | mean delta total | mean targets | bidir range |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| derived | response_latency | broad_named_anatomy | KS014 | 0/5 | 0/5 | -0.0026 | -0.0043/-0.0018 | -0.0053 | 0.731/0.759 | 3-3 |
| wheel | wheel_active | broad_named_anatomy | KS014 | 1/5 | 0/5 | -0.0008 | -0.0018/+0.0008 | -0.0016 | 0.583/0.600 | 1-3 |
| wheel | wheel_displacement | broad_named_anatomy | KS014 | 0/5 | 0/5 | -0.0057 | -0.0084/-0.0043 | -0.0085 | 0.572/0.614 | 3-3 |
| reaction | post_stim_speedup | broad_named_anatomy | KS014 | 0/5 | 0/5 | -0.0019 | -0.0035/-0.0010 | -0.0024 | 0.593/0.557 | 1-3 |
| reaction | wheel_reaction_latency | broad_named_anatomy | KS014 | 2/5 | 2/5 | -0.0002 | -0.0015/+0.0012 | +0.0027 | 0.675/0.718 | 3-3 |

## Decision

Do not train: subject-stable near misses do not robustly beat shuffled anatomy across seeds.
