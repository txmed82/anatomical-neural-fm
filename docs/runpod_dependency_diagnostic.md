# Cloud Phase 3-5 Results

Date: 2026-06-04T23:10:44Z

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

## Diagnostic Result

This was a launcher dependency diagnostic, not a training sweep. The missing
training summary is expected and is not evidence for or against the
two-holdout anatomical-control experiment.

The pod reached dependency setup, completed `uv sync --no-dev`, uploaded its
S3 log, and confirmed the runtime environment:

- `torch`, `boto3`, `h5py`, `numpy`, `one`, `iblatlas`, and `temporaldata`
  were importable.
- `torch` reported CUDA available with one visible device.
- The 80 GB container disk had about 67 GB available after dependency setup.

The diagnostic also exposed the launcher cleanup failure: the pod-side RunPod
DELETE request returned HTTP 403 after the diagnostic completed, so the pod
could remain in desired `RUNNING` state and restart. The local poller was then
hardened to watch the S3 diagnostic log for the completion marker and terminate
diagnostic pods from the local API instead of relying only on pod-side
self-deletion.
