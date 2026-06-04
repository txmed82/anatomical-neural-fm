# Cloud Phase 3-5 Results

Date: 2026-06-04T19:14:27Z

RunPod target: A100 pilot.

Exit status: 0

Configuration:

- branch: runpod-pilot-phases-3-5
- build recordings: 6
- max steps: 600
- eval batches: 50
- target mode: choice
- sweep script: scripts/run_phase2_cloud_a100.sh
- setup mode: minimal-data
- skip cell-type priors: True
- skip sweep: True
- startup smoke only: False
- max runtime seconds: 7200
- output root: `runs/compact_support80_best6_shard0_gpu`

## Within-Animal Summary


## Cross-Animal Summary

