# Model-Free Recording Replication Audit

Prospective recording-level screen using fixed report families. A recording is selected only from discovery reports, then tested on held-out validation reports to avoid defining a demo subset after seeing every gate row.

- discovery reports: `family centered, family centered l2=1, family centered l2=100, panel recording centered`
- validation reports: `family feedback, family prior side, source-target centered, source-target families`
- recording-subject rows: `28`
- selected by discovery rule: `3`
- replicated in validation: `0`
- decision: `no_replicating_recording_rule`

## Top Recording Rules

| subject | recording | selected | replicated | discovery bidir | discovery target0 | discovery target1 | validation bidir | validation target0 | validation target1 |
|---|---|---|---|---:|---:|---:|---:|---:|---:|
| KS014 | e1931de1-cf7b-49af-af33-2ade15e8abe7_probe00 | True | False | 4/4 (1.000) | 0.614 | 0.572 | 3/14 (0.214) | 0.479 | 0.491 |
| MFD_06 | 6899a67d-2e53-4215-a52a-c7021b5da5d4_probe00 | True | False | 3/4 (0.750) | 0.601 | 0.622 | 9/14 (0.643) | 0.557 | 0.530 |
| KS014 | 16693458-0801-4d35-a3f1-9115c7e5acfd_probe01 | True | False | 3/4 (0.750) | 0.567 | 0.552 | 1/14 (0.071) | 0.517 | 0.526 |
| CSH_ZAD_019 | edd22318-216c-44ff-bc24-49ce8be78374_probe00 | False | False | 3/4 (0.750) | 0.548 | 0.573 | 1/14 (0.071) | 0.525 | 0.518 |
| SWC_038 | 03063955-2523-47bd-ae57-f7489dd40f15_probe01 | False | False | 3/4 (0.750) | 0.584 | 0.532 | 5/14 (0.357) | 0.535 | 0.512 |
| SWC_038 | 4d8c7767-981c-4347-8e5e-5d5fffe38534_probe01 | False | False | 1/4 (0.250) | 0.455 | 0.524 | 0/14 (0.000) | 0.554 | 0.457 |
| NR_0019 | b887df2c-bb9c-44c9-a9c0-538da87b2cab_probe00 | False | False | 0/4 (0.000) | 0.470 | 0.451 | 1/14 (0.071) | 0.510 | 0.528 |
| NR_0019 | 63c70ae8-4dfb-418b-b21b-f0b1e5fba6c9_probe00 | False | False | 0/4 (0.000) | 0.451 | 0.554 | 1/14 (0.071) | 0.509 | 0.524 |
| SWC_043 | 6f09ba7e-e3ce-44b0-932b-c003fb44fb89_probe01 | False | False | 0/4 (0.000) | 0.506 | 0.555 | 1/14 (0.071) | 0.523 | 0.499 |
| SWC_038 | 41872d7f-75cb-4445-bb1a-132b354c44f0_probe01 | False | False | 0/4 (0.000) | 0.466 | 0.562 | 0/14 (0.000) | 0.499 | 0.520 |
| CSH_ZAD_019 | 5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe00 | False | False | 0/4 (0.000) | 0.517 | 0.520 | 0/14 (0.000) | 0.522 | 0.496 |
| NYU-12 | 032ffcdf-7692-40b3-b9ff-8def1fc18b2e_probe00 | False | False | 0/4 (0.000) | 0.430 | 0.592 | 1/14 (0.071) | 0.518 | 0.495 |
| NYU-12 | a8a8af78-16de-4841-ab07-fde4b5281a03_probe00 | False | False | 0/4 (0.000) | 0.415 | 0.493 | 0/14 (0.000) | 0.494 | 0.496 |
| SWC_043 | 4ecb5d24-f5cc-402c-be28-9d0f7cb14b3a_probe00 | False | False | 0/4 (0.000) | 0.433 | 0.423 | 2/14 (0.143) | 0.521 | 0.492 |

## Decision

A recording subset is not a credible next benchmark unless it is selected by the discovery rule and keeps bidirectional target support in validation. If this audit has zero replicated recordings, the next step is to redesign the target/control or manifest rather than launch GPU training.
