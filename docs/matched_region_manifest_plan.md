# Matched-Region Manifest Plan

Candidate recordings: 48
Candidate subjects: 12
Region granularity: `parent`
Local BrainSet cache: `/Users/colin/Desktop/Projects/anatomical-neural-fm/data/brainsets/ibl_bwm`

## Metadata Balance

| subject | selected_recordings | units_meta | labs | probes |
|---|---:|---:|---|---|
| CSHL045 | 4 | 1678 | churchlandlab | probe00:1, probe01:3 |
| CSH_ZAD_019 | 4 | 2426 | zadorlab | probe00:2, probe01:2 |
| DY_009 | 4 | 2568 | danlab | probe00:4 |
| KS014 | 4 | 5133 | cortexlab | probe00:3, probe01:1 |
| MFD_06 | 4 | 2832 | churchlandlab_ucla | probe00:4 |
| NR_0019 | 4 | 1466 | steinmetzlab | probe00:2, probe01:2 |
| NYU-12 | 4 | 1883 | angelakilab | probe00:2, probe01:2 |
| PL015 | 4 | 2310 | hausserlab | probe00:4 |
| SWC_038 | 4 | 2508 | mrsicflogellab | probe01:4 |
| SWC_043 | 4 | 3007 | hoferlab | probe00:3, probe01:1 |
| ZFM-01577 | 4 | 2745 | mainenlab | probe00:3, probe01:1 |
| ibl_witten_19 | 4 | 1512 | wittenlab | probe00:2, probe01:2 |

## Lab Counts

| lab | selected_recordings |
|---|---:|
| angelakilab | 4 |
| churchlandlab | 4 |
| churchlandlab_ucla | 4 |
| cortexlab | 4 |
| danlab | 4 |
| hausserlab | 4 |
| hoferlab | 4 |
| mainenlab | 4 |
| mrsicflogellab | 4 |
| steinmetzlab | 4 |
| wittenlab | 4 |
| zadorlab | 4 |

## Region-Family Scoring Status

The local cache covers 2 subjects and 3 recordings.

The candidate manifest is not fully built locally, so region-family matching cannot be scored yet.

Missing candidate subjects in local cache: CSHL045, CSH_ZAD_019, DY_009, KS014, MFD_06, NR_0019, NYU-12, PL015, SWC_038, SWC_043, ZFM-01577, ibl_witten_19

## Available Region Support

| subject | cached_recordings | units | region_families | unit_support_vs_others | top8_supported | missing_top_regions |
|---|---:|---:|---:|---:|---:|---|
| MFD_08 | 2 | 2396 | 20 | 9.8% | 1/8 | VNC, CENT, PRT, MY-mot, MBmot, VISp, cbf |
| MFD_09 | 1 | 1557 | 9 | 13.2% | 5/8 | LAT, SSp-tr, fxs |

## Decision Gate

Build this candidate manifest only if we are ready to spend on data construction, not training.
After build, rerun this planner and require at least 80% held-out unit support for most subjects before launching another seed sweep.

## Cloud Build Attempt

The 48-recording build/audit was attempted on RunPod A100 twice under the
project budget guard.

| attempt | cap | container_disk | result |
|---|---:|---:|---|
| `anfm-a100-matched-region-audit-20260604-040052` | 2h | 80 GB | manually stopped after missing cap; no pushed artifact |
| `anfm-a100-matched-region-audit-20260604-060316` | 4h | 160 GB | manually stopped after missing cap; no pushed artifact |

Estimated combined spend was about $8.45, and cleanup left zero pods and zero
network volumes. The practical next step is to split or persist the data build
before retrying the region-family scoring gate.
