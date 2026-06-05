# External Manifest Acquisition Gap Audit

No-spend audit that compares the broader S3-present metadata-scored manifest against local HDF5 coverage. It identifies support-qualified subjects whose recordings should be acquired before another local model-free gate.

- broad manifest recordings: `47`
- broad manifest subjects: `12`
- local HDF5 recordings in broad manifest: `28`
- support-qualified subjects: `8`
- support-qualified subjects missing HDF5: `2`
- missing HDF5 recordings for qualified subjects: `7`
- projected manifest: `31` recordings, `8` subjects
- decision: `external_support80_acquisition_candidate`

## Subject Gaps

| subject | support | broad recs | local HDF5 | missing HDF5 | qualified | missing top regions |
|---|---:|---:|---:|---:|---|---|
| CSHL045 | 0.852 | 4 | 0 | 4 | True | sAMY |
| ZFM-01577 | 0.841 | 3 | 0 | 3 | True | CENT, VISl |
| KS014 | 1.000 | 4 | 4 | 0 | True | none |
| MFD_06 | 0.998 | 4 | 4 | 0 | True | none |
| NYU-12 | 0.969 | 4 | 4 | 0 | True | none |
| SWC_038 | 0.916 | 4 | 4 | 0 | True | ORBvl |
| CSH_ZAD_019 | 0.900 | 4 | 4 | 0 | True | MED |
| NR_0019 | 0.846 | 4 | 4 | 0 | True | SSp-ul |
| PL015 | 0.758 | 4 | 0 | 4 | False | VISal, ECT, AUDpo |
| DY_009 | 0.745 | 4 | 0 | 4 | False | CN, HEM |
| ibl_witten_19 | 0.666 | 4 | 0 | 4 | False | ORBl, ILA |
| SWC_043 | 0.675 | 4 | 4 | 0 | False | LS, SSs |

## Written Manifests

- `missing_hdf5`: `manifests/ibl_bwm_external_support80_missing_hdf5.json`
- `projected_hdf5`: `manifests/ibl_bwm_external_support80_projected_hdf5.json`

## Decision

This is a data-acquisition trigger, not a training trigger. After these recordings are available as local HDF5s, rerun the local manifest candidate audit and then the same model-free true-vs-shuffle, total-baseline, target0/target1, and same-recording bidirectional gate before any GPU run.
