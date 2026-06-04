# Matched-Region Manifest Plan

Candidate recordings: 28
Candidate subjects: 7
Region granularity: `parent`
Local BrainSet cache: `/Users/colin/Desktop/Projects/anatomical-neural-fm/data/brainsets/ibl_bwm`
Region source: OpenAlyx cluster/channel metadata

## Metadata Balance

| subject | selected_recordings | units_meta | labs | probes |
|---|---:|---:|---|---|
| CSH_ZAD_019 | 4 | 2426 | zadorlab | probe00:2, probe01:2 |
| KS014 | 4 | 5133 | cortexlab | probe00:3, probe01:1 |
| MFD_06 | 4 | 2832 | churchlandlab_ucla | probe00:4 |
| NR_0019 | 4 | 1466 | steinmetzlab | probe00:2, probe01:2 |
| NYU-12 | 4 | 1883 | angelakilab | probe00:2, probe01:2 |
| SWC_038 | 4 | 2508 | mrsicflogellab | probe01:4 |
| SWC_043 | 4 | 3007 | hoferlab | probe00:3, probe01:1 |

## Lab Counts

| lab | selected_recordings |
|---|---:|
| angelakilab | 4 |
| churchlandlab_ucla | 4 |
| cortexlab | 4 |
| hoferlab | 4 |
| mrsicflogellab | 4 |
| steinmetzlab | 4 |
| zadorlab | 4 |

## Region-Family Scoring Status

The region source covers 7 subjects and 28 recordings.

## Available Region Support

| subject | cached_recordings | units | region_families | unit_support_vs_others | top8_supported | missing_top_regions |
|---|---:|---:|---:|---:|---:|---|
| CSH_ZAD_019 | 4 | 3564 | 29 | 84.8% | 7/8 | MED |
| KS014 | 4 | 3121 | 18 | 96.2% | 7/8 | SCs |
| MFD_06 | 4 | 5207 | 27 | 98.7% | 8/8 | none |
| NR_0019 | 4 | 2549 | 30 | 82.4% | 7/8 | SSp-ul |
| NYU-12 | 4 | 4255 | 31 | 94.6% | 8/8 | none |
| SWC_038 | 4 | 3842 | 16 | 82.5% | 6/8 | ORBvl, OLF |
| SWC_043 | 4 | 4827 | 27 | 65.8% | 6/8 | LS, SSs |

## Decision Gate

Build this candidate manifest only if we are ready to spend on data construction, not training.
Before launching another seed sweep, require at least 80% held-out unit support for most subjects.
If this report used metadata-only scoring, use it to choose the cache target, then confirm support again after the HDF5 build.
