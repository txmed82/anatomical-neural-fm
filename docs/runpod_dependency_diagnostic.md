# Cloud Phase 3-5 Results

Date: 2026-06-04T23:10:27Z

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
- dependency diagnostic: True
- max runtime seconds: 900
- output root: `runs/runpod_dependency_diagnostic`

## Missing Sweep Summary

No `runs/runpod_dependency_diagnostic/summary.md`, `within_summary.md`, or
`cross_summary.md` file was present when cleanup pushed artifacts. Treat this
cloud result as incomplete/non-evidence even if the pod exit status is 0.

