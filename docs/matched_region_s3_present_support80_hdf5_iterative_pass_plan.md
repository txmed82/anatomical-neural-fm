# Matched-Region Manifest Plan

Candidate recordings: 8
Candidate subjects: 2
Region granularity: `parent`
Local BrainSet cache: `/Users/colin/Desktop/Projects/anatomical-neural-fm/data/brainsets/ibl_bwm`
Region source: local BrainSet HDF5 cache

## Metadata Balance

| subject | selected_recordings | units_meta | labs | probes |
|---|---:|---:|---|---|
| MFD_06 | 4 | 2832 | churchlandlab_ucla | probe00:4 |
| NYU-12 | 4 | 1883 | angelakilab | probe00:2, probe01:2 |

## Lab Counts

| lab | selected_recordings |
|---|---:|
| angelakilab | 4 |
| churchlandlab_ucla | 4 |

## Region-Family Scoring Status

The region source covers 2 subjects and 8 recordings.

## Available Region Support

| subject | cached_recordings | units | region_families | unit_support_vs_others | top8_supported | missing_top_regions |
|---|---:|---:|---:|---:|---:|---|
| MFD_06 | 4 | 5207 | 27 | 98.7% | 8/8 | none |
| NYU-12 | 4 | 4255 | 31 | 88.5% | 8/8 | none |

## Decision Gate

Build this candidate manifest only if we are ready to spend on data construction, not training.
Before launching another seed sweep, require at least 80% held-out unit support for most subjects.
If this report used metadata-only scoring, use it to choose the cache target, then confirm support again after the HDF5 build.
