# Current Anatomy-Transfer Experiment State

Decision: `no_paid_broadening_without_new_mechanism`

## Strict Gate Runs

| experiment | holdout | gate | centered_delta | paired_true_vs_shuffle | specificity_gap | target0 | target1 | sign_flip_p | outcome | source |
|---|---|---|---:|---:|---:|---:|---:|---:|---|---|
| CSH centered original | CSH_ZAD_019 | False | +0.006 | 0.536 | -0.016 | n/a | n/a | 0.062 | fail: small centered delta, paired gate, specificity, sign-flip | `docs/lso_csh_full_eval_centered_anatomy_specific_gate.json` |
| NR_0019 centered replication | NR_0019 | False | +0.012 | 0.493 | +0.000 | n/a | n/a | 0.500 | fail: paired gate, specificity, sign-flip | `docs/lso_nr0019_full_eval_centered_anatomy_specific_gate.json` |
| CSH target-balanced | CSH_ZAD_019 | False | +0.009 | 0.516 | +0.051 | n/a | n/a | 0.125 | fail: small centered delta, paired gate, sign-flip | `docs/lso_csh_target_balanced_anatomy_specific_gate.json` |
| CSH recording-centered loss | CSH_ZAD_019 | False | -0.050 | 0.451 | -0.092 | n/a | n/a | 1.000 | fail: small centered delta, paired gate, specificity, sign-flip | `docs/lso_csh_recording_centered_loss_anatomy_specific_gate.json` |
| CSH within-recording shuffle | CSH_ZAD_019 | False | +0.001 | 0.448 | -0.103 | n/a | n/a | 0.250 | fail: small centered delta, paired gate, specificity, sign-flip | `docs/lso_csh_within_recording_shuffle_anatomy_specific_gate.json` |
| CSH recording-centered gate pilot | CSH_ZAD_019 | False | +0.001 | 0.448 | -0.103 | n/a | n/a | 0.250 | fail: small centered delta, paired gate, specificity, sign-flip | `docs/lso_csh_recording_centered_gate_pilot_anatomy_specific_gate.json` |
| CSH pairwise-rank objective pilot | CSH_ZAD_019 | False | -0.014 | 0.552 | +0.103 | 1.000 | 0.000 | 0.562 | fail: small centered delta, target1, sign-flip | `docs/lso_csh_pairwise_rank_pilot_anatomy_specific_gate.json` |
| CSH pairwise-rank centered-BCE pilot | CSH_ZAD_019 | False | -0.016 | 0.486 | +0.013 | 0.354 | 0.650 | 1.000 | fail: small centered delta, paired gate, target0, sign-flip | `docs/lso_csh_pairwise_rank_centered_bce_pilot_anatomy_specific_gate.json` |

## Fixed-Slice Runs

| experiment | holdout | true_delta | shuffle_delta | true_minus_shuffle | true_positive | shuffle_positive | outcome | source |
|---|---|---:|---:|---:|---:|---:|---|---|
| NYU-12 fixed carrier slice | NYU-12 | +0.013 | +0.020 | -0.007 | 2/3 | 3/3 | shuffle >= true | `docs/lso_nyu12_parent_slice_results.md` |
| SWC_038 stricter carrier slice | SWC_038 | -0.004 | +0.019 | -0.023 | 0/2 | 2/2 | shuffle >= true | `docs/lso_swc038_parent_slice_results.md` |

## Decision

No current strict-gate artifact supports paid broadening. The later recording-matched controls show the CSH true-region advantage is much smaller than the original sampled-eval signal, and both fixed carrier slice attempts let shuffled labels match or beat true labels.

Next mechanism: The bidirectional target-class gate and explicit recording-local AUC surrogate are now implemented. The next no-spend task is local objective debugging that can satisfy target0, target1, and recording-local AUC checks before any more paid broadening.

## Mechanism Audit Follow-Up

`docs/csh_mechanism_audit.md` performs that saved-artifact audit on the
recording-centered gate pilot. It does not find a transferable anatomical
mechanism:

- global paired true-vs-shuffle remains `0.448`
- specificity gap is `-0.103`
- carrier-parent embeddings are nearly identical between true and shuffled controls, with mean carrier cosine `0.992`
- carrier-rich negative recordings: `4`

Updated mechanism decision: no paid run is justified until the objective itself forces target-aware true-vs-shuffle separation. Region/subject selection and embedding inspection did not reveal a mechanism that the current controls can validate.

## Pairwise-Rank Objective Pilot

`docs/lso_csh_pairwise_rank_pilot_results.md` ran the implemented
`recording_pairwise_rank` objective on a one-seed L4 RunPod pilot. It improved
the global paired true-vs-shuffle check to `0.552`
and the specificity gap to `+0.103`,
so the objective change did move the right target-aware paired metric.

The strict anatomy-specific gate still failed:

- centered true-minus-shuffle delta: `-0.014`
- paired true-vs-shuffle: `0.552`
- specificity gap: `+0.103`
- recording sign-flip p-value: `0.562`

Updated decision before the mismatch audit: possible mechanism candidate, not demo evidence. Do not broaden yet; require a diagnostic that separates bidirectional target-aware ranking from one-direction probability shifts.

Pairwise mismatch audit: `docs/lso_csh_pairwise_rank_pilot_mismatch.md`
classifies the paired improvement as `paired_metric_explained_by_downward_shift`.
Raw probabilities moved downward on `1.000`
of paired trials; target-0 true-class probability improved on
`1.000`
of trials while target-1 improved on
`0.000`.

Next candidate objective: `recording_pairwise_rank_centered_bce`, which keeps the recording-local pairwise rank term but adds recording-centered BCE so a one-direction probability shift is not mistaken for anatomical ranking evidence.

Updated decision after mismatch audit: the scalar paired metric should not be used as a success gate. Require bidirectional target-class improvement and positive recording-local AUC against the shuffled control.

## Pairwise-Rank Centered-BCE Pilot

`docs/lso_csh_pairwise_rank_centered_bce_pilot_results.md` tested the
`recording_pairwise_rank_centered_bce` objective. It removed the previous
all-trial downward probability shift but did not produce anatomical transfer.

- centered true-minus-shuffle delta: `-0.016`
- paired true-vs-shuffle: `0.486`
- specificity gap: `+0.013`
- recording sign-flip p-value: `1.000`
- mechanism decision: `no_mechanism_found`
- mismatch decision: `paired_metric_not_recording_rank_stable`
- target0 true-class improved: `0.354`
- target1 true-class improved: `0.650`
- mechanism paired true-vs-shuffle: `0.486`

Updated decision: stop paid one-off objective variants for now. Use the implemented bidirectional gate and `recording_local_auc_surrogate` only for local objective debugging until a candidate satisfies target0, target1, and recording-local AUC checks.

## Local AUC-Surrogate Probe

`scripts/run_local_objective_probe.py` runs a no-spend tiny CPU probe with
deterministic held-out predictions and immediate strict-gate/mismatch audits.
The first probe used `recording_local_auc_surrogate` for two CPU steps.

- gate pass: `False`
- centered true-minus-shuffle delta: `-0.005`
- paired true-vs-shuffle: `0.494`
- target0 true-class improved: `0.556`
- target1 true-class improved: `0.419`
- positive recordings: `2/4`
- mismatch decision: `paired_metric_not_recording_rank_stable`
- true-minus-shuffle AUC: `-0.009`

Decision: reject this objective configuration locally. It does not justify a RunPod launch because it fails target1, centered AUC, and recording support.

## Local Probe Matrix

These CPU-only probes are the current promotion gate for objective and sampling variants. A candidate should pass the strict gate locally before any new RunPod spend.

| probe | gate | centered_delta | paired_true_vs_shuffle | specificity_gap | target0 | target1 | recordings | mismatch | outcome |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| local AUC surrogate | False | -0.005 | 0.494 | +0.030 | 0.556 | 0.419 | 2/4 | `paired_metric_not_recording_rank_stable` | reject: centered AUC, target1, recording support, mismatch |
| local recording-centered BCE | False | -0.005 | 0.494 | +0.029 | 0.557 | 0.416 | 2/4 | `paired_metric_not_recording_rank_stable` | reject: centered AUC, target1, recording support, mismatch |
| local rank + centered BCE | False | -0.005 | 0.494 | +0.030 | 0.556 | 0.419 | 2/4 | `paired_metric_not_recording_rank_stable` | reject: centered AUC, target1, recording support, mismatch |
| local AUC surrogate target-balanced | False | -0.005 | 0.502 | +0.039 | 0.580 | 0.406 | 2/4 | `paired_metric_not_recording_rank_stable` | reject: centered AUC, target1, recording support, mismatch |

Decision: all current tiny local variants are rejected for cloud promotion. They repeatedly improve target-0 more than target-1, lose centered true-vs-shuffle AUC, or fail recording support. The next no-spend step is to redesign the sampler/objective so both target classes improve within recordings before any paid run.

## Batch Sampling Contrast Audit

`docs/csh_batch_sampling_contrast_audit.md` checks whether samplers create
same-recording target-0/target-1 pairs before training. This is the minimum
condition for recording-local ranking losses to be active.

| sampler | target1_fraction | rankable_batch_fraction | mean_rankable_pairs | same_recording_adjacent_pairs |
|---|---:|---:|---:|---:|
| uniform | 0.477 | 0.022 | 0.022 | 0.022 |
| target_balanced | 0.500 | 0.040 | 0.040 | 0.040 |
| recording_target_balanced | 0.500 | 1.000 | 1.000 | 1.000 |

Interpretation: `recording_target_balanced` makes the recording-local rank loss active in every audited batch, while uniform and target-balanced sampling rarely produce same-recording contrast. Since the local probe matrix still fails under `recording_target_balanced`, the next failure is not pair availability; it is the anatomy/control signal or objective itself.

## Model-Free Region Signal Audit

`docs/csh_model_free_region_signal_audit.md` removes the transformer and
tests closed-form ridge classifiers on trial-level parent-region spike counts.

| feature_set | train_AUC | eval_AUC | eval_centered_AUC |
|---|---:|---:|---:|
| total_spikes | 0.503 | 0.555 | 0.553 |
| region_true | 0.597 | 0.499 | 0.487 |
| region_shuffle | 0.601 | 0.479 | 0.538 |

- true-minus-shuffle centered AUC: `-0.052`
- true-minus-total centered AUC: `-0.066`
- paired target0 improved vs shuffle: `0.338`
- paired target1 improved vs shuffle: `0.703`
- positive recordings vs shuffle: `1/4`
- decision: `no_model_free_true_region_advantage`

Interpretation: the current parent-region spike-count representation does not show model-free anatomical transfer for CSH. True region labels are worse than shuffled labels on recording-centered AUC and worse than a total-spike-count baseline, so the next no-spend step should redesign the anatomical feature/control target rather than spend on another neural model run.

## Model-Free Single-Region Candidate Scan

`docs/csh_model_free_region_candidate_scan.md` scans each parent region as a
single-feature ridge model against within-recording shuffled labels and the
total-spike baseline.

Candidates passing the strict local gate: `0`

| region | outcome | centered_AUC | delta_vs_shuffle | delta_vs_total | target0 | target1 | recordings | eval_nonzero |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| IB | reject: target0 | 0.728 | +0.300 | +0.175 | 0.275 | 0.703 | 1/4 | 0.285 |
| MBmot | reject: target1 | 0.645 | +0.226 | +0.092 | 0.820 | 0.219 | 1/4 | 0.285 |
| BS | reject: target0 | 0.672 | +0.225 | +0.119 | 0.015 | 0.991 | 1/4 | 0.285 |
| LZ | reject: target0 | 0.612 | +0.174 | +0.059 | 0.114 | 0.913 | 0/4 | 0.216 |
| RSPd | reject: target1 | 0.637 | +0.173 | +0.084 | 0.951 | 0.070 | 1/4 | 0.282 |
| CA | reject: target0 | 0.680 | +0.157 | +0.127 | 0.320 | 0.721 | 2/4 | 0.501 |
| DG | reject: target0 | 0.700 | +0.126 | +0.147 | 0.285 | 0.718 | 2/4 | 0.501 |
| VENT | reject: target0 | 0.578 | +0.119 | +0.025 | 0.230 | 0.800 | 0/4 | 0.216 |

Interpretation: no individual parent region is strong enough to promote. The best evaluable regions beat shuffle and total-spike baselines only in one target direction or too few recordings. The next no-spend feature step should test predefined aggregate region families or a different conserved target, not a GPU model run.

## Model-Free Region-Family Candidate Scan

`docs/csh_model_free_region_family_scan.md` scans predefined aggregate
region families as one-feature ridge models against within-recording
shuffled labels and the total-spike baseline.

Candidates passing the strict local gate: `0`

| family | outcome | centered_AUC | delta_vs_shuffle | delta_vs_total | target0 | target1 | recordings | eval_nonzero |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| basal_ganglia | reject: target1 | 0.607 | +0.100 | +0.157 | 1.000 | 0.000 | 1/4 | 0.499 |
| brainstem_interbrain | reject: target0 | 0.572 | +0.035 | +0.122 | 0.036 | 0.972 | 1/4 | 0.501 |
| cortical_retrosplenial | reject: target1 | 0.548 | +0.015 | +0.098 | 0.890 | 0.146 | 1/4 | 0.567 |
| hippocampal_formation | reject: target0 | 0.582 | +0.010 | +0.132 | 0.305 | 0.709 | 2/4 | 0.784 |
| cortical_sensorimotor | reject: shuffle | 0.587 | +0.008 | +0.137 | 0.701 | 0.282 | 1/4 | 0.433 |
| broad_named_anatomy | reject: shuffle | 0.451 | +0.003 | +0.001 | 0.698 | 0.362 | 2/4 | 1.000 |
| fiber_tracts | reject: shuffle | 0.551 | +0.002 | +0.101 | 0.507 | 0.481 | 1/4 | 1.000 |
| thalamic | reject: shuffle | 0.530 | -0.017 | +0.080 | 0.381 | 0.581 | 0/4 | 1.000 |

Interpretation: predefined region-family aggregates also fail the model-free promotion gate. The evidence now argues against spending on another CSH parent-region model variant. The next branch should be an alternative conserved target or a larger matched-region manifest audit.

## Alternative Target: Choice

The same model-free gates were rerun with `--target-mode choice` to test
whether a different behavioral target exposes anatomical transfer.

| feature_set | train_AUC | eval_AUC | eval_centered_AUC |
|---|---:|---:|---:|
| total_spikes | 0.518 | 0.456 | 0.389 |
| region_true | 0.636 | 0.477 | 0.480 |
| region_shuffle | 0.639 | 0.540 | 0.566 |

- true-minus-shuffle centered AUC: `-0.086`
- true-minus-total centered AUC: `+0.091`
- paired target0 improved vs shuffle: `0.807`
- paired target1 improved vs shuffle: `0.200`
- positive recordings vs shuffle: `2/4`
- full-region decision: `no_model_free_true_region_advantage`
- single-region candidates: `0`
- region-family candidates: `0`

Interpretation: `choice` does not rescue the CSH parent-region branch. Shuffled parent labels still beat true labels on recording-centered AUC, and the single-region/family scans find no promotable candidate.

## Matched-Region Cache Readiness

`docs/matched_region_cache_audit.md` audits the persistent S3 cache for the
48-recording matched-region manifest. This is the next gate before any
larger matched-region training attempt.

- present: `47/48` (`97.9%`)
- missing recording: `1`
- shards with missing recordings: `1`
- missing-only manifest: `manifests/ibl_bwm_region_matched_candidates_missing_s3.json` (1 recording, 1 subject)

| shard | recordings | present | missing |
|---:|---:|---:|---:|
| 3 | 2 | 1 | 1 |

Decision: do not launch training. Replace or drop the single failed recording, then rerun the matched-region support scorer and require the 80% held-out unit-support gate before any seed sweep.

## Matched-Region Support Scoring

Region support has been scored for the S3-present cache panel. Metadata-only
scoring is a planning gate; HDF5 scoring is the stronger pre-training check.

| manifest | recordings | subjects | support80 subjects | min support |
|---|---:|---:|---:|---:|
| `manifests/ibl_bwm_region_matched_candidates_s3_present_scored.json` | 47 | 12 | 8/12 | 66.6% |
| `manifests/ibl_bwm_region_matched_candidates_s3_present_support80.json` | 28 | 7 | 6/7 | 65.8% |
| `manifests/ibl_bwm_region_matched_candidates_s3_present_support80_hdf5_scored.json` | 28 | 7 | 6/7 | 65.8% |
| `manifests/ibl_bwm_region_matched_candidates_s3_present_support80_hdf5_iterative_pass.json` | 8 | 2 | 2/2 | 88.5% |

Decision: the HDF5-confirmed 28-recording panel is close but not clean at `6/7` support80 subjects, while the strict iterative all-pass filter collapses to 2 subjects. Do not claim a clean broad benchmark from this panel. Treat `SWC_043` as a known weak-support holdout in any bounded training gate, or run another no-spend/model-free screen before spending.

## Manifest Target/Anatomy Feasibility Audit

`docs/manifest_target_anatomy_feasibility.md` checks whether current
HDF5-backed manifests have balanced within-recording trials for each
target mode and enough shared anatomical family support for a benchmark
redesign.

| manifest | recordings | subjects | promotable targets | shared families | decision |
|---|---:|---:|---|---:|---|
| support80_hdf5_scored | 28 | 7 | choice, stimulus_side, feedback, prior_side | 4 | `manifest_has_target_and_family_feasibility` |
| support80_hdf5_iterative_pass | 8 | 2 | choice, stimulus_side, feedback, prior_side | 7 | `manifest_has_target_and_family_feasibility` |

Decision: the current full matched manifest is feasible enough for another local target/control redesign. The next branch should focus on specific shared families such as thalamic, hippocampal formation, and fiber tracts under the same recording-bidirectional gate, not on GPU training or recording-subset narrowing.

## Local Cached Manifest Candidate Audit

`docs/local_cached_manifest_candidates.md` tests whether the extra
locally cached recordings create a better prospective manifest before
any new data fetch or GPU launch.

- local recordings: `38`
- local subjects: `11`
- candidate panels: `2`
- new candidate panels: `1`
- best panel: `external_support80_projected_hdf5`
- decision: `local_expanded_candidate_ready_for_model_free_gate`

| panel | recordings | subjects | passing target/family rows | decision |
|---|---:|---:|---:|---|
| external_support80_projected_hdf5 | 31 | 8 | 4 | `candidate_panel_has_prospective_support` |
| current_support80_hdf5 | 28 | 7 | 4 | `candidate_panel_has_prospective_support` |
| all_local_cached | 38 | 11 | 0 | `candidate_panel_support_gap` |
| local_cached_min2_recordings_per_subject | 37 | 10 | 0 | `candidate_panel_support_gap` |

Decision: the extra local recordings add MFD_08/MFD_09 coverage, but the expanded panels fail the prospective per-subject target/family support floor. The next manifest branch needs a broader external selection rule or a different target/control definition, not a GPU run on the local expansion.

## External Manifest Acquisition Gap Audit

`docs/external_manifest_acquisition_gap.md` compares the broader
S3-present metadata-scored manifest against local HDF5 coverage.

- broad manifest recordings: `47`
- broad manifest subjects: `12`
- local HDF5 recordings in broad manifest: `28`
- support-qualified subjects: `8`
- support-qualified subjects missing HDF5: `2`
- missing HDF5 recordings for qualified subjects: `7`
- projected manifest: `31` recordings, `8` subjects
- decision: `external_support80_acquisition_candidate`

| subject | support | broad recs | local HDF5 | missing HDF5 | qualified |
|---|---:|---:|---:|---:|---|
| CSHL045 | 0.852 | 4 | 0 | 4 | True |
| ZFM-01577 | 0.841 | 3 | 0 | 3 | True |
| KS014 | 1.000 | 4 | 4 | 0 | True |
| MFD_06 | 0.998 | 4 | 4 | 0 | True |
| NYU-12 | 0.969 | 4 | 4 | 0 | True |
| SWC_038 | 0.916 | 4 | 4 | 0 | True |
| CSH_ZAD_019 | 0.900 | 4 | 4 | 0 | True |
| NR_0019 | 0.846 | 4 | 4 | 0 | True |

Decision: this is a data-acquisition trigger, not a training trigger. The concrete next set is seven missing HDF5 recordings for CSHL045 and ZFM-01577; after acquiring them, rerun the local manifest and model-free gates before any GPU run.

## Shared-Family Target/Control Gate

`docs/shared_family_target_control_gate.md` tests the feasible shared
families across all four target modes with the same model-free
true-vs-shuffled and recording-bidirectional promotion gate.

- rows: `112`
- candidates: `0`
- positive centered-delta rows: `55`
- max bidirectional recordings: `2`
- max bidirectional recording fraction: `0.500`
- decision: `no_shared_family_target_candidate`

| target | family | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs |
|---|---|---|---|---:|---:|---:|---:|---:|
| choice | broad_named_anatomy | SWC_043 | reject: shuffle | +0.008 | -0.160 | 0.534 | 0.610 | 2/4 |
| feedback | broad_named_anatomy | NYU-12 | reject: shuffle | -0.002 | -0.008 | 0.540 | 0.554 | 2/4 |
| choice | fiber_tracts | CSH_ZAD_019 | reject: recording bidirectionality | +0.199 | +0.221 | 0.558 | 0.614 | 1/4 |
| stimulus_side | thalamic | MFD_06 | reject: target0 | +0.179 | +0.269 | 0.089 | 0.930 | 1/4 |

Decision: shared-family target/control narrowing does not yet produce a promotable local signal. The best row has real centered deltas and global bidirectional target support, but fails same-recording support at `1/4`; do not launch GPU training from this branch.

## Shared-Family Near-Miss Mechanism

`docs/shared_family_choice_fiber_csh_near_miss.md` decomposes the
strongest shared-family row, `choice` + `fiber_tracts` on `CSH_ZAD_019`,
by held-out recording.

- centered delta vs shuffle: `+0.199`
- centered delta vs total: `+0.221`
- global target0: `0.558`
- global target1: `0.614`
- bidirectional recordings: `1/4`
- target0-positive recordings: `1/4`
- target1-positive recordings: `4/4`
- decision: `one_sided_target1_recording_effect`

Decision: this large-delta near miss is not a training trigger. It is recording-local target1 support with target0 clearing in only one recording, so a neural run would likely amplify the same one-sided artifact rather than demonstrate bidirectional anatomical transfer.

## Shared Broad-Anatomy Repair Sweep

`docs/shared_broad_anatomy_repair_sweep.md` reruns the two nearest
shared broad-anatomy misses across local feature transforms and ridge
regularization values.

- rows: `24`
- candidates: `0`
- max bidirectional recordings: `2`
- max min target margin: `-0.010`
- max centered delta vs shuffle: `+0.078`
- decision: `no_shared_broad_anatomy_repair_candidate`

| target | holdout | feature | l2 | missing | delta shuffle | delta total | targets | bidir recs |
|---|---|---|---:|---|---:|---:|---|---:|
| feedback | NYU-12 | recording_centered | 1 | shuffle_delta, total_delta, target0, recording_bidirectionality | -0.002 | -0.008 | 0.540/0.554 | 2/3 |
| feedback | NYU-12 | recording_centered | 10 | shuffle_delta, total_delta, target0, recording_bidirectionality | -0.002 | -0.008 | 0.540/0.554 | 2/3 |
| feedback | NYU-12 | recording_centered | 100 | shuffle_delta, total_delta, target0, recording_bidirectionality | -0.002 | -0.008 | 0.540/0.554 | 2/3 |
| choice | SWC_043 | recording_centered | 1 | total_delta, target0, recording_bidirectionality | +0.008 | -0.160 | 0.534/0.610 | 2/3 |
| choice | SWC_043 | recording_centered | 10 | total_delta, target0, recording_bidirectionality | +0.008 | -0.160 | 0.534/0.610 | 2/3 |
| choice | SWC_043 | recording_centered | 100 | total_delta, target0, recording_bidirectionality | +0.008 | -0.160 | 0.534/0.610 | 2/3 |

Decision: this closes the simple shared broad-anatomy repair branch. The best comparable rows remain one bidirectional recording short and also miss target0 and/or baseline controls, so they are not a GPU trigger.

## Shared-Family Iterative Manifest Gate

`docs/shared_family_iterative_manifest_gate.md` reruns the shared-family
target/control gate on the strict 8-recording, 2-subject iterative-pass
manifest using all families that pass its feasibility floor.

- rows: `56`
- candidates: `0`
- positive centered-delta rows: `20`
- max bidirectional recordings: `1`
- max bidirectional recording fraction: `0.250`
- decision: `no_shared_family_target_candidate`

| target | family | holdout | decision | delta shuffle | delta total | targets | bidir recs |
|---|---|---|---|---:|---:|---|---:|
| prior_side | thalamic | MFD_06 | reject: target1 | +0.299 | +0.362 | 0.954/0.095 | 1/4 |
| feedback | fiber_tracts | NYU-12 | reject: target0 | +0.168 | +0.049 | 0.415/0.703 | 1/4 |
| feedback | midbrain | NYU-12 | reject: target1 | +0.151 | +0.092 | 0.813/0.263 | 1/4 |
| stimulus_side | thalamic | MFD_06 | reject: target1 | +0.101 | +0.349 | 0.934/0.108 | 1/4 |
| prior_side | brainstem_interbrain | MFD_06 | reject: shuffle | +0.001 | -0.001 | 0.755/0.335 | 1/4 |
| feedback | broad_named_anatomy | NYU-12 | reject: shuffle | -0.002 | -0.008 | 0.571/0.476 | 1/4 |

Decision: stricter manifest support alone does not rescue the signal. The clean 2-subject panel is too narrow for a demo and still reaches only `1/4` same-recording bidirectional support, so the next branch must change the benchmark/control definition rather than further narrow this manifest.

## Next Benchmark/Control Options Audit

`docs/next_benchmark_control_options.md` ranks the remaining no-spend
branches after the current local negative audits.

- recommended next: `new manifest with prospective bidirectional support`
- closed branches: `17`
- decision: `no_local_training_trigger`
- GPU trigger: At least one local row on the proposed manifest must clear delta_vs_shuffle>=0, delta_vs_total>=0, target0>=0.55, target1>=0.55, and bidirectional_recording_fraction>=0.75 before training.

| priority | branch | status | next action |
|---:|---|---|---|
| 1 | new manifest with prospective bidirectional support | `recommended_next` | Do not launch GPU training from the projected support80 panel; its model-free family and feature-mode gates have no candidates. Redesign the target/control locally. |
| 86 | wheel-derived target family gate | `closed` | Do not spend on the tested wheel targets; move to a prospectively supported manifest. |
| 87 | reaction-dynamics wheel targets | `closed` | Do not spend on reaction-dynamics wheel targets; the near miss fails true-vs-shuffle and does not replicate across feature modes. |
| 88 | cell-type prior target/control gate | `closed` | Do not spend on broad ABC cell-class prior channels; they do not pass the local bidirectional gate. |

Decision: the current cached target, contextual target, wheel-derived target, reaction-dynamics target, cell-type prior target/control, waveform target/control, and meta-failure synthesis branches are closed as GPU triggers. The next aligned work is a prospectively supported benchmark/control redesign, still gated locally before any paid training.

## Behavior Cache Preflight

`docs/behavior_cache_preflight.md` inspects whether the active matched
HDF5 cache contains the richer behavior streams needed for the next
target/control branch.

- manifest recordings: `28`
- present files: `28`
- required stream coverage: `wheel=28/28`
- recordings needing behavior rebuild: `0`
- decision: `behavior_cache_ready`

Decision: the matched cache now has the required wheel stream, so the next no-spend step is the wheel-derived target family gate. GPU training remains blocked unless that local gate passes.

## Derived Target Family Gate

`docs/derived_target_family_gate.md` tests the recommended new
benchmark/control direction using three cached trial-field targets:
`contrast_strength`, `response_latency`, and `prior_engaged`.

- rows: `84`
- candidates: `0`
- positive centered-delta rows: `38`
- max bidirectional recordings: `3`
- max bidirectional recording fraction: `0.750`
- decision: `no_derived_target_family_candidate`

| target | trials | eligible recordings | recordings |
|---|---:|---:|---:|
| contrast_strength | 11556 | 28 | 28 |
| prior_engaged | 17882 | 28 | 28 |
| response_latency | 17868 | 28 | 28 |

| target | family | holdout | decision | delta shuffle | delta total | targets | bidir recs |
|---|---|---|---|---:|---:|---|---:|
| response_latency | broad_named_anatomy | KS014 | reject: shuffle | -0.004 | -0.005 | 0.714/0.745 | 3/4 |
| response_latency | hippocampal_formation | KS014 | reject: total baseline | +0.669 | -0.004 | 0.915/0.527 | 2/4 |
| prior_engaged | fiber_tracts | KS014 | reject: target1 | +0.263 | +0.220 | 0.850/0.473 | 2/4 |
| prior_engaged | fiber_tracts | CSH_ZAD_019 | reject: total baseline | +0.042 | -0.061 | 0.739/0.546 | 2/4 |
| response_latency | broad_named_anatomy | SWC_038 | reject: shuffle | -0.004 | -0.005 | 0.609/0.543 | 2/4 |
| contrast_strength | broad_named_anatomy | KS014 | reject: shuffle | -0.005 | -0.006 | 0.564/0.507 | 2/4 |

Decision: cached trial-field target redesign does not yet justify GPU training. `response_latency` gives the nearest symmetric row with `3/4` bidirectional recordings, but it still loses to the within-recording shuffle control. Other positive rows remain one-sided or fail the total-spike baseline.

## Contextual Target Family Gate

`docs/contextual_target_family_gate.md` tests trial-sequence target
definitions that are not direct task labels: `post_error`,
`prior_block_switch`, and `prior_block_late`.

- rows: `84`
- candidates: `0`
- positive centered-delta rows: `40`
- max bidirectional recordings: `2`
- max bidirectional recording fraction: `0.500`
- decision: `no_contextual_target_family_candidate`

| target | trials | eligible recordings | recordings |
|---|---:|---:|---:|
| post_error | 17854 | 28 | 28 |
| prior_block_late | 4798 | 28 | 28 |
| prior_block_switch | 7280 | 23 | 28 |

| target | family | holdout | decision | delta shuffle | delta total | targets | bidir recs |
|---|---|---|---|---:|---:|---|---:|
| post_error | fiber_tracts | SWC_043 | reject: shuffle | -0.031 | -0.050 | 0.527/0.472 | 2/4 |
| post_error | fiber_tracts | NYU-12 | reject: target0 | +0.083 | +0.130 | 0.411/0.679 | 1/4 |
| prior_block_late | thalamic | SWC_038 | reject: target0 | +0.022 | +0.047 | 0.094/0.943 | 1/4 |
| post_error | broad_named_anatomy | MFD_06 | reject: target0 | +0.013 | +0.009 | 0.476/0.500 | 1/4 |
| post_error | hippocampal_formation | NYU-12 | reject: target0 | +0.003 | +0.119 | 0.426/0.651 | 1/4 |
| post_error | broad_named_anatomy | SWC_038 | reject: total baseline | +0.002 | -0.069 | 0.502/0.536 | 1/4 |

Decision: trial-sequence context does not create a training trigger. The best contextual rows still fail the shuffle control, one global target direction, or the total-spike baseline, and max same-recording bidirectional support is only `2/4`.

## Wheel Target Family Gate

`docs/wheel_target_family_gate.md` tests target definitions derived
from cached wheel position: `wheel_active`, `wheel_displacement`,
and `choice_aligned_wheel`.

- rows: `84`
- candidates: `0`
- positive centered-delta rows: `39`
- max bidirectional recordings: `3`
- max bidirectional recording fraction: `0.750`
- decision: `no_wheel_target_family_candidate`

| target | trials | eligible recordings | recordings |
|---|---:|---:|---:|
| choice_aligned_wheel | 16549 | 23 | 28 |
| wheel_active | 16982 | 28 | 28 |
| wheel_displacement | 16967 | 28 | 28 |

| target | family | holdout | decision | delta shuffle | delta total | targets | bidir recs |
|---|---|---|---|---:|---:|---|---:|
| wheel_active | broad_named_anatomy | KS014 | reject: shuffle | -0.002 | -0.002 | 0.587/0.598 | 3/4 |
| wheel_displacement | broad_named_anatomy | KS014 | reject: shuffle | -0.008 | -0.009 | 0.556/0.593 | 3/4 |
| choice_aligned_wheel | broad_named_anatomy | SWC_043 | reject: recording bidirectionality | +0.008 | +0.007 | 0.558/0.584 | 2/4 |
| wheel_displacement | hippocampal_formation | KS014 | reject: shuffle | -0.019 | -0.009 | 0.788/0.370 | 2/4 |
| wheel_displacement | thalamic | MFD_06 | reject: target0 | +0.216 | +0.198 | 0.097/0.958 | 1/4 |
| wheel_displacement | thalamic | SWC_038 | reject: target0 | +0.211 | +0.039 | 0.111/0.955 | 1/4 |

Decision: wheel-derived targets only justify paid training if they clear the same true-vs-shuffle, total-baseline, global target, and same-recording bidirectional gate used by the prior audits.

## Matched-Region Model-Free Panel

`docs/model_free_matched_support80_hdf5_panel.md` runs the closed-form
parent-region ridge audit leave-subject-out across the HDF5-confirmed
28-recording matched support80 panel.

- holdouts: `7`
- model-free candidates: `0`
- positive centered-delta holdouts: `2/7`
- mean true-minus-shuffle centered AUC: `-0.003`
- decision: `no_model_free_panel_signal`

| holdout | decision | centered delta | target0 | target1 | rec support |
|---|---|---:|---:|---:|---:|
| CSH_ZAD_019 | no_model_free_true_region_advantage | -0.052 | 0.338 | 0.703 | 1/4 |
| KS014 | weak_model_free_true_region_advantage | +0.030 | 0.547 | 0.538 | 2/4 |
| MFD_06 | no_model_free_true_region_advantage | -0.016 | 0.567 | 0.451 | 2/4 |
| NR_0019 | weak_model_free_true_region_advantage | +0.079 | 0.776 | 0.249 | 3/4 |
| NYU-12 | no_model_free_true_region_advantage | -0.015 | 0.410 | 0.624 | 2/4 |
| SWC_038 | no_model_free_true_region_advantage | -0.032 | 0.629 | 0.336 | 0/4 |
| SWC_043 | no_model_free_true_region_advantage | -0.014 | 0.738 | 0.212 | 2/4 |

Decision: do not promote this panel to a broad training sweep. The model-free anatomical feature screen has zero passing holdouts; `KS014` and `NR_0019` have positive centered deltas, but fail bidirectional target-class and/or recording-support gates.

## Positive-Holdout Mechanism Audit

`docs/model_free_positive_holdouts_mechanism.md` inspects the two weak
positive centered-delta holdouts from the matched-region panel at target-class
and recording resolution.

| holdout | centered delta | target0 | target1 | positive recordings | interpretation |
|---|---:|---:|---:|---:|---|
| KS014 | +0.030 | 0.547 | 0.538 | 2/4 | not bidirectional |
| NR_0019 | +0.079 | 0.776 | 0.249 | 3/4 | not bidirectional |

Decision: these positive deltas are not a training trigger. `KS014` is marginal and below the bidirectional gate; `NR_0019` is strongly one-sided toward target-0 and fails target-1. Keep the next step no-spend: redesign the target/control or require a cleaner local model-free pass before any RunPod training.

## Recording-Bidirectional Model-Free Gate

`docs/model_free_recording_bidirectional_gate.md` applies the stricter
same-recording rule across the full matched panel: a recording counts only
when true labels beat the shuffled control for target0 and target1 inside
that same recording.

- candidates: `0/7`
- positive centered-delta holdouts: `2/7`
- mean bidirectional recording fraction: `0.036`
- decision: `no_recording_bidirectional_model_free_signal`

| holdout | centered delta | target0 | target1 | bidirectional recs | decision |
|---|---:|---:|---:|---:|---|
| CSH_ZAD_019 | -0.052 | 0.338 | 0.703 | 0/4 | reject: centered delta |
| KS014 | +0.030 | 0.547 | 0.538 | 0/4 | reject: global target0 |
| MFD_06 | -0.016 | 0.567 | 0.451 | 0/4 | reject: centered delta |
| NR_0019 | +0.079 | 0.776 | 0.249 | 0/4 | reject: global target1 |
| NYU-12 | -0.015 | 0.410 | 0.624 | 1/4 | reject: centered delta |
| SWC_038 | -0.032 | 0.629 | 0.336 | 0/4 | reject: centered delta |
| SWC_043 | -0.014 | 0.738 | 0.212 | 0/4 | reject: centered delta |

Decision: this closes the weak-positive loophole for the current matched panel. Only `NYU-12` has even one bidirectional held-out recording, and it still has negative centered true-minus-shuffle AUC. Do not spend on training until a new target/control produces at least one local pass under this recording-bidirectional gate.

## Region-Fraction Feature Gate

`docs/model_free_recording_bidirectional_gate_fractions.md` reruns the
same recording-bidirectional gate after normalizing each trial's parent-region
spike counts to fractions of that trial's total spikes.

- candidates: `0/7`
- positive centered-delta holdouts: `3/7`
- mean bidirectional recording fraction: `0.000`
- decision: `no_recording_bidirectional_model_free_signal`

Decision: simple region-composition normalization does not rescue the anatomical feature branch. It creates three positive centered-delta holdouts, but all are one-sided and have `0/4` bidirectional recordings.

## Recording-Centered Feature Gate

`docs/model_free_recording_bidirectional_gate_recording_centered.md` subtracts
each recording's own mean parent-region feature vector before ridge fitting.

- candidates: `0/7`
- positive centered-delta holdouts: `2/7`
- mean bidirectional recording fraction: `0.071`
- decision: `no_recording_bidirectional_model_free_signal`

Decision: feature-level recording centering is the least one-sided normalization so far, but it remains below the gate. `KS014` has only `1/4` bidirectional recordings and both positive-delta holdouts still miss global target0.

## Grandparent Recording-Centered Feature Gate

`docs/model_free_recording_bidirectional_gate_grandparent_recording_centered.md`
reruns the hardened local gate at coarser Allen grandparent granularity
with recording-centered features.

- candidates: `0/7`
- positive centered-delta holdouts: `5/7`
- positive holdouts: `CSH_ZAD_019, KS014, MFD_06, NR_0019, NYU-12`
- mean bidirectional recording fraction: `0.071`
- decision: `no_recording_bidirectional_model_free_signal`

Decision: coarser atlas granularity increases weak positive centered deltas, but it does not produce bidirectional evidence. The positive holdouts still fail global target0 and have at most `1/4` bidirectional recordings.

## Unit-Residual Feature Gate

`docs/model_free_recording_bidirectional_gate_unit_residuals.md` subtracts
each recording's expected region counts from every trial, using total spikes
times that recording's static unit-region distribution.

- candidates: `0/7`
- positive centered-delta holdouts: `6/7`
- positive holdouts: `CSH_ZAD_019, KS014, NR_0019, NYU-12, SWC_038, SWC_043`
- mean bidirectional recording fraction: `0.000`
- decision: `no_recording_bidirectional_model_free_signal`

Decision: residualizing static anatomical coverage increases the number of positive centered deltas, but does not create a valid transfer signal. Every positive holdout remains one target direction with `0/4` bidirectional recordings.

## Source-Target Pair Gate

`docs/model_free_source_target_pair_gate_recording_centered.md` trains
the same closed-form recording-centered anatomy classifier on one source
subject at a time and evaluates each target subject against the
within-recording shuffled-label control.

- source-target pairs: `42`
- candidates: `0`
- positive centered-delta pairs: `20`
- mean bidirectional recording fraction: `0.065`
- decision counts: `reject: centered delta: 22, reject: global target0: 12, reject: global target1: 8`
- decision: `no_source_target_model_free_signal`

Decision: single-source training does not reveal a hidden compatible animal pair. The best positive centered-delta pairs still fail global target0 or target1 and have at most `1/4` bidirectional target recordings.

## Family Source-Target Pair Gate

`docs/model_free_source_target_pair_gate_families_recording_centered.md`
combines the single-source split redesign with predefined family-aggregate
features and recording centering.

- source-target pairs: `42`
- candidates: `0`
- positive centered-delta pairs: `19`
- mean bidirectional recording fraction: `0.095`
- decision counts: `reject: centered delta: 29, reject: global target0: 10, reject: global target1: 3`
- decision: `no_source_target_model_free_signal`

Decision: combining source-target pairing with family aggregation still does not produce a local transfer candidate. It slightly increases same-recording bidirectional support, but top pairs remain below global target0/target1 and never exceed `1/4` bidirectional recordings.

## Model-Free Gate Blocker Audit

`docs/model_free_gate_blocker_audit.md` aggregates the current local
holdout and source-target model-free gates to identify which promotion
checks actually block the anatomy-transfer claim.

- rows audited: `168`
- candidates: `0`
- positive centered-delta rows: `86`
- max bidirectional recordings: `2`
- max bidirectional recording fraction: `0.500`
- blocker counts: `centered_delta=97, target0=130, target1=136, recording_bidirectionality=168`

| report | label | centered delta | target0 | target1 | bidir recs | missing checks |
|---|---|---:|---:|---:|---:|---|
| family centered l2=1 | KS014 | +0.081 | 0.510 | 0.549 | 2/4 | target0, target1, recording_bidirectionality |
| family centered | KS014 | +0.080 | 0.510 | 0.548 | 2/4 | target0, target1, recording_bidirectionality |
| family centered l2=100 | KS014 | +0.078 | 0.505 | 0.555 | 2/4 | target0, recording_bidirectionality |
| family feedback | NR_0019 | +0.011 | 0.532 | 0.500 | 2/4 | target0, target1, recording_bidirectionality |

Decision: the next useful experiment should not be another small feature or regularization variant. The universal blocker is same-recording bidirectionality, so any new benchmark/control proposal must first create target0+target1 evidence inside the same recordings before GPU training.

## Model-Free Recording Support Audit

`docs/model_free_recording_support_audit.md` aggregates per-recording
target0/target1 support across all current model-free holdout and
source-target gate artifacts.

- observations: `672`
- recordings: `28`
- bidirectional observations: `53`
- recordings with any bidirectional support: `19`
- max bidirectional observations/recording: `12`

| recording | subjects | observations | bidir obs | mean target0 | mean target1 |
|---|---|---:|---:|---:|---:|
| 6899a67d-2e53-4215-a52a-c7021b5da5d4_probe00 | MFD_06 | 24 | 12 | 0.566 | 0.524 |
| 03063955-2523-47bd-ae57-f7489dd40f15_probe01 | SWC_038 | 24 | 8 | 0.474 | 0.574 |
| e1931de1-cf7b-49af-af33-2ade15e8abe7_probe00 | KS014 | 24 | 8 | 0.592 | 0.444 |
| edd22318-216c-44ff-bc24-49ce8be78374_probe00 | CSH_ZAD_019 | 24 | 4 | 0.462 | 0.585 |

Decision: rare same-recording bidirectional observations are not concentrated enough to define a stable demo subset from the current cache. The next benchmark redesign should prospectively create target0+target1 evidence inside recordings, then rerun the same model-free local gate before GPU training.

## Recording Bidirectionality Prospectus

`docs/recording_bidirectionality_prospectus.md` aggregates per-recording
target0/target1 support across the current local-gate artifacts, including
the newer wheel, reaction-dynamics, cell-prior, waveform, and projected
support80 sweeps.

- observations: `8544`
- recordings: `35`
- bidirectional observations: `262`
- recordings with bidirectional support: `32`
- prospect recordings: `18`
- decision: `prospective_recording_leads_present_not_training_ready`

| recording | holdouts | observations | bidir obs | bidir sources | bidir targets | mean sym |
|---|---|---:|---:|---:|---:|---:|
| 6899a67d-2e53-4215-a52a-c7021b5da5d4_probe00 | MFD_06 | 288 | 33 | 9 | 11 | 0.228 |
| b887df2c-bb9c-44c9-a9c0-538da87b2cab_probe01 | NR_0019 | 288 | 23 | 9 | 9 | 0.222 |
| e1931de1-cf7b-49af-af33-2ade15e8abe7_probe00 | KS014 | 288 | 19 | 9 | 9 | 0.239 |
| b9c205c3-feac-485b-a89d-afc96d9cb280_probe00 | KS014 | 288 | 19 | 6 | 11 | 0.215 |

Decision: this prospectus can only inform the next prospective target/control rule. It is not a GPU trigger; the unchanged local gate must pass before training.

## Prospect-Lead Derived Target Gate

`docs/derived_target_family_gate_prospect_leads.md` reruns the derived
cached-target local gate on the 18-recording prospect-lead manifest.

- rows: `84`
- candidates: `3`
- max bidirectional recordings: `3`
- max bidirectional recording fraction: `1.000`
- decision: `derived_target_family_candidate`

| target | family | holdout | decision | delta shuffle | delta total | target0 | target1 | bidir recs |
|---|---|---|---|---:|---:|---:|---:|---:|
| response_latency | thalamic | MFD_06 | candidate | +0.050 | +0.012 | 0.687 | 0.716 | 1/1 |
| prior_engaged | broad_named_anatomy | NR_0019 | candidate | +0.033 | +0.004 | 0.844 | 0.603 | 1/1 |
| response_latency | broad_named_anatomy | NR_0019 | candidate | +0.021 | +0.009 | 0.615 | 0.686 | 1/1 |
| response_latency | broad_named_anatomy | KS014 | reject: shuffle | -0.004 | -0.005 | 0.698 | 0.704 | 3/4 |

## Prospect-Lead Candidate Validation

`docs/prospect_lead_candidate_validation.md` compares prospect-lead
candidates against the full-manifest derived target gate.

- prospect candidates: `3`
- validated candidates: `0`
- single-recording candidates: `3`
- subset-only candidates: `3`
- decision: `no_validated_prospect_lead_candidate`

Decision: prospect-lead rows remain design leads only. They do not justify GPU training until they validate outside the selected subset.

## Prospect-Lead Feature-Mode Validation

`docs/prospect_lead_feature_mode_validation.md` validates prospect-lead
derived target candidates across recording-centered, counts, fractions,
and unit-residual feature modes against the corresponding full-manifest gates.

- feature modes: `4`
- prospect candidates: `4`
- full-manifest candidates: `0`
- validated candidates: `0`
- single-recording candidates: `4`
- subset-only candidates: `4`
- decision: `no_validated_prospect_lead_feature_mode_candidate`

Decision: feature-mode variation does not validate the prospect-lead derived candidates. Keep the next step local and do not launch GPU training from these selected-subset rows.

## Prospect-Lead Subject Stability Audit

`docs/prospect_lead_subject_stability.md` checks whether the prospect-lead
derived candidates also hold on same-subject non-lead recordings.

- prospect candidates: `4`
- same-subject stable candidates: `0`
- candidates with non-lead failure: `4`
- decision: `no_same_subject_stable_prospect_candidate`

Decision: the prospect-lead rows are selected-recording effects, not subject-stable transfer signals. A future target/control rule must be stable across multiple recordings within the held-out subject before any GPU run.

## Subject-Stable Local Gate Prospectus

`docs/subject_stable_local_gate_prospectus.md` searches all current
local-gate rows for target/control definitions that are stable across
multiple recordings in the held-out subject.

- rows: `2428`
- subject-stable rows: `5`
- subject-stable candidates: `0`
- subject-stable one-failure rows: `1`
- subject-stable holdouts: `KS014`
- decision: `no_subject_stable_local_gate_candidate`

| source | target | feature | holdout | failures | delta shuffle | delta total | targets | bidir recs |
|---|---|---|---|---|---:|---:|---:|---:|
| reaction_recording_centered | wheel_reaction_latency | broad_named_anatomy | KS014 | shuffle | -0.001 | +0.003 | 0.667/0.715 | 3/4 |
| wheel_targets | wheel_active | broad_named_anatomy | KS014 | shuffle, total_baseline | -0.002 | -0.002 | 0.587/0.598 | 3/4 |
| reaction_recording_centered | post_stim_speedup | broad_named_anatomy | KS014 | shuffle, total_baseline | -0.004 | -0.002 | 0.608/0.584 | 3/4 |
| derived_recording_centered | response_latency | broad_named_anatomy | KS014 | shuffle, total_baseline | -0.004 | -0.005 | 0.714/0.745 | 3/4 |
| wheel_targets | wheel_displacement | broad_named_anatomy | KS014 | shuffle, total_baseline | -0.008 | -0.009 | 0.556/0.593 | 3/4 |

Decision: the best stable local branch is now a shuffle-control problem, not just a recording-support problem. The next redesign should target anatomical information that beats within-recording shuffled anatomy while preserving KS014-like subject stability.

## Subject-Stable Shuffle Seed Sensitivity

`docs/subject_stable_shuffle_seed_sensitivity.md` reruns the subject-stable
near misses across multiple within-recording shuffle seeds.

- cases: `5`
- robust shuffle-seed candidates: `0`
- max positive shuffle-delta fraction: `0.400`
- decision: `no_subject_stable_shuffle_seed_candidate`

| source | target | feature | holdout | positive seeds | candidate seeds | mean shuffle delta | mean total delta |
|---|---|---|---|---:|---:|---:|---:|
| derived | response_latency | broad_named_anatomy | KS014 | 0/5 | 0/5 | -0.0026 | -0.0053 |
| wheel | wheel_active | broad_named_anatomy | KS014 | 1/5 | 0/5 | -0.0008 | -0.0016 |
| wheel | wheel_displacement | broad_named_anatomy | KS014 | 0/5 | 0/5 | -0.0057 | -0.0085 |
| reaction | post_stim_speedup | broad_named_anatomy | KS014 | 0/5 | 0/5 | -0.0019 | -0.0024 |
| reaction | wheel_reaction_latency | broad_named_anatomy | KS014 | 2/5 | 2/5 | -0.0002 | +0.0027 |

Decision: the KS014 stable near misses are not robust to the within-recording shuffle seed. A future local trigger should require positive true-vs-shuffle evidence across multiple shuffle seeds before any GPU run.

## Model-Free Recording Directionality Audit

`docs/model_free_recording_directionality_audit.md` classifies every
per-recording target-support observation as bidirectional, target0-only,
target1-only, or neither across current model-free artifacts.

- observations: `1120`
- bidirectional: `80`
- target0-only: `302`
- target1-only: `311`
- neither: `427`
- one-sided fraction: `0.547`
- decision: `one_sided_recording_effects_are_common`

Decision: one-sided recording effects are common enough that future candidate screens must report target-direction classes before any global delta can be considered a training trigger.

## Symmetric Recording Support Audit

`docs/symmetric_recording_support_audit.md` ranks candidate rows by
recording-local `min(target0_improved, target1_improved)` so one-sided
effects cannot dominate the promotion order.

- rows: `280`
- candidates: `0`
- max bidirectional recordings: `2`
- max bidirectional recording fraction: `0.500`
- max mean symmetric support: `0.543`
- decision: `no_symmetric_recording_candidate`

| report | context | bidir recs | mean sym | min sym | one-sided |
|---|---|---:|---:|---:|---:|
| shared family target/control | choice / broad_named_anatomy / SWC_043 | 2/4 | 0.531 | 0.446 | 2 |
| shared family target/control | feedback / broad_named_anatomy / NYU-12 | 2/4 | 0.487 | 0.347 | 1 |
| family centered l2=100 | stimulus_side / KS014 | 2/4 | 0.485 | 0.358 | 1 |
| family centered l2=1 | stimulus_side / KS014 | 2/4 | 0.485 | 0.362 | 1 |

Decision: use this symmetric ranking before any future GPU trigger. It currently finds no candidate; even the best rows top out at `2/4` bidirectional recordings.

## Symmetric Threshold Sensitivity Audit

`docs/symmetric_threshold_sensitivity_audit.md` sweeps the target-improvement
and bidirectional-recording thresholds for the symmetric recording-support
gate.

- threshold settings: `20`
- settings with candidates: `8`
- strict candidates at target>=0.55 and bidir>=0.75: `0`
- strict max bidirectional recordings: `2`
- decision: `threshold_relaxation_needed_for_candidates`

At the default target threshold (`0.55`), candidates only appear when recording support is relaxed to `0.25` (`3` candidates).

Decision: the current failure is not a tiny threshold miss. A candidate at the default target floor requires accepting only `1/4` bidirectional recordings, which is too weak for a cross-animal demo trigger.

## Symmetric Strict Failure Mode Audit

`docs/symmetric_strict_failure_modes.md` ranks the nearest rows
against the strict symmetric promotion gate and reports the exact
missing requirements.

- rows: `280`
- strict candidates: `0`
- global-target-clear rows: `4`
- one-recording-short and global-clear rows: `0`
- blocker counts: `global_target0=197, global_target1=215, recording_bidirectionality=280`
- decision: `strict_failure_modes_identified`

| report | context | blockers | targets | bidir recs | missing | mean sym |
|---|---|---|---|---:|---:|---:|
| shared family target/control | feedback / broad_named_anatomy / NYU-12 | recording_bidirectionality, global_target0 | 0.540/0.554 | 2/3 | 1 | 0.487 |
| shared family target/control | choice / broad_named_anatomy / SWC_043 | recording_bidirectionality, global_target0 | 0.534/0.610 | 2/3 | 1 | 0.531 |
| family centered l2=1 | stimulus_side / KS014 | recording_bidirectionality, global_target0, global_target1 | 0.510/0.549 | 2/3 | 1 | 0.485 |
| family centered | stimulus_side / KS014 | recording_bidirectionality, global_target0, global_target1 | 0.510/0.548 | 2/3 | 1 | 0.484 |
| family centered l2=100 | stimulus_side / KS014 | recording_bidirectionality, global_target0 | 0.505/0.555 | 2/3 | 1 | 0.485 |

Decision: there is no clean one-recording-short row that already clears both global target floors. The nearest actionable branch is a local redesign around shared broad-anatomy rows, where target0 is marginally below threshold and recording support is one hit short.

## Model-Free Recording Replication Audit

`docs/model_free_recording_replication_audit.md` tests whether a
recording subset selected from fixed discovery reports keeps bidirectional
support in held-out validation report families.

- recording-subject rows: `28`
- selected by discovery rule: `3`
- replicated in validation: `0`
- decision: `no_replicating_recording_rule`

| subject | recording | selected | replicated | discovery bidir | validation bidir | validation target0 | validation target1 |
|---|---|---|---|---:|---:|---:|---:|
| KS014 | e1931de1-cf7b-49af-af33-2ade15e8abe7_probe00 | True | False | 4/4 | 3/14 | 0.479 | 0.491 |
| MFD_06 | 6899a67d-2e53-4215-a52a-c7021b5da5d4_probe00 | True | False | 3/4 | 9/14 | 0.557 | 0.530 |
| KS014 | 16693458-0801-4d35-a3f1-9115c7e5acfd_probe01 | True | False | 3/4 | 1/14 | 0.517 | 0.526 |
| CSH_ZAD_019 | edd22318-216c-44ff-bc24-49ce8be78374_probe00 | False | False | 3/4 | 1/14 | 0.525 | 0.518 |

Decision: recording-subset selection is not currently a credible demo path. The selected discovery recordings lose bidirectional target support in validation, so the next local work should redesign the target/control or matched manifest rather than narrow this cache.

## Family-Aggregate Recording-Centered Gate

`docs/model_free_family_bidirectional_gate_recording_centered.md` combines
predefined parent-region family aggregates with feature-level recording
centering and the same same-recording bidirectional gate.

- candidates: `0/7`
- positive centered-delta holdouts: `4/7`
- mean bidirectional recording fraction: `0.179`
- decision: `no_recording_bidirectional_model_free_signal`

Decision: this is the strongest local near miss so far, but still not a training trigger. `KS014` reaches centered delta `+0.080` and `2/4` bidirectional recordings, yet misses global target0 at `0.510`.

## Family-Aggregate L2 Sensitivity

The strongest family-aggregate near-miss gate was rerun across ridge
regularization strengths to check whether the local decision is an
artifact of the default `l2=10` setting.

| l2 | candidates | positive deltas | mean bidir rec frac | decision |
|---:|---:|---:|---:|---|
| 1 | 0/7 | 4/7 | 0.179 | `no_recording_bidirectional_model_free_signal` |
| 10 | 0/7 | 4/7 | 0.179 | `no_recording_bidirectional_model_free_signal` |
| 100 | 0/7 | 4/7 | 0.179 | `no_recording_bidirectional_model_free_signal` |

Decision: the family near miss is not a ridge-regularization artifact. The candidate count, positive-delta count, and mean bidirectional recording fraction are unchanged across the tested l2 range.

## KS014 Family Near-Miss Mechanism

`docs/model_free_family_ks014_near_miss_mechanism.md` decomposes the
strongest family-aggregate near miss by family contribution.

- bidirectional family candidates: `0`
- decision: `No family contribution is bidirectional enough to explain a promotable signal. The KS014 near miss is still a mixture of one-sided family movements.`

| family | class | mean delta | target0 | target1 | recordings |
|---|---|---:|---:|---:|---:|
| midbrain | weak_or_mixed | -0.016 | 0.410 | 0.547 | 2/4 |
| broad_named_anatomy | target0_only | +0.015 | 0.589 | 0.456 | 2/4 |
| cortical_retrosplenial | target1_only | +0.016 | 0.130 | 0.898 | 3/4 |
| fiber_tracts | target0_only | +0.005 | 0.657 | 0.465 | 2/4 |
| hippocampal_formation | target1_only | -0.004 | 0.206 | 0.724 | 2/4 |

Decision: the KS014 family-level near miss is a mixture of one-sided family movements, not a hidden bidirectional anatomical mechanism.

## Family-Aggregate Alternative Target Gates

`prior_side` and `feedback` were also tested with recording-centered
family-aggregate features, using the same same-recording bidirectional gate.

| target | candidates | positive deltas | mean bidir rec frac | notable positive holdouts | decision |
|---|---:|---:|---:|---|---|
| prior_side | 0/7 | 6/7 | 0.107 | CSH_ZAD_019, KS014, MFD_06, NR_0019, NYU-12, SWC_043 | `no_recording_bidirectional_model_free_signal` |
| feedback | 0/7 | 4/7 | 0.107 | CSH_ZAD_019, MFD_06, NR_0019, SWC_043 | `no_recording_bidirectional_model_free_signal` |

Decision: family aggregation increases some positive centered deltas on alternative targets, especially `prior_side`, but still produces zero candidate holdouts. The failure remains the same: global or same-recording bidirectional target evidence does not hold.

## Alternative Target Bidirectional Gates

Two additional trial targets exposed by the cached IBL trials were tested
through the same recording-bidirectional model-free gate.

| target | candidates | positive deltas | mean bidir rec frac | notable positive holdouts | decision |
|---|---:|---:|---:|---|---|
| prior_side | 0/7 | 3/7 | 0.000 | KS014, NR_0019, SWC_043 | `no_recording_bidirectional_model_free_signal` |
| feedback | 0/7 | 4/7 | 0.000 | MFD_06, NR_0019, SWC_038, SWC_043 | `no_recording_bidirectional_model_free_signal` |

Decision: `prior_side` and `feedback` do not rescue the matched-panel branch. Both produce zero candidate holdouts and zero mean same-recording bidirectional support. More positive global centered deltas are still class-direction artifacts under the stricter gate.
