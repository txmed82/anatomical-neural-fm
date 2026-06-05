# Prospect-Lead Candidate Validation

Compares candidate rows from the prospect-lead manifest against the full-manifest local gate.

- prospect candidates: `3`
- validated candidates: `0`
- single-recording candidates: `3`
- subset-only candidates: `3`
- decision: `no_validated_prospect_lead_candidate`

| target | family | holdout | full decision | prospect delta shuffle | prospect delta total | target0 | target1 | bidir recs |
|---|---|---|---|---:|---:|---:|---:|---:|
| response_latency | thalamic | MFD_06 | reject: target1 | +0.050 | +0.012 | 0.687 | 0.716 | 1/1 |
| response_latency | broad_named_anatomy | NR_0019 | reject: total baseline | +0.021 | +0.009 | 0.615 | 0.686 | 1/1 |
| prior_engaged | broad_named_anatomy | NR_0019 | reject: shuffle | +0.033 | +0.004 | 0.844 | 0.603 | 1/1 |

## Decision

Treat prospect-lead rows as design leads only; require full-manifest or held-out validation before GPU training.
