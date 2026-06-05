# Prospect-Lead Subject Stability Audit

Checks whether prospect-lead derived candidates also hold on same-subject non-lead recordings.

- prospect candidates: `4`
- same-subject stable candidates: `0`
- candidates with non-lead failure: `4`
- decision: `no_same_subject_stable_prospect_candidate`

| feature | target | family | holdout | full decision | lead bidir | nonlead bidir | lead targets | nonlead targets |
|---|---|---|---|---|---:|---:|---:|---:|
| recording_centered | response_latency | thalamic | MFD_06 | reject: target1 | 1/1 | 0/3 | 0.672/0.697 | 1.000/0.000 |
| recording_centered | response_latency | broad_named_anatomy | NR_0019 | reject: total baseline | 1/1 | 0/3 | 0.699/0.816 | 0.499/0.550 |
| recording_centered | prior_engaged | broad_named_anatomy | NR_0019 | reject: shuffle | 1/1 | 0/3 | 0.922/0.603 | 0.211/0.432 |
| counts | prior_engaged | broad_named_anatomy | NR_0019 | reject: shuffle | 0/1 | 0/3 | 0.856/0.353 | 0.670/0.187 |

## Decision

Do not train on prospect-lead candidates; same-subject non-lead recordings do not validate them.
