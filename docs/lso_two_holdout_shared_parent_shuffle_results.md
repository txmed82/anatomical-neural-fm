# Cloud Phase 3-5 Results

Date: 2026-06-04T22:47:44Z

RunPod target: A100 pilot.

Exit status: 0

Configuration:

- branch: runpod-pilot-phases-3-5
- build recordings: 0
- max steps: 300
- eval batches: 20
- target mode: stimulus_side
- sweep script: scripts/run_lso_two_holdout_shared_parent_shuffle_a100.sh
- setup mode: project
- skip cell-type priors: True
- skip sweep: False
- startup smoke only: False
- max runtime seconds: 5400
- output root: `runs/lso_two_holdout_shared_parent_shuffle`

## Missing Sweep Summary

No `runs/lso_two_holdout_shared_parent_shuffle/summary.md`, `within_summary.md`, or
`cross_summary.md` file was present when cleanup pushed artifacts. Treat this
cloud result as incomplete/non-evidence even if the pod exit status is 0.

