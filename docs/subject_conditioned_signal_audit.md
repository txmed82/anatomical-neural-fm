# Subject-Conditioned Signal Audit

Manifest: `manifests/ibl_bwm_phase4.json`
LSO result source: `docs/lso_promising_results.md`
Local BrainSet cache: `data/brainsets/ibl_bwm`

## Coverage Status

The 20-recording manifest contains 10 subjects. The local HDF5 cache currently covers 2 subjects and 3 recordings.

Local cache subjects not present in the 20-recording manifest:

- `MFD_08`
- `MFD_09`

Trial class balance and region overlap are therefore partial locally. Run this script on the same RunPod-built dataset for the full audit.

## Manifest Subject Summary

| subject | recordings | units_meta | lab | probes | mean_alignment_qc | best_confirmed_delta |
|---|---:|---:|---|---|---:|---:|
| CSHL045 | 2 | 993 | churchlandlab | probe01:2 | 0.864 | waveform_only +0.024 |
| DY_008 | 2 | 1051 | danlab | probe00:2 | 0.888 | pure_anatomy +0.045 |
| KS014 | 2 | 3096 | cortexlab | probe00:2 | 0.918 | pure_anatomy -0.017 |
| MFD_05 | 2 | 1495 | churchlandlab_ucla | probe00:2 | 0.956 | waveform_only +0.018 |
| NR_0019 | 2 | 946 | steinmetzlab | probe00:2 | 0.452 | n/a |
| NYU-11 | 2 | 1340 | angelakilab | probe00:1, probe01:1 | 0.965 | n/a |
| PL015 | 2 | 1280 | hausserlab | probe00:2 | 0.908 | n/a |
| SWC_038 | 2 | 1479 | mrsicflogellab | probe01:2 | 0.966 | n/a |
| SWC_042 | 2 | 650 | hoferlab | probe00:2 | 0.957 | n/a |
| ZFM-01576 | 2 | 1030 | mainenlab | probe00:1, probe01:1 | 0.903 | n/a |

## Candidate Confirmation Deltas

| subject | pure_anatomy | region_only | waveform_only | strongest arm | positive pure seeds |
|---|---:|---:|---:|---|---:|
| CSHL045 | -0.002 | -0.033 | +0.024 | waveform_only | 2/3 |
| DY_008 | +0.045 | +0.041 | +0.015 | pure_anatomy | 3/3 |
| KS014 | -0.017 | -0.027 | -0.017 | pure_anatomy | 2/3 |
| MFD_05 | +0.006 | +0.003 | +0.018 | waveform_only | 2/3 |

## Local Trial And Region Audit

| subject | cached_recordings | valid_target_trials | target_balance | units | regions | top_regions |
|---|---:|---:|---|---:|---:|---|
| MFD_08 | 2 | 1337 | L:686, R:651 | 2396 | 29 | MV:486, APN:348, CENT2:319, PARN:181, CA1:136, arb:123, CENT3:119, VISp6a:94 |
| MFD_09 | 1 | 500 | L:261, R:239 | 1557 | 16 | PO:1014, LP:133, CA1:93, SSp-tr6a:73, SSp-tr5:59, SSp-tr4:59, CA3:54, DG-mo:31 |

## Interpretation

`DY_008` remains the only confirmed subject where both `pure_anatomy` and `region_only` beat the shared null by more than +0.03 across all three seeds. The current local cache is insufficient to prove whether that is due to region coverage, trial balance, or a real transferable anatomical factor.

Next action: rerun this audit on the full RunPod-built 20-recording dataset, then launch only a region-balanced LSO rerun if `DY_008` has comparable training/eval region support.
