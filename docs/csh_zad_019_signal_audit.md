# CSH_ZAD_019 Cross-Animal Anatomy Signal Audit

Holdout: `CSH_ZAD_019`
Manifest: `manifests/ibl_bwm_region_matched_support80_best6.json`

## Data Footprint

The matched manifest contains 28 recordings from 7 subjects. `CSH_ZAD_019` contributes 4 recordings, 2426 metadata units, and probes probe00, probe01 from zadorlab.

## Shared-Parent Split Diagnostic

The stricter control used `shared_regions` with `parent` region labels, leaving 21 shared parent regions.

| train_subjects | eval_subjects | train_trials | eval_trials | train_balance | eval_balance |
|---|---|---:|---:|---|---|
| KS014, MFD_06, NR_0019, NYU-12, SWC_038, SWC_043 | CSH_ZAD_019 | 13015 | 2726 | {'L': 6688, 'R': 6327} | {'L': 1504, 'R': 1222} |

Allowed parent regions:

`BS`, `CA`, `DG`, `IB`, `LAT`, `LZ`, `MBmot`, `MOp`, `PRT`, `RSPagl`, `RSPd`, `VENT`, `VL`, `VP`, `VS`, `cc`, `fxs`, `hc`, `mfbc`, `root`, `void`

## Evidence Ladder

| source | arm | n_seeds | mean_AUC | mean_delta_vs_shared | seed_deltas | positive_seeds |
|---|---|---:|---:|---:|---|---:|
| matched seed0 screen | pure_anatomy | 1 | n/a | +0.002 | +0.002 | 1/1 |
| matched seed0 screen | region_only | 1 | n/a | +0.029 | +0.029 | 1/1 |
| matched seeds1-2 confirmation | pure_anatomy | 2 | 0.528 | +0.040 | +0.048,+0.032 | 2/2 |
| matched seeds1-2 confirmation | region_only | 2 | 0.537 | +0.049 | +0.054,+0.044 | 2/2 |
| matched seed0 + seeds1-2 | pure_anatomy | 3 | 0.528 | +0.027 | +0.002,+0.048,+0.032 | 3/3 |
| matched seed0 + seeds1-2 | region_only | 3 | 0.537 | +0.042 | +0.029,+0.054,+0.044 | 3/3 |
| fine region shuffle control | region_only | 3 | 0.548 | +0.042 | +0.029,+0.054,+0.044 | 3/3 |
| fine region shuffle control | region_shuffle | 3 | 0.494 | -0.012 | +0.001,-0.036,+0.000 | 1/3 |
| shared-parent shuffle control | region_only | 3 | 0.544 | +0.038 | +0.014,+0.045,+0.056 | 3/3 |
| shared-parent shuffle control | region_shuffle | 3 | 0.494 | -0.012 | -0.008,-0.030,+0.003 | 1/3 |

## Interpretation

The strongest current evidence is not a broad aggregate gain; it is a controlled single-holdout signal. `CSH_ZAD_019` is positive for `region_only` across the matched seed0 screen and the two confirmation seeds, and the effect persists under two label-identity controls.

The fine-region control shows true labels at +0.042 mean delta while shuffled labels are -0.012. The stricter shared-parent control shows true labels at +0.038 while shuffled parent labels are also -0.012. That makes a simple model-capacity or marginal label-frequency explanation unlikely.

The honest claim is still subject-specific: this is a credible demo nucleus for cross-animal anatomical transfer, not yet evidence that the effect is general across IBL animals. The next paid experiment should broaden the same shared-parent true-vs-shuffled control to a small number of additional matched holdouts instead of rerunning `CSH_ZAD_019` again.

## Source Documents

- `docs/lso_matched_support80_best6_seed0_results.md`
- `docs/lso_matched_support80_best6_confirm_results.md`
- `docs/lso_csh_zad_019_region_shuffle_results.md`
- `docs/lso_csh_zad_019_shared_parent_shuffle_results.md`
- `docs/cloud_phase3_5_runpod.log`
