# Prospect-Lead Feature-Mode Validation

Validates prospect-lead derived target candidates across all tested feature modes.

- feature modes: `4`
- prospect candidates: `4`
- full-manifest candidates: `0`
- validated candidates: `0`
- single-recording candidates: `4`
- subset-only candidates: `4`
- decision: `no_validated_prospect_lead_feature_mode_candidate`

## Feature Modes

| feature mode | prospect candidates | full candidates | validated | single-rec | subset-only | prospect max bidir | full max bidir |
|---|---:|---:|---:|---:|---:|---:|---:|
| recording_centered | 3 | 0 | 0 | 3 | 3 | 3 | 3 |
| counts | 1 | 0 | 0 | 1 | 1 | 1 | 1 |
| fractions | 0 | 0 | 0 | 0 | 0 | 1 | 2 |
| unit_residuals | 0 | 0 | 0 | 0 | 0 | 1 | 2 |

## Prospect Candidates

| feature mode | target | family | holdout | full decision | bidir recs |
|---|---|---|---|---|---:|
| recording_centered | response_latency | thalamic | MFD_06 | reject: target1 | 1/1 |
| recording_centered | response_latency | broad_named_anatomy | NR_0019 | reject: total baseline | 1/1 |
| recording_centered | prior_engaged | broad_named_anatomy | NR_0019 | reject: shuffle | 1/1 |
| counts | prior_engaged | broad_named_anatomy | NR_0019 | reject: shuffle | 1/1 |

## Decision

Do not spend on prospect-lead derived candidates; they fail full-manifest feature-mode validation.
