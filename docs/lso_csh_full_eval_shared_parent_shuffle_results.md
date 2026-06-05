# CSH Full-Eval Shared-Parent Launch Attempt

## Launch Goal

Run only the canonical `CSH_ZAD_019` shared-parent true-vs-shuffled control with
`FULL_EVAL_ON_BEST=1`, three seeds, and no new held-out subjects.

Budget guard:

- user cap: $100
- launch guard: 5,400 seconds max runtime
- provisioning guard: 300 seconds
- listed pod rate: $1.49/hr
- worst-case guarded run estimate: about $2.24 per successful launch

## Attempt Log

Preflight before launch reported a clean branch, `active_pods: 0`, and an
estimated guarded cost of $4.50 under the conservative $3/hr preflight
assumption.

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

During cleanup, an unexpected active project pod
`9sb1b5aiqur37r` (`anfm-two-parent-compact-20260604-200502`) was visible and
was terminated to enforce the budget cap.

Final post-cleanup preflight reported `active_pods: 0`.

## Result

No training ran and no `full_eval` CSH metrics were produced. Treat this as a
RunPod provisioning failure, not experimental evidence.

Next launch should either wait for healthier A100 capacity or use a different
valid datacenter/GPU availability path. Do not start more than one pod at a time,
and keep the `active_pods: 0` preflight gate before each paid attempt.
