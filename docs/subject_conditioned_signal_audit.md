# Cloud Phase 3-5 Results

Date: 2026-06-04T06:31:04Z

RunPod target: A100 pilot.

Exit status: 0

Configuration:

- branch: runpod-pilot-phases-3-5
- build recordings: 20
- max steps: 1
- eval batches: 1
- target mode: stimulus_side
- sweep script: scripts/run_subject_audit_a100.sh
- max runtime seconds: 3600
- output root: `runs/subject_conditioned_audit_a100`

## Summary

# Subject-Conditioned Signal Audit

Manifest: `manifests/ibl_bwm_phase4.json`
LSO result source: `docs/lso_promising_results.md`
Local BrainSet cache: `data/brainsets/ibl_bwm`

## Coverage Status

The 20-recording manifest contains 10 subjects. The local HDF5 cache currently covers 10 subjects and 20 recordings.

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
| CSHL045 | 2 | 1387 | L:667, R:720 | 1889 | 24 | CUL4 5:429, RT:223, IRN:214, int:140, MEA:137, PARN:115, SPIV:95, arb:88 |
| DY_008 | 2 | 781 | L:405, R:376 | 1699 | 27 | PO:378, VPM:183, CA1:137, VPL:115, CP:106, SSp-bfd6a:100, LP:99, SSp-tr5:72 |
| KS014 | 2 | 1075 | L:583, R:492 | 1336 | 22 | RN:284, SCiw:242, SCig:228, MRN:194, APN:121, SCsg:32, fp:27, MB:26 |
| MFD_05 | 2 | 1162 | L:587, R:575 | 2356 | 32 | SPVI:308, ProS:247, arb:223, RN:184, MY:160, CENT3:156, SCig:108, MRN:106 |
| NR_0019 | 2 | 1212 | L:597, R:615 | 1548 | 20 | VPM:372, MRN:235, VPL:201, MB:190, APN:112, ZI:79, LHA:66, VAL:61 |
| NYU-11 | 2 | 758 | L:314, R:444 | 1728 | 31 | BMAp:270, int:237, CEAl:174, LGd-co:143, COApl:111, TH:100, CA1:98, GPe:92 |
| PL015 | 2 | 1133 | L:519, R:614 | 1634 | 29 | CA1:495, AUDp6a:99, AUDpo5:89, VISal2/3:89, ECT2/3:81, VISal5:74, TEa5:71, ENTl5:68 |
| SWC_038 | 2 | 1222 | L:628, R:594 | 2735 | 13 | MOs5:642, CP:474, MOs6a:445, ORBvl6a:324, MOs2/3:278, AON:191, ACB:123, DP:80 |
| SWC_042 | 2 | 913 | L:441, R:472 | 2664 | 28 | CA3:591, LGv:244, DG-mo:237, DG-sg:222, SSp-bfd6a:153, HATA:151, void:133, SSp-bfd4:113 |
| ZFM-01576 | 2 | 1624 | L:900, R:724 | 1626 | 30 | SIM:293, LAV:259, MOp5:123, MOp2/3:111, PVT:99, MOs6a:86, arb:83, PARN:75 |

## Interpretation

`DY_008` remains the only confirmed subject where both `pure_anatomy` and `region_only` beat the shared null by more than +0.03 across all three seeds. The current local cache is insufficient to prove whether that is due to region coverage, trial balance, or a real transferable anatomical factor.

Next action: rerun this audit on the full RunPod-built 20-recording dataset, then launch only a region-balanced LSO rerun if `DY_008` has comparable training/eval region support.
