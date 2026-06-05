# Next Benchmark/Control Options Audit

Ranks remaining no-spend branches after the current local audits. This is the planning gate before any new RunPod training.

- recommended next: `new benchmark/control target definition`
- closed branches: `6`
- decision: `new_benchmark_control_definition_required`
- GPU trigger: At least one local row must clear delta_vs_shuffle>=0, delta_vs_total>=0, target0>=0.55, target1>=0.55, and bidirectional_recording_fraction>=0.75.

| priority | branch | status | next action |
|---:|---|---|---|
| 1 | new benchmark/control target definition | `recommended_next` | Define a prospectively balanced target/control that is not just another feature transform of the four cached trial targets. Before training, run the same model-free true-vs-shuffle, total-baseline, global target, and same-recording bidirectional gate. |
| 2 | new manifest with prospective bidirectional support | `secondary_after_new_target` | Only build or fetch more recordings after a target/control proposal defines which recordings should prospectively contain target0+target1 evidence. |
| 90 | more feature-mode or l2 sweeps on shared broad anatomy | `closed` | Do not spend more local or GPU time on simple broad-anatomy feature/regularization repair. |
| 91 | narrow existing manifest further | `closed` | Do not keep shrinking the existing cache as the primary rescue path. |
| 92 | recording-subset selection from current artifacts | `closed` | Do not train on selected current recordings unless a new target/control first passes locally. |
| 93 | current shared-family target/control grid | `closed` | Do not rerun the same target/family grid without a new target/control definition. |
| 94 | alternative cached targets plus family aggregation | `closed` | Do not expect prior_side or feedback alone to rescue the signal under current controls. |
| 95 | source-target pair narrowing | `closed` | Do not run a paid source-target pair sweep without a new local gate pass. |

## Evidence

### new benchmark/control target definition
- current cached trial targets and shared-family controls all fail strict same-recording bidirectionality
- strict symmetric gate has 0 candidates and 0 one-recording-short global-clear rows
- threshold sensitivity only finds default-target candidates when bidirectional support is relaxed to 0.25 (3 candidates)
- GPU trigger: At least one local row must clear delta_vs_shuffle>=0, delta_vs_total>=0, target0>=0.55, target1>=0.55, and bidirectional_recording_fraction>=0.75.

### new manifest with prospective bidirectional support
- current 28-recording manifest is feasible but not clean enough to pass the local gate
- strict iterative 8-recording manifest has 0 candidates and max bidir 0.250
- recording-subset replication selected zero stable validation rows
- GPU trigger: Same local gate as above, measured on the proposed manifest before training.

### more feature-mode or l2 sweeps on shared broad anatomy
- shared broad-anatomy repair sweep has 0 candidates, max bidir 2, and max min target margin -0.010
- GPU trigger: none

### narrow existing manifest further
- iterative manifest gate has 0 candidates and max bidir recordings 1
- 2-subject manifest is too narrow for the intended cross-animal demo
- GPU trigger: none

### recording-subset selection from current artifacts
- recording replication audit selected 3 rows and replicated 0
- GPU trigger: none

### current shared-family target/control grid
- shared-family gate has 0 candidates across 112 rows
- top rows are one-sided or fail baseline controls
- GPU trigger: none

### alternative cached targets plus family aggregation
- prior_side family gate candidates=0; feedback family gate candidates=0
- GPU trigger: none

### source-target pair narrowing
- family source-target pair gate candidates=0
- GPU trigger: none
