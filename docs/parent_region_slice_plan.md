# Parent-Region Slice Plan

Manifest: `manifests/ibl_bwm_region_matched_support80_best6.json`
Data cache: `data/brainsets/ibl_bwm`
Reference holdout: `CSH_ZAD_019`
Target: `stimulus_side` over 1.0s stimulus-aligned windows

## Slice Definition

Reference carrier criteria:

- parent is present in both train and `CSH_ZAD_019` held-out split
- at least 100 `CSH_ZAD_019` units
- at least 3.0% of `CSH_ZAD_019` units
- absolute right-minus-left spike-rate contrast at least 0.100 Hz

Candidate inclusion gate:

- at least 500 units in the carrier-region slice
- at least 2 carrier parents with >= 50 units
- at least 75.0% of carrier-slice units have the same stimulus-side contrast sign as `CSH_ZAD_019`

## CSH Carrier Parents

| parent | CSH_units | CSH_unit_mass | CSH_right_minus_left_hz | units_x_abs_delta |
|---|---:|---:|---:|---:|
| PRT | 439 | 12.3% | -0.321 | 141.0 |
| CA | 480 | 13.5% | -0.145 | 69.7 |
| VP | 335 | 9.4% | +0.201 | 67.5 |
| MOp | 477 | 13.4% | -0.121 | 57.6 |
| DG | 159 | 4.5% | -0.239 | 37.9 |
| mfbc | 152 | 4.3% | +0.109 | 16.6 |

## Subject-Level Candidate Scores

| subject | pass | slice_units | present_carriers | carriers_with_min_units | aligned_unit_mass | present_parents | aligned_parents |
|---|---|---:|---:|---:|---:|---|---|
| NYU-12 | yes | 750 | 3/6 | 2 | 100.0% | CA, VP, DG | CA, VP, DG |
| SWC_038 | yes | 503 | 4/6 | 3 | 76.7% | PRT, CA, MOp, DG | CA, MOp, DG |
| KS014 | no | 121 | 1/6 | 1 | 100.0% | PRT | PRT |
| SWC_043 | no | 723 | 3/6 | 3 | 74.0% | CA, MOp, DG | MOp, DG |
| NR_0019 | no | 749 | 4/6 | 2 | 20.8% | PRT, VP, DG, mfbc | PRT, DG |
| MFD_06 | no | 242 | 3/6 | 2 | 1.2% | CA, VP, DG | VP |

## Recording-Level Candidate Scores

| recording | subject | pass | slice_units | present_carriers | carriers_with_min_units | aligned_unit_mass | present_parents | aligned_parents |
|---|---|---|---:|---:|---:|---:|---|---|
| a8a8af78-16de-4841-ab07-fde4b5281a03_probe01 | NYU-12 | yes | 591 | 2/6 | 2 | 100.0% | CA, DG | CA, DG |
| 03063955-2523-47bd-ae57-f7489dd40f15_probe01 | SWC_038 | no | 300 | 1/6 | 1 | 100.0% | MOp | MOp |
| a8a8af78-16de-4841-ab07-fde4b5281a03_probe00 | NYU-12 | no | 159 | 3/6 | 1 | 100.0% | CA, VP, DG | CA, VP, DG |
| b887df2c-bb9c-44c9-a9c0-538da87b2cab_probe00 | NR_0019 | no | 156 | 2/6 | 1 | 100.0% | PRT, DG | PRT, DG |
| e1931de1-cf7b-49af-af33-2ade15e8abe7_probe00 | KS014 | no | 121 | 1/6 | 1 | 100.0% | PRT | PRT |
| 88d24c31-52e4-49cc-9f32-6adbeb9eba87_probe00 | SWC_043 | no | 121 | 1/6 | 1 | 100.0% | MOp | MOp |
| 6f09ba7e-e3ce-44b0-932b-c003fb44fb89_probe01 | SWC_043 | no | 602 | 2/6 | 2 | 68.8% | CA, DG | DG |
| 41872d7f-75cb-4445-bb1a-132b354c44f0_probe01 | SWC_038 | no | 203 | 3/6 | 2 | 42.4% | PRT, CA, DG | CA, DG |
| 6899a67d-2e53-4215-a52a-c7021b5da5d4_probe00 | MFD_06 | no | 242 | 3/6 | 2 | 1.2% | CA, VP, DG | VP |
| 63c70ae8-4dfb-418b-b21b-f0b1e5fba6c9_probe00 | NR_0019 | no | 573 | 1/6 | 1 | 0.0% | VP | none |
| b887df2c-bb9c-44c9-a9c0-538da87b2cab_probe01 | NR_0019 | no | 20 | 1/6 | 0 | 0.0% | mfbc | none |
| b182b754-3c3e-4942-8144-6ee790926b58_probe01 | NYU-12 | no | 0 | 0/6 | 0 | 0.0% | none | none |

## Decision

The current matched cache contains subject-level slice candidates: NYU-12, SWC_038. The first paid test was a fixed carrier-parent true-vs-shuffled control on the top passing subject using the explicit parent-region include filter.

At recording level, the strongest slice candidate is `a8a8af78-16de-4841-ab07-fde4b5281a03_probe01` from `NYU-12`. This supports using the slice as an inclusion rule, but a subject-level cross-animal claim still needs whole-subject held-out evaluation.

Completed paid result: `docs/lso_nyu12_parent_slice_results.md` ran `NYU-12` with `--region-filter include_regions`, `--region-granularity parent`, and `--region-include "PRT,CA,VP,MOp,DG,mfbc"`. The true-label arm was weakly positive (`region_only` +0.013 mean delta, 2/3 positive seeds), but the shuffled-label arm was larger and more consistent (`region_shuffle` +0.020 mean delta, 3/3 positive seeds).

Conclusion: this carrier-parent gate is not sufficient for a demo-grade cross-animal anatomical transfer claim. Do not spend on the same fixed-slice run again. The next step should be a no-spend diagnostic that explains why the CSH_ZAD_019 carrier parents transfer under true labels while `NYU-12` does not separate true labels from shuffled labels.

Follow-up diagnostic: `docs/transfer_success_mode_audit.md` tightens the gate
from CSH-sign alignment to leave-subject-out training alignment plus
CSH-weighted carrier coverage. Under that stricter screen, `NYU-12` fails
because it covers only 44.9% of the CSH carrier-weighted signal. `SWC_038` is
the next candidate because it has 503 slice units, 78.5% CSH carrier-weighted
coverage, and 76.7% sign-aligned unit mass against its LSO training aggregate.

Next paid test, if launched: `SWC_038` only, same parent include list
(`PRT,CA,VP,MOp,DG,mfbc`), same true-vs-shuffled control, and stop unless true
labels beat shuffled labels.
