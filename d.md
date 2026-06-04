# Cloud Phase 3-5 Results

Date: 2026-06-04T22:43:55Z

RunPod target: A100 pilot.

Exit status: 0

Configuration:

- branch: runpod-pilot-phases-3-5
- build recordings: 0
- max steps: 300
- eval batches: 20
- target mode: stimulus_side
- sweep script: t.sh
- setup mode: project
- skip cell-type priors: True
- skip sweep: False
- startup smoke only: False
- max runtime seconds: 7200
- output root: `r`

## Missing Sweep Summary

No `r/summary.md`, `within_summary.md`, or
`cross_summary.md` file was present when cleanup pushed artifacts. Treat this
cloud result as incomplete/non-evidence even if the pod exit status is 0.

