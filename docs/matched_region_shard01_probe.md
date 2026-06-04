# Cloud Phase 3-5 Results

Date: 2026-06-04T16:00:44Z

RunPod target: A100 pilot.

Exit status: 0

Configuration:

- branch: runpod-pilot-phases-3-5
- build recordings: 48
- max steps: 1
- eval batches: 1
- target mode: stimulus_side
- sweep script: scripts/run_matched_region_audit_a100.sh
- max runtime seconds: 5400
- output root: `runs/matched_region_shard01_probe_a100`

## Build Report

# IBL BrainSet Batch Build

Manifest: `manifests/ibl_bwm_region_matched_candidates.json`
Shard: 2/24
Selected recordings: 2
Available recordings: 2
Skipped existing: 2
Failures: 0
Elapsed seconds: 0

## Available

| session | probe | path |
|---|---|---|
| 3f71aa98-08c6-4e79-b4c8-00eae4f03eff | probe00 | `data/brainsets/ibl_bwm/3f71aa98-08c6-4e79-b4c8-00eae4f03eff_probe00.h5` |
| 16693458-0801-4d35-a3f1-9115c7e5acfd | probe00 | `data/brainsets/ibl_bwm/16693458-0801-4d35-a3f1-9115c7e5acfd_probe00.h5` |

## Summary

# Matched-Region Manifest Plan

Candidate recordings: 48
Candidate subjects: 12
Region granularity: `parent`
Local BrainSet cache: `data/brainsets/ibl_bwm`

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

The local cache covers 4 subjects and 4 recordings.

The candidate manifest is not fully built locally, so region-family matching cannot be scored yet.

Missing candidate subjects in local cache: CSH_ZAD_019, DY_009, NR_0019, PL015, SWC_038, SWC_043, ZFM-01577, ibl_witten_19

## Available Region Support

| subject | cached_recordings | units | region_families | unit_support_vs_others | top8_supported | missing_top_regions |
|---|---:|---:|---:|---:|---:|---|
| CSHL045 | 1 | 1237 | 10 | 0.1% | 0/8 | MY-mot, CUL, VNC, cbf, CBN, CB, MY-sen, V4 |
| KS014 | 1 | 917 | 5 | 93.3% | 3/5 | SCs, cett |
| MFD_06 | 1 | 1689 | 4 | 0.0% | 0/4 | void, ENTm, VISpor, VISpl |
| NYU-12 | 1 | 1255 | 9 | 59.0% | 4/8 | P-sen, MBsta, P-mot, scp |

## Decision Gate

Build this candidate manifest only if we are ready to spend on data construction, not training.
After build, rerun this planner and require at least 80% held-out unit support for most subjects before launching another seed sweep.
