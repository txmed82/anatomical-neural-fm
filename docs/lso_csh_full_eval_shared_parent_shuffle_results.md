# Cloud Phase 3-5 Results

Date: 2026-06-05T01:06:04Z

RunPod target: A100 pilot.

Exit status: 0

Configuration:

- branch: runpod-pilot-phases-3-5
- build recordings: 0
- max steps: 300
- eval batches: 20
- target mode: stimulus_side
- sweep script: scripts/run_lso_csh_zad_019_shared_parent_shuffle_a100.sh
- setup mode: project
- skip cell-type priors: True
- skip sweep: False
- startup smoke only: False
- dependency diagnostic: False
- max runtime seconds: 5400
- output root: `runs/lso_csh_full_eval_shared_parent_shuffle`
- sweep env: `FULL_EVAL_ON_BEST=1, SAVE_DIAGNOSTICS=0`

## Missing Sweep Summary

No `runs/lso_csh_full_eval_shared_parent_shuffle/summary.md`, `within_summary.md`, or
`cross_summary.md` file was present when cleanup pushed artifacts. Treat this
cloud result as incomplete/non-evidence even if the pod exit status is 0.

