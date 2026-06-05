# Next Benchmark/Control Options Audit

Ranks remaining no-spend branches after the current local audits. This is the planning gate before any new RunPod training.

- recommended next: `new manifest with prospective bidirectional support`
- closed branches: `18`
- decision: `no_local_training_trigger`
- GPU trigger: At least one local row on the proposed manifest must clear delta_vs_shuffle>=0, delta_vs_total>=0, target0>=0.55, target1>=0.55, and bidirectional_recording_fraction>=0.75 before training.

| priority | branch | status | next action |
|---:|---|---|---|
| 1 | new manifest with prospective bidirectional support | `recommended_next` | Do not launch GPU training from the projected support80 panel; its model-free family and feature-mode gates have no candidates. Redesign the target/control locally. |
| 85 | extreme-quantile behavioral target gate | `closed` | Do not train: the coarse root-region row beats shuffle across seeds, but target and recording bidirectionality do not remain stable. |
| 86 | wheel-derived target family gate | `closed` | Do not spend on the tested wheel targets; move to a prospectively supported manifest. |
| 87 | reaction-dynamics wheel targets | `closed` | Do not spend on reaction-dynamics wheel targets; the near miss fails true-vs-shuffle and does not replicate across feature modes. |
| 88 | cell-type prior target/control gate | `closed` | Do not spend on broad ABC cell-class prior channels; they do not pass the local bidirectional gate. |
| 89 | waveform target/control gate | `closed` | Do not spend on simple waveform-channel controls; they do not pass the local bidirectional gate. |
| 90 | local gate meta-failure synthesis | `closed` | Use the meta-audit redesign rule: require prospectively defined same-recording target0+target1 evidence before any GPU run. |
| 90 | recording bidirectionality prospectus | `closed` | Run the unchanged local gate on manifests/ibl_bwm_recording_bidirectionality_prospect_leads.json; treat any pass as a local redesign candidate, not a training trigger. |
| 90 | prospect-lead derived target validation | `closed` | Do not train on prospect-lead candidates; same-subject non-lead recordings do not validate them. |
| 90 | subject-stable local gate prospectus | `closed` | Do not train from the current subject-stable broad-anatomy branch; exact family gates remain negative. |
| 91 | behavior-inclusive cache rebuild | `closed` | Cache rebuild is complete; all matched recordings now expose wheel. Use the wheel-derived local target gate before any training. |
| 92 | direct cached-field derived targets | `closed` | Do not launch GPU training from contrast_strength, response_latency, or prior_engaged. |
| 93 | contextual cached trial-state targets | `closed` | Do not spend on contextual trial-sequence targets from the compact cache. |
| 94 | more feature-mode or l2 sweeps on shared broad anatomy | `closed` | Do not spend more local or GPU time on simple broad-anatomy feature/regularization repair. |
| 95 | narrow existing manifest further | `closed` | Do not keep shrinking the existing cache as the primary rescue path. |
| 96 | recording-subset selection from current artifacts | `closed` | Do not train on selected current recordings unless a new target/control first passes locally. |
| 97 | current shared-family target/control grid | `closed` | Do not rerun the same target/family grid without a new target/control definition. |
| 98 | alternative cached targets plus family aggregation | `closed` | Do not expect prior_side or feedback alone to rescue the signal under current controls. |
| 99 | source-target pair narrowing | `closed` | Do not run a paid source-target pair sweep without a new local gate pass. |

## Evidence

### new manifest with prospective bidirectional support
- current 28-recording manifest is feasible but not clean enough to pass the local gate
- local cached manifest candidate audit found 1 new candidate panels across 38 local recordings (local_expanded_candidate_ready_for_model_free_gate)
- external acquisition gap audit identifies 7 missing HDF5 recordings for 2 support-qualified subjects, projecting 31 recordings across 8 subjects
- strict iterative 8-recording manifest has 0 candidates and max bidir 0.250
- projected support80 shared-family gate has 0 candidates across 128 rows and max bidir 0.500
- projected support80 all-family feature-mode sweep has 0 candidates across 1280 rows, 4 feature modes, and max bidir 0.500
- local gate meta-failure audit has 0 candidates across 1924 rows; recording bidirectionality fails in 1919 rows
- recording bidirectionality prospectus found 18 prospect recordings from 262 bidirectional observations
- prospect-lead manifest has 18 recordings across 7 subjects with 0 missing local recordings
- subject-stable shuffle-seed sensitivity found 0 robust candidates; max positive seed fraction=0.4
- recording-subset replication selected zero stable validation rows
- GPU trigger: At least one local row on the proposed manifest must clear delta_vs_shuffle>=0, delta_vs_total>=0, target0>=0.55, target1>=0.55, and bidirectional_recording_fraction>=0.75 before training.

### extreme-quantile behavioral target gate
- extreme-quantile target family gate found 1 candidates across 175 rows and max bidir 1.000
- seed sensitivity found 0 robust candidates; max positive seed fraction=0.400
- cutoff sensitivity found 0 robust cutoffs; best cutoff=20/80 with 2/5 candidate seeds
- region specificity scan found 1 strict parent-region candidates across 79 regions
- region seed sensitivity found 0 robust candidates; max positive seed fraction=1.000
- GPU trigger: A candidate must pass the unchanged local gate and remain positive across multiple within-recording shuffle seeds before training.

### wheel-derived target family gate
- behavior-cache preflight has wheel in 28/28 matched recordings
- wheel target family gate has 0 candidates across 84 rows and max bidir 0.750
- GPU trigger: At least one local wheel row must clear delta_vs_shuffle>=0, delta_vs_total>=0, target0>=0.55, target1>=0.55, and bidirectional_recording_fraction>=0.75.

### reaction-dynamics wheel targets
- reaction-dynamics target family feature-mode sweep has 0 candidates across 336 rows, 4 feature modes, and max bidir 0.750
- best recording-centered near miss is wheel_reaction_latency/broad_named_anatomy/KS014: target0=0.667, target1=0.715, bidir=3/4, total delta +0.003, but shuffle delta -0.001
- GPU trigger: none

### cell-type prior target/control gate
- cell-type prior target/control gate has 0 candidates across 112 rows and max bidir 0.500
- best rows clear global target fractions but reach only 2/4 same-recording bidirectional support
- GPU trigger: none

### waveform target/control gate
- waveform target/control gate has 0 candidates across 84 rows and max bidir 0.500
- best depth/choice near miss clears global target fractions but reaches only 2/4 same-recording bidirectional support
- GPU trigger: none

### local gate meta-failure synthesis
- meta-audit aggregates 1924 rows from 11 artifacts with 0 candidates and 11 one-failure rows
- recording bidirectionality is the dominant blocker; it appears in 1919 rows
- GPU trigger: none

### recording bidirectionality prospectus
- prospectus aggregates 8544 per-recording observations with 262 bidirectional observations across 32 recordings
- candidate recordings are only design leads, not a GPU trigger
- prospect-lead manifest materializes 18 recordings across 7 subjects
- GPU trigger: none

### prospect-lead derived target validation
- prospect-lead derived gate found 3 candidates across 84 rows
- recording-centered validation found 0 validated candidates; 3 prospect candidates were single-recording and 3 were subset-only
- feature-mode validation found 0 validated candidates from 4 prospect candidates across 4 feature modes
- subject-stability audit found 0 same-subject stable candidates and 4 candidates with same-subject non-lead failure
- GPU trigger: none

### subject-stable local gate prospectus
- prospectus found 5 subject-stable rows, 0 candidates, and 1 one-failure rows
- subject-stable failures are shuffle=5, total_baseline=4
- shuffle-seed sensitivity found 0 robust candidates across 5 subject-stable near misses
- broad-anatomy mechanism audit found 9 contribution candidates but 0 exact family-gate candidates
- GPU trigger: none

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
