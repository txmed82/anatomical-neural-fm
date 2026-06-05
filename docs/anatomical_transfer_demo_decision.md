# Anatomical Transfer Demo Decision

## Current Claim

The project has a real, narrow contribution candidate for open computational neuroscience:
a reproducible cross-animal anatomical readout for post-error response-latency
extremes using a fixed `broad_named_anatomy` aggregate. This is useful because
it gives an auditable, open-data path for testing whether conserved anatomical
composition carries behavior-linked signal across animals.

The project does not yet support the stronger claim that a trained neural
foundation model has learned an anatomical transfer mechanism. The A100 pilot
and the cloud-aligned training readout were negative for that claim.

## How Close We Are

Ready to package:

- Model-free demo: `docs/model_free_anatomical_transfer_demo_package.md`
- Fixed train-path bridge: `docs/fixed_broad_family_train_arm_runpod_panel.md`
- Strict prediction gate: `docs/fixed_broad_family_train_arm_prediction_gate.md`

Best current evidence:

| holdout | status | centered delta vs shuffle | recording-local gate |
|---|---|---:|---|
| `NR_0019` | strict fixed-feature candidate | `+0.0036` | `4/4` bidirectional recordings |
| `CSHL045` | aggregate-positive only | `+0.0132` | `2/4` bidirectional recordings |

Interpretation: `NR_0019` is the cleanest demo holdout. `CSHL045` should be
reported as supportive aggregate evidence, not as a strict recording-local
candidate.

## Roadmap

### 1. Package the narrow open-science result

Prepare the contribution as a transparent benchmark/demo, not as a foundation
model claim:

- fixed `broad_named_anatomy` feature definition
- exact true-vs-within-recording-shuffle controls
- held-out-animal evaluation
- trial-paired prediction gate
- all scripts, manifests, and prediction rows committed

Success bar: another user can rerun the documented commands and recover the
same `NR_0019` candidate decision.

### 2. Add a no-spend local mechanism bridge

Before any more GPU spend, implement a constrained training branch that forces
the model to use the proven fixed-family signal as an explicit auxiliary input
or head, then compare:

- fixed-family-only arm
- transformer-only arm
- transformer plus fixed-family auxiliary arm
- matched within-recording shuffle controls

Success bar: local prediction rows must pass the same target0, target1, and
recording-local bidirectionality gate on at least `NR_0019`.

### 3. Only then run a bounded cloud confirmation

If the local constrained branch passes, run one cheap cloud confirmation with:

- one holdout first: `NR_0019`
- one seed first
- true plus within-recording shuffle
- L4 or the cheapest available GPU sufficient for the run
- hard max cost below the existing `$100` cap, preferably below `$8`

Success bar: cloud predictions reproduce the local gate and remain positive
against shuffle.

### 4. Broaden only after replication

Do not broaden to many animals or tasks until the constrained mechanism
replicates on `NR_0019`. If it does, add `CSHL045` as the next diagnostic case
and treat failures by recording, not only by aggregate AUC.

## Practical Next Step

The next code step should be the no-spend constrained mechanism bridge. The
first version should run locally and emit the same `eval_predictions.jsonl`
schema as the fixed-feature arm, so the existing prediction-gate audit can be
reused without changing the success criterion.
