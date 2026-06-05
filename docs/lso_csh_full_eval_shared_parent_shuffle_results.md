# Cloud Phase 3-5 Results

Date: 2026-06-05T01:15:32Z

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
- max runtime seconds: 7200
- output root: `runs/lso_csh_full_eval_shared_parent_shuffle`
- sweep env: `FULL_EVAL_ON_BEST=1, SAVE_DIAGNOSTICS=0`

## Build Report

# IBL BrainSet Batch Build

Manifest: `manifests/ibl_bwm_region_matched_support80_best6.json`
Shard: 1/1
Selected recordings: 28
Available recordings: 28
Skipped existing: 28
Failures: 0
Elapsed seconds: 0
Include wheel: `True`
Trial-window-only spikes: `False`
Window length: `1.0`

## Available

| session | probe | path |
|---|---|---|
| b182b754-3c3e-4942-8144-6ee790926b58 | probe01 | `data/brainsets/ibl_bwm/b182b754-3c3e-4942-8144-6ee790926b58_probe01.h5` |
| 3f71aa98-08c6-4e79-b4c8-00eae4f03eff | probe00 | `data/brainsets/ibl_bwm/3f71aa98-08c6-4e79-b4c8-00eae4f03eff_probe00.h5` |
| 16693458-0801-4d35-a3f1-9115c7e5acfd | probe00 | `data/brainsets/ibl_bwm/16693458-0801-4d35-a3f1-9115c7e5acfd_probe00.h5` |
| 4ecb5d24-f5cc-402c-be28-9d0f7cb14b3a | probe00 | `data/brainsets/ibl_bwm/4ecb5d24-f5cc-402c-be28-9d0f7cb14b3a_probe00.h5` |
| 4d8c7767-981c-4347-8e5e-5d5fffe38534 | probe01 | `data/brainsets/ibl_bwm/4d8c7767-981c-4347-8e5e-5d5fffe38534_probe01.h5` |
| 63c70ae8-4dfb-418b-b21b-f0b1e5fba6c9 | probe00 | `data/brainsets/ibl_bwm/63c70ae8-4dfb-418b-b21b-f0b1e5fba6c9_probe00.h5` |
| 5adab0b7-dfd0-467d-b09d-43cb7ca5d59c | probe00 | `data/brainsets/ibl_bwm/5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe00.h5` |
| a8a8af78-16de-4841-ab07-fde4b5281a03 | probe00 | `data/brainsets/ibl_bwm/a8a8af78-16de-4841-ab07-fde4b5281a03_probe00.h5` |
| 6899a67d-2e53-4215-a52a-c7021b5da5d4 | probe00 | `data/brainsets/ibl_bwm/6899a67d-2e53-4215-a52a-c7021b5da5d4_probe00.h5` |
| e1931de1-cf7b-49af-af33-2ade15e8abe7 | probe00 | `data/brainsets/ibl_bwm/e1931de1-cf7b-49af-af33-2ade15e8abe7_probe00.h5` |
| 6fb1e12c-883b-46d1-a745-473cde3232c8 | probe00 | `data/brainsets/ibl_bwm/6fb1e12c-883b-46d1-a745-473cde3232c8_probe00.h5` |
| 1e45d992-c356-40e1-9be1-a506d944896f | probe01 | `data/brainsets/ibl_bwm/1e45d992-c356-40e1-9be1-a506d944896f_probe01.h5` |
| b887df2c-bb9c-44c9-a9c0-538da87b2cab | probe00 | `data/brainsets/ibl_bwm/b887df2c-bb9c-44c9-a9c0-538da87b2cab_probe00.h5` |
| 5adab0b7-dfd0-467d-b09d-43cb7ca5d59c | probe01 | `data/brainsets/ibl_bwm/5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe01.h5` |
| a8a8af78-16de-4841-ab07-fde4b5281a03 | probe01 | `data/brainsets/ibl_bwm/a8a8af78-16de-4841-ab07-fde4b5281a03_probe01.h5` |
| a1782f4f-86b0-480c-a7f2-3d8f1ab482ab | probe00 | `data/brainsets/ibl_bwm/a1782f4f-86b0-480c-a7f2-3d8f1ab482ab_probe00.h5` |
| b9c205c3-feac-485b-a89d-afc96d9cb280 | probe00 | `data/brainsets/ibl_bwm/b9c205c3-feac-485b-a89d-afc96d9cb280_probe00.h5` |
| 88d24c31-52e4-49cc-9f32-6adbeb9eba87 | probe00 | `data/brainsets/ibl_bwm/88d24c31-52e4-49cc-9f32-6adbeb9eba87_probe00.h5` |
| 03063955-2523-47bd-ae57-f7489dd40f15 | probe01 | `data/brainsets/ibl_bwm/03063955-2523-47bd-ae57-f7489dd40f15_probe01.h5` |
| 63c70ae8-4dfb-418b-b21b-f0b1e5fba6c9 | probe01 | `data/brainsets/ibl_bwm/63c70ae8-4dfb-418b-b21b-f0b1e5fba6c9_probe01.h5` |
| 49e0ab27-827a-4c91-bcaa-97eea27a1b8d | probe01 | `data/brainsets/ibl_bwm/49e0ab27-827a-4c91-bcaa-97eea27a1b8d_probe01.h5` |
| 032ffcdf-7692-40b3-b9ff-8def1fc18b2e | probe00 | `data/brainsets/ibl_bwm/032ffcdf-7692-40b3-b9ff-8def1fc18b2e_probe00.h5` |
| 35eeb752-8f4f-4040-9714-ba0f5b7ccdfe | probe00 | `data/brainsets/ibl_bwm/35eeb752-8f4f-4040-9714-ba0f5b7ccdfe_probe00.h5` |
| 16693458-0801-4d35-a3f1-9115c7e5acfd | probe01 | `data/brainsets/ibl_bwm/16693458-0801-4d35-a3f1-9115c7e5acfd_probe01.h5` |
| 6f09ba7e-e3ce-44b0-932b-c003fb44fb89 | probe01 | `data/brainsets/ibl_bwm/6f09ba7e-e3ce-44b0-932b-c003fb44fb89_probe01.h5` |
| 41872d7f-75cb-4445-bb1a-132b354c44f0 | probe01 | `data/brainsets/ibl_bwm/41872d7f-75cb-4445-bb1a-132b354c44f0_probe01.h5` |
| b887df2c-bb9c-44c9-a9c0-538da87b2cab | probe01 | `data/brainsets/ibl_bwm/b887df2c-bb9c-44c9-a9c0-538da87b2cab_probe01.h5` |
| edd22318-216c-44ff-bc24-49ce8be78374 | probe00 | `data/brainsets/ibl_bwm/edd22318-216c-44ff-bc24-49ce8be78374_probe00.h5` |

## Cache Audit

# BrainSet S3 Cache Audit

Manifest: `manifests/ibl_bwm_region_matched_support80_best6.json`
Cache: `s3://rppfvo6ifn/brainsets/ibl_bwm`
Present: 28/28 (100.0%)

## Missing

none

## Present

| filename |
|---|
| `03063955-2523-47bd-ae57-f7489dd40f15_probe01.h5` |
| `032ffcdf-7692-40b3-b9ff-8def1fc18b2e_probe00.h5` |
| `16693458-0801-4d35-a3f1-9115c7e5acfd_probe00.h5` |
| `16693458-0801-4d35-a3f1-9115c7e5acfd_probe01.h5` |
| `1e45d992-c356-40e1-9be1-a506d944896f_probe01.h5` |
| `35eeb752-8f4f-4040-9714-ba0f5b7ccdfe_probe00.h5` |
| `3f71aa98-08c6-4e79-b4c8-00eae4f03eff_probe00.h5` |
| `41872d7f-75cb-4445-bb1a-132b354c44f0_probe01.h5` |
| `49e0ab27-827a-4c91-bcaa-97eea27a1b8d_probe01.h5` |
| `4d8c7767-981c-4347-8e5e-5d5fffe38534_probe01.h5` |
| `4ecb5d24-f5cc-402c-be28-9d0f7cb14b3a_probe00.h5` |
| `5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe00.h5` |
| `5adab0b7-dfd0-467d-b09d-43cb7ca5d59c_probe01.h5` |
| `63c70ae8-4dfb-418b-b21b-f0b1e5fba6c9_probe00.h5` |
| `63c70ae8-4dfb-418b-b21b-f0b1e5fba6c9_probe01.h5` |
| `6899a67d-2e53-4215-a52a-c7021b5da5d4_probe00.h5` |
| `6f09ba7e-e3ce-44b0-932b-c003fb44fb89_probe01.h5` |
| `6fb1e12c-883b-46d1-a745-473cde3232c8_probe00.h5` |
| `88d24c31-52e4-49cc-9f32-6adbeb9eba87_probe00.h5` |
| `a1782f4f-86b0-480c-a7f2-3d8f1ab482ab_probe00.h5` |
| `a8a8af78-16de-4841-ab07-fde4b5281a03_probe00.h5` |
| `a8a8af78-16de-4841-ab07-fde4b5281a03_probe01.h5` |
| `b182b754-3c3e-4942-8144-6ee790926b58_probe01.h5` |
| `b887df2c-bb9c-44c9-a9c0-538da87b2cab_probe00.h5` |
| `b887df2c-bb9c-44c9-a9c0-538da87b2cab_probe01.h5` |
| `b9c205c3-feac-485b-a89d-afc96d9cb280_probe00.h5` |
| `e1931de1-cf7b-49af-af33-2ade15e8abe7_probe00.h5` |
| `edd22318-216c-44ff-bc24-49ce8be78374_probe00.h5` |

## Missing Sweep Summary

No `runs/lso_csh_full_eval_shared_parent_shuffle/summary.md`, `within_summary.md`, or
`cross_summary.md` file was present when cleanup pushed artifacts. Treat this
cloud result as incomplete/non-evidence even if the pod exit status is 0.

## Provisioning Attempt Notes

Launch goal: run only the canonical `CSH_ZAD_019` shared-parent
true-vs-shuffled control with `FULL_EVAL_ON_BEST=1`, three seeds, and no new
held-out subjects.

Budget guard:

- user cap: $100
- A100 launch guard: 5,400 seconds max runtime, 300 seconds provisioning
- L4 fallback guard: 7,200 seconds max runtime, 300 seconds provisioning
- observed rates: $1.49/hr for A100 placements, $0.39/hr for L4 placement

Attempt 1:

- pod: `wprz1ze9ox8uvx`
- name: `anfm-csh-full-eval-20260604-195834`
- GPU request: `NVIDIA A100 80GB PCIe,NVIDIA A100-SXM4-80GB`
- datacenter: `ANY`
- rate: $1.49/hr
- outcome: RunPod assigned machine id `oqo2eflpgwbo`, but the pod never exposed
  machine details or a public IP. The 300-second provisioning guard terminated
  it before training started.

Attempt 2:

- datacenter `US-MO-1`: rejected by current RunPod API because that datacenter
  id is no longer valid.
- datacenter `US-IL-1`: rejected before pod creation because no matching A100
  capacity was available.
- pod: `8piygo34j6vdt0`
- name: `anfm-csh-full-eval-20260604-200451`
- GPU request: `NVIDIA A100-SXM4-80GB`
- datacenter: `ANY`
- rate: $1.49/hr
- outcome: RunPod again assigned machine id `oqo2eflpgwbo` with no runtime
  access. The pod was manually terminated before the full guard window.

Attempt 3:

- pod: `0tjka0eux9n54n`
- name: `anfm-csh-full-eval-l4-20260604-201016`
- GPU request: `NVIDIA L4`
- datacenter: `ANY`
- rate: $0.39/hr
- outcome: cheaper GPU fallback also received a machine id without runtime
  access, machine details, or a public IP. The hardened 300-second provisioning
  guard terminated the pod before training started.

Attempt 4:

- pod: `l999fy3799ni7b`
- name: `anfm-csh-centered-l4-20260604-203923`
- GPU request: `NVIDIA L4`
- datacenter: `ANY`
- rate: `$0.39/hr`
- output root: `runs/lso_csh_full_eval_centered_shared_parent_shuffle`
- result doc: `docs/lso_csh_full_eval_centered_shared_parent_shuffle_results.md`
- sweep env: `FULL_EVAL_ON_BEST=1, SAVE_DIAGNOSTICS=1, BEST_METRIC=full_eval_centered_auc`
- outcome: RunPod created the pod and assigned machine id `so5311pahl76`.
  Repeated status polls showed no public IP and no usable machine details, so
  the 300-second provisioning guard terminated it. S3/Git artifacts later
  showed that the container did run partially despite the status API: seed 0
  completed all three arms, seed 1 completed only the shared baseline, and the
  cleanup pushed `docs/lso_csh_full_eval_centered_shared_parent_shuffle_results.md`
  plus diagnostic JSONL files.

During cleanup, an unexpected active project pod
`9sb1b5aiqur37r` (`anfm-two-parent-compact-20260604-200502`) was visible and
was terminated to enforce the budget cap. Final post-cleanup preflight reported
`active_pods: 0`.

Attempts 1-3 produced no training evidence. Attempt 4 produced partial
evidence, but it is not a canonical three-seed result and the executable gate
failed: seed 0 had region-only centered AUC `0.517` vs shared `0.511`, full AUC
`0.505` vs shared `0.511`, and true-vs-shuffle paired improvement `0.513`
against the `0.550` threshold.

Follow-up attempt `jt36y9tajx4p5u` (`anfm-csh-centered-l4-20260604-205209`)
used the S3-log-aware polling guard and completed all three centered-selection
seeds. The canonical gate still failed with `n_passing_seeds=1/3`; see
`docs/lso_csh_full_eval_centered_shared_parent_shuffle_results.md` and
`docs/lso_csh_full_eval_centered_shared_parent_shuffle_gate.json`.

Next launch should wait for healthier RunPod runtime provisioning or use a
different cloud backend. Do not start more than one pod at a time, and keep the
`active_pods: 0` preflight gate before each paid attempt.
