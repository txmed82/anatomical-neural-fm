# Cloud Phase 3-5 Results

Date: 2026-06-05T05:09:30Z

RunPod target: CPU cpu3c,cpu3g,cpu3m.

Exit status: 0

Configuration:

- branch: runpod-pilot-phases-3-5
- build recordings: 6
- max steps: 600
- eval batches: 50
- target mode: choice
- sweep script: scripts/run_phase2_cloud_a100.sh
- setup mode: minimal-data
- build mode: incremental
- skip cell-type priors: True
- skip sweep: True
- startup smoke only: False
- dependency diagnostic: False
- max runtime seconds: 14400
- output root: `runs/matched_region_missing_incremental`
- sweep env: `<none>`

## Cache Audit

# BrainSet S3 Cache Audit

Manifest: `manifests/ibl_bwm_region_matched_candidates_missing_s3.json`
Cache: `s3://rppfvo6ifn/brainsets/ibl_bwm`
Present: 18/19 (94.7%)

## Missing

| filename |
|---|
| `de588204-8fd6-4ce3-92da-7a6d1dcae238_probe00.h5` |

## Present

| filename |
|---|
| `034e726f-b35f-41e0-8d6c-a22cc32391fb_probe01.h5` |
| `09156021-9a1d-4e1d-ae59-48cbde3c5d42_probe00.h5` |
| `09b2c4d1-058d-4c84-9fd4-97530f85baf6_probe00.h5` |
| `30e5937e-e86a-47e6-93ae-d2ae3877ff8e_probe00.h5` |
| `4ddb8a95-788b-48d0-8a0a-66c7c796da96_probe00.h5` |
| `4ddb8a95-788b-48d0-8a0a-66c7c796da96_probe01.h5` |
| `5d6aa933-4b00-4e99-ae2d-5003657592e9_probe01.h5` |
| `63f3dbc1-1a5f-44e5-98dd-ce25cd2b7871_probe00.h5` |
| `64977c74-9c04-437a-9ea1-50386c4996db_probe00.h5` |
| `65f5c9b4-4440-48b9-b914-c593a5184a18_probe00.h5` |
| `6668c4a0-70a4-4012-a7da-709660971d7a_probe00.h5` |
| `90e524a2-aa63-47ce-b5b8-1b1941a1223a_probe00.h5` |
| `9a6e127b-bb07-4be2-92e2-53dd858c2762_probe00.h5` |
| `a19c7a3a-7261-42ce-95d5-1f4ca46007ed_probe00.h5` |
| `dfd8e7df-dc51-4589-b6ca-7baccfeb94b4_probe01.h5` |
| `e5c772cd-9c92-47ab-9525-d618b66a9b5d_probe00.h5` |
| `f8041c1e-5ef4-4ae6-afec-ed82d7a74dc1_probe01.h5` |
| `fa704052-147e-46f6-b190-a65b837e605e_probe00.h5` |

## Incremental Build Summary

```json
{
  "success": [
    "034e726f-b35f-41e0-8d6c-a22cc32391fb_probe01.h5",
    "09156021-9a1d-4e1d-ae59-48cbde3c5d42_probe00.h5",
    "09b2c4d1-058d-4c84-9fd4-97530f85baf6_probe00.h5",
    "30e5937e-e86a-47e6-93ae-d2ae3877ff8e_probe00.h5",
    "4ddb8a95-788b-48d0-8a0a-66c7c796da96_probe00.h5",
    "4ddb8a95-788b-48d0-8a0a-66c7c796da96_probe01.h5",
    "5d6aa933-4b00-4e99-ae2d-5003657592e9_probe01.h5",
    "63f3dbc1-1a5f-44e5-98dd-ce25cd2b7871_probe00.h5",
    "64977c74-9c04-437a-9ea1-50386c4996db_probe00.h5",
    "65f5c9b4-4440-48b9-b914-c593a5184a18_probe00.h5",
    "6668c4a0-70a4-4012-a7da-709660971d7a_probe00.h5",
    "90e524a2-aa63-47ce-b5b8-1b1941a1223a_probe00.h5",
    "9a6e127b-bb07-4be2-92e2-53dd858c2762_probe00.h5",
    "a19c7a3a-7261-42ce-95d5-1f4ca46007ed_probe00.h5",
    "dfd8e7df-dc51-4589-b6ca-7baccfeb94b4_probe01.h5",
    "e5c772cd-9c92-47ab-9525-d618b66a9b5d_probe00.h5",
    "f8041c1e-5ef4-4ae6-afec-ed82d7a74dc1_probe01.h5",
    "fa704052-147e-46f6-b190-a65b837e605e_probe00.h5"
  ],
  "failed": [
    {
      "filename": "de588204-8fd6-4ce3-92da-7a6d1dcae238_probe00.h5",
      "build_rc": 1
    }
  ],
  "elapsed_seconds": 551.8
}
```

## Failure Note

The remaining file, `de588204-8fd6-4ce3-92da-7a6d1dcae238_probe00.h5`, failed
during public OpenAlyx data loading because the required ALF trials object was
not found. This looks like a dataset/object-availability issue for that
recording, not a RunPod capacity or S3 upload failure.

## Missing Sweep Summary

No `runs/matched_region_missing_incremental/summary.md`, `within_summary.md`, or
`cross_summary.md` file was present when cleanup pushed artifacts. Treat this
cloud result as incomplete/non-evidence even if the pod exit status is 0.
