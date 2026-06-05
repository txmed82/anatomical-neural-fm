# Matched-Region Manifest Plan

Candidate recordings: 48
Candidate subjects: 12
Region granularity: `parent`
Local BrainSet cache: `/Users/colin/Desktop/Projects/anatomical-neural-fm/data/brainsets/ibl_bwm`
Region source: OpenAlyx cluster/channel metadata

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

The region source covers 12 subjects and 47 recordings.

## Available Region Support

| subject | cached_recordings | units | region_families | unit_support_vs_others | top8_supported | missing_top_regions |
|---|---:|---:|---:|---:|---:|---|
| CSHL045 | 4 | 3260 | 35 | 85.2% | 7/8 | sAMY |
| CSH_ZAD_019 | 4 | 3564 | 29 | 90.0% | 7/8 | MED |
| DY_009 | 4 | 4226 | 28 | 74.5% | 6/8 | CN, HEM |
| KS014 | 4 | 3121 | 18 | 100.0% | 8/8 | none |
| MFD_06 | 4 | 5207 | 27 | 99.8% | 8/8 | none |
| NR_0019 | 4 | 2549 | 30 | 84.6% | 7/8 | SSp-ul |
| NYU-12 | 4 | 4255 | 31 | 96.9% | 8/8 | none |
| PL015 | 4 | 3548 | 24 | 75.8% | 5/8 | VISal, ECT, AUDpo |
| SWC_038 | 4 | 3842 | 16 | 91.6% | 7/8 | ORBvl |
| SWC_043 | 4 | 4827 | 27 | 67.5% | 6/8 | LS, SSs |
| ZFM-01577 | 3 | 2710 | 20 | 84.1% | 6/8 | CENT, VISl |
| ibl_witten_19 | 4 | 2948 | 21 | 66.6% | 6/8 | ORBl, ILA |

## Metadata Region Failures

| session | probe | error |
|---|---|---|
| de588204-8fd6-4ce3-92da-7a6d1dcae238 | probe00 | Dataset "clusters.channels.npy" not found 
 The ALF object was not found.  This may occur if the object or namespace or incorrectly formatted e.g. the object "_ibl_trials.intervals.npy" would be found with the filters `object="trials", namespace="ibl"`  |

## Decision Gate

Build this candidate manifest only if we are ready to spend on data construction, not training.
Before launching another seed sweep, require at least 80% held-out unit support for most subjects.
If this report used metadata-only scoring, use it to choose the cache target, then confirm support again after the HDF5 build.
