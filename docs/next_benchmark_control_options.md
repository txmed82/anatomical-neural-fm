# Next Benchmark/Control Options Audit

Ranks remaining no-spend branches after the current local audits. This is the planning gate before any new RunPod training.

- recommended next: `new manifest with prospective bidirectional support`
- closed branches: `10`
- decision: `no_local_training_trigger`
- GPU trigger: At least one local row on the proposed manifest must clear delta_vs_shuffle>=0, delta_vs_total>=0, target0>=0.55, target1>=0.55, and bidirectional_recording_fraction>=0.75 before training.

| priority | branch | status | next action |
|---:|---|---|---|
| 1 | new manifest with prospective bidirectional support | `recommended_next` | The local cache expansion does not create a supported panel; build or fetch the external support80 missing-HDF5 set, then rerun the local manifest candidate audit and the same model-free gate before training. |
| 86 | wheel-derived target family gate | `closed` | Do not spend on the tested wheel targets; move to a prospectively supported manifest. |
| 87 | behavior-inclusive cache rebuild | `closed` | Cache rebuild is complete; all matched recordings now expose wheel. Use the wheel-derived local target gate before any training. |
| 88 | direct cached-field derived targets | `closed` | Do not launch GPU training from contrast_strength, response_latency, or prior_engaged. |
| 89 | contextual cached trial-state targets | `closed` | Do not spend on contextual trial-sequence targets from the compact cache. |
| 90 | more feature-mode or l2 sweeps on shared broad anatomy | `closed` | Do not spend more local or GPU time on simple broad-anatomy feature/regularization repair. |
| 91 | narrow existing manifest further | `closed` | Do not keep shrinking the existing cache as the primary rescue path. |
| 92 | recording-subset selection from current artifacts | `closed` | Do not train on selected current recordings unless a new target/control first passes locally. |
| 93 | current shared-family target/control grid | `closed` | Do not rerun the same target/family grid without a new target/control definition. |
| 94 | alternative cached targets plus family aggregation | `closed` | Do not expect prior_side or feedback alone to rescue the signal under current controls. |
| 95 | source-target pair narrowing | `closed` | Do not run a paid source-target pair sweep without a new local gate pass. |

## Evidence

### new manifest with prospective bidirectional support
- current 28-recording manifest is feasible but not clean enough to pass the local gate
- local cached manifest candidate audit found 0 new candidate panels across 31 local recordings (local_expansion_support_gap)
- external acquisition gap audit identifies 7 missing HDF5 recordings for 2 support-qualified subjects, projecting 31 recordings across 8 subjects
- strict iterative 8-recording manifest has 0 candidates and max bidir 0.250
- recording-subset replication selected zero stable validation rows
- GPU trigger: At least one local row on the proposed manifest must clear delta_vs_shuffle>=0, delta_vs_total>=0, target0>=0.55, target1>=0.55, and bidirectional_recording_fraction>=0.75 before training.

### wheel-derived target family gate
- behavior-cache preflight has wheel in 28/28 matched recordings
- wheel target family gate has 0 candidates across 84 rows and max bidir 0.750
- GPU trigger: At least one local wheel row must clear delta_vs_shuffle>=0, delta_vs_total>=0, target0>=0.55, target1>=0.55, and bidirectional_recording_fraction>=0.75.

### behavior-inclusive cache rebuild
- current cached trial targets and shared-family controls all fail strict same-recording bidirectionality
- direct derived cached-field target gate has 0 candidates and max bidir 0.750
- contextual trial-state target gate has 0 candidates and max bidir 0.500
- behavior-cache preflight has wheel in 28/28 matched recordings
- strict symmetric gate has 0 candidates and 0 one-recording-short global-clear rows
- threshold sensitivity only finds default-target candidates when bidirectional support is relaxed to 0.25 (3 candidates)
- GPU trigger: At least one local row must clear delta_vs_shuffle>=0, delta_vs_total>=0, target0>=0.55, target1>=0.55, and bidirectional_recording_fraction>=0.75.

### direct cached-field derived targets
- derived target family gate has 0 candidates across 84 rows
- nearest response_latency row reaches 3/4 bidirectional recordings but fails true-vs-shuffle
- GPU trigger: none

### contextual cached trial-state targets
- contextual target family gate has 0 candidates across 84 rows and max bidir 0.500
- post_error, prior_block_switch, and prior_block_late do not clear the local gate
- GPU trigger: none

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
