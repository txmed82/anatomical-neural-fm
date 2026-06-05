# Cloud Phase 3-5 Results

Date: 2026-06-04T15:41:20Z

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
- output root: `runs/matched_region_shard00_probe_a100`

## Build Report

# IBL BrainSet Batch Build

Manifest: `manifests/ibl_bwm_region_matched_candidates.json`
Shard: 1/24
Selected recordings: 2
Available recordings: 2
Skipped existing: 2
Failures: 0
Elapsed seconds: 0

## Available

| session | probe | path |
|---|---|---|
| b182b754-3c3e-4942-8144-6ee790926b58 | probe01 | `data/brainsets/ibl_bwm/b182b754-3c3e-4942-8144-6ee790926b58_probe01.h5` |
| 7939711b-8b4d-4251-b698-b97c1eaa846e | probe01 | `data/brainsets/ibl_bwm/7939711b-8b4d-4251-b698-b97c1eaa846e_probe01.h5` |

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

The local cache covers 2 subjects and 2 recordings.

The candidate manifest is not fully built locally, so region-family matching cannot be scored yet.

Missing candidate subjects in local cache: CSH_ZAD_019, DY_009, KS014, MFD_06, NR_0019, PL015, SWC_038, SWC_043, ZFM-01577, ibl_witten_19

## Available Region Support

| subject | cached_recordings | units | region_families | unit_support_vs_others | top8_supported | missing_top_regions |
|---|---:|---:|---:|---:|---:|---|
| CSHL045 | 1 | 1237 | 10 | 0.1% | 0/8 | MY-mot, CUL, VNC, cbf, CBN, CB, MY-sen, V4 |
| NYU-12 | 1 | 1255 | 9 | 22.1% | 1/8 | MBmot, P-sen, SCm, MBsta, BS, P-mot, scp |

## Decision Gate

Build this candidate manifest only if we are ready to spend on data construction, not training.
After build, rerun this planner and require at least 80% held-out unit support for most subjects before launching another seed sweep.
